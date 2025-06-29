import os
import paramiko

from config.server_config import REMOTE_SERVER_URL, USER_NAME, PASSWORD, REMOTE_PATH
from util.path_util import get_allure_html_report_path


class SftpUploader:
    def __init__(self, hostname, port, username, password):
        self.hostname = hostname
        self.port = port
        self.username = username
        self.password = password
        self.client = paramiko.SSHClient()
        self.client.set_missing_host_key_policy(paramiko.AutoAddPolicy())

    def connect(self):
        self.client.connect(self.hostname, self.port, self.username, self.password)

    def disconnect(self):
        self.client.close()

    def create_remote_dir_structure(self, local_dir, remote_dir):
        with self.client.open_sftp() as sftp:
            for root, dirs, files in os.walk(local_dir):
                for dirname in dirs:
                    local_path = os.path.join(root, dirname)
                    remote_path = remote_dir + '/' + os.path.relpath(local_path, local_dir).replace('\\', '/')
                    try:
                        sftp.chdir(remote_path)
                    except IOError:
                        sftp.mkdir(remote_path)
                        print(f"远程目录 {remote_path} 创建成功")
                self.upload_files(root, files, local_dir, remote_dir, sftp)

    def upload_files(self, root, files, local_dir, remote_dir, sftp):
        for file in files:
            local_path = os.path.join(root, file)
            remote_path = remote_dir + '/' + os.path.relpath(local_path, local_dir).replace('\\', '/')
            sftp.put(local_path, remote_path, confirm=True)  # 添加 confirm=True 参数以直接覆盖已存在文件
            print(f"文件 {local_path} 已成功上传到 {remote_path}")


if __name__ == '__main__':
    # 设置连接信息和目录路径
    hostname = REMOTE_SERVER_URL
    port = 22
    username = USER_NAME
    password = PASSWORD
    local_dir = get_allure_html_report_path()
    remote_dir = REMOTE_PATH

    # 创建 SftpUploader 实例并上传文件
    uploader = SftpUploader(hostname, port, username, password)
    uploader.connect()
    uploader.create_remote_dir_structure(local_dir, remote_dir)
    uploader.disconnect()
