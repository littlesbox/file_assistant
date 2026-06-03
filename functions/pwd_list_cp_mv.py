import os
import json
import shutil
from typing import Optional
from _ensure_in_workspace import _ensure_in_workspace

# ---------- 功能函数 ----------
def get_current_directory() -> str:
    """返回当前工作目录的绝对路径"""
    cwd = os.getcwd()
    return json.dumps({"current_directory": cwd}, ensure_ascii=False)


def list_current_directory_files(extension: str = None, name_contains: str = None) -> str:
    """
    列出当前工作目录下的所有文件（不包含子文件夹），
    可按扩展名或文件名关键字过滤。
    参数：
        extension: 如 ".pdf", ".xlsx"，可选
        name_contains: 文件名包含的字符串，可选
    返回 JSON 字符串，包含文件列表和数量。
    """
    path = os.getcwd()
    files = []
    for f in os.listdir(path):
        full_path = os.path.join(path, f)
        if not os.path.isfile(full_path):
            continue
        # 过滤扩展名
        if extension and not f.lower().endswith(extension.lower()):
            continue
        # 过滤文件名包含字符串
        if name_contains and name_contains.lower() not in f.lower():
            continue
        stat = os.stat(full_path)
        files.append({
            "name": f,
            "path": full_path,
            "extension": os.path.splitext(f)[1].lower(),
            "size_bytes": stat.st_size,
            "modified_time": stat.st_mtime  # 时间戳，方便LLM处理
        })
    return json.dumps({"files": files, "count": len(files)}, ensure_ascii=False)


def list_files(path: Optional[str] = None,
               extension: Optional[str] = None,
               name_contains: Optional[str] = None) -> str:
    """
    列出指定目录下的所有文件（不包含子文件夹）。
    参数：
        path: 目录路径，默认为当前工作目录
        extension: 过滤扩展名，如 ".pdf", ".xlsx"，可选
        name_contains: 文件名包含的字符串，可选
    返回 JSON 字符串，包含文件列表和数量。
    """
    if path is None:
        path = os.getcwd()
    else:
        path = os.path.abspath(path)

    # 校验：目录路径必须在工作目录下
    error = _ensure_in_workspace(path)
    if error:
        return error

    if not os.path.isdir(path):
        return json.dumps({"error": f"目录不存在: {path}"}, ensure_ascii=False)

    files = []
    for f in os.listdir(path):
        full_path = os.path.join(path, f)
        if not os.path.isfile(full_path):
            continue          # 跳过子目录，只保留文件

        # 过滤扩展名
        if extension and not f.lower().endswith(extension.lower()):
            continue
        # 过滤文件名包含字符串
        if name_contains and name_contains.lower() not in f.lower():
            continue

        stat = os.stat(full_path)
        files.append({
            "name": f,
            "path": full_path,
            "extension": os.path.splitext(f)[1].lower(),
            "size_bytes": stat.st_size,
            "modified_time": stat.st_mtime
        })

    return json.dumps({"files": files, "count": len(files)}, ensure_ascii=False)


def list_files_recursive(path: Optional[str] = None,
                         extension: Optional[str] = None,
                         name_contains: Optional[str] = None) -> str:
    """
    递归列出指定目录下的所有文件（包含所有子目录中的文件）。
    参数：
        path: 目录路径，默认为当前工作目录
        extension: 过滤扩展名，如 ".pdf", ".xlsx"，可选
        name_contains: 文件名包含的字符串，可选
    返回 JSON 字符串，包含文件列表和数量。
    """
    if path is None:
        path = os.getcwd()
    else:
        path = os.path.abspath(path)

    # 校验：目录路径必须在工作目录下
    error = _ensure_in_workspace(path)
    if error:
        return error

    if not os.path.isdir(path):
        return json.dumps({"error": f"目录不存在: {path}"}, ensure_ascii=False)

    files = []
    for dirpath, dirnames, filenames in os.walk(path):
        for f in filenames:
            # 过滤扩展名
            if extension and not f.lower().endswith(extension.lower()):
                continue
            # 过滤文件名包含字符串
            if name_contains and name_contains.lower() not in f.lower():
                continue

            full_path = os.path.join(dirpath, f)
            stat = os.stat(full_path)
            files.append({
                "name": f,
                "path": full_path,
                "extension": os.path.splitext(f)[1].lower(),
                "size_bytes": stat.st_size,
                "modified_time": stat.st_mtime
            })

    return json.dumps({"files": files, "count": len(files)}, ensure_ascii=False)



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
    print(list_current_directory_files())