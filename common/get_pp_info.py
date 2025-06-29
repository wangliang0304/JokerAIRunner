import base64
import json
import logging
import os
import urllib

from Crypto.Hash import MD5
from Crypto.PublicKey import RSA
from Crypto.Signature import PKCS1_v1_5

from config.Bussiness_config import B_DEVICE_ID, B_DEVICE_TYPE, B_CLIENT_VER
from util.time_util import get_timestamp
from util.yaml_util import get_device_id_in_yml, get_device_type_in_yml, get_device_ver_in_yml


def get_sign(data, type=1):
    """使用了RSA非对称加密算法，通过私钥对data进行MD5哈希后再进行数字签名。同时，对签名结果进行Base64编码以及URL编码
    type: 1:默认C端秘钥，2：B端秘钥
    """
    logging.warning(f"-------------生成sign的传入的请求体数据：{data}")
    PRIVATE_KEY_C = '''MIICdwIBADANBgkqhkiG9w0BAQEFAASCAmEwggJdAgEAAoGBAMNvMFAJ5Ut6Yyba6xndMOl5yOTEU8T/oCzFYAbsnOxcpTHij7xSr8ls1YMv8AQf2igiIK8wJj3y52M2AiMFaDcnkhJ0cUDRRVMMYmuZSWiOpUcH+ET5q9jJH56ZT90trjqab987gvk5fHnBa0cM4HHYmo7xa+Qh11CVLdkeKmOhAgMBAAECgYB/SR+yQX+x1RhW6iZNRh7hMYyCUswsdkEgZ7zPRbQ+zWhaQTFUepY7HkNBmis8xHIVyYR4FWgS2O2TVE23+YGRpudEUMS/C/PcolTQWYBlR3Bvqsdw88tdurDWoHg/+GKaHlR5RBj2zVYPf6meXg/mYLt9xXRU0yDgyXxEWGsgAQJBAOqHXfS7Jfi8giLjwgAN1kbfdSh1WqSalnXdELrM3VZFW/+q9AQI0TOrJsCYfbzyIzbwl6a7DCUj5LOQZEG2tUECQQDVU5Fy6w1uXDDP3U/ccuyayu9ixHVWHv8Rdprpe2RPDr9EiF6tqe1y30gTywBZCJkLpEPpNK4zB1Daps08tDZhAkEAocxD0JvwRVrfuOxCIcFqC7kL3Z6gqyCPHr8lVIoTRPpSzt6Eu+fNVAUGliZd0KWID9YJ+ZffeBv8IrlBwWgoQQJBALI71DZTtTETzaSen+7sBkt+amv3AKIn26zXj66r7a8v/xZfadtnMoDblPkUjwHUcSqM4ECkRzdTUXaeDrQ9TYECQD7Fx4ZEphiWIfKSS+W4C9ZYpx6KcRLSehG9tHBNRc4CA/dRZprdRQL7ZpJLm2xhaXFQ0RGyzEyZEDS3Ugm+7fI='''
    PRIVATE_KEY_B = """MIICdwIBADANBgkqhkiG9w0BAQEFAASCAmEwggJdAgEAAoGBAMmNFvVzs2EbZu5LpEJy0KJeITbsMDDybnaO22vleYM5PHhXo3j3XpDU1o4bhl2WPQ57MutKQn9lvjr/VnsWOfiSxpgaDZQb2p7/RGKVWDgDd6R217YiRU1ok7aeWs2/JrzleuQ4/mUOc54WgDxLVBCZGMuZUi44W1uFGDSrsNoFAgMBAAECgYAatONR6t7eAy+Ea+l8FJKosShdirZoBfe1JgDVLzcGuFLW72Xt5XlWX51+fw8y33F/tbttig19rBGk56ih7rQHi9R+or6PmmqlAArxE7WfW1si5MkES8HK7FTdBIiQsa53sZRJWY8jmm2sLifyALJMxsDhXnsm41dH/WOZtwvOkQJBAOh+K+W/wPOPot6yBQXX5KUI0Xth20vINX/c4htorVyljhmojtR4sPQNHvQ5HOUxBOAKKGNeM97ZFyyrUAWNr5cCQQDd7gZYeDTDwrBYOxK47cf2AIEmRGpSPbFB/AIaxwzcsUC35ODV07shyqZn2ILI8XoQJlXgF+cONpVV198HX/bDAkBcLao57U0TRF/O68YSCwccZ+KmiKXp5fdQOsNrGpWhpgIxKiN3GmMOYCVlrz9Fn6nPKjfZLgBi2q/Vhha0HPkBAkEArr+B15+vTIW8fXzmXR8+WIJFL3Cnl2JkdOSOc69QfWZE44ghUb2KmC0Noq9lK/yYdKb6751inlp0dEeqog/6KQJBAOT6P73J87ESDJO0SlfhBq5eYCZFHP3tML2RW4jwHJnR1EFR5n6qlPZpHnmn7oEEIzljeHXmRw3WAJH72DTm4ZQ="""
    # 默认使用C端私钥，如果需要使用B端私钥，将type改为2
    if type == 1:
        logging.warning("使用C端私钥")
        privateKey = PRIVATE_KEY_C
    elif type == 2:
        logging.warning("使用B端私钥")
        privateKey = PRIVATE_KEY_B
    else:
        raise ValueError("type must be 1 or 2")
    private_keyBytes = base64.b64decode(privateKey)
    priKey = RSA.importKey(private_keyBytes)
    signer = PKCS1_v1_5.new(priKey)
    hash_obj = MD5.new(data.encode('utf-8'))
    signature = base64.b64encode(signer.sign(hash_obj))
    import urllib.parse
    da = urllib.parse.quote(signature)
    return da


