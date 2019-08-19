<template>
    <div id="home">
        <Breadcrumb :style="{margin: '24px 0'}">
            <BreadcrumbItem>上传文件</BreadcrumbItem>
        </Breadcrumb>
        <Content :style="{padding: '24px', minHeight: '280px', background: '#fff'}">
            <Row type="flex" justify="center" align="middle">
                <Col>
                    <div class="demo-upload-list" v-for="item in uploadList">
                        <template v-if="item.status === 'finished'">
                            <img :src="item.url" @click="handleView">
                        </template>
                        <template v-else>
                            <Progress v-if="item.showProgress" status="active" :percent="item.percentage"
                                      hide-info></Progress>
                        </template>
                    </div>
                    <Upload v-show="uploadList.length < 1" ref="upload"
                            :show-upload-list="false" :default-file-list="defaultList"
                            :format="['jpg','jpeg','png']" :max-size="10240"
                            :on-success="handleSuccess" :on-format-error="handleFormatError"
                            :on-exceeded-size="handleMaxSize" :before-upload="handleBeforeUpload"
                            type="drag" action="//jsonplaceholder.typicode.com/posts/">
                        <div class="upload-button">
                            <div style="padding: 20px 0">
                                <Icon type="ios-camera" size="52" style="color: #3399ff"></Icon>
                                <p>添加图片</p>
                            </div>
                        </div>
                    </Upload>
                </Col>

            </Row>
            <Row type="flex" justify="center" align="middle" style="margin-top: 20px">
                <Button type="dashed" @click="handleRemove(uploadList[0])">清除文件</Button>
                <divider type="vertical"></divider>
                <Button type="primary">上传识别</Button>
            </Row>

        </Content>
        <Modal title="查看图片" v-model="visible">
            <img src="https://ss0.bdstatic.com/70cFuHSh_Q1YnxGkpoWK1HF6hhy/it/u=508387608,2848974022&fm=26&gp=0.jpg"
                 v-if="visible" style="width: 100%">
        </Modal>
    </div>
</template>
<script>
    export default {
        data() {
            return {
                defaultList: [],
                imgName: '',
                visible: false,
                uploadList: []
            }
        },
        methods: {
            handleView(name) {
                this.imgName = name
                this.visible = true
            },
            handleRemove(file) {
                const fileList = this.$refs.upload.fileList
                this.$refs.upload.fileList.splice(fileList.indexOf(file), 1)
            },
            handleSuccess(res, file) {
                file.url = 'https://ss0.bdstatic.com/70cFuHSh_Q1YnxGkpoWK1HF6hhy/it/u=508387608,2848974022&fm=26&gp=0.jpg'
                file.name = 'temp'
                console.log(this.uploadList);
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
            handleBeforeUpload() {
                const check = this.uploadList.length < 1
                if (!check) {
                    this.$Notice.warning({
                        title: '仅可上传一张图片'
                    })
                }
                return check
            }
        },
        mounted() {
            this.uploadList = this.$refs.upload.fileList
        }
    }
</script>
<style>
    .demo-upload-list {
        display: flex;
        flex-direction: column;
        justify-content: center;
        border: 1px solid transparent;
        border-radius: 4px;
        overflow: hidden;
        height: 300px;
        width: 600px;
        /*text-align: center;*/
        line-height: 60px;
        background: #fff;
        position: relative;
        box-shadow: 0 1px 1px rgba(0, 0, 0, .2);
        margin-right: 4px;
        /*width: 100%;*/
    }

    .demo-upload-list img {
        width: 100%;
        height: 100%;
    }

    .upload-button {
        display: flex;
        flex-direction: column;
        justify-content: center;
        width: 600px;
        height: 300px
    }
</style>
