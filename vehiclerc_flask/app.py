import datetime
import math
import os
from datetime import timedelta
import sqlalchemy
from flask import Flask, request, session, Response
from flask_restful import Resource, Api
from sqlalchemy import and_, or_

import enums
import speech
import utils
from database import db_session
from enums import CarStatus
from models import Cars, ParkingLog, ParkingSpace, Users
from recognition import get_license_plate
from restriction import get_restriction_info
from utils import queryToJson, messageToJson, PaginationHelper, is_login, who_is_login, md5, current_time, calc_price, \
    utc_to_local

app = Flask(__name__)
app.config['SECRET_KEY'] = os.urandom(24)  # 设置为24位的字符,每次运行服务器都是不同的，所以服务器启动一次上次的session就清除。
app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(days=7)  # 设置session的保存时间。
api = Api(app)

basedir = os.path.abspath(os.path.dirname(__file__))


@app.route('/')
def hello_world():
    return 'Hello World!'


class UserView(Resource):
    # 获取用户信息
    def get(self):
        if not is_login():
            return messageToJson("请先登录"), 401
        userInfo = Users.query.filter(Users.id == who_is_login()).first()
        return_message = messageToJson(data={"id": userInfo.id, "name": userInfo.name, "email": userInfo.email})
        db_session.close()
        return return_message, 200

    # 注册
    def post(self):
        name = request.form['name']
        email = request.form['email']
        password = request.form['password']
        if name and email and password:
            current_user = Users.query.filter(Users.email == email).first()
            if current_user:
                return_message = messageToJson(message="用户已存在")
                db_session.close()
                return return_message, 400
            new_user = Users(name, email, password)
            db_session.add(new_user)
            db_session.commit()
            return_message = messageToJson(message="注册成功", data={"email": email, "name": name})
            db_session.close()
            return return_message, 202
        else:
            return messageToJson(message="请确认已填写必填字段"), 400


class AuthView(Resource):
    # 注销
    def get(self):
        session.clear()
        return messageToJson("注销完成"), 200

    # 登录
    def post(self):
        email = request.form['email']
        password = request.form['password']
        if email and password:
            current_user = Users.query.filter(Users.email == email).first()
            if current_user:
                password = md5(password)
                if current_user.password == password:
                    session.permanent = True
                    session['ISLOGIN'] = "true"
                    session['USERUNIQUEID'] = current_user.id
                    return_message = messageToJson(message="登录成功", data={"userID": current_user.id})
                    db_session.close()
                    return return_message, 202
                else:
                    return_message = messageToJson(message="密码错误")
                    db_session.close()
                    return return_message, 400
            else:
                return_message = messageToJson(message="用户不存在")
                db_session.close()
                return return_message, 400
        else:
            return messageToJson(message="请确认已填写必填字段"), 400


class CarList(Resource):
    # 业主车列表
    def get(self):
        if not is_login():
            return messageToJson(message="请先登录"), 401
        status = request.args.get('status')
        filter_method = request.args.get('filterMethod')
        filter_text = request.args.get('filterText')
        page_size = request.args.get('pageSize')
        page_num = request.args.get('pageNum')
        # 判断参数是否正确
        if page_size and page_num:
            try:
                page_num = int(page_num)
                page_size = int(page_size)
            except ValueError:
                return messageToJson("分页参数不正确"), 500
            # 进行筛选查询
            car_list = Cars.query
            if status == "外出" or status == "停泊":
                car_list = car_list.filter(Cars.status == status)
            if filter_text and filter_text != "":
                if filter_method == "车牌号":
                    car_list = car_list.filter(Cars.plateNumber.like('%' + filter_text + '%'))
                elif filter_method == "车主姓名":
                    car_list = car_list.filter(Cars.name.like('%' + filter_text + '%'))
                elif filter_method == "车主住址":
                    car_list = car_list.filter(Cars.houseNumber.like('%' + filter_text + '%'))
                elif filter_method == "车主电话":
                    car_list = car_list.filter(Cars.phoneNum.like('%' + filter_text + '%'))
                elif filter_method == "车主身份证号":
                    car_list = car_list.filter(Cars.idCardNum.like('%' + filter_text + '%'))
            # 分页助手
            pagination_helper = PaginationHelper(car_list.count(), page_size)
            if pagination_helper.total_page < page_num:
                db_session.close()
                return messageToJson(message="页面不存在"), 500

            return_message = messageToJson(data={
                "totalPage": pagination_helper.total_page,
                "dataCount": pagination_helper.data_count,
                "currentPage": page_num,
            },
                queryData=car_list.limit(page_size).offset(pagination_helper.get_offset(page_num)).all())
            db_session.close()
            return return_message, 200
        else:
            return messageToJson("请求参数不正确"), 500

    # 添加业主车
    def post(self):
        if not is_login():
            return messageToJson(message="请先登录"), 401
        brand = request.form['brand']
        plate_number = request.form['plateNumber']
        name = request.form['name']
        house_number = request.form['houseNumber']
        phone_num = request.form['phoneNum']
        id_card_num = request.form['idCardNum']
        if brand and plate_number and name and house_number and phone_num and id_card_num:
            try:
                new_car = Cars(brand, plate_number, name, house_number, phone_num, id_card_num)
                db_session.add(new_car)
                db_session.commit()
                return_message = queryToJson(new_car)
                db_session.close()
                return return_message, 201
            except sqlalchemy.exc.IntegrityError:
                db_session.close()
                return messageToJson(message="该车牌已存在"), 500
        else:
            return messageToJson(message="请确认必填项已填写"), 400

    # 批量删除业主车
    def delete(self):
        if not is_login():
            return messageToJson(message="请先登录"), 401
        id_to_del = request.json['idToDel']
        if id_to_del:
            id_list = id_to_del.split(" ")  # 根据逗号分割字符串
            id_list.pop()
            current_car = Cars.query.filter(Cars.id.in_(id_list)).all()
            if current_car:
                for car in current_car:
                    db_session.delete(car)
                db_session.commit()
                return_message = messageToJson(message="删除成功", queryData=current_car)
                db_session.close()
                return return_message, 200
            else:
                db_session.close()
                return messageToJson(message="车辆不存在"), 400
        else:
            return messageToJson(message="请选择要删除的车辆"), 400


