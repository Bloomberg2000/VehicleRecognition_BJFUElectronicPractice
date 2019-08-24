import datetime
import os
from datetime import timedelta

import sqlalchemy
from flask import Flask, request, session
from flask_restful import Resource, Api

import enums
from database import db_session
from enums import CarStatus
from models import Cars, ParkingLog, ParkingSpace, Users
from recognition import get_license_plate
from utils import queryToJson, messageToJson, PaginationHelper, is_login, md5, current_time, calc_price

app = Flask(__name__)
app.config['SECRET_KEY'] = os.urandom(24)  # 设置为24位的字符,每次运行服务器都是不同的，所以服务器启动一次上次的session就清除。
app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(days=7)  # 设置session的保存时间。
api = Api(app)

basedir = os.path.abspath(os.path.dirname(__file__))


@app.route('/')
def hello_world():
    return 'Hello World!'


class AuthView(Resource):
    def get(self):
        if not is_login():
            return messageToJson("请先登录"), 401
        session.clear()
        return messageToJson("注销完成"), 200

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
                    return messageToJson(message="登录成功", data={"userID": current_user.id}), 202
                else:
                    return messageToJson(message="密码错误"), 400
            else:
                return messageToJson(message="用户不存在"), 400
        else:
            return messageToJson(message="请确认已填写比天资端"), 400


class CarList(Resource):
    # 业主车列表
    def get(self):
        if not is_login():
            return messageToJson(message="请先登录"), 401
        status = request.args.get('status')
        filiter_method = request.args.get('filiterMethod')
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
                if filiter_method == "车牌号":
                    car_list = car_list.filter(Cars.plateNumber.like('%' + filter_text + '%'))
                elif filiter_method == "车主姓名":
                    car_list = car_list.filter(Cars.name.like('%' + filter_text + '%'))
                elif filiter_method == "车主住址":
                    car_list = car_list.filter(Cars.houseNumber.like('%' + filter_text + '%'))
            # 分页助手
            pagination_helper = PaginationHelper(car_list.count(), page_size)
            if pagination_helper.total_page < page_num:
                return messageToJson(message="页面不存在"), 500
            return messageToJson(data={
                "totalPage": pagination_helper.total_page,
                "dataCount": pagination_helper.data_count,
                "currentPage": page_num,
            },
                queryData=car_list.limit(page_size).offset(pagination_helper.get_offset(page_num)).all()), 200
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
        if brand and plate_number and name and house_number:
            try:
                new_car = Cars(brand, plate_number, name, house_number)
                db_session.add(new_car)
                db_session.commit()
                return queryToJson(new_car), 201
            except sqlalchemy.exc.IntegrityError:
                return messageToJson(message="该车牌已存在"), 500
        else:
            return messageToJson(message="请确认必填项已填写"), 400

    # 批量删除业主车
    def delete(self):
        if not is_login():
            return messageToJson(message="请先登录"), 401
        id_to_del = request.form['idToDel']
        if id_to_del:
            id_list = id_to_del.split(" ")  # 根据逗号分割字符串
            current_car = Cars.query.filter(Cars.id.in_(id_list)).all()
            if current_car:
                for car in current_car:
                    db_session.delete(car)
                db_session.commit()
                return messageToJson(message="删除成功", queryData=current_car), 200
            else:
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
            return queryToJson(current_car), 200
        else:
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
            if brand and plate_number and name and house_number:
                try:
                    current_car.brand = brand
                    current_car.plateNumber = plate_number
                    current_car.name = name
                    current_car.houseNumber = house_number
                    db_session.commit()
                    return queryToJson(current_car), 200
                except sqlalchemy.exc.IntegrityError:
                    return messageToJson(message="该车牌已存在"), 500
            else:
                return messageToJson(message='请确认必填项已填写'), 400
        else:
            return messageToJson(message="车辆不存在"), 400

    # 删除业主车
    def delete(self, car_id):
        if not is_login():
            return messageToJson(message="请先登录"), 401
        current_car = Cars.query.get(car_id)
        if current_car:
            db_session.delete(current_car)
            db_session.commit()
            return messageToJson(message="删除成功", queryData=current_car), 200
        else:
            return messageToJson(message="车辆不存在"), 400


class ParkingLogList(Resource):
    # 停车记录列表
    def get(self):
        if not is_login():
            return messageToJson(message="请先登录"), 401
        status = request.args.get('status')
        filter_text = request.args.get('filterText')
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
            parking_list = ParkingLog.query
            if type == "外来车" or type == "业主车":
                parking_list = parking_list.filter(ParkingLog.type == type)
            if status == "停泊" or status == "已驶离":
                parking_list = parking_list.filter(ParkingLog.status == status)
            if filter_text and filter_text != "":
                parking_list = parking_list.filter(ParkingLog.plateNumber.like('%' + filter_text + '%'))
            # 分页助手
            pagination_helper = PaginationHelper(parking_list.count(), page_size)
            if pagination_helper.total_page < page_num:
                return messageToJson(message="页面不存在"), 500
            return messageToJson(data={
                "totalPage": pagination_helper.total_page,
                "dataCount": pagination_helper.data_count,
                "currentPage": page_num,
            },
                queryData=parking_list.limit(page_size).offset(pagination_helper.get_offset(page_num)).all()), 200
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
            return messageToJson(message="删除成功", queryData=current_log), 200
        else:
            return messageToJson(message="记录不存在"), 400


