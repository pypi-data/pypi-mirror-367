import platform

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
