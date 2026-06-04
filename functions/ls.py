import os
import json
# import shutil
from typing import Optional
import datetime
from ._ensure_in_workspace import _ensure_in_workspace


# def list_current_directory_files(extension: str = None, name_contains: str = None) -> str:
#     """
#     列出当前工作目录下的所有文件（不包含子文件夹），
#     可按扩展名或文件名关键字过滤。
#     参数：
#         extension: 如 ".pdf", ".xlsx"，可选
#         name_contains: 文件名包含的字符串，可选
#     返回 JSON 字符串，包含文件列表和数量。
#     """
#     path = os.getcwd()
#     files = []
#     for f in os.listdir(path):
#         full_path = os.path.join(path, f)
#         if not os.path.isfile(full_path):
#             continue
#         # 过滤扩展名
#         if extension and not f.lower().endswith(extension.lower()):
#             continue
#         # 过滤文件名包含字符串
#         if name_contains and name_contains.lower() not in f.lower():
#             continue
#         stat = os.stat(full_path)
#         files.append({
#             "name": f,
#             "path": full_path,
#             "extension": os.path.splitext(f)[1].lower(),
#             "size_bytes": stat.st_size,
#             "modified_time": datetime.datetime.fromtimestamp(stat.st_mtime).strftime("%Y-%m-%d %H:%M:%S")  # 时间戳，方便LLM处理
#         })
#     return json.dumps({"files": files, "count": len(files)}, ensure_ascii=False)









# def list_files(path: Optional[str] = None,
#                extension: Optional[str] = None,
#                name_contains: Optional[str] = None) -> str:
#     """
#     列出指定目录下的所有文件（不包含子文件夹）。
#     参数：
#         path: 目录路径，默认为当前工作目录
#         extension: 过滤扩展名，如 ".pdf", ".xlsx"，可选
#         name_contains: 文件名包含的字符串，可选
#     返回 JSON 字符串，包含文件列表和数量。
#     """
#     if path is None:
#         path = os.getcwd()
#     else:
#         path = os.path.abspath(path)

#     # 校验：目录路径必须在工作目录下
#     error = _ensure_in_workspace(path)
#     if error:
#         return error

#     if not os.path.isdir(path):
#         return json.dumps({"error": f"目录不存在: {path}"}, ensure_ascii=False)

#     files = []
#     for f in os.listdir(path):
#         full_path = os.path.join(path, f)
#         if not os.path.isfile(full_path):
#             continue          # 跳过子目录，只保留文件

#         # 过滤扩展名
#         if extension and not f.lower().endswith(extension.lower()):
#             continue
#         # 过滤文件名包含字符串
#         if name_contains and name_contains.lower() not in f.lower():
#             continue

#         stat = os.stat(full_path)
#         files.append({
#             "name": f,
#             "path": full_path,
#             "extension": os.path.splitext(f)[1].lower(),
#             "size_bytes": stat.st_size,
#             "modified_time": datetime.datetime.fromtimestamp(stat.st_mtime).strftime("%Y-%m-%d %H:%M:%S")
#         })

