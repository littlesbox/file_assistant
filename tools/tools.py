# tools.py
"""
将 pwd_list_cp_mv 等模块中的函数封装为 LangChain 工具。
新增工具时，按同样模式添加即可。
"""
from typing import Optional
from langchain_core.tools import tool
from functions import (
    get_current_directory,
    list_current_directory_files,
    list_files_recursive,
    list_files,
    copy_file,
    move_file,
    rename_file,
    create_directory,
    get_current_time,
    delete_file,
    delete_directory,
)

# ------------------------ 工具封装 ------------------------
@tool
def get_current_directory_tool() -> str:
    """
    获取当前工作目录的绝对路径，返回 JSON 格式字符串。
    示例输出：{"current_directory": "/home/user/projects"}
    """
    return get_current_directory()

@tool
def list_current_directory_files_tool(
    extension: Optional[str] = None,
    name_contains: Optional[str] = None
) -> str:
    """
    列出当前工作目录下的所有文件（不包含子文件夹），可按扩展名或文件名关键字过滤。
    参数:
        extension: 文件扩展名，如 ".pdf", ".xlsx"，可选。
        name_contains: 文件名包含的字符串，可选。
    返回 JSON 字符串，包含文件列表和数量。
    """
    return list_current_directory_files(extension=extension, name_contains=name_contains)

@tool
def list_files_recursive_tool(
    path: Optional[str] = None,
    extension: Optional[str] = None,
    name_contains: Optional[str] = None
) -> str:
    """
    递归列出指定目录下的所有文件（包含所有子目录中的文件）。
    参数:
        path: 目录路径，默认为当前工作目录。
        extension: 过滤扩展名，如 ".pdf", ".xlsx"，可选。
        name_contains: 文件名包含的字符串，可选。
    返回 JSON 字符串，包含文件列表和数量。
    """
    return list_files_recursive(path=path, extension=extension, name_contains=name_contains)


@tool
def list_files_tool(
    path: Optional[str] = None,
    extension: Optional[str] = None,
    name_contains: Optional[str] = None
) -> str:
    """
    列出指定目录下的所有文件（不包含子文件夹）。
    参数：
        path: 目录路径，默认为当前工作目录
        extension: 过滤扩展名，如 ".pdf", ".xlsx"，可选
        name_contains: 文件名包含的字符串，可选
    返回 JSON 字符串，包含文件列表和数量。
    """
    return list_files(path=path, extension=extension, name_contains=name_contains)


@tool
def copy_file_tool(source: str, destination: str) -> str:
    """
    复制文件到目标目录（保留原文件名）。
    目标目录(destination)必须是一个已存在的目录，否则操作失败；请先使用 create_directory 工具创建目录。
    参数:
        source: 源文件的完整路径。
        destination: 目标目录的完整路径（不能是文件路径）。
    返回 JSON 字符串，包含成功状态、旧路径和新路径。
    """
    return copy_file(source, destination)

@tool
def move_file_tool(source: str, destination: str) -> str:
    """
    移动文件到目标目录（保留原文件名）。
    目标目录(destination)必须是一个已存在的目录，否则操作失败；请先使用 create_directory 工具创建目录。
    参数:
        source: 源文件的完整路径。
        destination: 目标目录的完整路径（不能是文件路径）。
    返回 JSON 字符串，包含成功状态、旧路径和新路径。
    """
    return move_file(source, destination)

@tool
def rename_file_tool(path: str, new_name: str) -> str:
    """
    重命名文件，仅允许修改文件名，不允许跨目录移动。
    参数:
        path: 文件当前的绝对路径。
        new_name: 新文件名（含扩展名），不能包含路径分隔符。
    返回 JSON 字符串，包含操作结果。
    """
    return rename_file(path, new_name)

@tool
def create_directory_tool(path: str) -> str:
    """
    创建目录，支持递归创建（类似 mkdir -p）。
    参数:
        path: 目录的绝对路径。
    返回 JSON 字符串，包含操作结果。
    """
    return create_directory(path)

@tool
def delete_file_tool(path: str) -> str:
    """
    删除文件（优先移入回收站，否则永久删除）。
    参数：path（文件绝对路径，不能是目录）。
    """
    return delete_file(path)

@tool
def delete_directory_tool(path: str) -> str:
    """
    递归删除整个文件夹（包含所有子文件夹和文件）。优先移入回收站，否则永久删除。
    参数：path（文件夹绝对路径，必须是目录）。
    """
    return delete_directory(path)

@tool
def get_current_time_tool() -> str:
    """获取当前系统日期和时间，返回 ISO 格式字符串。"""
    return get_current_time()

# 所有文件操作工具列表，可直接传给 Agent
all_file_tools = [
    get_current_directory_tool,
    list_current_directory_files_tool,
    list_files_tool,
    list_files_recursive_tool,
    copy_file_tool,
    move_file_tool,
    rename_file_tool,
    create_directory_tool,
    get_current_time,
    delete_file_tool,
    delete_directory_tool,
]

# 如果未来有多个模块的工具，可以合并列表：
# from other_module import tool_a, tool_b
# all_tools = file_tools + [tool_a, tool_b]