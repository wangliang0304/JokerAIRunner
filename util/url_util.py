from urllib.parse import urlparse


def extract_path_from_url(url):
    """urlparse(提取path部分)
    示例：/api/cfront/betting/homepage
    """
    parsed_url = urlparse(url)
    return parsed_url.path


if __name__ == '__main__':
    # 示例URL
    url = "https://ng-apptest.transspay.net/api/cfront/betting/homepage"

    # 提取路径部分
    path = extract_path_from_url(url)
    print(path)
