<template>
    <div id="home">
        <Breadcrumb :style="{margin: '24px 0'}">
            <BreadcrumbItem>停车场实时信息</BreadcrumbItem>
        </Breadcrumb>
        <Content :style="{padding: '24px', minHeight: '600px', background: '#fff'}">
            <Row type="flex" justify="start" align="middle">
                <Select ref="status" v-model="status" placeholder="全部状态" style="width:90px" clearable>
                    <Option v-for="item in statusList" :value="item.value" :key="item.value">{{ item.label }}
                    </Option>
                </Select>
                <divider type="vertical"></divider>
                <Select ref="carType" v-model="carType" placeholder="全部类型" style="width:90px" clearable>
                    <Option v-for="item in carTypeList" :value="item.value" :key="item.value">{{ item.label }}
                    </Option>
                </Select>
                <divider type="vertical"></divider>
                <Select ref="filterMethod" v-model="filterMethod" placeholder="筛选条件" @on-change="filterChange"
                        style="width:100px" clearable>
                    <Option v-for="item in filterList" :value="item.value" :key="item.value">{{ item.label }}
                    </Option>
                </Select>
                <Divider type="vertical"/>
                <Input v-model="filterText" :placeholder="placeHolder" style="width: 150px"/>
                <Divider type="vertical"/>
                <DatePicker v-model="filterTime" type="datetimerange" placeholder="筛选入库时间"
                            style="width: 300px"></DatePicker>
                <Divider type="vertical"/>
                <ButtonGroup>
                    <Button type="primary" style="margin-left: 10px" @click="doSearch">搜索</Button>
                    <Button @click="clearSearch">清除</Button>
                </ButtonGroup>
            </Row>
            <div style="margin-top: 20px">
                <Table border ref="selection" :columns="columns" :data="tableData"></Table>
                <div style="margin: 10px;overflow: hidden"></div>
            </div>
            <Button style="visibility: hidden" type="error">批量删除</Button>
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
                timer: '',
                placeHolder: "请选择筛选条件",
                filterText: '',
                filterMethod: '',
                filterTime: [],
                filterList: [
                    {
                        value: '车牌号',
                        label: '车牌号'
                    },
                    {
                        value: '车位号',
                        label: '车位号'
                    }
                ],
                statusList: [
                    {
                        value: '停泊',
                        label: '停泊'
                    },
                    {
                        value: '驶离',
                        label: '驶离'
                    },
                    {
                        value: '外出',
                        label: '外出'
                    }
                ],
                carType: '',
                carTypeList: [
                    {
                        value: '外来车',
                        label: '外来车'
                    },
                    {
                        value: '业主车',
                        label: '业主车'
                    }
                ],
                columns: [
                    {title: '当前状态', key: 'status'},
                    {title: '类型', key: 'type'},
                    {title: '车型', key: 'plateColor'},
                    {title: '车位号', key: 'spaceName'},
                    {title: '车位类型', key: 'spaceType'},
                    {title: '车牌号', key: 'plateNumber'},
                    {title: '进库时间', key: 'enterTime'},
                    {title: '出库时间', key: 'outTime'},
                    {title: '产生费用', key: 'cost', width: 100},
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
                                        size: 'small',
                                        disabled: this.tableData[params.index].spaceName !== '-'
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
                freeChargeParingPlace: 0,
                freeNormalParingPlace: 0,
                pageData: {
                    totalPage: 0,
                    dataCount: 0,
                    currentPage: 1,
                    pageSize: 10
                },
            }
        },
        destroyed() {
            clearInterval(this.timer);
        },
        mounted() {
            if (this.$store.state.currentUserID === "") {
                this.$Message.info("请先登录");
                this.tableData = [];
                this.login();
            }
            let _this = this;
            // 实时获取登录态
            _this.getParkingLotInfoList(this.pageData.pageSize, 1);
            clearInterval(this.timer);
            this.timer = window.setInterval(function () {
                _this.getParkingLotInfoList(_this.pageData.pageSize, _this.pageData.currentPage);
            }, 5000);
        },
        methods: {
            getParkingLotInfoList(pageSize, pageNum) {
                axios.get(ParkingLog, {
                    params: {
                        status: this.status,
                        filterMethod: this.filterMethod,
                        filterText: this.filterText,
                        startTime: this.filterTime[0],
                        endTime: this.filterTime[1],
                        pageSize: pageSize,
                        pageNum: pageNum,
                        type: this.carType
                    }
                }).then(res => {
                    let queryData = res.data.queryData;
                    let tableData = [];
                    for (let data of queryData) {
                        let spaceName = '';
                        let spaceType = '';
                        if (!data[1] && typeof (data[1]) != "undefined" && data[1] !== 0) {
                            spaceName = '-';
                            spaceType = '-'
                        } else {
                            spaceName = data[1].spaceName
                            spaceType = data[1].type
                        }
                        tableData.push({
                            id: data[0].id,
                            cost: data[0].cost + '元',
                            enterTime: data[0].enterTime,
                            outTime: data[0].outTime,
                            plateColor: (data[0].plateColor === 'green') ? '新能源车' : '燃油车',
                            plateNumber: data[0].plateNumber,
                            status: data[0].status,
                            type: data[0].type,
                            spaceName: spaceName,
                            spaceType: spaceType
                        })
                    }
                    this.tableData = tableData;
                    let pageData = res.data.data;
                    this.freeNormalParingPlace = pageData.freeNormalParingPlace;
                    this.freeChargeParingPlace = pageData.freeChargeParingPlace;
                    this.pageData.totalPage = pageData.totalPage;
                    this.pageData.dataCount = pageData.dataCount;
                    this.pageData.currentPage = pageData.currentPage;
                }).catch(err => {
                    this.$Message.error("列表查询出错，请刷新页面" + err.response.data.message);
                })
            },
            doSearch() {
                this.pageData.currentPage = 1;
                this.getParkingLotInfoList(this.pageData.pageSize, this.pageData.currentPage)
            },
            clearSearch() {
                this.$refs.status.clearSingleSelect();
                this.$refs.carType.clearSingleSelect();
                this.filterText = '';
                this.filterTime = '';
                this.pageData.currentPage = 1;
                this.getParkingLotInfoList(this.pageData.pageSize, this.pageData.currentPage)
            },
            filterChange(text) {
                if (typeof (text) === "undefined") {
                    this.placeHolder = "请选择筛选条件"
                    return;
                }
                this.placeHolder = "请输入" + text
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
                this.getParkingLotInfoList(this.pageData.pageSize, pageNum)
            },
            changePageSize(pageSize) {
                this.pageData.currentPage = 1;
                this.pageData.pageSize = pageSize
                this.getParkingLotInfoList(this.pageData.pageSize, this.pageData.currentPage)
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
                    this.getParkingLotInfoList(this.pageData.pageSize, 1);
                } else {
                    this.$Message.info("请先登录");
                    this.tableData = [];
                    this.login();
                }
            },
        },
    }
</script>