class ParkingSpaceList(Resource):
    # 停车记录列表
    def get(self):
        if not is_login():
            return messageToJson(message="请先登录"), 401
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
            space_list = ParkingSpace.query
            # 分页助手
            pagination_helper = PaginationHelper(space_list.count(), page_size)
            if pagination_helper.total_page < page_num:
                return messageToJson(message="页面不存在"), 500
            return messageToJson(data={
                "totalPage": pagination_helper.total_page,
                "dataCount": pagination_helper.data_count,
                "currentPage": page_num,
            },
                queryData=space_list.limit(page_size).offset(pagination_helper.get_offset(page_num)).all()), 200
        else:
            return messageToJson("请求参数不正确"), 500


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
        except KeyError:
            return messageToJson(message="未检测到车牌"), 500

        message = {
            'isOwnerCar': False,
            'inOrOut': '',
            'color': plate_color,
            'number': plate_number
        }
        # 检索是否为业主车
        owner_car = Cars.query.filter(Cars.plateNumber == plate_number).first()
        if owner_car:
            message['isOwnerCar'] = True
        else:
            message['isOwnerCar'] = False
        # 检索停车记录表最新的一条记录
        parking_log = ParkingLog.query.filter(ParkingLog.plateNumber == plate_number).order_by(
            -ParkingLog.enterTime).first()
        if parking_log and parking_log.status == CarStatus.PARKING:
            # 有记录且未离开（本次为出库）
            message['inOrOut'] = 'out'
            parking_log.outTime = current_time()  # 储存外出时间
            # 是否为业主车
            if message['isOwnerCar']:
                parking_log.status = CarStatus.OUT  # 状态为外出
                owner_car.status = CarStatus.OUT  # 同时修改业主车表
                message['ownerData'] = queryToJson(owner_car)  # 返回业主车状态数据
            else:
                parking_log.status = CarStatus.LEAVED  # 状态为驶离开
            # 计算停车时长和应缴费用
            park_time = (datetime.datetime.strptime(parking_log.outTime,
                                                    "%Y-%m-%d %H:%M:%S") - parking_log.enterTime).total_seconds() // 3600  # 计算小时数
            message['parkTime'] = park_time
            message['price'] = calc_price(park_time)
            message['logInfo'] = queryToJson(parking_log)
            # 查询车位状态
            parking_space = ParkingSpace.query.filter(ParkingSpace.plateNumber == plate_number).first()
            if parking_space:
                # 令车位空闲
                parking_space.status = enums.ParkingSpaceStatus.FREE
                parking_space.plateNumber = '-'
                db_session.commit()  # 保存数据库状态
                return messageToJson(data=message)
            else:
                # 车为出库状态，但无入库记录，发出警告
                db_session.commit()  # 保存数据库状态
                return messageToJson(message="车辆状态有误，请联系管理员检查", data=message), 500
        else:
            # 有记录且已离开/无记录（本次为入库）
            message['inOrOut'] = 'in'
            new_parking_log = ParkingLog(plate_number, plate_color, current_time())
            # 是否为业主车
            if message['isOwnerCar']:
                new_parking_log.type = enums.CarType.OWNER
                owner_car.status = CarStatus.PARKING  # 当前状态为停泊
                message['ownerData'] = queryToJson(owner_car)  # 返回业主车状态数据
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
                if parking_space.count > 0:
                    parking_space = parking_space.order_by(ParkingSpace.id).first()
                else:
                    # 此处不保存任何数据库状态
                    return messageToJson(message="已无空闲车位，请稍后", data=message), 500
            # 改变车位状态
            parking_space.status = enums.ParkingSpaceStatus.USED
            parking_space.plateNumber = plate_number
            message['logInfo'] = queryToJson(new_parking_log)
            message['parkingSpace'] = parking_space.spaceName
            # 保存数据库信息
            db_session.commit()
        return messageToJson(data=message)


api.add_resource(AuthView, '/auth')
api.add_resource(RecognitionView, '/recognition')
api.add_resource(CarList, '/car')
api.add_resource(CarDetail, '/car/<car_id>')
api.add_resource(ParkingLogList, '/parkingLog')
api.add_resource(ParkingLogDetail, '/parkingLog/<log_id>')
api.add_resource(ParkingSpaceList, '/parkingSpace')

if __name__ == '__main__':
    app.run(debug=True)
