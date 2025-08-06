
import httpx
from mcp.server.fastmcp import FastMCP
import os
import uuid
import json
from typing import Optional
from loguru import logger
mcp = FastMCP("Weibots")



# Static resource
@mcp.resource("config://version")
def get_version(): 
    return "0.0.1"

@mcp.tool()
async def weiBots_kb_query(
    query: str,
    isWebSearch: Optional[bool] = False,
    isDeepSearch: Optional[bool] = False,
    isReplyOrigin: Optional[bool] = False
):
    """
    根据用户提出的问题，智能检索知识库内容，并生成精准的答案进行回复。

    参数
    ----------
    query : str
        ⽤⼾问题，String类型，必填
    isWebSearch : bool, optional
        是否开启互联⽹检索，Boolean类型，默认false，⾮必填
    isDeepSearch : bool, optional
        是否开启深度检索，Boolean类型，默认false，⾮必填
    isReplyOrigin : bool, optional
        是否原⽂回答，Boolean类型，默认false，⾮必填

    返回
    -------
    回答内容
    """

    weibots_domain = os.getenv("WEIBOTS_DOMAIN")
    weibots_api_key = os.getenv("WEIBOTS_API_KEY")
    weibots_app_id = os.getenv("WEIBOTS_APP_ID")

    # 环境变量检查
    if weibots_domain is None or weibots_domain == "":
        yield json.dumps({"error": "环境变量缺失，请在MCP环境变量中指定WEIBOTS_DOMAIN"},ensure_ascii=False)
        return
    
    if weibots_api_key is None or weibots_api_key == "":
        yield json.dumps({"error": "环境变量缺失，请在MCP环境变量中指定WEIBOTS_API_KEY"},ensure_ascii=False)
        return

    if weibots_app_id is None or weibots_app_id == "":
        yield json.dumps({"error": "环境变量缺失，请在MCP环境变量中指定WEIBOTS_APP_ID"},ensure_ascii=False)
        return


    # 参数检查
    if query is None:
        yield json.dumps({"error": "参数缺失，请在接口参数中指定query"},ensure_ascii=False)
        return

    elif query == "":
        yield json.dumps({"error": "参数缺失，query不能为空"},ensure_ascii=False)
        return
    
    # 联网检索开启时需要同时开启深度检索
    if isWebSearch:
        isDeepSearch = True

    # 请求构造
    url = f"{weibots_domain}/api/v1/chat/completions"
    
    stream = True
    data = {
        "title": "MCP",
        "stream": stream,
        "isTvily": isWebSearch,
        "isDeepSearch": isDeepSearch,
        "appId": weibots_app_id,
        "replyOrigin": 1 if isReplyOrigin else 0,
        "isSaveHistory": False,  
        "messages": [
            {
            "role": "user",
            "content": query
            }
        ]
    }
    headers = {
        "Authorization": f"Bearer {weibots_api_key}"
    }

    # 异步迭代调用weibots api
    async with httpx.AsyncClient(timeout=None) as client:
        async with client.stream("POST",url, json=data, headers=headers) as resp:
            resp.raise_for_status()
            async for raw_line in resp.aiter_lines():
                yield raw_line

    # try:
        
    # except Exception as e:
    #     yield json.dumps({"error": str(e)},ensure_ascii=False)



def main():
    '''
    Streamable HTTP is a modern, efficient transport for exposing your MCP server via HTTP. It is the recommended transport for web-based deployments.
    fastmcp==2.3.0
    '''
    # 指定使用 SSE 传输模式
    mcp.run(transport="http")

if __name__ == "__main__":
   import asyncio   
   import os
   
   host = os.getenv("WEIBOTS_DOMAIN")

   # 测试
   async def test_weiBots_kb_query():
        os.environ["WEIBOTS_API_KEY"] = "hwllm-mRB3qF62qeP4GomZn0dwO56OnYRDWUtEw5SyeVb6gJ4"
        os.environ["WEIBOTS_APP_ID"] = "594757926678167552"
        os.environ["WEIBOTS_DOMAIN"] = "http://192.168.3.23:7090"
        # query = "今天有哪些新闻"
        # isWebSearch = True
        # isDeepSearch = False
        # isReplyOrigin = False
        # async for reply in weiBots_kb_query(query,isWebSearch,isDeepSearch,isReplyOrigin):
        #     print(reply)

        # query = "李静是谁"
        # isWebSearch = False
        # isDeepSearch = True
        # isReplyOrigin = False
        # async for reply in weiBots_kb_query(query,isWebSearch,isDeepSearch,isReplyOrigin):
        #     print(reply)

        # query = "李静是谁"
        # isWebSearch = False
        # isDeepSearch = False
        # isReplyOrigin = False
        # async for reply in weiBots_kb_query(query,isWebSearch,isDeepSearch,isReplyOrigin):
        #     print(reply)
        
        query = "李静是谁"
        isWebSearch = False
        isDeepSearch = False
        isReplyOrigin = True
        async for reply in weiBots_kb_query(query,isWebSearch,isDeepSearch,isReplyOrigin):
            print(reply)

   
   ret = asyncio.run(test_weiBots_kb_query())
   print(ret)