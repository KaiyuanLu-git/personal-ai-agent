from openai import OpenAI
import os
from dotenv import load_dotenv
import datetime
import json
import requests
from my_rag import knowledge_search


def get_current_time():
    return datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

def calculator(expression):
    expression = str(expression)
    try:
        allowed_chars = set("0123456789+-*/(). ")
        if not all(c in allowed_chars for c in expression):
            return 'error: charactor not allowed'
        else:
            return str(eval(expression))
    except Exception as e:
        return f"error: {e}"

def web_search(query):
    tvly_api_key = os.getenv("TAVILY_API_KEY")
    url = "https://api.tavily.com/search"
    json = {"api_key": tvly_api_key, "query": query}
    headers={"Content-Type": "application/json"}
    response = requests.post(url, json=json, headers=headers)
    res_dict = response.json()
    res = '查询' + query + "的结果包括： "
    for result in res_dict['results']:
        res += ("来自" + result['title'] + "的描述是： " + clean_content(result["content"][:100]) + ";")
    return res

def clean_content(text):
    lines = text.split("\n")
    seen = set()
    cleaned_lines = []
    for line in lines:
        line = line.strip()
        if len(line) < 5:          
            continue
        if line in seen:            
            continue
        seen.add(line)
        cleaned_lines.append(line)
    return "\n".join(cleaned_lines)

def one_shot(messages):
    load_dotenv()
    max_iter = 10

    client = OpenAI(
        api_key=os.getenv("DEEPSEEK_API_KEY"),
        base_url="https://api.deepseek.com"
    )


    response = client.chat.completions.create(
        model="deepseek-chat",
        messages=messages,
        tools=tools,
    )

    i = 0
    finish_flag = 0
    while(i < max_iter):
        message = response.choices[0].message
        print(message)
        if not message.tool_calls:
            finish_flag = 1
            break
        messages.append(message)
        for tool_call in message.tool_calls:

            id = tool_call.id
            func_name = tool_call.function.name
            func_arg_json = tool_call.function.arguments
            func_arg = json.loads(func_arg_json)

            print(func_arg)



            func_to_call = available_functions[func_name]
            result = func_to_call(**func_arg)



            tool_result = {
                "role": "tool",
                "tool_call_id": id,
                "content": str(result)
            }
            messages.append(tool_result)

        response = client.chat.completions.create(
            model="deepseek-chat",
            messages=messages,
            tools=tools,
        )
        i += 1

    if finish_flag == 0:
        print("查询超时")
        print()
    else:
        print(response.choices[0].message.content)
    res = response.choices[0].message.content
    return res

def main():
    messages = []
    while True:
        user_input = input()
        if user_input in ['quit', "exit", "退出"]:
            break
        messages.append({"role":"user", "content": user_input})
        message = one_shot(messages)
        messages.append({"role":"assistant", "content": message})


tools = [
    {
        "type": "function",
        "function": {
            "name": "get_current_time",
            "description": "获取当前时间",
            "parameters": {
                "type": "object",
                "properties": {},
                "required": []
            }
        }
    },
    {
            "type": "function",
            "function": {
                "name": "calculator",
                "description": "计算表达式的值",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "expression": {
                            "type": "string",
                            "description": "所查询表达式的string"
                        }
                    },
                    "required": ["expression"]
                }
            }
        },
        {
                    "type": "function",
                    "function": {
                        "name": "web_search",
                        "description": "用tavily网页搜索特定内容",
                        "parameters": {
                            "type": "object",
                            "properties": {
                                "query": {
                                    "type": "string",
                                    "description": "所查询关键内容的string"
                                }
                            },
                            "required": ["query"]
                        }
                    }
                },
                    {
            "type": "function",
            "function": {
                "name": "knowledge_search",
                "description": "在本地知识库搜索结果，可查询kaiyuan的个人资料",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "expression": {
                            "type": "string",
                            "description": "所查询关键内容的string"
                        }
                    },
                    "required": ["query"]
                }
            }
        },
]

available_functions = {
    "get_current_time": get_current_time,
    "calculator": calculator,
    "web_search": web_search,
    "knowledge_search": knowledge_search,
}

if __name__ == "__main__":
    main()