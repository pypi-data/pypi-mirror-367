import os
import platform
import shutil

import psutil


def get_platform_info() -> dict:
    """获取平台的相关信息"""
    platform_info: dict[str:str] = {
        "操作系统": platform.system(),
        "系统发行版本": platform.release(),
        "系统版本信息": platform.version(),
        "平台网络名": platform.node(),
        "平台架构": platform.machine(),
        "CPU信息": platform.processor(),
        "总内存(GB)": round(psutil.virtual_memory().total / (1024 ** 3), 2),  # round(...,2)将一个数四舍五入并保留2位小数
    }
    return platform_info


def get_env(key: str) -> str:
    """获取指定环境变量的值"""
    path_env = os.getenv(key)
    return path_env


def get_compress_format() -> dict:
    """获取支持的压缩格式"""
    return {".zip": "zip", ".tar": "tar", ".tar.gz": "gztar", ".tar.bz": "bztar", ".tar.xz": "xztar"}


def make_archive(src: str, compress_format: str) -> str:
    """
    打包并压缩指定内容；
    :param src:需要打包的文件或目录
    :param compress_format:压缩格式
    :return:打包后文件的完整路径
    """
    src_abs = os.path.abspath(src)  # 获取源文件/目录的绝对路径
    if os.path.isfile(src_abs):  # 判断源路径是否为文件，压缩单个文件时需要传递4个参数
        dir_path = os.path.dirname(src_abs)
        file_name = os.path.basename(src_abs)
        shutil.make_archive(src_abs, compress_format, dir_path, file_name)
    else:
        shutil.make_archive(src_abs, compress_format, src_abs)
    return f'已打包为{src_abs}.{compress_format}文件'

# 1.解包文件
# 2.研究下MCP中提示词的用法
