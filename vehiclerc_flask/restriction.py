import sys
import urllib, json
import urllib.request
from urllib.parse import urlencode
import importlib

importlib.reload(sys)


def get_restriction_info(type):
    """
    type:查询限号类型，1:今天 2:明天 3:后天
    """
    params = {"key": "63dff571549c3ff165a9d685027c5fe0", "city": "beijing", "type": type}
    return restriction_query(params)


def restriction_query(params):
    params = urlencode(params)
    url = 'http://v.juhe.cn/xianxing/index?%s' % params
    wp = urllib.request.urlopen(url)
    content = wp.read()
    res = json.loads(content)
    if res:
        error_code = res['error_code']
        if error_code == 0:
            return res['result']
        else:
            return False
    else:
        return False
