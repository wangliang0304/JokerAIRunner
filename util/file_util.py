import logging
import os
import shutil


class FileUtils(object):
    """处理本地文件的工具类"""

    def remove_file(self, file_path):
        """删除文件"""
        try:
            os.remove(file_path)
            logging.warning(f"File '{file_path}' has been successfully deleted.")
        except OSError as e:
            print(f"Error deleting file: {e}")

    def remove_dir(self, dir_path):
        """删除目录"""
        try:
            shutil.rmtree(dir_path)
            print(f"Directory '{dir_path}' and its contents have been successfully deleted.")
        except OSError as e:
            print(f"Error deleting directory: {e}")
