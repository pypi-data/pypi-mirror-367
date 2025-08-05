import platform
import pyperclip
import struct
import os
import io
import base64
import tempfile
from PIL import Image
from typing import Union, Tuple, List
# 假设 file_downloader.py 在同一目录下
from .file_downloader import FileDownloader
import time
import loguru
import win32console
import win32gui
# --- 新增依赖 ---
# 这个模块需要 'requests' 库来处理 URL。
# 请通过 'pip install requests' 安装。
try:
    import requests
except ImportError:
    requests = None

# --- 全局常量 ---
SUPPORTED_IMAGE_EXTENSIONS = {'.png', '.jpg', '.jpeg', '.bmp', '.gif', '.tiff', '.webp'}
# 【重要】创建全局下载器实例，以便在多次调用中共享缓存
downloader = FileDownloader(cache_duration=10*24*60*60)

# --- Windows 专用模块导入 ---
if platform.system() == 'Windows':
    import win32clipboard
    import win32con

# --- 核心功能函数 ---

def _open_clipboard_with_retry(retries: int = 5, delay: float = 0.1) -> bool:
    """
    尝试打开剪贴板，并在失败时重试。
    
    返回:
        bool: 是否成功打开。
    """
    ...

def save_clipboard() -> dict:
    """保存当前剪贴板内容（Windows支持多格式，其他平台仅保存文本）"""
    ...

def restore_clipboard(saved_data: dict):
    """恢复剪贴板内容"""
    ...

def set_clipboard_text(text: str) -> Tuple[bool, str]:
    """设置剪贴板文本内容（跨平台）"""
    ...

def copy_files_to_clipboard(file_paths: List[str]) -> Tuple[bool, str]:
    """将一个或多个文件路径复制到剪贴板（仅限Windows）。"""
    ...

def copy_image_to_clipboard_from_binary(image_data: bytes) -> Tuple[bool, str]:
    """从二进制数据复制图片到剪贴板。"""
    ...

def set_clipboard_image(image_path: str) -> Tuple[bool, str]:
    ...

def copy_image_to_clipboard_from_base64(base64_data: str) -> Tuple[bool, str]:
    ...

def copy_file_to_clipboard_from_binary(file_data: bytes, filename: str, temp_dir: str = None) -> Tuple[bool, str]:
    ...

def copy_file_to_clipboard_from_base64(base64_data: str, filename: str, temp_dir: str = None) -> Tuple[bool, str]:
    ...


# --- 类型自动识别与读取 ---

def _process_and_copy_url_list(items: List[dict]) -> Tuple[bool, str]:
    """辅助函数：处理含URL或Base64的字典列表，下载并复制为文件。"""
    ...

def copy_auto(content: Union[str, bytes, List], **kwargs) -> Tuple[bool, str]:
    """【修改】自动识别内容类型并复制到剪贴板。"""
    ...


def get_clipboard_content() -> Tuple[Union[str, None], Union[str, list, bytes, None]]:
    """智能检测并获取剪贴板内容（文本、图片或文件）。"""
    ...
