# file_tools.py 中追加
import os
import json
import shutil
from ._ensure_in_workspace import _ensure_in_workspace

def delete_file(path: str) -> str:
    """
    删除文件。
    优先尝试移入系统回收站/废纸篓（需要安装 send2trash 库），
    如果不可用则永久删除，并在返回值中警告。
    参数：
        path: 文件绝对路径（不能是目录）
    返回 JSON 字符串。
    """

    # 校验：源文件路径必须在工作目录下
    error = _ensure_in_workspace(path)
    if error:
        return error

    if not os.path.exists(path):
        return json.dumps({"success": False, "error": f"文件不存在: {path}"}, ensure_ascii=False)

    if os.path.isdir(path):
        return json.dumps({"success": False, "error": f"路径是目录，不允许删除目录: {path}"}, ensure_ascii=False)

    # 尝试使用 send2trash（跨平台回收站）
    try:
        import send2trash
        send2trash.send2trash(path)
        return json.dumps({"success": True, "method": "trash", "path": path}, ensure_ascii=False)
    except ImportError:
        # 如果没有安装 send2trash，回退到永久删除
        try:
            os.remove(path)
            return json.dumps({
                "success": True,
                "method": "permanent_delete",
                "path": path,
                "warning": "send2trash 未安装，文件已永久删除。建议 pip install send2trash 启用回收站功能。"
            }, ensure_ascii=False)
        except Exception as e:
            return json.dumps({"success": False, "error": str(e)}, ensure_ascii=False)
    except Exception as e:
        # send2trash 存在但调用失败，也尝试永久删除
        try:
            os.remove(path)
            return json.dumps({
                "success": True,
                "method": "permanent_delete",
                "path": path,
                "warning": f"移入回收站失败（{e}），文件已永久删除。"
            }, ensure_ascii=False)
        except Exception as e2:
            return json.dumps({"success": False, "error": str(e2)}, ensure_ascii=False)
        

def delete_directory(path: str) -> str:
    """
    递归删除整个文件夹（包含其中所有文件和子文件夹）。
    优先尝试移入系统回收站/废纸篓（需要安装 send2trash 库），
    如果不可用则永久删除，并在返回值中警告。
    参数：
        path: 文件夹绝对路径（必须是目录）
    返回 JSON 字符串。
    """
    # 校验：源文件路径必须在工作目录下
    error = _ensure_in_workspace(path)
    if error:
        return error

    if not os.path.exists(path):
        return json.dumps({"success": False, "error": f"路径不存在: {path}"}, ensure_ascii=False)

    if not os.path.isdir(path):
        return json.dumps({"success": False, "error": f"路径不是目录: {path}。请使用 delete_file 删除文件。"}, ensure_ascii=False)

    # 尝试使用 send2trash（跨平台回收站）
    try:
        import send2trash
        send2trash.send2trash(path)
        return json.dumps({"success": True, "method": "trash", "path": path}, ensure_ascii=False)
    except ImportError:
        # 没有 send2trash，回退到永久删除
        try:
            shutil.rmtree(path)
            return json.dumps({
                "success": True,
                "method": "permanent_delete",
                "path": path,
                "warning": "send2trash 未安装，文件夹已永久删除。建议 pip install send2trash 启用回收站功能。"
            }, ensure_ascii=False)
        except Exception as e:
            return json.dumps({"success": False, "error": str(e)}, ensure_ascii=False)
    except Exception as e:
        # send2trash 存在但调用失败，回退到永久删除
        try:
            shutil.rmtree(path)
            return json.dumps({
                "success": True,
                "method": "permanent_delete",
                "path": path,
                "warning": f"移入回收站失败（{e}），文件夹已永久删除。"
            }, ensure_ascii=False)
        except Exception as e2:
            return json.dumps({"success": False, "error": str(e2)}, ensure_ascii=False)