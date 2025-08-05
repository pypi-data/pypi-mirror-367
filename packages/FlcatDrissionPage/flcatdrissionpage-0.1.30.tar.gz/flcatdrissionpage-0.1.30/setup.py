# setup.py
from setuptools import setup, Extension
from Cython.Build import cythonize
import os

# --- 在这里定义你要编译的模块 ---
# 格式：Extension("包名.模块名", ["源文件路径"])
extensions = [
    Extension(
        "DrissionPage",
        ["DrissionPage/func_replace.pyx"]
    ),
    Extension(
        "DrissionPage",
        ["DrissionPage/mouse_trajectory.pyx"]
    ),
    # 如果有更多文件，继续在这里添加
]

# setup() 函数只需要包含 ext_modules 参数。
# 所有其他的项目元数据（如 name, version, author）都由 pyproject.toml 管理。
setup(
    ext_modules=cythonize(
        extensions,
        compiler_directives={'language_level': "3"}, # 指定使用 Python 3 语法
        # anntate=True # 可选：生成一个 HTML 报告来分析 Cython 代码
    )
)