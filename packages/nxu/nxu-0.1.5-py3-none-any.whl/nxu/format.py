from .config import get_config
from pathlib import Path


def format_code(path: Path):
    config = get_config()

    config.format(path)
    print("🎉 格式化完成")
