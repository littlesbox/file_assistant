import sys
import nest_asyncio
import asyncio

from llm import llm_factory
from tools import all_file_tools

from langchain.agents import create_agent
from langgraph.checkpoint.memory import InMemorySaver

from langchain_core.messages import (
    AIMessage,
    ToolMessage,
)

from rich.console import Console
from rich.panel import Panel
from rich.markdown import Markdown
from rich.live import Live

from prompt_toolkit import prompt

# 解决事件循环嵌套冲突
nest_asyncio.apply()

console = Console()
memory = InMemorySaver()

SYSTEM_PROMPT = """
**你是一个文件管理助手，你能辅助人类进行文件管理，有如下工具供你使用**。

---
- `get_current_directory_tool` 查看当前的工作目录
- `list_directory_tool` 列出指定目录下的所有项目（不进行递归，支持文件名和扩展名过滤）
- `list_directory_recursive_tool` 列出指定目录下的所有项目（进行递归，支持文件名和扩展名过滤）
- `copy_file_tool` 复制文件
- `move_file_tool` 移动文件
- `rename_file_tool` 重命名文件
- `create_directory_tool` 创建文件夹
- `delete_file_tool` 删除文件
- `delete_directory_tool` 删除文件夹，递归删除文件夹下的所有文件夹和文件
- `get_current_time_tool` 获取当前系统时间
---

当你收到指令时，应该进行充分思考和规划。

当用户让你列出文件夹内容时：

1. 明确指定哪个文件夹
2. 询问是否递归
3. 明确后再调用工具

无论什么时候收到指令：

1. 先明确当前工作目录
2. 再明确目录结构
3. 然后再采取行动
"""

llm = llm_factory("qwen")
agent = create_agent(
    model=llm,
    system_prompt=SYSTEM_PROMPT,
    tools=all_file_tools,
    checkpointer=memory
)


def print_message(msg):
    """一次性打印工具调用或工具结果"""
    if isinstance(msg, AIMessage) and msg.tool_calls:
        for call in msg.tool_calls:
            console.print(
                Panel(
                    f"[bold]Tool:[/bold] {call['name']}\n\n"
                    f"[bold]Args:[/bold]\n{call['args']}",
                    title="🔧 Tool Call",
                    border_style="yellow",
                )
            )
    elif isinstance(msg, ToolMessage):
        console.print(
            Panel(
                str(msg.content),
                title=f"✅ Tool Result ({msg.name})",
                border_style="green",
            )
        )


async def process_one_message(user_input: str):
    """
    处理单条用户输入。
    工具调用/结果用原有面板输出；最终AI文字回复用 Live 面板动态刷新。
    """
    streaming_live = None
    accumulated_text = ""

    async for event in agent.astream_events(
        {"messages": [{"role": "user", "content": user_input}]},
        config={"configurable": {"thread_id": "1"}},
        version="v2",
    ):
        kind = event["event"]

        # ---------- 流式 token ----------
        if kind == "on_chat_model_stream":
            content = event["data"]["chunk"].content
            if content:
                if streaming_live is None:
                    streaming_live = Live(
                        Panel("", title="🤖 Assistant", border_style="cyan"),
                        console=console,
                        refresh_per_second=10,
                        transient=False
                    )
                    streaming_live.start()
                accumulated_text += content
                streaming_live.update(
                    Panel(Markdown(accumulated_text), title="🤖 Assistant", border_style="cyan")
                )

        # ---------- 模型生成结束 ----------
        elif kind == "on_chat_model_end":
            # 显示工具调用（如果有）
            output = event["data"]["output"]
            if isinstance(output, AIMessage) and output.tool_calls:
                print_message(output)

            # 结束流式面板（如果有）
            if streaming_live is not None:
                streaming_live.update(
                    Panel(Markdown(accumulated_text), title="🤖 Assistant", border_style="cyan")
                )
                streaming_live.stop()
                streaming_live = None
                accumulated_text = ""

        # ---------- 工具结果 ----------
        elif kind == "on_tool_end":
            output = event["data"]["output"]
            if isinstance(output, ToolMessage):
                print_message(output)
            # 可能还有一些情况 output 是带有 tool_calls 的 AIMessage？但通常已在 on_chat_model_end 中处理，忽略

    # 安全关闭
    if streaming_live is not None:
        streaming_live.stop()


def run_conversation():
    console.print("[bold green]输入 exit 结束对话[/bold green]\n")

    while True:
        user_input = prompt("用户：").strip()
        if user_input.lower() in ("exit", "quit"):
            break
        if not user_input:
            continue

        console.print(
            Panel(
                user_input,
                title="👤 User",
                border_style="blue",
            )
        )

        try:
            asyncio.run(process_one_message(user_input))
        except Exception as e:
            console.print(
                Panel(str(e), title="❌ Error", border_style="red")
            )


if __name__ == "__main__":
    run_conversation()