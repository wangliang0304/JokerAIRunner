import json
import logging

import yaml

from common.get_pp_info import get_sign_params_data_bussiness
from config.Bussiness_config import B_DEVICE_ID, B_DEVICE_TYPE, B_CLIENT_VER, B_PHONE, B_PASSWORD
from config.palmpay_config import PP_MOBILE_NO, PP_PIN
from util.path_util import get_token_path, get_token_path_bussiness
from util.time_util import get_timestamp


def get_token_bussiness():
    """获取B端token"""
    file = get_token_path_bussiness()
    with open(file, "r", encoding="utf-8") as f:
        data = yaml.safe_load(f)
        logging.debug("读取B端Token配置")

    # 获取第一行数据
    first_line = data.split('\n')[0]
    logging.debug("获取B端Token成功")
    return first_line


def bussiness_login_token():
    body = {
        "birthday": "2002-01-19",
        "firstName": "Ajibade",
        "middleName": "null",
        "lastName": "Oluwasegun",
        "gender": 1,
        "loginPasswordExits": "true",
        "loginPreOperation": ["otpCheck"],
        "memberExits": "true",
        "palmPayPinExits": "true",
        "payPasswordExits": "true",
        "mobileNo": B_PHONE,
        "phone": B_PHONE,
        "supplement": "false",
        "loginPassword": "16D0EB124EA150070CD00B062EBAFC72",
        "appSource": "1",
        "oldLoginPassword": "16D0EB124EA150070CD00B062EBAFC72",
        "otpToken": "xx",
        "deviceInfo": {
            "appVersion": "3.12.4",
            "blackBox": "vGPVE1713506315RU4afywZvJd",
            "brand": "INFINIX",
            "deviceInfo": "c77d77a4a7568dd8",
            "deviceModel": "InfinixX671B",
            "deviceVersion": "Android13",
            "fcmToken": "dSxv4fKgS_SN6pgIOGBjPc:APA91bFQ2Ib0D1uywI956xM17IBZ0ioJA9D9w6m0O_5pKPH-mn_CNOvN3Zvhp3cu2HDh2lyC1NM7SoZ4OQToPLQt52rf2VmJsycdY6s4zZRkG-LBrbJxCa6EwRJogv7bjotT4rPIvfyP",
            "gaid": "715131e3-1810-4c6d-8dc3-c6776a8b63cc",
            "imei": "PARTNER_c77d77a4a7568dd8012345",
            "resolution": "2400X1080_480"
        }
    }

    headers = {
        'pp_device_id': 'PARTNER_c77d77a4a7568dd8012345',
        'pp_device_type': 'ANDROID',
        'pp_client_ver': '3.12.4&604021107',
        "pp_client_ver_code": "604021107",
        'pp_timestamp': '1713430492119',
        'memberid': '0',
        'pp_token': '',
        'pp_req_sign': 'Hiohtl5nAzo1k3WheSR9lR7XteQhACOYPMLWAER%2FsA0UcaQaqpjrZO2gb4aBG2yZ4RI8mGkQbF2sV0sUp5X3djlvce6csKkEpZ0%2FwUWQvMJVWEfaepXO6Owo5ACeKsRL7BL8r8d%2BHN4Nf48EFofcUPJgCEy8uZf184C4r80dizU%3D',
        'pp_req_sign_2': 'Va%2BqH%2B%2B%2F2fQ2JYTblgJMHyN6GqxqI%2FdY50gs4e%2B9S%2FTh6ABJyRC%2B1KmVmZFH3MsPUh6K7twqv5xFnv%2FWtugVnxmnOwhYHM6VnoGm1BQyrSG5zeycelyH66SNwlvGebqlbeqEV2NLmGfLAAzOZh%2FMYet3OLcyODLFfcBuOHZTfuk%3D',
        'content-type': 'application/json; charset=utf-8',
    }

    from common.get_pp_info import get_data, get_sign

    timestamp = get_timestamp()
    data = get_sign_params_data_bussiness(timestamp=timestamp, token="")
    sign1 = get_sign(data, type=2)
    sign2 = get_sign(json.dumps(body), type=2)
    headers['pp_device_id'] = B_DEVICE_ID
    headers['memberid'] = B_DEVICE_ID
    headers['pp_device_type'] = B_DEVICE_TYPE
    headers['pp_client_ver'] = B_CLIENT_VER
    headers['pp_timestamp'] = timestamp
    headers['pp_req_sign'] = sign1
    headers['pp_req_sign_2'] = sign2
    logging.warning(f"headers：{headers}")

    import requests
    # 前置调用otp接口，获取对应的otp Token
    otp_url = "https://ng-pa-apptest.transspay.net/api/cfront/risk/checkOTP"
    otp_body = {
        "businessType": 2,
        "voiceSms": 0,
        "mobileNo": "023409017764039",
        "verifyCode": "2580"
    }
    r = requests.post(otp_url, json=otp_body, headers=headers)
    if r.status_code == 200:
        logging.info("B端OTP验证成功")
    else:
        logging.error("B端OTP验证失败")
    otp_toeken = r.json().get("data").get("securityToken")
    logging.debug("获取OTP Token完成")

    # B端登录调用
    url = "https://ng-pa-apptest.transspay.net/api/business-bff-product/merchant/micro/user/login"
    body["otpToken"] = otp_toeken   # 替换body中的otpToken
    logging.debug("更新登录请求体")
    response = requests.request("POST", url, headers=headers, json=body)
    token = response.json().get("data").get("token")
    logging.info("B端登录成功，Token获取完成")

    return token


def write_bussiness_token_to_yml():
    file = get_token_path_bussiness()
    token = bussiness_login_token()
    #  `default_flow_style=False` 参数，可以禁用默认的文档分隔符，保证在写入文件时不会出现多余的点号
    with open(file, "w", encoding="utf-8") as f:
        yaml.safe_dump(token, f, default_flow_style=False)


if __name__ == '__main__':
    # bussiness_login_token()
    write_bussiness_token_to_yml()
    get_token_bussiness()
