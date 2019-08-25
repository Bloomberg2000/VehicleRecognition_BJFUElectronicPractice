<template>
    <div class="layout">
        <Layout>
            <Header>
                <Menu mode="horizontal" theme="dark" active-name="1" @on-select="menuSelect">
                    <img class=layout-logo :src="imgpath.public.logo">
                    <!--                        阿勒奥格-->
                    <div class="layout-nav">
                        <MenuItem name="notifications">
                            <Icon type="md-notifications-outline" size="20"/>
                        </MenuItem>
                        <MenuItem v-show="isLogin" name="userName">
                            <Icon type="ios-contact" size="20"/>
                            {{userInfo.name}}
                        </MenuItem>
                        <MenuItem v-show="isLogin" name="logout">
                            注销
                        </MenuItem>
                        <MenuItem v-show="!isLogin" name="login">
                            登录
                        </MenuItem>
                        <MenuItem v-show="!isLogin" name="register">
                            注册
                        </MenuItem>
                    </div>
                </Menu>
            </Header>
            <Layout>
                <Sider hide-trigger :style="{background: '#fff'}">
                    <Menu theme="light" width="auto" @on-select="navigateTo">
                        <MenuItem name="/">
                            <Icon type="ios-home"/>
                            首页
                        </MenuItem>
                        <MenuItem name="/ownervehicle">
                            <Icon type="md-car"/>
                            业主车辆信息
                        </MenuItem>
                        <MenuItem name="/parkinglot">
                            <Icon type="md-car"/>
                            停车场实时信息
                        </MenuItem>
<!--                        <MenuItem name="/parkinglot">-->
<!--                            <Icon type="md-car"/>-->
<!--                            停车场实时信息-->
<!--                        </MenuItem>-->
                    </Menu>
                </Sider>
                <Layout :style="{padding: '0 24px 24px'}">
                    <router-view/>
                </Layout>
            </Layout>
        </Layout>
        <Modal v-model="loginModal" title="登录">
            <Form ref="LoginForm" :model="LoginForm" :rules="LoginRules" :label-width="80">
                <FormItem prop="email" label="电子邮箱">
                    <Input v-model="LoginForm.email" placeholder="请输入电子邮箱"></Input>
                </FormItem>
                <FormItem prop="password" label="密码">
                    <Input v-model="LoginForm.password" type="password" placeholder="请输入密码"></Input>
                </FormItem>
            </Form>
            <div slot="footer">
                <Button type="text" size="large" @click="closeModal">取消</Button>
                <Button type="primary" size="large" @click="doLogin">登录</Button>
            </div>
        </Modal>
        <Modal v-model="registerModal" title="注册">
            <Form ref="RegisterForm" :model="RegisterForm" :rules="RegisterRules" :label-width="80">
                <FormItem prop="name" label="用户名">
                    <Input v-model="RegisterForm.name" required placeholder="请输入用户名"></Input>
                </FormItem>
                <FormItem prop="email" label="电子邮箱">
                    <Input v-model="RegisterForm.email" placeholder="请输入电子邮箱"></Input>
                </FormItem>
                <FormItem prop="password" label="输入密码">
                    <Input v-model="RegisterForm.password" type="password" placeholder="请输入密码"></Input>
                </FormItem>
            </Form>
            <div slot="footer">
                <Button type="text" size="large" @click="closeModal">取消</Button>
                <Button type="primary" size="large" @click="doRegister">注册</Button>
            </div>
        </Modal>
    </div>
