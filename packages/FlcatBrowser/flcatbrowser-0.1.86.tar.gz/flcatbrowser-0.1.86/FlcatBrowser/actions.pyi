import random
import time
from enum import Enum
from DrissionPage._pages.mix_tab import MixTab
from DrissionPage.common import Keys
from .utils import clipboard as cb
from typing import List
import loguru
import random

class ActionsConfig:
    def __init__(self, action_speed_ratio = 1, get_need_wait = None, clipboard_lock = None):
        ...

default_config = ActionsConfig()

def get_random_offset(element, min_x_offset=None, max_x_offset=None, min_y_offset=None, max_y_offset=None):
    ...

# 最后的bool表示是否应用action_speed_ratio
class SleepTime(Enum):
    MOUSE_RELEASE = (0.1, 0.2, False)
    KEY_RELEASE = (0.05, 0.1, False)
    KEY_INTERVAL = (0.03, 0.05, False)
    KEY_DOWN = (0.05, 0.1, False)
    HUMAN_THINK = (0.2, 2, True)
    WAIT_PAGE = (1, 1.5, True)
    NONE_OPERATION = (1, 5, True)
    DELETE_TEXT = (5, 10, True)

def sleep(sleep_time: SleepTime, config: ActionsConfig):
    ...
def move_to(tab: MixTab, ele_or_loc, timeout=3, offset_x: float = 0, offset_y: float = 0, min_x_offset=None, max_x_offset=None, min_y_offset=None, max_y_offset=None, config: ActionsConfig = default_config):
    ...
def click(tab: MixTab, ele_or_loc, more_real=True, act_click=False, timeout=3, offset_x: float = 0, offset_y: float = 0, min_x_offset=None, max_x_offset=None, min_y_offset=None, max_y_offset=None, config: ActionsConfig = default_config):
    ...    
def hold(tab: MixTab, ele_or_loc, more_real=True, act_click=False, timeout=3, offset_x: float = 0, offset_y: float = 0, config: ActionsConfig = default_config):
    ...    
def release(tab: MixTab, config: ActionsConfig = default_config):
    ...
def type_message_to_shift_and_enter(message: str):
    ...
def _get_ele_text(tab: MixTab, ele_or_loc, timeout=3):
    ...
def type(tab: MixTab, ele_or_loc, message: str | dict, more_real=True, timeout=3, config=default_config, assist_ele=None):
    ...
def __paste(tab: MixTab, message, config=default_config):
    ...
def _paste(tab: MixTab, message, config=default_config):
    ...        
def type_and_send(tab: MixTab, ele_or_loc, messages: str | List[dict], more_real=True, timeout=3, config=default_config, assist_ele=None):
    ...
def send_key(tab: MixTab, key: Keys, config: ActionsConfig = default_config):
    ...
def scroll(tab: MixTab, ele_or_loc, delta_y, delta_x, timeout=3, config: ActionsConfig = default_config):
    ...
def simulated_human(tab: MixTab, config: ActionsConfig = default_config):
    ...