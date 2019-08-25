<template>
    <div id="home">
        <Breadcrumb :style="{margin: '24px 0'}">
            <BreadcrumbItem>业主车辆信息</BreadcrumbItem>
        </Breadcrumb>
        <Content :style="{padding: '24px', minHeight: '600px', background: '#fff'}">
            <Row type="flex" justify="start" align="middle">
                <Col span="22">
                    <Select ref="status" v-model="status" placeholder="全部状态" style="width:100px" clearable>
                        <Option v-for="item in statusList" :value="item.value" :key="item.value">{{ item.label }}
                        </Option>
                    </Select>
                    <divider type="vertical"></divider>
                    <Select ref="filterMethod" v-model="filterMethod" placeholder="筛选条件" @on-change="filterChange"
                            style="width:100px" clearable>
                        <Option v-for="item in filterList" :value="item.value" :key="item.value">{{ item.label }}
                        </Option>
                    </Select>
                    <divider type="vertical"></divider>
                    <Input v-model="filterText" :placeholder="placeHolder" style="width: 300px"/>
                    <Divider type="vertical"/>
                    <ButtonGroup>
                        <Button type="primary" style="margin-left: 10px" @click="doSearch">搜索</Button>
                        <Button @click="clearSearch">清除</Button>
                    </ButtonGroup>
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
                <Page :total="pageData.dataCount" :current="pageData.currentPage" :page-size="pageData.pageSize"
                      :page-size-opts="[5,10,15,20,25,30]"
                      @on-change="changePage"
                      @on-page-size-change="changePageSize" show-total
                      show-sizer show-elevator></Page>
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
                    <Input v-model="AddModalForm.name" placeholder="请输入车主姓名"></Input>
                </FormItem>
                <FormItem label="身份证号">
                    <Input v-model="AddModalForm.idCardNum" placeholder="请输入身份证号"></Input>
                </FormItem>
                <FormItem label="电话号码">
                    <Input v-model="AddModalForm.phoneNum" placeholder="请输入电话号码"></Input>
                </FormItem>
                <FormItem label="住址">
                    <Input v-model="AddModalForm.houseNumber" placeholder="请输入车主住址"></Input>
                </FormItem>
                <FormItem label="车型">
                    <Input v-model="AddModalForm.brand" placeholder="请输入车型"></Input>
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
                    <Input v-model="EditModalForm.name" placeholder="请输入车主姓名"></Input>
                </FormItem>
                <FormItem label="身份证号">
                    <Input v-model="EditModalForm.idCardNum" placeholder="请输入身份证号"></Input>
                </FormItem>
                <FormItem label="电话号码">
                    <Input v-model="EditModalForm.phoneNum" placeholder="请输入电话号码"></Input>
                </FormItem>
                <FormItem label="住址">
                    <Input v-model="EditModalForm.houseNumber" placeholder="请输入车主住址"></Input>
                </FormItem>
                <FormItem label="车型">
                    <Input v-model="EditModalForm.brand" placeholder="请输入车型"></Input>
                </FormItem>
                <FormItem label="车牌号">
                    <Input v-model="EditModalForm.plateNumber" placeholder="请输入车牌号"></Input>
                </FormItem>
            </Form>
        </Modal>
    </div>
