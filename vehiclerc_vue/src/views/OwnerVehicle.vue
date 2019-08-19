<template>
    <div id="home">
        <Breadcrumb :style="{margin: '24px 0'}">
            <BreadcrumbItem>业主车辆信息</BreadcrumbItem>
        </Breadcrumb>
        <Content :style="{padding: '24px', minHeight: '600px', background: '#fff'}">
            <Row type="flex" justify="start" align="middle">
                <Col span="22">
                    <Select v-model="status" placeholder="全部状态" style="width:100px">
                        <Option v-for="item in statusList" :value="item.value" :key="item.value">{{ item.label }}
                        </Option>
                    </Select>
                    <divider type="vertical"></divider>
                    <Select v-model="filter" placeholder="筛选条件" @on-change="filterChange" style="width:100px">
                        <Option v-for="item in filterList" :value="item.value" :key="item.value">{{ item.label }}
                        </Option>
                    </Select>
                    <divider type="vertical"></divider>
                    <Input v-model="searchText" :placeholder="placeHolder" style="width: 300px"/>
                    <Button type="primary" style="margin-left: 10px">搜索</Button>
                </Col>
                <Col span="2">
                    <Button type="text" @click="addModal = true">
                        <Icon type="md-add"/>
                        增加信息
                    </Button>
                </Col>
            </Row>
            <div style="margin-top: 20px">
                <Table border ref="selection" :columns="columns" :data="tableData"
                       @on-selection-change="selectionChange"></Table>
                <div style="margin: 10px;overflow: hidden">
                </div>
            </div>

            <Button type="error" @click="batchDeletion">批量删除</Button>
            <div style="float: right;">
                <Page :total="1" :current="1" @on-change="changePage" show-total show-sizer show-elevator></Page>
            </div>
        </Content>
        <Modal
                v-model="addModal"
                title="业主车辆信息增加"
                :closable="false"
                @on-ok="doAdd"
                @on-cancel="cancelOrNot('add')">
            <Form :model="AddModalForm" :label-width="80">
                <FormItem label="车主姓名">
                    <Input v-model="AddModalForm.ownerName" placeholder="请输入车主姓名"></Input>
                </FormItem>
                <FormItem label="身份证号">
                    <Input v-model="AddModalForm.ownerIDNum" placeholder="请输入身份证号"></Input>
                </FormItem>
                <FormItem label="电话号码">
                    <Input v-model="AddModalForm.ownerPhoneNum" placeholder="请输入电话号码"></Input>
                </FormItem>
                <FormItem label="住址">
                    <Input v-model="AddModalForm.ownerAddress" placeholder="请输入车主住址"></Input>
                </FormItem>
                <FormItem label="车型">
                    <Input v-model="AddModalForm.type" placeholder="请输入车型"></Input>
                </FormItem>
                <FormItem label="车牌号">
                    <Input v-model="AddModalForm.plateNumber" placeholder="请输入车牌号"></Input>
                </FormItem>
            </Form>
        </Modal>
        <Modal
                v-model="editModal"
                title="业主车辆信息编辑"
                :closable="false"
                @on-ok="doEdit"
                @on-cancel="cancelOrNot('edit')">
            <Form :model="EditModalForm" :label-width="80">
                <FormItem label="车主姓名">
                    <Input v-model="EditModalForm.ownerName" placeholder="请输入车主姓名"></Input>
                </FormItem>
                <FormItem label="身份证号">
                    <Input v-model="EditModalForm.ownerIDNum" placeholder="请输入身份证号"></Input>
                </FormItem>
                <FormItem label="电话号码">
                    <Input v-model="EditModalForm.ownerPhoneNum" placeholder="请输入电话号码"></Input>
                </FormItem>
                <FormItem label="住址">
                    <Input v-model="EditModalForm.ownerAddress" placeholder="请输入车主住址"></Input>
                </FormItem>
                <FormItem label="车型">
                    <Input v-model="EditModalForm.type" placeholder="请输入车型"></Input>
                </FormItem>
                <FormItem label="车牌号">
                    <Input v-model="EditModalForm.plateNumber" placeholder="请输入车牌号"></Input>
                </FormItem>
            </Form>
        </Modal>
    </div>
