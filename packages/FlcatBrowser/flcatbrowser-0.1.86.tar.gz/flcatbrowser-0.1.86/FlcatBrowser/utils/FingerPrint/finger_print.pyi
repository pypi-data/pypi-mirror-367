#!/usr/bin/env python
# -*- coding:utf-8 -*-
from DrissionPage._pages.mix_tab import MixTab

class FingerPrint:
    def __init__(self, tab: MixTab):
        ...

    def set_timezone(self, timezone="Europe/London"):
        ...

    def set_set_geolocation(self, latitude=51.5074, longitude=-0.1276, accuracy=100):
        ...

    def set_user_agent(self, user_agent, platform='iPhone', accept_language='en-GB'):
        ...
    
    def set_touch_mode(self, enabled=True, max_touch_points=1):
        ...
    
    def set_rpa_feature(self, enabled=True):
        ...

    def disable_cookies(self):
        ...

    def set_cpu_core(self,core=2):
        ... 

    def time_speed(self, policy='advance', budget=1000):
        ...
    
    def set_locale(self, locale):  # 设置模拟的地理位置、语言和时区
        ...
    
    def set_3d(self, x=1, y=0, z=0, alpha=10, beta=20, gamma=30):
        ...

    def set_size(self, width=360, height=740, mobile=True, scale=1):
        """
        mobile必须为true才能设置屏幕尺寸否则开启模拟后将被检测到使用固定屏幕尺寸，浏览器内窗口尺寸却会变化
        """
        ...

    def reset_size(self):
        ...
    