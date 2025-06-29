import json
import logging

import yaml

from config.palmpay_config import PP_MOBILE_NO, PP_PIN
from util.path_util import get_token_path
from util.time_util import get_timestamp


def get_token():
    """获取C端token"""
    file = get_token_path()
    with open(file, "r", encoding="utf-8") as f:
        data = yaml.safe_load(f)
        print(f"获取的data为：{data}")

    # 获取第一行数据
    first_line = data.split('\n')[0]
    print(f"获取的token为：{first_line}")
    return first_line


def pp_login_token():
    body = {
        "blackBox": "kGPVt1709101301snISt5F87Ic",
        "pinType": 1,
        "appVersion": "5.3.0",
        "brand": "INFINIX",
        "deviceInfo": "bee648d4b0a5ab70",
        "deviceModel": "InfinixX671B",
        "deviceTag": "",
        "deviceVersion": "Android13",
        "fcmToken": "eXIQkBq6S1iiC3EZOqcp52:APA91bF1BWaENypIZmaDktQ3OHdRYCQSNDozYSAcTK2cTirTtZZV4MbEDrQc7QmeXIl4Hv5S1As2ovOdFuW0ScxQxjNBpnlLi-XBvF59BUFSmKEiVvZi3wbzAjbfCYkXrVMdmI8mIyI9",
        "gaid": "715131e3-1810-4c6d-8dc3-c6776a8b63cc",
        "imei": "bee648d4b0a5ab70012345",
        "mobileNo": PP_MOBILE_NO,
        "phoneLock": "0",
        "phoneLockIsActive": False,
        "phoneLockStatus": -128,
        "pin": PP_PIN,
        "resolution": "2400X1080_480",
        "supplement": False,
    }

    headers = {
        'pp_device_id': 'A84076CC-2FC7-47C8-A1B6-0E2F5D693E52',
        'pp_device_type': 'IOS',
        'pp_client_ver': '5.3.0&2402281',
        'pp_timestamp': '1709522542394',
        'user-agent': 'PalmPay/5.3.0&602280702 (Android 13)',
        'pp_channel': 'googleplay',
        'pp_token': '',
        'pp_req_sign': 'Hiohtl5nAzo1k3WheSR9lR7XteQhACOYPMLWAER%2FsA0UcaQaqpjrZO2gb4aBG2yZ4RI8mGkQbF2sV0sUp5X3djlvce6csKkEpZ0%2FwUWQvMJVWEfaepXO6Owo5ACeKsRL7BL8r8d%2BHN4Nf48EFofcUPJgCEy8uZf184C4r80dizU%3D',
        'pp_req_sign_2': 'Va%2BqH%2B%2B%2F2fQ2JYTblgJMHyN6GqxqI%2FdY50gs4e%2B9S%2FTh6ABJyRC%2B1KmVmZFH3MsPUh6K7twqv5xFnv%2FWtugVnxmnOwhYHM6VnoGm1BQyrSG5zeycelyH66SNwlvGebqlbeqEV2NLmGfLAAzOZh%2FMYet3OLcyODLFfcBuOHZTfuk%3D',
        'content-type': 'application/json; charset=utf-8',
        'content-length': '634',
        'accept-encoding': 'gzip'
    }

    from common.get_pp_info import get_data, get_sign
    from util.yaml_util import get_device_id_in_yml, get_device_ver_in_yml, get_device_type_in_yml

    PP_DEVICE_ID = get_device_id_in_yml()
    PP_DEVICE_TYPE = get_device_type_in_yml()
    PP_CLIENT_VER = get_device_ver_in_yml()
    timestamp = get_timestamp()
    data = get_data(timestamp=timestamp, token="")
    sign1 = get_sign(data)
    sign2 = get_sign(json.dumps(body))
    headers['pp_device_id'] = PP_DEVICE_ID
    headers['pp_device_type'] = PP_DEVICE_TYPE
    headers['pp_client_ver'] = PP_CLIENT_VER
    headers['pp_timestamp'] = timestamp
    headers['pp_req_sign'] = sign1
    headers['pp_req_sign_2'] = sign2
    logging.warning(f"headers：{headers}")

    import requests

    url = "https://ng-apptest.transspay.net/api/c-bff-product/start/loginV2"
    response = requests.request("POST", url, headers=headers, json=body)
    # print(response.text)
    token = response.json().get("data").get("token")
    logging.warning(f"登录获取的token：{token}")

    return token


def write_token_to_yml():
    file = get_token_path()
    token = pp_login_token()
    #  `default_flow_style=False` 参数，可以禁用默认的文档分隔符，保证在写入文件时不会出现多余的点号
    with open(file, "w", encoding="utf-8") as f:
        yaml.safe_dump(token, f, default_flow_style=False)


if __name__ == '__main__':
    # pp_login_token()
    # write_token_to_yml()
    get_token()
