from sqlalchemy import Column, Integer, String, Time, Boolean, DateTime
from database import Base
from enums import CarStatus, CarType
from utils import md5


class Users(Base):
    __tablename__ = 'users'
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    name = Column(String(100))
    email = Column(String(100), unique=True)
    password = Column(String(100))

    def __init__(self, name, email, password):
        self.name = name
        self.email = email
        self.password = md5(password)


class Cars(Base):
    __tablename__ = 'cars'
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    brand = Column(String(100))
    plateNumber = Column(String(100), unique=True)
    name = Column(String(100))
    houseNumber = Column(String(100))
    phoneNum = Column(String(11))
    idCardNum = Column(String(30))
    status = Column(String(32))

    def __init__(self, brand, plateNumber, name, houseNumber, phoneNum, idCardNum, status=CarStatus.PARKING):
        self.brand = brand
        self.plateNumber = plateNumber
        self.name = name
        self.houseNumber = houseNumber
        self.status = status
        self.phoneNum = phoneNum
        self.idCardNum = idCardNum


class ParkingLog(Base):
    __tablename__ = 'parking_log'
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    plateNumber = Column(String(100))
    plateColor = Column(String(100))
    enterTime = Column(DateTime)
    outTime = Column(DateTime, nullable=True)
    status = Column(String(32))
    cost = Column(Integer, default=0)
    type = Column(String(32), default="外来车")

    def __init__(self, plateNumber, plateColor, enterTime, carType=CarType.FOREIGN, status=CarStatus.PARKING, cost=0):
        self.plateNumber = plateNumber
        self.plateColor = plateColor
        self.enterTime = enterTime
        self.type = carType
        self.status = status
        self.cost = cost


class ParkingSpace(Base):
    __tablename__ = 'parking_space'
    id = Column(Integer, primary_key=True, unique=True, index=True, autoincrement=True)
    type = Column(String(32))
    status = Column(Boolean)
    spaceName = Column(String(100), unique=True)
    plateNumber = Column(String(32), default='0')

    def __init__(self, type, status, spaceName, plateNumber='0'):
        self.type = type
        self.status = status
        self.spaceName = spaceName
        self.plateNumber = plateNumber
