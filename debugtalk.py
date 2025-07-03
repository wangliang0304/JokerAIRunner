import json
import logging
import os
import sys
import time
from typing import List

from common.get_pp_info import get_sign, get_data, get_device_id, get_device_ver, get_device_type, get_data_business

# import pymysql
import yaml

from common.get_token import get_token, write_token_to_yml
from common.get_token_bussiness import write_bussiness_token_to_yml, get_token_bussiness
from config.Bussiness_config import B_DEVICE_ID, B_DEVICE_TYPE, B_CLIENT_VER
from util.time_util import get_timestamp


# commented out function will be filtered
# def get_headers():
#     return {"User-Agent": "hrp"}


def get_user_agent():
    return "hrp/funppy"


def sleep(n_secs):
    time.sleep(n_secs)


def sum(*args):
    result = 0
    for arg in args:
        result += arg
    return result


def sum_ints(*args: List[int]) -> int:
    result = 0
    for arg in args:
        result += arg
    return result


def sum_two_int(a: int, b: int) -> int:
    return a + b


def sum_two_string(a: str, b: str) -> str:
    return a + b


def sum_strings(*args: List[str]) -> str:
    result = ""
    for arg in args:
        result += arg
    return result


def concatenate(*args: List[str]) -> str:
    result = ""
    for arg in args:
        result += str(arg)
    return result


def get_pp_timestamp() -> str:
    milliseconds_timestamp = get_timestamp()
    return str(milliseconds_timestamp)


def setup_hooks_request(request):
    logging.debug("正在处理C端请求前置信息")
    # 请求体参数
    body_data = request.get('data') if request.get('data') else request.get('req_json')
    _timestamp = get_pp_timestamp()
    multi_env = {'multi_env': 'wl'}
    _device_id = get_device_id()
    _device_type = get_device_type()
    _device_ver = get_device_ver()
    _token = get_token()
    data = get_data(_timestamp, _token)
    _get_pp_sign = get_sign(data)
    if body_data:
        if type(body_data) is dict:
            body_data = json.dumps(body_data)  # 兼容with_data 和 with_json
        sign2 = get_sign(body_data)
    else:
        sign2 = _get_pp_sign
    pp_device_id = {'pp_device_id': _device_id}
    pp_device_type = {'pp_device_type': _device_type}
    pp_client_ver = {'pp_client_ver': _device_ver}
    pp_token = {'pp_token': _token}
    pp_req_sign = {'pp_req_sign': _get_pp_sign}
    pp_timestamp = {'pp_timestamp': _timestamp}
    pp_req_sign_2 = {'pp_req_sign_2': sign2}
    header = {
        'multi_env': multi_env,
        'pp_device_id': _device_id,
        'pp_device_type': _device_type,
        'pp_client_ver': _device_ver,
        'pp_token': _token,
        'pp_req_sign': _get_pp_sign,
        'pp_timestamp': _timestamp,
        'pp_req_sign_2': sign2
    }
    if 'headers' in request:
        if bool(request['headers']) is True:
            request['headers'].update(multi_env)
            request['headers'].update(pp_device_id)
            request['headers'].update(pp_device_type)
            request['headers'].update(pp_client_ver)
            request['headers'].update(pp_token)
            request['headers'].update(pp_req_sign)
            request['headers'].update(pp_timestamp)
            request['headers'].update(pp_req_sign_2)
        else:
            request['headers'].update(header)
    else:
        request['headers'] = header
    return request


def setup_hooks_request_business(request):
    logging.debug("正在处理B端请求前置信息")
    # 请求体参数
    body_data = request.get('data') if request.get('data') else request.get('req_json')
    _timestamp = get_pp_timestamp()
    multi_env = {'multi_env': 'joker'}
    _device_id = B_DEVICE_ID
    _device_type = B_DEVICE_TYPE
    _device_ver = B_CLIENT_VER
    # 获取B端token
    _token = get_token_bussiness()
    # 验签入参
    data = get_data_business(_timestamp, _token)
    _get_pp_sign = get_sign(data=data, type=2)
    if body_data:
        if type(body_data) is dict:
            body_data = json.dumps(body_data)  # 兼容with_data 和 with_json
        sign2 = get_sign(data=body_data, type=2)
    else:
        sign2 = _get_pp_sign
    pp_device_id = {'pp_device_id': _device_id}
    pp_device_type = {'pp_device_type': _device_type}
    pp_client_ver = {'pp_client_ver': _device_ver}
    pp_token = {'pp_token': _token}
    pp_req_sign = {'pp_req_sign': _get_pp_sign}
    pp_timestamp = {'pp_timestamp': _timestamp}
    pp_req_sign_2 = {'pp_req_sign_2': sign2}
    header = {
        'multi_env': multi_env,
        'pp_device_id': _device_id,
        'pp_device_type': _device_type,
        'pp_client_ver': _device_ver,
        'pp_token': _token,
        'pp_req_sign': _get_pp_sign,
        'pp_timestamp': _timestamp,
        'pp_req_sign_2': sign2
    }
    if 'headers' in request:
        if bool(request['headers']) is True:
            request['headers'].update(multi_env)
            request['headers'].update(pp_device_id)
            request['headers'].update(pp_device_type)
            request['headers'].update(pp_client_ver)
            request['headers'].update(pp_token)
            request['headers'].update(pp_req_sign)
            request['headers'].update(pp_timestamp)
            request['headers'].update(pp_req_sign_2)
        else:
            request['headers'].update(header)
    else:
        request['headers'] = header
    return request


def get_pp_sign(timestamp="", data="", token="", **kwargs):
    """
    获取rsa签名
    :param data: get请求不传数据，默认生成sign，post请求需要传data数据，用于生成sign2
    :param kwargs:
    :return:
    """
    logging.debug("正在生成RSA签名")
    if data:
        # 请求体加密：sign2
        sign = get_sign(data, **kwargs)
    else:
        # 请求同加密sign1
        data = get_data(timestamp, token)
        sign = get_sign(data, **kwargs)
    return sign


def get_token_plugin():
    return get_token()


def setup_hook_example(name):
    logging.debug("执行示例前置钩子")
    return f"setup_hook_example: {name}"


def setup_hook_session():
    logging.info("开始初始化会话Token")
    # C端：token预处理
    write_token_to_yml()
    # B端：token预处理
    write_bussiness_token_to_yml()
    logging.info("会话Token初始化完成")


def teardown_hook_example(name):
    logging.debug("执行示例后置钩子")
    return f"teardown_hook_example: {name}"


if __name__ == '__main__':
    get_pp_timestamp()
    # connect_database('config.yml', 'SELECT * FROM test')
