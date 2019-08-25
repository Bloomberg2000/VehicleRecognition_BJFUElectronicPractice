<template>
    <div id="home">
        <Breadcrumb :style="{margin: '24px 0'}">
            <BreadcrumbItem>外来车辆信息</BreadcrumbItem>
        </Breadcrumb>
        <Content :style="{padding: '24px', minHeight: '600px', background: '#fff'}">
            <Row type="flex" justify="start" align="middle">
                <Select ref="status" v-model="status" placeholder="全部状态" style="width:100px" clearable>
                    <Option v-for="item in statusList" :value="item.value" :key="item.value">{{ item.label }}
                    </Option>
                </Select>
                <divider type="vertical"></divider>
                <Input v-model="filterText" placeholder="请输入车牌号" style="width: 300px"/>
                <Button type="primary" style="margin-left: 10px" @click="doSearch">搜索</Button>
                <Divider type="vertical"/>
                <Button style="margin-left: 10px" @click="clearSearch">清除</Button>
            </Row>
            <div style="margin-top: 20px">
                <Table border ref="selection" :columns="columns" :data="tableData"></Table>
            </div>
            <div style="margin: 10px;overflow: hidden"></div>
            <div style="float: right;">
                <Page :total="pageData.dataCount" :current="pageData.currentPage" :page-size="pageData.pageSize"
                      :page-size-opts="[5,10,15,20,25,30]"
                      @on-change="changePage"
                      @on-page-size-change="changePageSize" show-total
                      show-sizer show-elevator></Page>
            </div>
        </Content>
    </div>
</template>
<script>
    import {ParkingLog} from "../assets/js/url";
    import axios from 'axios'

    export default {
        inject: ['login'],
        data() {
            return {
                status: '',
                filterText: '',
                statusList: [
                    {
                        value: '停泊',
                        label: '停泊'
                    },
                    {
                        value: '驶离',
                        label: '驶离'
                    }
                ],
                columns: [
                    {title: '当前状态', key: 'status'},
                    {title: '车型', key: 'plateColor'},
                    {title: '车牌号', key: 'plateNumber'},
                    {title: '进库时间', key: 'enterTime'},
                    {title: '出库时间', key: 'outTime'},
                    {title: '产生费用', key: 'cost'},
                    {
                        title: '操作',
                        key: 'action',
                        width: 100,
                        align: 'center',
                        render: (h, params) => {
                            return h('div', [
                                h('Button', {
                                    props: {
                                        type: 'error',
                                        size: 'small'
                                    },
                                    on: {
                                        click: () => {
                                            this.remove(params.index)
                                        }
                                    }
                                }, '删除信息')
                            ]);
                        }
                    }
                ],
                tableData: [],
                pageData: {
                    totalPage: 0,
                    dataCount: 0,
                    currentPage: 1,
                    pageSize: 10
                }
            }
        },
        mounted() {
            this.getForeignVehicalList(this.pageData.pageSize, 1);
            if (this.$store.state.currentUserID === "") {
                this.$Message.info("请先登录");
                this.tableData = [];
                this.login();
            }
        },
        methods: {
            getForeignVehicalList(pageSize, pageNum) {
                axios.get(ParkingLog, {
                    params: {
                        status: this.status,
                        filterText: this.filterText,
                        pageSize: pageSize,
                        pageNum: pageNum,
                        type: "外来车"
                    }
                }).then(res => {
                    this.tableData = res.data.queryData;
                    for (let data of this.tableData) {
                        data.plateColor = (data.plateColor === 'green' ? '新能源车' : '燃油车');
                        data.cost = (data.cost === 0 ? '暂无' : data.cost + '元');
                    }
                    let pageData = res.data.data;
                    this.pageData.totalPage = pageData.totalPage;
                    this.pageData.dataCount = pageData.dataCount;
                    this.pageData.currentPage = pageData.currentPage;
                }).catch(err => {
                    this.$Message.error("列表查询出错，请刷新页面" + err.response.data.message);
                })
            },
            doSearch() {
                this.pageData.currentPage = 1;
                this.getForeignVehicalList(this.pageData.pageSize, this.pageData.currentPage)
            },
            clearSearch() {
                this.$refs.status.clearSingleSelect();
                this.filterText = '';
                this.pageData.currentPage = 1;
                this.getForeignVehicalList(this.pageData.pageSize, this.pageData.currentPage)
            },
            remove(index) {
                let that = this;
                this.$Modal.confirm({
                    title: "删除",
                    content: "确认要删除该记录吗?",
                    onOk() {
                        axios.delete(ParkingLog + '/' + that.tableData[index].id)
                            .then(
                                res => {
                                    that.$Message.error(res.data.data.message);
                                })
                            .catch(
                                err => {
                                    that.$Message.error(err.response.data.message);
                                }
                            );
                        that.tableData.splice(index, 1);
                    }
                })
            },
            changePage(pageNum) {
                this.getForeignVehicalList(this.pageData.pageSize, pageNum)
            },
            changePageSize(pageSize) {
                this.pageData.currentPage = 1;
                this.pageData.pageSize = pageSize
                this.getForeignVehicalList(this.pageData.pageSize, this.pageData.currentPage)
            },
        },
        computed: {
            currentUserID() {
                return this.$store.state.currentUserID;
            },
        },
        watch: {
            currentUserID(userID) {
                // 用户ID变化重新获取用户信息
                if (userID !== "") {
                    this.getForeignVehicalList(this.pageData.pageSize, 1);
                } else {
                    this.$Message.info("请先登录");
                    this.tableData = [];
                    this.login();
                }
            },
        },
    }
</script>
