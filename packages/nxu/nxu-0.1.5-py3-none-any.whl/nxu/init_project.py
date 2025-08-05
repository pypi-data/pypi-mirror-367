import os


def setup_project():
    print("🏠当前目录：", os.getcwd())
    print("🔍检查是否存在.nxu.py文件")
    if os.path.exists(".nxu.py"):
        print("🔍.nxu.py文件存在")
    else:
        print("    .nxu.py文件不存在,创建中...")
        with open(".nxu.py", "w", encoding="utf-8") as f:
            f.write("""# 设置代码格式化函数, 以下是使用ruff的示例
from pathlib import Path
#import subprocess

#def format(path):
#    subprocess.run(["uvx", "ruff", "format", path])

target_path = Path() / "_target_config.py"

def format(path):
    pass""")
        print("    .nxu.py文件创建成功")
