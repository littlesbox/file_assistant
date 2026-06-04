import os
import json
import shutil
from typing import Optional
import datetime
from ._ensure_in_workspace import _ensure_in_workspace


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
            "modified_time": datetime.datetime.fromtimestamp(stat.st_mtime).strftime("%Y-%m-%d %H:%M:%S")  # 时间戳，方便LLM处理
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
            "modified_time": datetime.datetime.fromtimestamp(stat.st_mtime).strftime("%Y-%m-%d %H:%M:%S")
        })

    return json.dumps({"files": files, "count": len(files)}, ensure_ascii=False)


def list_directory(path: Optional[str] = None,
                   extension: Optional[str] = None,
                   name_contains: Optional[str] = None) -> str:
    """
    列出指定目录下的所有项目（包括文件和子文件夹），不进行递归。
    参数：
        path: 目录路径，默认为当前工作目录
        extension: 过滤扩展名（仅对文件有效），如 ".pdf"，可选
        name_contains: 名称中包含的字符串（对文件和文件夹均有效），可选
    返回 JSON 字符串，包含项目列表和总数。
    """
    if path is None:
        path = os.getcwd()
    else:
        path = os.path.abspath(path)

    # 校验：目录路径必须在工作目录下（复用已有的安全函数）
    error = _ensure_in_workspace(path)
    if error:
        return error

    if not os.path.isdir(path):
        return json.dumps({"error": f"目录不存在: {path}"}, ensure_ascii=False)

    items = []
    for entry in os.listdir(path):
        full_path = os.path.join(path, entry)

        # 判断是文件还是目录
        is_dir = os.path.isdir(full_path)
        is_file = os.path.isfile(full_path)

        # 跳过既不是文件也不是目录的（如符号链接，可根据需要处理）
        if not (is_dir or is_file):
            continue

        # 如果是文件，应用扩展名过滤
        if is_file and extension and not entry.lower().endswith(extension.lower()):
            continue

        # 名称包含过滤（对文件和文件夹都有效）
        if name_contains and name_contains.lower() not in entry.lower():
            continue

        item_info = {
            "name": entry,
            "path": full_path,
            "type": "directory" if is_dir else "file",
        }

        # 仅对文件添加额外元数据
        if is_file:
            stat = os.stat(full_path)
            item_info["extension"] = os.path.splitext(entry)[1].lower()
            item_info["size_bytes"] = stat.st_size
            item_info["modified_time"] = datetime.datetime.fromtimestamp(stat.st_mtime).strftime("%Y-%m-%d %H:%M:%S")
        else:
            # 目录也可以添加修改时间等信息，按需提供
            stat = os.stat(full_path)
            item_info["modified_time"] = datetime.datetime.fromtimestamp(stat.st_mtime).strftime("%Y-%m-%d %H:%M:%S")

        items.append(item_info)

    return json.dumps({"items": items, "count": len(items)}, ensure_ascii=False)


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
                "modified_time": datetime.datetime.fromtimestamp(stat.st_mtime).strftime("%Y-%m-%d %H:%M:%S")
            })

    return json.dumps({"files": files, "count": len(files)}, ensure_ascii=False)