#     return json.dumps({"files": files, "count": len(files)}, ensure_ascii=False)







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
    目录项额外包含 'is_empty' 字段（true/false/null 表示未知）。
    """
    if path is None:
        path = os.getcwd()
    else:
        path = os.path.abspath(path)

    error = _ensure_in_workspace(path)
    if error:
        return error

    if not os.path.isdir(path):
        return json.dumps({"error": f"目录不存在: {path}"}, ensure_ascii=False)

    items = []
    for entry in os.listdir(path):
        full_path = os.path.join(path, entry)
        is_dir = os.path.isdir(full_path)
        is_file = os.path.isfile(full_path)

        if not (is_dir or is_file):
            continue

        if is_file and extension and not entry.lower().endswith(extension.lower()):
            continue

        if name_contains and name_contains.lower() not in entry.lower():
            continue

        item_info = {
            "name": entry,
            "path": full_path,
            "type": "directory" if is_dir else "file",
        }

        if is_file:
            stat = os.stat(full_path)
            item_info["extension"] = os.path.splitext(entry)[1].lower()
            item_info["size_bytes"] = stat.st_size
            item_info["modified_time"] = datetime.datetime.fromtimestamp(stat.st_mtime).strftime("%Y-%m-%d %H:%M:%S")
        else:
            stat = os.stat(full_path)
            item_info["modified_time"] = datetime.datetime.fromtimestamp(stat.st_mtime).strftime("%Y-%m-%d %H:%M:%S")
            # 新增：标注文件夹是否为空
            try:
                item_info["is_empty"] = len(os.listdir(full_path)) == 0
            except Exception:
                item_info["is_empty"] = None   # 无法判断时用 null

        items.append(item_info)

    return json.dumps({"items": items, "count": len(items)}, ensure_ascii=False)







def list_directory_recursive(path: Optional[str] = None,
                             extension: Optional[str] = None,
                             name_contains: Optional[str] = None) -> str:
    """
    递归列出指定目录下的所有项目（包括子文件夹中的文件和文件夹）。
    参数：
        path: 目录路径，默认为当前工作目录
        extension: 过滤扩展名（仅对文件有效），如 ".pdf"，可选
        name_contains: 名称中包含的字符串（对文件和文件夹均有效），可选
    返回 JSON 字符串，包含项目列表和总数。
    目录项额外包含 'is_empty' 字段（true/false/null 表示未知）。
    """
    if path is None:
        path = os.getcwd()
    else:
        path = os.path.abspath(path)

    error = _ensure_in_workspace(path)
    if error:
        return error

    if not os.path.isdir(path):
        return json.dumps({"error": f"目录不存在: {path}"}, ensure_ascii=False)

    items = []

    def walk(current_dir: str):
        """递归遍历目录"""
        try:
            entries = os.listdir(current_dir)
        except PermissionError:
            # 无法读取目录内容，跳过该目录
            return
        except Exception:
            return

        for entry in entries:
            full_path = os.path.join(current_dir, entry)
            is_dir = os.path.isdir(full_path)
            is_file = os.path.isfile(full_path)

            if not (is_dir or is_file):
                continue

            # 提前判断目录是否为空（在过滤前，因为“空”是指物理上无内容）
            is_empty = None
            if is_dir:
                try:
                    contents = os.listdir(full_path)
                    is_empty = len(contents) == 0
                except Exception:
                    is_empty = None  # 无法判断

            # 过滤逻辑：先判断当前条目本身是否需要被加入结果
            include_this = True

            # 文件扩展名过滤（只对文件生效）
            if is_file and extension and not entry.lower().endswith(extension.lower()):
                include_this = False

            # 名称包含过滤（对文件和目录都生效）
            if name_contains and name_contains.lower() not in entry.lower():
                include_this = False

            # 如果该条目符合条件，构建信息并加入结果
            if include_this:
                item_info = {
                    "name": entry,
                    "path": full_path,
                    "type": "directory" if is_dir else "file",
                }
                if is_file:
                    stat = os.stat(full_path)
                    item_info["extension"] = os.path.splitext(entry)[1].lower()
                    item_info["size_bytes"] = stat.st_size
                    item_info["modified_time"] = datetime.datetime.fromtimestamp(stat.st_mtime).strftime("%Y-%m-%d %H:%M:%S")
                else:
                    stat = os.stat(full_path)
                    item_info["modified_time"] = datetime.datetime.fromtimestamp(stat.st_mtime).strftime("%Y-%m-%d %H:%M:%S")
                    item_info["is_empty"] = is_empty

                items.append(item_info)

            # 如果是目录，无论它本身是否被过滤，都要递归进入，以确保内部匹配的文件/目录被发现
            if is_dir:
                walk(full_path)

    walk(path)
    return json.dumps({"items": items, "count": len(items)}, ensure_ascii=False)








# def list_files_recursive(path: Optional[str] = None,
#                          extension: Optional[str] = None,
#                          name_contains: Optional[str] = None) -> str:
#     """
#     递归列出指定目录下的所有文件（包含所有子目录中的文件）。
#     参数：
#         path: 目录路径，默认为当前工作目录
#         extension: 过滤扩展名，如 ".pdf", ".xlsx"，可选
#         name_contains: 文件名包含的字符串，可选
#     返回 JSON 字符串，包含文件列表和数量。
#     """
#     if path is None:
#         path = os.getcwd()
#     else:
#         path = os.path.abspath(path)

#     # 校验：目录路径必须在工作目录下
#     error = _ensure_in_workspace(path)
#     if error:
#         return error

#     if not os.path.isdir(path):
#         return json.dumps({"error": f"目录不存在: {path}"}, ensure_ascii=False)

#     files = []
#     for dirpath, dirnames, filenames in os.walk(path):
#         for f in filenames:
#             # 过滤扩展名
#             if extension and not f.lower().endswith(extension.lower()):
#                 continue
#             # 过滤文件名包含字符串
#             if name_contains and name_contains.lower() not in f.lower():
#                 continue

#             full_path = os.path.join(dirpath, f)
#             stat = os.stat(full_path)
#             files.append({
#                 "name": f,
#                 "path": full_path,
#                 "extension": os.path.splitext(f)[1].lower(),
#                 "size_bytes": stat.st_size,
#                 "modified_time": datetime.datetime.fromtimestamp(stat.st_mtime).strftime("%Y-%m-%d %H:%M:%S")
#             })

#     return json.dumps({"files": files, "count": len(files)}, ensure_ascii=False)