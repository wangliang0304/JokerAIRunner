import logging

import yaml

from util.path_util import get_config_path


# 读取 YAML 配置文件
def get_config_content():
    file = get_config_path()
    # logging.warning("读取配置文件：%s" % file)
    with open(file, 'r', encoding='utf-8') as file:
        config = yaml.safe_load(file)
    # 输出配置信息
    # print(config)
    return config


def get_device_id_in_yml():
    config = get_config_content()
    device_id = config['pp_app']['device_id']
    return device_id


def get_device_type_in_yml():
    config = get_config_content()
    device_type = config['pp_app']['device_type']
    return device_type


def get_device_ver_in_yml():
    config = get_config_content()
    device_ver = config['pp_app']['device_ver']
    return device_ver


if __name__ == '__main__':
    get_device_id_in_yml()
