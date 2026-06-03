import os
import dotenv
dotenv.load_dotenv()

def qwen_llm():
    from langchain_qwq import ChatQwen
    #qwen
    qwen = ChatQwen(
        model="qwen-max",
        api_key=os.getenv("DASHSCOPE_API_KEY"),
        base_url="https://dashscope.aliyuncs.com/compatible-mode/v1",
        temperature=0.7
    )
    return qwen

def deepseek_llm():
    #deepseek
    from langchain_openai import ChatOpenAI
    DEEPSEEK_API_KEY = os.getenv("DEEPSEEK_API_KEY")

    deepseek_chat = ChatOpenAI(
                        base_url="https://api.deepseek.com",
                        api_key=DEEPSEEK_API_KEY,
                        model="deepseek-chat",
                        temperature=0,
                        timeout=30,
                        max_retries=3
                    )

    return deepseek_chat

def gemini_llm():
    #google gemini
    from langchain_google_genai import ChatGoogleGenerativeAI
    GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
    gemini = ChatGoogleGenerativeAI(
        api_key=GEMINI_API_KEY,
        model="gemini-3-flash-preview",
        temperature=0,  # Gemini 3.0+ defaults to 1.0
        max_tokens=None,
        timeout=None,
        max_retries=2,
        # other params...
    )
    return gemini


def zhipu_llm():
    #zhipu
    from langchain_community.chat_models import ChatZhipuAI
    ZHIPU_API_KEY = os.getenv("ZHIPU_API_KEY")
    zhipu_glm47 = ChatZhipuAI(
        model="glm-4.7",
        temperature=0,
        api_key=ZHIPU_API_KEY,
    )
    return zhipu_glm47



llm_map = {
    'zhipu':zhipu_llm,
    'gemini':gemini_llm,
    'deepseek':deepseek_llm,
    'qwen':qwen_llm
}


def llm_factory(name: str):
    llm_func = llm_map.get(name)
    if llm_func:
        llm = llm_func()
        return llm

if __name__ == '__main__':
    llm = llm_factory('qwen')
    response = llm.invoke("你是谁")
    print(response.content)