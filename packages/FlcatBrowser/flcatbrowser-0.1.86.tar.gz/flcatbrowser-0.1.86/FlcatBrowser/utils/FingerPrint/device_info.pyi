import random

from DrissionPage import Chromium

from .ua import UserAgentManager

from .finger_print import FingerPrint

def generate_random_device_info(user_agent: str) -> dict:
    """
    根据传入的 user_agent，在合理范围内随机生成其它指纹信息并返回。
    返回数据结构示例：
    {
        "cpu_core": 4,
        "timezone": "Europe/London",
        "latitude": 51.5074,
        "longitude": -0.1276,
        "user_agent": "传入或随机生成的UA",
        "platform": "iPhone",
        "accept_language": "en-GB",
        "disable_cookies": False,
        "touch_mode": {
            "enabled": True,
            "max_touch_points": 16
        },
        "screen_size": {
            "width": 360,
            "height": 740,
            "mobile": True,
            "scale": 1.1
        }
    }
    """
    ...

def apply_device_info(fp: FingerPrint, device_info):
    """
    将随机选出的设备信息应用到 FingerPrint 实例中。
    """
    ...