</template>
<script>
    import axios from 'axios'
    import {Auth, User} from "./assets/js/url";

    export default {
        provide() {
            return {
                login: this.login,
            }
        },
        data: () => ({
            isRouterAlive: true,
            isLogin: false,
            loginModal: false,
            registerModal: false,
            timer: '',
            userInfo: [],
            RegisterForm: {
                name: '',
                email: '',
                password: ''
            },
            RegisterRules: {
                name: [
                    {required: true, message: '用户名不能为空', trigger: 'blur'},
                ],
                email: [
                    {required: true, message: '电子邮箱不能为空', trigger: 'blur'},
                    {type: 'email', message: '电子邮箱格式不正确', trigger: 'blur'}
                ],
                password: [
                    {required: true, message: '密码不能为空', trigger: 'blur'},
                ]
            },
            LoginForm: {
                email: '',
                password: ''
            },
            LoginRules: {
                email: [
                    {required: true, message: '电子邮箱不能为空', trigger: 'blur'},
                    {type: 'email', message: '电子邮箱格式不正确', trigger: 'blur'}
                ],
                password: [
                    {required: true, message: '密码不能为空', trigger: 'blur'},
                ]
            },
        }),
        destroyed() {
            clearInterval(this.timer);
        },
        mounted() {
            let _this = this;
            // 实时获取登录态
            this.isLoginWatcher();
            clearInterval(this.timer);
            this.timer = window.setInterval(function () {
                _this.isLoginWatcher();
            }, 100);
            // 每次打开页面重新获取用户信息
            let userID = this.$store.state.currentUserID;
            if (userID !== '') {
                this.getUserInfo();
            }
        },
        watch: {
            currentUserID(userID) {
                // 用户ID变化重新获取用户信息
                if (userID !== "") {
                    this.getUserInfo();
                }
            },
        },
        methods: {
            login() {
                this.loginModal = true;
            },
            navigateTo(name) {
                this.$router.push(name);
            },
            isLoginWatcher() {
                this.isLogin = this.$store.state.currentUserID !== ""
            },
            menuSelect(name) {
                if (name === 'notifications') {

                }
                if (name === 'logout') {
                    let that = this;
                    this.$Modal.confirm({
                        title: "注销",
                        content: "确认要注销当前账户吗?",
                        onOk() {
                            axios.get(Auth).then(
                                res => {
                                    if (res.status === 200) {
                                        that.$store.commit("userChange", '');
                                        that.userInfo = [];
                                        that.isLoginWatcher();
                                        that.$Message.info(res.data.message);
                                    }
                                }
                            ).catch(
                                err => {
                                    that.$Message.info(err.response.data.message);
                                }
                            )
                        }
                    });
                }
                if (name === 'login') {
                    this.loginModal = true;
                }
                if (name === 'register') {
                    this.registerModal = true;
                }
            },
            doLogin() {
                this.$refs['LoginForm'].validate((valid) => {
                    if (valid) {
                        let formData = new FormData();
                        formData.append('email', this.LoginForm.email);
                        formData.append('password', this.LoginForm.password);
                        axios.post(Auth, formData).then(
                            res => {
                                if (res.status === 202) {
                                    this.$Message.info(res.data.message);
                                    this.$store.commit("userChange", res.data.data.userID + '');
                                    this.closeModal();
                                }
                            }
                        ).catch(
                            err => {
                                this.$Message.error(err.response.data.message);
                            }
                        )
                    } else {
                        this.$Message.error("请确认所有数据填写正确");
                    }
                });
            },
            doRegister() {
                this.$refs['RegisterForm'].validate((valid) => {
                    if (valid) {
                        let formData = new FormData();
                        formData.append('name', this.RegisterForm.name);
                        formData.append('email', this.RegisterForm.email);
                        formData.append('password', this.RegisterForm.password);
                        axios.post(User, formData).then(
                            res => {
                                if (res.status === 202) {
                                    this.$Message.info(res.data.message);
                                    this.closeModal();
                                }
                            }
                        ).catch(
                            err => {
                                this.$Message.error(err.response.data.message);
                            }
                        )
                    } else {
                        this.$Message.error("请确认所有数据填写正确");
                    }
                });
            },
            getUserInfo() {
                axios.get(User).then(
                    res => {
                        if (res.status === 200) {
                            this.userInfo = res.data.data;
                        }
                    }
                ).catch(
                    err => {
                        this.$store.commit("userChange", '');
                        this.$Message.info(err.response.data.message);
                    }
                )
            },
            closeModal() {
                this.loginModal = false;
                this.registerModal = false;
                this.RegisterForm.name = '';
                this.RegisterForm.email = '';
                this.RegisterForm.password = '';
                this.RegisterForm.passwordAgain = '';
                this.LoginForm.email = '';
                this.LoginForm.password = '';
            }
        },
        computed: {
            imgpath() {
                return this.$store.state.imageStyle;
            },
            currentUserID() {
                return this.$store.state.currentUserID;
            },
        }
    }
</script>
<style scoped>
    .layout {
        border: 1px solid #d7dde4;
        background: #f5f7f9;
        position: relative;
        border-radius: 4px;
        overflow: hidden;
    }

    .layout-title {
        width: 200px;
        height: 30px;
        float: left;
        position: relative;
        font-size: 18px;
        font-weight: bold;
        color: #ffffff;
    }

    .layout-logo {
        float: left;
        position: relative;
        height: 40px;
        margin-top: 10px;
    }

    .layout-nav {
        float: right;
    }
</style>
