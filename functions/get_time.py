import json

def get_current_time() -> str:
    """获取当前系统日期和时间，返回 ISO 格式字符串。"""
    from datetime import datetime
    return json.dumps({"current_time": datetime.now().isoformat()}, ensure_ascii=False)