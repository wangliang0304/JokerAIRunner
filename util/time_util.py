import time


def get_timestamp() -> str:
    """
    获取毫秒级时间戳
    :return:
    """
    milliseconds_timestamp = str(round(time.time() * 1000))
    return milliseconds_timestamp


"""
函数实现功能：
1. 根据当前时间获取当日日期：如 20240414
2. 返回值为字符串类型
"""
def get_today_date():
    return time.strftime('%Y%m%d', time.localtime(time.time()))

if __name__ == '__main__':
    # 测试代码
    import logging
    logging.basicConfig(level=logging.INFO)
    logging.info(f"当前日期：{get_today_date()}")
    logging.info(f"时间戳：{get_timestamp()}")
