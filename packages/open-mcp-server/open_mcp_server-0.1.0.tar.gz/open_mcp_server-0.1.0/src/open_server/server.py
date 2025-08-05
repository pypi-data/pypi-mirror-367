import requests
from typing import  Optional
from requests.exceptions import RequestException, Timeout, ConnectionError
from fastmcp import FastMCP
import json
import sys
import os

# 添加当前目录到Python路径中，确保可以导入同目录下的模块
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# 导入本地模块
try:
    import open_platform_interface
except ImportError as e:
    print(f"导入open_platform_interface模块失败: {e}")
    print("请确保open_platform_interface.py文件与server.py在同一目录下")
    raise

# 初始化FastMCP服务器
mcp = FastMCP("mcptool")

@mcp.tool()
async def get_org_subject_info(subject: str) -> dict:
    """
    获取机构主体信息
    """
    try:
        result = open_platform_interface.get_org_subject_info(subject)
        # 检查result是否已经是字典，如果不是才进行json.loads
        if isinstance(result, str):
            return json.loads(result)
        return result
    except Exception as e:
        return {"error": f"获取机构主体信息失败: {str(e)}"}

@mcp.tool()
async def query_ant_block_info(safe_id: str) -> dict:
    """
    区块链存证结果查询
    """
    try:
        result = open_platform_interface.query_ant_block_info(safe_id)
        # 检查result是否已经是字典，如果不是才进行json.loads
        if isinstance(result, str):
            return json.loads(result)
        return result
    except Exception as e:
        return {"error": f"查询区块链存证结果失败: {str(e)}"}

def main():
    #mcp.run(transport='streamable-http', port=8098, path='/mcp')
    mcp.run(transport='stdio', port=8098, path='/mcp')

# 直接运行时的示例用法
if __name__ == "__main__":
    main()