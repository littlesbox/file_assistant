import os
import json
from _ensure_in_workspace import _ensure_in_workspace


def rename_file(path: str, new_name: str) -> str:
    """
    重命名文件，仅允许修改文件名，不允许跨目录移动。
    参数：
        path: 文件当前绝对路径
        new_name: 新文件名（含扩展名），不能包含路径分隔符
    返回 JSON 字符串，包含操作结果。
    """

    # 校验：源文件路径必须在工作目录下
    error = _ensure_in_workspace(path)
    if error:
        return error

    # 检查源文件是否存在
    if not os.path.isfile(path):
        return json.dumps({"success": False, "error": f"文件不存在: {path}"}, ensure_ascii=False)

    # 新文件名不能是空字符串
    if not new_name:
        return json.dumps({"success": False, "error": "新文件名不能为空"}, ensure_ascii=False)

    # 新文件名中禁止包含路径分隔符，确保不会跨目录
    if os.sep in new_name or os.altsep and os.altsep in new_name:
        return json.dumps({"success": False, "error": "新文件名不能包含路径分隔符，仅允许修改文件名本身"}, ensure_ascii=False)

    # 构造新路径（保持原目录）
    dir_name = os.path.dirname(path)
    new_path = os.path.join(dir_name, new_name)

    # 校验：新路径也在工作目录下（双重保险）
    error = _ensure_in_workspace(new_path)
    if error:
        return error

    # 检查新路径是否已存在
    if os.path.exists(new_path):
        return json.dumps({"success": False, "error": f"目标文件名已存在: {new_path}"}, ensure_ascii=False)

    try:
        os.rename(path, new_path)
        return json.dumps({"success": True, "old_name": os.path.basename(path), "new_name": new_name, "path": new_path}, ensure_ascii=False)
    except Exception as e:
        return json.dumps({"success": False, "error": str(e)}, ensure_ascii=False)



def create_directory(path: str) -> str:
    """
    创建目录，支持递归创建（类似 mkdir -p）。
    参数：
        path: 目录绝对路径
    返回 JSON 字符串，包含操作结果。
    """

     # 校验：目标路径必须在工作目录下
    error = _ensure_in_workspace(path)
    if error:
        return error

    # 如果路径已存在且是目录，视为成功
    if os.path.isdir(path):
        return json.dumps({"success": True, "path": path, "note": "目录已存在"}, ensure_ascii=False)

    # 如果路径已存在但是文件，报错
    if os.path.isfile(path):
        return json.dumps({"success": False, "error": f"路径已存在，但它是文件而非目录: {path}"}, ensure_ascii=False)

    try:
        os.makedirs(path, exist_ok=True)
        return json.dumps({"success": True, "path": path}, ensure_ascii=False)
    except Exception as e:
        return json.dumps({"success": False, "error": str(e)}, ensure_ascii=False)