class CarDetail(Resource):
    # 获取指定业主车详情
    def get(self, car_id):
        if not is_login():
            return messageToJson(message="请先登录"), 401
        current_car = Cars.query.get(car_id)
        if current_car:
            return_message = queryToJson(current_car)
            db_session.close()
            return return_message, 200
        else:
            db_session.close()
            return messageToJson("车辆不存在"), 400

    # 编辑业主车
    def put(self, car_id):
        if not is_login():
            return messageToJson(message="请先登录"), 401
        current_car = Cars.query.get(car_id)
        if current_car:
            brand = request.form['brand']
            plate_number = request.form['plateNumber']
            name = request.form['name']
            house_number = request.form['houseNumber']
            phone_num = request.form['phoneNum']
            id_card_num = request.form['idCardNum']
            if brand and plate_number and name and house_number and phone_num and id_card_num:
                try:
                    current_car.brand = brand
                    current_car.plateNumber = plate_number
                    current_car.name = name
                    current_car.houseNumber = house_number
                    current_car.phoneNum = phone_num
                    current_car.idCardNum = id_card_num
                    db_session.commit()
                    return_message = queryToJson(current_car)
                    db_session.close()
                    return return_message, 200
                except sqlalchemy.exc.IntegrityError:
                    db_session.close()
                    return messageToJson(message="该车牌已存在"), 500
            else:
                db_session.close()
                return messageToJson(message='请确认必填项已填写'), 400
        else:
            db_session.close()
            return messageToJson(message="车辆不存在"), 400

    # 删除业主车
    def delete(self, car_id):
        if not is_login():
            return messageToJson(message="请先登录"), 401
        current_car = Cars.query.get(car_id)
        if current_car:
            db_session.delete(current_car)
            db_session.commit()
            return_message = messageToJson(message="删除成功", queryData=current_car)
            db_session.close()
            return return_message, 200
        else:
            db_session.close()
            return messageToJson(message="车辆不存在"), 400


