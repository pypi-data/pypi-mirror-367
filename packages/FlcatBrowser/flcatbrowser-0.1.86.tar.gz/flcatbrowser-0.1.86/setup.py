# setup.py
from setuptools import setup, Extension
from Cython.Build import cythonize
import os

# --- 在这里定义你要编译的模块 ---
# 格式：Extension("包名.模块名", ["源文件路径"])
extensions = [
    Extension(
        "FlcatBrowser.actions",
        ["FlcatBrowser/actions.pyx"]
    ),
    Extension(
        "FlcatBrowser.utils.clipboard",
        ["FlcatBrowser/utils/clipboard.pyx"]
    ),
    Extension(
        "FlcatBrowser.utils.FingerPrint.finger_print",
        ["FlcatBrowser/utils/FingerPrint/finger_print.pyx"]
    ),
    Extension(
        "FlcatBrowser.utils.FingerPrint.device_info",
        ["FlcatBrowser/utils/FingerPrint/device_info.pyx"]
    ),
    Extension(
        "FlcatBrowser.utils.FingerPrint.ua",
        ["FlcatBrowser/utils/FingerPrint/ua.pyx"]
    ),
    Extension(
        "FlcatBrowser._js.base_requests",
        ["FlcatBrowser/_js/base_requests.pyx"]
    ),
    # 如果有更多文件，继续在这里添加
]

# setup() 函数只需要包含 ext_modules 参数。
# 所有其他的项目元数据（如 name, version, author）都由 pyproject.toml 管理。
setup(
    ext_modules=cythonize(
        extensions,
        compiler_directives={'emit_code_comments': False,'language_level': "3"}, # 指定使用 Python 3 语法
        # anntate=True # 可选：生成一个 HTML 报告来分析 Cython 代码
    )
)