def get_device_id():
    # 读取环境变量信息
    PP_DEVICE_ID = os.getenv('PP_DEVICE_ID')
    return PP_DEVICE_ID


def get_device_type():
    # 读取环境变量信息
    PP_DEVICE_TYPE = os.getenv('PP_DEVICE_TYPE')
    return PP_DEVICE_TYPE


def get_device_ver():
    # 读取环境变量信息
    PP_CLIENT_VER = os.getenv('PP_CLIENT_VER')
    return PP_CLIENT_VER


def get_data(timestamp="", token="", **kwargs):
    """C端：验签入参规则"""
    PP_DEVICE_ID = get_device_id_in_yml()
    PP_DEVICE_TYPE = get_device_type_in_yml()
    PP_CLIENT_VER = get_device_ver_in_yml()
    if timestamp is None:
        timestamp = get_timestamp()
        logging.warning(f"-----生成的header中的timestamp: {timestamp}")
    data = PP_DEVICE_ID + PP_DEVICE_TYPE + PP_CLIENT_VER + timestamp + token

    return data


def get_data_business(timestamp="", token="", **kwargs):
    """B端：验签入参规则"""
    if timestamp is None:
        timestamp = get_timestamp()
        logging.warning(f"-----生成的header中的timestamp: {timestamp}")
    data = B_DEVICE_ID + B_DEVICE_TYPE + B_CLIENT_VER + timestamp + token
    logging.warning(f"-----验签入参规则的数据：{data}")

    return data


def get_sign_params_data_bussiness(timestamp="", token="", **kwargs):
    """Bussiness端，不带body的请求，获取验签入参规则"""
    if timestamp is None:
        timestamp = get_timestamp()
        logging.warning(f"-----生成的header中的timestamp: {timestamp}")
    data = B_DEVICE_ID + B_DEVICE_TYPE + B_CLIENT_VER + timestamp + token
    logging.warning(f"-----get请求的拼接参数：{data}")
    return data


if __name__ == '__main__':
    _sign = "uke%2B1BQdyFexJVQpui8VSw3gpuBvT1JwP0XzNArOdMjXE6qjduoqWTUi3vKOpFYX8cNkI%2FtqAwFQd8eQHd8M%2BuWeaQknPQmrF5OGVeMqN9ul%2BJG87RpCxisksCQ6yXSmmLAIVaxWe43wvEU3xvQWxdSeshI0fqWFZewcWsxMuY0%3D"
    _sign_2 = "Va%2BqH%2B%2B%2F2fQ2JYTblgJMHyN6GqxqI%2FdY50gs4e%2B9S%2FTh6ABJyRC%2B1KmVmZFH3MsPUh6K7twqv5xFnv%2FWtugVnxmnOwhYHM6VnoGm1BQyrSG5zeycelyH66SNwlvGebqlbeqEV2NLmGfLAAzOZh%2FMYet3OLcyODLFfcBuOHZTfuk%3D"
    _timestamp = "1709567880945"
    data = get_data(timestamp=_timestamp)
    sign_1 = get_sign(data)
    logging.warning(f"生成sign1：{sign_1}")
    logging.warning(f"抓包sign1：{_sign}")

    body = '{"month": "2024-03"}'
    sign_2 = get_sign(body)
    logging.warning(f"生成sign2：{sign_2}")
    logging.warning(f"抓包sign2：{_sign_2}")
