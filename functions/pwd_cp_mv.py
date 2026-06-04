import os
import json
import shutil
from typing import Optional
from ._ensure_in_workspace import _ensure_in_workspace

# ---------- 功能函数 ----------
def get_current_directory() -> str:
    """返回当前工作目录的绝对路径"""
    cwd = os.getcwd()
    return json.dumps({"current_directory": cwd}, ensure_ascii=False)


def copy_file(source: str, destination: str) -> str:
    """
    复制文件到目标目录（保留原文件名）。
    destination 必须是已存在的目录，否则报错。
    """

    # 校验：源文件和目标目录都必须在工作目录下
    error = _ensure_in_workspace(source, destination)
    if error:
        return error

    if not os.path.isfile(source):
        return json.dumps({"success": False, "error": f"源文件不存在: {source}"}, ensure_ascii=False)

    # 目标必须是一个已存在的目录
    if not os.path.isdir(destination):
        return json.dumps({
            "success": False,
            "error": f"目标目录不存在: {destination}。请先使用 create_directory 工具创建该目录。"
        }, ensure_ascii=False)

    dest_file = os.path.join(destination, os.path.basename(source))

    try:
        shutil.copy2(source, dest_file)
        return json.dumps({"success": True, "old_path": source, "new_path": dest_file}, ensure_ascii=False)
    except Exception as e:
        return json.dumps({"success": False, "error": str(e)}, ensure_ascii=False)



def move_file(source: str, destination: str) -> str:
    """
    移动文件到目标目录（保留原文件名）。
    destination 必须是已存在的目录，否则报错。
    """

    # 校验：源文件和目标目录都必须在工作目录下
    error = _ensure_in_workspace(source, destination)
    if error:
        return error

    if not os.path.isfile(source):
        return json.dumps({"success": False, "error": f"源文件不存在: {source}"}, ensure_ascii=False)

    if not os.path.isdir(destination):
        return json.dumps({
            "success": False,
            "error": f"目标目录不存在: {destination}。请先使用 create_directory 工具创建该目录。"
        }, ensure_ascii=False)

    dest_file = os.path.join(destination, os.path.basename(source))

    try:
        shutil.move(source, dest_file)
        return json.dumps({"success": True, "old_path": source, "new_path": dest_file}, ensure_ascii=False)
    except Exception as e:
        return json.dumps({"success": False, "error": str(e)}, ensure_ascii=False)



if __name__ == "__main__":
    print(get_current_directory())