</template>
<script>
    import axios from 'axios'
    import {Car} from "../assets/js/url";

    export default {
        inject: ['login'],
        data() {
            return {
                addModal: false,
                editModal: false,
                status: '',
                filterMethod: '',
                filterText: '',
                placeHolder: '请选择筛选条件',
                AddModalForm: {
                    name: '',
                    idCardNum: '',
                    phoneNum: '',
                    houseNumber: '',
                    brand: '',
                    plateNumber: ''
                },
                EditModalForm: {
                    id: '',
                    name: '',
                    idCardNum: '',
                    phoneNum: '',
                    houseNumber: '',
                    brand: '',
                    plateNumber: ''
                },
                selection: [],
                statusList: [
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
                        value: '车主电话',
                        label: '车主电话'
                    },
                    {
                        value: '车主身份证号',
                        label: '车主身份证号'
                    }
                ],
                columns: [
                    {type: 'selection', width: 60, align: 'center'},
                    {title: '车型', key: 'brand'},
                    {title: '车牌号', key: 'plateNumber'},
                    {title: '车主姓名', key: 'name'},
                    {title: '车主住址', key: 'houseNumber'},
                    {title: '车主电话', key: 'phoneNum'},
                    {title: '车主身份证号', key: 'idCardNum'},
                    {title: '当前状态', key: 'status'},
                    {
                        title: '操作',
                        key: 'action',
                        width: 200,
                        align: 'center',
                        render: (h, params) => {
                            return h('ButtonGroup', [
                                h('Button', {
                                    props: {
                                        type: 'default',
                                        size: 'small'
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
            this.getOwnerVehicalList(this.pageData.pageSize, 1);
            if (this.$store.state.currentUserID === "") {
                this.$Message.info("请先登录");
                this.tableData = [];
                this.login();
            }
        },
        methods: {
            getOwnerVehicalList(pageSize, pageNum) {
                axios.get(Car, {
                    params: {
                        status: this.status,
                        filterMethod: this.filterMethod,
                        filterText: this.filterText,
                        pageSize: pageSize,
                        pageNum: pageNum
                    }
                }).then(res => {
                    this.tableData = res.data.queryData;
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
                this.getOwnerVehicalList(this.pageData.pageSize, this.pageData.currentPage)
            },
            clearSearch() {
                this.$refs.status.clearSingleSelect();
                this.$refs.filterMethod.clearSingleSelect();
                this.filterText = '';
                this.pageData.currentPage = 1;
                this.getOwnerVehicalList(this.pageData.pageSize, this.pageData.currentPage)
            },
            filterChange(text) {
                if (typeof (text) === "undefined") {
                    this.placeHolder = "请选择筛选条件"
                    return;
                }
                this.placeHolder = "请输入" + text
            },
            batchDeletion() {
                let that = this;
                this.$Modal.warning({
                    title: "批量删除",
                    content: "确认要删除已选择的记录吗?",
                    onOk() {
                        let idToDel = ''
                        for (let dataToDel of that.selection) {
                            idToDel += dataToDel.id + ' ';
                        }
                        let param = {'idToDel': idToDel};
                        axios.delete(Car, {data: param})
                            .then(
                                res => {
                                    console.log(res);
                                    that.$Message.info(res.data.message);
                                })
                            .catch(
                                err => {
                                    that.$Message.error(err.response.data.message);
                                }
                            );
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
                this.EditModalForm.id = data.id;
                this.EditModalForm.name = data.name;
                this.EditModalForm.idCardNum = data.idCardNum;
                this.EditModalForm.phoneNum = data.phoneNum;
                this.EditModalForm.houseNumber = data.houseNumber;
                this.EditModalForm.brand = data.brand;
                this.EditModalForm.plateNumber = data.plateNumber;
                this.EditModalForm.phoneNum = data.phoneNum;
                this.EditModalForm.idCardNum = data.idCardNum;
            },
            show(index) {
                this.$Modal.info({
                    title: '车辆信息',
                    content: `类型：${this.tableData[index].brand}<br>` +
                        `车牌号：${this.tableData[index].plateNumber}<br>` +
                        `车主姓名：${this.tableData[index].name}<br>` +
                        `车主住址：${this.tableData[index].houseNumber}<br>` +
                        `车主电话：${this.tableData[index].phoneNum}<br>` +
                        `车主身份证号：${this.tableData[index].idCardNum}<br>` +
                        `状态：${this.tableData[index].status}<br>`
                })
            },
            remove(index) {
                let that = this;
                this.$Modal.confirm({
                    title: "删除",
                    content: "确认要删除该记录吗?",
                    onOk() {
                        axios.delete(Car + '/' + that.tableData[index].id)
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
            selectionChange(selection) {
                this.selection = selection;
            },
            changePage(pageNum) {
                this.getOwnerVehicalList(this.pageData.pageSize, pageNum)
            },
            changePageSize(pageSize) {
                this.pageData.currentPage = 1;
                this.pageData.pageSize = pageSize
                this.getOwnerVehicalList(this.pageData.pageSize, this.pageData.currentPage)
            },
            doAdd() {
                this.addModal = false;
                let formData = new FormData();
                formData.append('brand', this.AddModalForm.brand);
                formData.append('plateNumber', this.AddModalForm.plateNumber);
                formData.append('name', this.AddModalForm.name);
                formData.append('houseNumber', this.AddModalForm.houseNumber);
                formData.append('phoneNum', this.AddModalForm.phoneNum);
                formData.append('idCardNum', this.AddModalForm.idCardNum);
                let that = this
                axios.post(Car, formData).then(
                    res => {
                        if (res.status === 201) {
                            that.$Message.info("添加成功");
                            that.getOwnerVehicalList(that.pageData.pageSize, that.getLastPage('add'));
                            that.closeModal();
                        }
                        that.clearForm('add')
                    }
                ).catch(
                    err => {
                        that.$Message.error(err.response.data.message);
                    }
                )
            },
            getLastPage(method, count = 1) {
                if (method === 'add') {
                    return Math.ceil((this.pageData.dataCount + count) / this.pageData.pageSize);
                }
            },
            doEdit() {
                this.editModal = false;
                let formData = new FormData();
                formData.append('brand', this.EditModalForm.brand);
                formData.append('plateNumber', this.EditModalForm.plateNumber);
                formData.append('name', this.EditModalForm.name);
                formData.append('houseNumber', this.EditModalForm.houseNumber);
                formData.append('phoneNum', this.EditModalForm.phoneNum);
                formData.append('idCardNum', this.EditModalForm.idCardNum);
                let that = this
                axios.put(Car + '/' + this.EditModalForm.id, formData).then(
                    res => {
                        if (res.status === 200) {
                            that.$Message.info("编辑成功");
                            that.getOwnerVehicalList(that.pageData.pageSize, that.pageData.currentPage);
                            that.closeModal();
                        }
                        that.clearForm('edit')
                    }
                ).catch(
                    err => {
                        that.$Message.error(err.response.data.message);
                    }
                )
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
                    this.AddModalForm.name = ''
                    this.AddModalForm.idCardNum = ''
                    this.AddModalForm.phoneNum = ''
                    this.AddModalForm.houseNumber = ''
                    this.AddModalForm.brand = ''
                    this.AddModalForm.plateNumber = ''
                }
                if (formName === 'edit') {
                    this.EditModalForm.name = ''
                    this.EditModalForm.idCardNum = ''
                    this.EditModalForm.phoneNum = ''
                    this.EditModalForm.houseNumber = ''
                    this.EditModalForm.brand = ''
                    this.EditModalForm.plateNumber = ''
                }
            }
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
                    this.getOwnerVehicalList(this.pageData.pageSize, 1);
                } else {
                    this.$Message.info("请先登录");
                    this.tableData = [];
                    this.login();
                }
            },
        },

    }
</script>
