from Crypto.PublicKey import RSA
from Crypto.Cipher import PKCS1_v1_5

import base64


def rsa_encrypt():
    # 生成密钥对
    key = RSA.generate(2048)

    # 获取公钥和私钥
    public_key = key.publickey().export_key()
    private_key = key.export_key()

    # 加密明文消息
    message = b"Hello, this is a test message."
    cipher = PKCS1_v1_5.new(RSA.import_key(public_key))
    cipher_text = cipher.encrypt(message)

    # 对加密后的消息进行base64编码
    cipher_text_base64 = base64.b64encode(cipher_text)

    print("加密后的密文: ", cipher_text_base64)


if __name__ == '__main__':
    rsa_encrypt()
