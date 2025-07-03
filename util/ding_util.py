import base64
import hashlib
import hmac
import logging
import urllib

import requests
import os
import json
import multiprocessing
import time

from config.ding_config import DING_SECRET, DING_WEBHOOK_URL
from util.path_util import get_allure_report_summary_path
from util.time_util import get_timestamp, get_today_date


def get_ding_sign():
    """获取钉钉的加密验签
    密钥 secret 当做签名字符串，使用HmacSHA256算法计算签名，然后进行Base64 encode，最后再把签名参数再进行urlEncode
    """
    timestamp = get_timestamp()
    secret = DING_SECRET
    secret_enc = secret.encode('utf-8')
    string_to_sign = '{}\n{}'.format(timestamp, secret)
    string_to_sign_enc = string_to_sign.encode('utf-8')
    hmac_code = hmac.new(secret_enc, string_to_sign_enc, digestmod=hashlib.sha256).digest()
    sign = urllib.parse.quote_plus(base64.b64encode(hmac_code))
    print(timestamp)
    print(sign)
    return sign


def send_ding_msg():
    # allure报告结果json路径
    file_name = get_allure_report_summary_path()
    with open(file_name, 'r', encoding='utf-8') as f:
        data = json.load(f)
    logging.info("读取测试报告数据成功")
    case_json = data['statistic']
    case_all = case_json['total']  # 测试用例总数
    case_fail = case_json['failed'] + case_json['broken']  # 失败用例数量（包括broken的用例）
    case_pass = case_json['passed']  # 成功用例数量
    if case_all >= 0:
        # 计算出来当前失败率
        case_rate = round((case_pass / case_all) * 100, 2)
    else:
        logging.warning('未获取到测试执行结果')

    # allure远程在线报告地址
    allure_report_url = f"http://10.130.9.31:10086/{get_today_date()}/index.html"
    # 发送报告内容
    text = f"用例通过率：{case_rate}%" \
           f"\n执行用例数：{case_all}个" \
           f"\n成功用例数：{case_pass}个" \
           f"\n失败用例数：{case_fail}个" \
           f"\n测试报告地址：{allure_report_url}"
    data = {"msgtype":
                "text", "text":
                {"content": "%s" % text},
            "at": {
                # 要@的人
                "atMobiles": " ",
                # 是否@所有人
                "isAtAll": False
            }
            }
    # 钉钉调用URL：https://oapi.dingtalk.com/robot/send?access_token=XXXXXX&timestamp=XXX&sign=XXX
    url = DING_WEBHOOK_URL + f"&timestamp={get_timestamp()}" + f"&sign={get_ding_sign()}"
    headers = {'Content-Type': 'application/json'}
    r = requests.post(url, headers=headers, data=json.dumps(data))
    if r.status_code == 200:
        logging.info("钉钉消息发送成功")
    else:
        logging.error(f"钉钉消息发送失败，状态码：{r.status_code}")


if __name__ == '__main__':
    def allure_report():
        # 执行生成 Allure 报告的操作
        print("Generating Allure report...")
        time.sleep(5)  # 模拟生成报告的耗时操作


    # # 执行生成allure报告
    # a = multiprocessing.Process(target=allure_report)
    # # 执行发送钉钉机器人
    # b = multiprocessing.Process(target=send_ding)
    # a.start()
    # time.sleep(5)
    # b.start()

    # 保证报告生成后，才发送邮件
    a = multiprocessing.Process(target=allure_report)
    b = multiprocessing.Process(target=send_ding_msg)

    a.start()
    a.join()  # 等待 allure_report 执行完毕
    b.start()
