"""
实现自动化平台数据统计：调用次数 + 节省时长
"""
import base64
import logging
import time
import uuid
from typing import Union

import requests
from Crypto.Cipher import AES
from Crypto.Util.Padding import pad


# 1. 通过 ak 和 sk 来生成 signature算法
def aes_encrypt(src: str, secret_key: str, iv: str) -> str:
    if not secret_key:
        raise ValueError("secret_key is empty")

    try:
        # Convert secret_key and iv to bytes
        secret_key = secret_key.encode('utf-8')
        iv = iv.encode('utf-8')

        # Create AES cipher object in CBC mode with PKCS5 padding
        cipher = AES.new(secret_key, AES.MODE_CBC, iv)

        # Pad the input data to a multiple of AES block size
        padded_data = pad(src.encode('utf-8'), AES.block_size)

        # Encrypt the data
        encrypted = cipher.encrypt(padded_data)

        # Return the encrypted data as a base64-encoded string
        return base64.b64encode(encrypted).decode('utf-8')
    except Exception as e:
        raise RuntimeError("AES encrypt error") from e


# 2. 生成签名，并设置到 header
def get_headers(access_key: str, secret_key: str) -> dict:
    timestamp = int(round(time.time() * 1000))

    combox_key = access_key + '|padding|' + str(timestamp)
    signature = aes_encrypt(combox_key, secret_key, access_key)

    return {'accessKey': access_key, 'signature': signature}


# 3. 调用自动化平台造数接口（统计自动化次数和节省时间）
class MeterSphere:
    def __init__(self):
        # self.domain = "https://ms.chuanyinet.com" #域名升级20240506
        # self.domain = "https://ms.palmpay-inc.com"
        self.domain = "https://metersphere-daily.palmpay-inc.com"
        self.access_key = "ERKbeWJiStvyPQsc"
        self.secret_key = "sxmwgxBv91bxxLV1"

    def _request(self, path: str, body: dict = None) -> Union[dict, list]:
        """
        :param path:
        :param body: if body is empty, will use get method
        :return:
        """
        url = f"{self.domain.rstrip('/')}/{path.lstrip('/')}"

        headers = {'Content-Type': 'application/json', 'ACCEPT': 'application/json'}
        headers.update(get_headers(self.access_key, self.secret_key))

        logging.debug("请求URL: %s", url)
        if body:
            resp = requests.post(url, headers=headers, json=body)
        else:
            resp = requests.get(url, headers=headers)

        if resp.status_code == 200:
            logging.info("自动化平台API调用成功")
        else:
            logging.error("自动化平台API调用失败，状态码: %s", resp.status_code)
        return resp.json()

    def post_factory_api(self):
        res = self._request('/data-factory/data/run', body={
            "id": 539,
            "params": [],
            "mode": "run",
            "env": "TEST"
        })
        logging.info("自动化数据统计接口调用完成")
        return res

    def get_autocase(self):
        res = self._request('/dashboards/scenario?startTime=2025-03-31&endTime=2025-04-07')
        logging.info("获取自动化用例数据完成")
        return res

if __name__ == '__main__':
    ms = MeterSphere()
    # ms.post_factory_api()
    ms.get_autocase()
