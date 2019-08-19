<template>
    <div id="home">
        <Breadcrumb :style="{margin: '24px 0'}">
            <BreadcrumbItem>外来车辆信息</BreadcrumbItem>
        </Breadcrumb>
        <Content :style="{padding: '24px', minHeight: '600px', background: '#fff'}">
            <Row type="flex" justify="start" align="middle">
                <Select v-model="status" placeholder="全部状态" style="width:100px">
                    <Option v-for="item in statusList" :value="item.value" :key="item.value">{{ item.label }}
                    </Option>
                </Select>
                <divider type="vertical"></divider>
                <Input v-model="searchText" placeholder="请输入车牌号" style="width: 300px"/>
                <Button type="primary" style="margin-left: 10px">搜索</Button>
            </Row>
            <div style="margin-top: 20px">
                <Table border ref="selection" :columns="columns" :data="tableData"></Table>
                <div style="margin: 10px;overflow: hidden">
                </div>
            </div>
            <div style="float: right;">
                <Page :total="1" :current="1" @on-change="changePage" show-total show-sizer show-elevator></Page>
            </div>
        </Content>
    </div>
</template>
<script>
    export default {
        data() {
            return {
                status: '',
                filter: '',
                searchText: '',
                statusList: [
                    {
                        value: '全部状态',
                        label: '全部状态'
                    },
                    {
                        value: '停泊',
                        label: '停泊'
                    },
                    {
                        value: '已驶离',
                        label: '已驶离'
                    }
                ],
                filterList: [
                    {
                        value: '车牌号',
                        label: '车牌号'
                    }
                ],
                columns: [
                    {type: 'selection', width: 60, align: 'center'},
                    {title: '当前状态', key: 'status'},
                    {title: '车型', key: 'type'},
                    {title: '车牌号', key: 'plateNumber'},
                    {title: '进库时间', key: 'entryTime'},
                    {title: '出库时间', key: 'exitTime'},
                    {title: '产生费用', key: 'price'},
                    {
                        title: '操作',
                        key: 'action',
                        width: 200,
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
                tableData: [
                    {
                        status: "停泊",
                        type: "广汽传祺GS3",
                        plateNumber: "苏BH2222",
                        entryTime: "2019-08-19 14:30",
                        exitTime: "暂未出库",
                        price: "暂无"

                    },
                    {
                        status: "已驶离",
                        type: "宝骏530",
                        plateNumber: "豫A1A350",
                        entryTime: "2019-08-19 14:30",
                        exitTime: "2019-08-19 16:30",
                        price: "10元"
                    },
                    {
                        status: "已驶离",
                        type: "奔驰GLA",
                        plateNumber: "苏EB06E6",
                        entryTime: "2019-08-18 21:39",
                        exitTime: "2019-08-19 06:30",
                        price: "100元"
                    },
                    {
                        status: "已驶离",
                        type: "奇瑞瑞虎",
                        plateNumber: "沪B69999",
                        entryTime: "2019-08-20 10:30",
                        exitTime: "2019-08-20 12:30",
                        price: "30元"
                    },
                    {
                        status: "停泊",
                        type: "沃尔沃XC60",
                        plateNumber: "贵AP2168",
                        entryTime: "2019-08-20 10:30",
                        exitTime: "暂未出库",
                        price: "暂无"
                    },
                ],
            }
        },
        methods: {
            remove(index) {
                let that = this;
                this.$Modal.confirm({
                    title: "删除",
                    content: "确认要删除该记录吗?",
                    onOk() {
                        that.tableData.splice(index, 1);
                    }
                })
            },
            changePage() {
            }
        }
    }
</script>
