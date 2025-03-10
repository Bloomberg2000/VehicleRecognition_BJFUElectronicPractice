import gzip
import json
import os
import urllib

import enums
import utils
from aip import AipSpeech

basedir = os.path.abspath(os.path.dirname(__file__))

""" 你的 APPID AK SK """
APP_ID = ''
API_KEY = ''
SECRET_KEY = ''
client = AipSpeech(APP_ID, API_KEY, SECRET_KEY)


def speech(is_owner_car, in_or_out, plate_number="", restriction_array=[], parking_place="",
           parking_time="", parking_cost=""):
    content = ""
    # 业主车
    if is_owner_car:
        if in_or_out == 'in':
            content += "欢迎回家！"
            content += "您的车位号为" + parking_place + "。"
            if utils.is_restriction(plate_number, restriction_array):
                content += "温馨提示，您的车辆明日限行！提前做好出行规划！"
            # 判断限行

        if in_or_out == 'out':
            if utils.is_restriction(plate_number, restriction_array):
                content += "温馨提示，您的车辆今日限行！"
            weather = get_weather_data()
            today_weather = weather['data']['forecast'][0]
            today_weather['high'] = today_weather['high'].replace("高温", "最高温度")
            today_weather['low'] = today_weather['low'].replace("低温", "最低温度")
            content += "今天天气" + today_weather['type'] + '。'+today_weather['high'] + \
                       today_weather['low']
            content += '祝您一路顺风'

    else:
        if in_or_out == 'in':
            content += "您好！欢迎光临！您的车位号为" + parking_place + "。"
            if utils.is_restriction(plate_number, restriction_array):
                content += "温馨提示，您的车辆明日限行！提前做好出行规划！"
        if in_or_out == 'out':
            content += "您的停车时间为" + parking_time + "小时，需缴费" + parking_cost + "元。"
            weather = get_weather_data()
            today_weather = weather['data']['forecast'][0]
            today_weather['high'] = today_weather['high'].replace("高温", "最高温度")
            today_weather['low'] = today_weather['low'].replace("低温", "最低温度")
            content += "今天天气" + today_weather['type'] + '。' + today_weather['high'] + \
                       today_weather['low']

    result = client.synthesis(content, 'zh', 1, {'spd': 5, 'vol': 6, 'per': 0})
    # 识别正确返回语音二进制 错误则返回dict 参照下面错误码
    filename = utils.md5(utils.current_time())
    if not isinstance(result, dict):
        with open(basedir + "/static/audio/{}".format(filename) + '.mp3', 'wb') as f:
            f.write(result)
    return filename


# 获取天气
def get_weather_data():
    url1 = 'http://wthrcdn.etouch.cn/weather_mini?city=' + urllib.parse.quote("北京")
    weather_data = urllib.request.urlopen(url1).read()
    weather_data = gzip.decompress(weather_data).decode('utf-8')
    return json.loads(weather_data)
