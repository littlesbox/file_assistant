from llm import llm_factory
from tools import all_file_tools
from langchain.agents import create_agent
from langgraph.checkpoint.memory import InMemorySaver

memory = InMemorySaver()

SYSTEM_PROMPT = '''**你是一个文件管理助手，你能辅助人类进行文件管理，有如下工具供你使用**。
---
- `get_current_directory_tool` 查看当前的工作目录
- `list_current_directory_files_tool` 列出当前工作目录下的文件（不进行递归，不包含子文件夹，支持文件名和扩展名过滤）
- `list_files_tool` 列出指定目录下的文件（不进行递归，不包含子文件夹，支持文件名和扩展名过滤）
- `list_directory_tool` 列出指定目录下的所有项目（不进行递归，支持文件名和扩展名过滤）
- `list_files_recursive_tool` 列出指定目录下的文件和文件夹（进行递归，支持文件名和扩展名过滤）
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
    while(True):
        user_input = input("用户：").strip()
        if user_input.lower() in ("exit", "quit"):
            break
        if not user_input:
            continue
        result  = agent.invoke(
        {"messages":[{"role":"user", "content":user_input}]},
        config={
            "configurable": {
                "thread_id": "1"
            }
        }
        )
        for msg in result["messages"]:
            print(type(msg).__name__)
            print(msg.content)
            print("=" * 50)

if __name__ == "__main__":
    run_conversation()