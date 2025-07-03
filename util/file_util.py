import logging
import os
import shutil


class FileUtils(object):
    """处理本地文件的工具类"""

    def remove_file(self, file_path):
        """删除文件"""
        try:
            os.remove(file_path)
            logging.info(f"文件删除成功：{file_path}")
        except OSError as e:
            logging.error(f"文件删除失败：{e}")

    def remove_dir(self, dir_path):
        """删除目录"""
        try:
            shutil.rmtree(dir_path)
            logging.info(f"目录删除成功：{dir_path}")
        except OSError as e:
            logging.error(f"目录删除失败：{e}")
