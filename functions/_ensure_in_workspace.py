import os
import json
from typing import Optional

def _ensure_in_workspace(*paths: str) -> Optional[str]:
    """
    校验所有给定路径是否都在当前工作目录下。
    如果全部合规，返回 None；否则返回错误 JSON 字符串。
    """
    workspace = os.getcwd()
    for p in paths:
        # 获取规范化的绝对路径
        abs_path = os.path.abspath(p)
        # 检查是否以工作目录为前缀（允许完全相等）
        if not abs_path.startswith(workspace + os.sep) and abs_path != workspace:
            return json.dumps({
                "success": False,
                "error": f"操作越界：路径 {p} 不在当前工作目录 {workspace} 下"
            }, ensure_ascii=False)
    return None