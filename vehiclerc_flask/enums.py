# from enum import Enum


class CarStatus:
    PARKING = "停泊"
    LEAVED = "驶离"
    OUT = "外出"


class ParkingSpaceStatus:
    FREE = 0
    USED = 1


class CarType:
    OWNER = "业主车"
    FOREIGN = "外来车"


class ParkingSpaceType:
    FUEL = "燃油车位"
    WASHING_ENERGY = "新能源车位"


# 每小时价格
pricePerHour = 10
