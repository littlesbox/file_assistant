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
from prompt_toolkit import prompt

console = Console()

memory = InMemorySaver()

SYSTEM_PROMPT = '''**你是一个文件管理助手，你能辅助人类进行文件管理，有如下工具供你使用**。
---
- `get_current_directory_tool` 查看当前的工作目录
- `list_directory_tool` 列出指定目录下的所有项目（**不进行递归，支持文件名和扩展名过滤**）
- `list_directory_recursive_tool` 列出指定目录下的所有项目（**进行递归，支持文件名和扩展名过滤**）
- `copy_file_tool` 复制文件
- `move_file_tool` 移动文件
- `rename_file_tool` 重命名文件
- `create_directory_tool` 创建文件夹
- `delete_file_tool` 删除文件
- `delete_directory_tool` 删除文件夹，递归删除文件夹下的所有文件夹和文件
- `get_current_time_tool` 用于获取当前的系统时间
---
**你可以根据需要使用上面的工具。**
---
当你收到指令时，应该进行充分的思考和规划，当你觉得指令模糊的时候应该及时与使用者进行沟通，而不是擅自行动。
当你觉得只使用一次工具调用无法完成工作指令的时候应该合理地进行规划，在充分思考之后再调用工具，尽量避免不必要的重复操作。
当用户让你列出文件夹的内容你应该明确指定的文件夹；然后询问用户是否要进行递归列出文件夹中的所有内容，明确之后再调用工具。
无论什么时候收到指令，都应该先明确当前的工作目录，和目录下的文件分布情况，然后再采取行动。
'''

llm = llm_factory('qwen')

agent = create_agent(
    model=llm,
    system_prompt=SYSTEM_PROMPT,
    tools=all_file_tools,
    checkpointer=memory
)

def run_conversation():
    print("输入 exit 结束对话：")

    seen = set()
    while True:
        # print("\n")
        user_input = prompt("用户：")

        if user_input.lower() in ("exit", "quit"):
            break

        if not user_input:
            continue

        console.print(
            Panel(
                user_input,
                title="👤 User",
                border_style="blue"
            )
        )

        
        for chunk in agent.stream(
            {
                "messages": [
                    {
                        "role": "user",
                        "content": user_input
                    }
                ]
            },
            config={
                "configurable": {
                    "thread_id": "1"
                }
            },
            stream_mode="values"
        ):

            for msg in chunk["messages"]:
                if msg.id in seen:
                    continue

                seen.add(msg.id)
                # -------------------------
                # AI 调用工具
                # -------------------------
                if (
                    isinstance(msg, AIMessage)
                    and msg.tool_calls
                ):
                    for call in msg.tool_calls:

                        console.print(
                            Panel(
                                f"[bold]Tool:[/bold] {call['name']}\n\n"
                                f"[bold]Args:[/bold]\n{call['args']}",
                                title="🔧 Tool Call",
                                border_style="yellow"
                            )
                        )

                # -------------------------
                # 工具返回结果
                # -------------------------
                elif isinstance(msg, ToolMessage):

                    console.print(
                        Panel(
                            str(msg.content),
                            title=f"✅ Tool Result ({msg.name})",
                            border_style="green"
                        )
                    )

                # -------------------------
                # AI 最终回复
                # -------------------------
                elif (
                    isinstance(msg, AIMessage)
                    and not msg.tool_calls
                    and msg.content
                ):

                    console.print(
                        Panel(
                            Markdown(msg.content),
                            title="🤖 Assistant",
                            border_style="cyan"
                        )
                    )

if __name__ == "__main__":
    run_conversation()