class ParkingLogList(Resource):
    # 停车记录列表
    def get(self):
        if not is_login():
            return messageToJson(message="请先登录"), 401
        status = request.args.get('status')
        filter_method = request.args.get('filterMethod')
        filter_text = request.args.get('filterText')
        start_time = request.args.get('startTime')
        end_time = request.args.get('endTime')
        page_size = request.args.get('pageSize')
        page_num = request.args.get('pageNum')
        type = request.args.get('type')
        # 判断参数是否正确
        if page_size and page_num:
            try:
                page_num = int(page_num)
                page_size = int(page_size)
            except ValueError:
                return messageToJson("分页参数不正确"), 500
            # 进行筛选查询
            # parking_list = ParkingLog.query
            parking_list = db_session.query(ParkingLog, ParkingSpace) \
                .outerjoin(ParkingSpace, and_(ParkingLog.plateNumber == ParkingSpace.plateNumber,
                                              ParkingLog.status == CarStatus.PARKING))
            if type == "外来车" or type == "业主车":
                parking_list = parking_list.filter(ParkingLog.type == type)
            if status == "停泊" or status == "驶离" or status == "外出":
                parking_list = parking_list.filter(ParkingLog.status == status)
            if filter_text and filter_text != "":
                if filter_method == "车牌号":
                    parking_list = parking_list.filter(ParkingLog.plateNumber.like('%' + filter_text + '%'))
                elif filter_method == "车位号":
                    parking_list = parking_list.filter(ParkingSpace.spaceName.like('%' + filter_text + '%'))
            if start_time and end_time and start_time != "" and end_time != "":
                start_time = utc_to_local(start_time)
                end_time = utc_to_local(end_time)
                parking_list = parking_list.filter(
                    and_(ParkingLog.enterTime >= start_time, ParkingLog.enterTime <= end_time))
            # 分页助手
            pagination_helper = PaginationHelper(parking_list.count(), page_size)
            if pagination_helper.total_page < page_num:
                db_session.close()
                return messageToJson(message="页面不存在"), 500
            return_message = messageToJson(data={
                "totalPage": pagination_helper.total_page,
                "dataCount": pagination_helper.data_count,
                "currentPage": page_num,
                "freeNormalParingPlace": ParkingSpace.query.filter(
                    ParkingSpace.status == enums.ParkingSpaceStatus.FREE).filter(
                    ParkingSpace.type == enums.ParkingSpaceType.FUEL).count(),
                "freeChargeParingPlace": ParkingSpace.query.filter(
                    ParkingSpace.status == enums.ParkingSpaceStatus.FREE).filter(
                    ParkingSpace.type == enums.ParkingSpaceType.WASHING_ENERGY).count()
            },
                queryData=parking_list.order_by(-ParkingLog.enterTime).limit(page_size).offset(
                    pagination_helper.get_offset(page_num)).all())
            db_session.close()
            return return_message, 200
        else:
            return messageToJson("请求参数不正确"), 500


class ParkingLogDetail(Resource):
    # 停车记录删除
    def delete(self, log_id):
        if not is_login():
            return messageToJson(message="请先登录"), 401
        current_log = ParkingLog.query.get(log_id)
        if current_log:
            db_session.delete(current_log)
            db_session.commit()
            return_message = messageToJson(message="删除成功", queryData=current_log)
            db_session.close()
            return return_message, 200
        else:
            db_session.close()
            return messageToJson(message="记录不存在"), 400


class AudioDetail(Resource):
    def get(self, file_name):
        def generate():
            path = basedir + "/static/audio/{}".format(file_name)
            with open(path, 'rb') as fmp3:
                data = fmp3.read(1024)
                while data:
                    yield data
                    data = fmp3.read(1024)

        return Response(generate(), mimetype="audio/mpeg3")


