<template>
    <div id="home">
        <Breadcrumb :style="{margin: '24px 0'}">
            <BreadcrumbItem>上传文件</BreadcrumbItem>
        </Breadcrumb>
        <Content :style="{padding: '24px', minHeight: '320px', background: '#fff'}">
            <Upload ref='upload'
                    type="drag"
                    name="platePhoto"
                    :format="['jpg','jpeg','png']"
                    :max-size="10240"
                    :action="uploadUrl"
                    :before-upload="handleBeforeUpload"
                    :on-success="handleSuccess"
                    :on-error="handleError"
                    :on-format-error="handleFormatError"
                    :on-exceeded-size="handleMaxSize">
                <div :style="{padding: '20px', minHeight: '280px'}">
                    <div class="upload-button">
                        <Icon type="ios-camera" size="52" style="color: #E58E0B"></Icon>
                        <p>添加/拖拽车牌图片到此处</p>
                        <p class="tips">文件最大不得超过10M</p>
                        <p class="tips">请上传jpg/jpeg/png格式的文件</p>
                    </div>
                </div>
            </Upload>
            <Row type="flex" justify="center" align="middle" style="margin-top: 20px">
                <Button type="dashed" @click="clear">清除上传历史</Button>
            </Row>

        </Content>
        <Modal title="识别结果" v-model="visible">
            <Row v-show="!success" type="flex" justify="center" align="middle" style="margin-top: 20px">
                <Button type="text" loading>加载中...</Button>
            </Row>
            <Form v-if="success" :model="recognitionData" :label-width="120">
                <FormItem label="车牌号">
                    {{recognitionData.data.number}}
                </FormItem>
                <FormItem label="车辆类别">
                    {{recognitionData.data.type}}
                </FormItem>
                <FormItem label="当前状态">
                    {{recognitionData.data.inOrOutText}}
                </FormItem>
                <FormItem label="停车时长" v-show="recognitionData.data.inOrOut === 'out'">
                    {{recognitionData.data.parkTime}}小时
                </FormItem>
                <FormItem label="应缴费用"
                          v-show="recognitionData.data.inOrOut === 'out' && !recognitionData.data.isOwnerCar">
                    {{recognitionData.data.price}}
                </FormItem>
                <FormItem label="每小时价格"
                          v-show="recognitionData.data.inOrOut === 'in' && !recognitionData.data.isOwnerCar">
                    {{recognitionData.data.pricePerHour}}元
                </FormItem>
                <FormItem label="推荐车位号码" v-show="recognitionData.data.inOrOut === 'in'">
                    <Tag color="volcano">{{recognitionData.data.parkingSpace}}</Tag>
                </FormItem>
                <FormItem label="今日限行"
                          v-if="recognitionData.data.isOwnerCar && recognitionData.data.inOrOut === 'out'">
                    <Tag color="warning">{{recognitionData.data.restriction.xxweihao[0]}}</Tag>
                    <Tag color="warning">{{recognitionData.data.restriction.xxweihao[1]}}</Tag>
                </FormItem>
                <FormItem label="明日限行"
                          v-if="recognitionData.data.isOwnerCar && recognitionData.data.inOrOut === 'in'">
                    <Tag color="warning">{{recognitionData.data.restriction.xxweihao[0]}}</Tag>
                    <Tag color="warning">{{recognitionData.data.restriction.xxweihao[1]}}</Tag>
                </FormItem>
            </Form>
        </Modal>
    </div>
</template>
<script>
    import {AudioPath, Recognition} from "../assets/js/url";

    export default {
        inject: ['login'],
        data() {
            return {
                visible: false,
                success: false,
                uploadUrl: Recognition,
                recognitionData: [],
                timer: ''
            }
        },
        mounted() {
            if (this.$store.state.currentUserID === "") {
                this.$Message.info("请先登录");
                this.tableData = [];
                this.login();
            }
        },
        watch: {
            currentUserID(userID) {
                // 用户ID变化重新获取用户信息
                if (userID === "") {
                    this.$Message.info("请先登录");
                    this.login();
                }
            },
        },
        methods: {
            handleBeforeUpload() {
                this.success = false;
                this.visible = true;
            },
            handleSuccess(response, file, fileList) {
                this.success = true;
                this.recognitionData = response;
                let src = AudioPath + '/' + response.data.audioPath;
                let audio = new Audio();
                audio.src = src;
                audio.play();
                console.log(response);
            },
            handleError(error, file, fileList) {
                this.success = false;
                this.visible = false;
                this.$Notice.error({
                    title: '识别失败',
                    desc: file.message
                })
            },
            handleFormatError(file) {
                this.$Notice.warning({
                    title: '文件格式错误',
                    desc: '文件\"' + file.name + '\"格式错误，请选择一张图片'
                })
            },
            handleMaxSize(file) {
                this.$Notice.warning({
                    title: '图片文件过大',
                    desc: '文件\"' + file.name + '\"过大，图片文件不能超过10M'
                })
            },
            clear() {
                this.$refs.upload.clearFiles();
            }
        }
    }
</script>
<style>
    .upload-button {
        display: flex;
        flex-direction: column;
        justify-content: center;
        width: 100%;
        height: 280px;
    }

    .tips {
        color: rgba(0, 0, 0, 0.3);
        font-size: 10px;
    }
</style>