</template>
<script>
    export default {
        data() {
            return {
                addModal: false,
                editModal: false,
                status: '',
                filter: '',
                searchText: '',
                placeHolder: '请选择筛选条件',
                AddModalForm: {
                    ownerName: '',
                    ownerIDNum: '',
                    ownerPhoneNum: '',
                    ownerAddress: '',
                    type: '',
                    plateNumber: ''
                },
                EditModalForm: {
                    ownerName: '',
                    ownerIDNum: '',
                    ownerPhoneNum: '',
                    ownerAddress: '',
                    type: '',
                    plateNumber: ''
                },
                selection: [],
                statusList: [
                    {
                        value: '全部状态',
                        label: '全部状态'
                    },
                    {
                        value: '外出',
                        label: '外出'
                    },
                    {
                        value: '停泊',
                        label: '停泊'
                    }
                ],
                filterList: [
                    {
                        value: '车牌号',
                        label: '车牌号'
                    },
                    {
                        value: '车主姓名',
                        label: '车主姓名'
                    },
                    {
                        value: '车主住址',
                        label: '车主住址'
                    },
                    {
                        value: '车主身份证号',
                        label: '车主身份证号'
                    }
                ],
                columns: [
                    {type: 'selection', width: 60, align: 'center'},
                    {title: '编号', key: 'id'},
                    {title: '车型', key: 'type'},
                    {title: '车牌号', key: 'plateNumber'},
                    {title: '车主姓名', key: 'ownerName'},
                    {title: '车主住址', key: 'ownerAddress'},
                    {title: '当前状态', key: 'status'},
                    {
                        title: '操作',
                        key: 'action',
                        width: 200,
                        align: 'center',
                        render: (h, params) => {
                            return h('div', [
                                h('Button', {
                                    props: {
                                        type: 'default',
                                        size: 'small'
                                    },
                                    style: {
                                        marginRight: '5px'
                                    },
                                    on: {
                                        click: () => {
                                            this.show(params.index)
                                        }
                                    }
                                }, '查看'),
                                h('Button', {
                                    props: {
                                        type: 'default',
                                        size: 'small'
                                    },
                                    style: {
                                        marginRight: '5px'
                                    },
                                    on: {
                                        click: () => {
                                            this.beforeEdit(params.index)
                                        }
                                    }
                                }, '编辑'),
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
                                }, '删除')
                            ]);
                        }
                    }
                ],
                tableData: [
                    {
                        id: 1,
                        type: "广汽传祺GS3",
                        plateNumber: "苏BH2222",
                        ownerName: "韩战军",
                        ownerAddress: "8#1502",
                        status: "外出"
                    },
                    {
                        id: 2,
                        type: "宝骏530",
                        plateNumber: "豫A1A350",
                        ownerName: "王欣",
                        ownerAddress: "4#0801",
                        status: "外出"
                    },
                    {
                        id: 3,
                        type: "奔驰GLA",
                        plateNumber: "苏EB06E6",
                        ownerName: "袁宜君",
                        ownerAddress: "1#1704",
                        status: "外出"
                    },
                    {
                        id: 4,
                        type: "奇瑞瑞虎",
                        plateNumber: "沪B69999",
                        ownerName: "赵薇",
                        ownerAddress: "6#1804",
                        status: "外出"
                    },
                    {
                        id: 5,
                        type: "沃尔沃XC60",
                        plateNumber: "贵AP2168",
                        ownerName: "王敬轩",
                        ownerAddress: "10#1303",
                        status: "外出"
                    },
                ],
            }
        },
        methods: {
            filterChange(text) {
                this.placeHolder = "请输入" + text
            },
            batchDeletion() {
                let that = this;
                this.$Modal.warning({
                    title: "批量删除",
                    content: "确认要删除已选择的记录吗?",
                    onOk() {
                        for (let dataToDel of that.selection) {
                            for (let i in that.tableData) {
                                if (that.tableData[i].id === dataToDel.id) {
                                    that.tableData.splice(i, 1);
                                    break;
                                }
                            }
                        }
                    }
                })
            },
            beforeEdit(index) {
                this.editModal = true;
                let data = this.tableData[index];
                this.EditModalForm.ownerName = data.ownerName;
                this.EditModalForm.ownerIDNum = '';
                this.EditModalForm.ownerPhoneNum = '';
                this.EditModalForm.ownerAddress = data.ownerAddress;
                this.EditModalForm.type = data.type;
                this.EditModalForm.plateNumber = data.plateNumber;
            },
            show(index) {
                this.$Modal.info({
                    title: '车辆信息',
                    content: `类型：${this.tableData[index].type}<br>` +
                        `车牌号：${this.tableData[index].plateNumber}<br>` +
                        `车主姓名：${this.tableData[index].ownerName}<br>` +
                        `车主住址：${this.tableData[index].ownerAddress}<br>` +
                        `状态：${this.tableData[index].status}<br>`
                })
            },
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
            selectionChange(selection) {
                this.selection = selection;
            },
            changePage() {
            },
            doAdd() {
                this.addModal = false;
                this.clearForm('add')
            },
            doEdit() {
                this.editModal = false;
                this.clearForm('edit')
            },
            cancelOrNot(modalName) {
                let that = this;
                this.$Modal.confirm({
                    title: "尚未保存",
                    content: "您输入的内容尚未提交，确认要取消吗?",
                    onOk() {
                        if (modalName === 'add') {
                            that.addModal = false;
                            that.clearForm('add')
                        }
                        if (modalName === 'edit') {
                            that.editModal = false;
                            that.clearForm('edit')
                        }
                    },
                    onCancel() {
                        if (modalName === 'add') {
                            that.addModal = true;
                        }
                        if (modalName === 'edit') {
                            that.editModal = true;
                        }
                    }
                })
            },
            clearForm(formName) {
                if (formName === 'add') {
                    this.AddModalForm.ownerName = ''
                    this.AddModalForm.ownerIDNum = ''
                    this.AddModalForm.ownerPhoneNum = ''
                    this.AddModalForm.ownerAddress = ''
                    this.AddModalForm.type = ''
                    this.AddModalForm.plateNumber = ''
                }
                if (formName === 'edit') {
                    this.EditModalForm.ownerName = ''
                    this.EditModalForm.ownerIDNum = ''
                    this.EditModalForm.ownerPhoneNum = ''
                    this.EditModalForm.ownerAddress = ''
                    this.EditModalForm.type = ''
                    this.EditModalForm.plateNumber = ''
                }
            }
        }
    }
</script>
