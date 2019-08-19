<template>
    <div class="layout">
        <Layout>
            <Header>
                <Menu mode="horizontal" theme="dark" active-name="1">

                        <img class=layout-logo src="@/assets/logo.png">
<!--                        阿勒奥格-->
                    <div class="layout-nav">
                        <MenuItem name="1">
                            <Icon type="md-notifications-outline"/>
                        </MenuItem>
                        <MenuItem name="2">
                            用户名
                        </MenuItem>
                        <MenuItem name="3">
                            退出登录
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
                        <MenuItem name="/foreignvehicle">
                            <Icon type="md-car"/>
                            外来车辆信息
                        </MenuItem>
                        <MenuItem name="/parkinglot ">
                            <Icon type="md-car"/>
                            停车场实时信息
                        </MenuItem>
                    </Menu>
                </Sider>
                <Layout :style="{padding: '0 24px 24px'}">
                    <router-view/>
                </Layout>
            </Layout>
        </Layout>
    </div>
</template>
<script>
    export default {
        methods: {
            navigateTo(name) {
                this.$router.push(name);
            }
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