class RecognitionView(Resource):
    # 文件识别
    def post(self):
        if not is_login():
            return messageToJson(message="请先登录"), 401
        plate_photo = request.files.get('platePhoto')
        dir_path = basedir + "/static/userUpload/"
        image_path = dir_path + plate_photo.filename
        plate_photo.save(image_path)
        # 获取识别结果
        recognition_result = get_license_plate(image_path)
        try:
            plate_color = recognition_result['words_result']['color']
            plate_number = recognition_result['words_result']['number']
            os.remove(image_path)
        except KeyError:
            os.remove(image_path)
            return messageToJson(message="未检测到车牌"), 500

        type = '新能源车' if (plate_color == 'green') else '燃油车'
        message = {
            'isOwnerCar': False,
            'inOrOut': '',
            'inOrOutText': '',
            'type': type,
            'number': plate_number,
            'fileName': plate_photo.filename
        }
        # 检索是否为业主车
        owner_car = Cars.query.filter(Cars.plateNumber == plate_number).first()
        if owner_car:
            message['isOwnerCar'] = True
            message['type'] += " 业主车"
        else:
            message['isOwnerCar'] = False
            message['type'] += " 外来车"
        # 检索停车记录表最新的一条记录
        parking_log = ParkingLog.query.filter(ParkingLog.plateNumber == plate_number).order_by(
            -ParkingLog.enterTime).first()
        if parking_log and parking_log.status == CarStatus.PARKING:
            # 有记录且未离开（本次为出库）
            message['inOrOut'] = 'out'
            message['inOrOutText'] = '出库'
            parking_log.outTime = current_time()  # 储存外出时间
            # 是否为业主车
            restriction = get_restriction_info("1")  # 返回业主车状态数据
            if message['isOwnerCar']:
                parking_log.status = CarStatus.OUT  # 状态为外出
                owner_car.status = CarStatus.OUT  # 同时修改业主车表
                message['ownerData'] = queryToJson(owner_car)  # 返回业主车状态数据
                message['restriction'] = restriction
            else:
                parking_log.status = CarStatus.LEAVED  # 状态为驶离开
            # 计算停车时长和应缴费用
            # park_time = (datetime.datetime.strptime(parking_log.outTime,
            #                                         "%Y-%m-%d %H:%M:%S") - parking_log.enterTime).total_seconds() // 3600  # 计算小时数
            park_time = (datetime.datetime.strptime(parking_log.outTime,
                                                    "%Y-%m-%d %H:%M:%S") - parking_log.enterTime).total_seconds()  # 计算小时数
            message['parkTime'] = park_time
            if not message['isOwnerCar']:
                parking_log.cost = calc_price(park_time)  # 状态为驶离开
                message['price'] = str(calc_price(park_time)) + '元'
            message['logInfo'] = queryToJson(parking_log)
            # 查询车位状态
            parking_space = ParkingSpace.query.filter(ParkingSpace.plateNumber == plate_number).first()
            if parking_space:
                # 令车位空闲
                parking_space.status = enums.ParkingSpaceStatus.FREE
                parking_space.plateNumber = '-'
                message['audioPath'] = speech.speech(message['isOwnerCar'], message['inOrOut'], plate_number,
                                                     restriction['xxweihao'], parking_time=str(math.ceil(park_time)),
                                                     parking_cost=str(calc_price(park_time))) + '.mp3'
                db_session.commit()  # 保存数据库状态
                db_session.close()
                return messageToJson(data=message), 200
            else:
                # 车为出库状态，但无入库记录，发出警告
                db_session.commit()  # 保存数据库状态
                db_session.close()
                return messageToJson(message="车辆状态有误，请联系管理员检查", data=message), 500
        else:
            # 有记录且已离开/无记录（本次为入库）
            message['inOrOut'] = 'in'
            message['inOrOutText'] = '入库'
            new_parking_log = ParkingLog(plate_number, plate_color, current_time())
            # 是否为业主车
            restriction = get_restriction_info("2")  # 返回业主车状态数据
            if message['isOwnerCar']:
                new_parking_log.type = enums.CarType.OWNER
                owner_car.status = CarStatus.PARKING  # 当前状态为停泊
                message['ownerData'] = queryToJson(owner_car)  # 返回业主车状态数据
                message['restriction'] = restriction  # 返回业主车状态数据
            else:
                message['pricePerHour'] = enums.pricePerHour  # 外来车辆提供价格信息
            db_session.add(new_parking_log)  # 添加入库记录
            # 查询空闲车位状态
            parking_space = ParkingSpace.query.filter(ParkingSpace.status == enums.ParkingSpaceStatus.FREE)
            # 默认新能源车和汽油车分开查询
            if plate_color == 'green':
                parking_space = parking_space.filter(ParkingSpace.type == enums.ParkingSpaceType.WASHING_ENERGY)
            else:
                parking_space = parking_space.filter(ParkingSpace.type == enums.ParkingSpaceType.FUEL)
            if parking_space.count() > 0:
                # 对应停车区有车位，停在编号最小但的区域
                parking_space = parking_space.order_by(ParkingSpace.id).first()
            else:
                # 对应区域没有车位，全局查询
                parking_space = ParkingSpace.query.filter(ParkingSpace.status == enums.ParkingSpaceStatus.FREE)
                if parking_space.count() > 0:
                    parking_space = parking_space.order_by(ParkingSpace.id).first()
                else:
                    # 此处不保存任何数据库状态
                    db_session.close()
                    return messageToJson(message="已无空闲车位，请稍后", data=message), 500
            # 改变车位状态
            parking_space.status = enums.ParkingSpaceStatus.FREE
            parking_space.plateNumber = plate_number
            message['logInfo'] = queryToJson(new_parking_log)
            message['parkingSpace'] = parking_space.spaceName
            message['audioPath'] = speech.speech(message['isOwnerCar'], message['inOrOut'], plate_number,
                                                 restriction['xxweihao'],
                                                 parking_place=parking_space.spaceName) + '.mp3'
            # 保存数据库信息
            db_session.commit()
            db_session.close()
            return messageToJson(data=message), 200


api.add_resource(UserView, '/vehiclerc/user')
api.add_resource(AuthView, '/vehiclerc/auth')
api.add_resource(RecognitionView, '/vehiclerc/recognition')
api.add_resource(CarList, '/vehiclerc/car')
api.add_resource(CarDetail, '/vehiclerc/car/<car_id>')
api.add_resource(ParkingLogList, '/vehiclerc/parkingLog')
api.add_resource(ParkingLogDetail, '/vehiclerc/parkingLog/<log_id>')
api.add_resource(AudioDetail, '/vehiclerc/audio/<file_name>')

if __name__ == '__main__':
    app.run(debug=True)
