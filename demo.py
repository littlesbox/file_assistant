import os
import json
import shutil

# ---------- 功能函数 ----------
def get_current_directory() -> str:
    """返回当前工作目录的绝对路径"""
    cwd = os.getcwd()
    return json.dumps({"current_directory": cwd}, ensure_ascii=False)

if __name__ == "__main__":
    print(get_current_directory())