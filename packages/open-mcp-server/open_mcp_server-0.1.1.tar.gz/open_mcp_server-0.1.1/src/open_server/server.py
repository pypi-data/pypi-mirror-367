from fastmcp import FastMCP
import json
import sys
import os
import logging

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# 添加当前目录到Python路径中，确保可以导入同目录下的模块
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# 导入本地模块
import open_platform_interface
# try:
#     import open_platform_interface
#     logger.info("成功导入open_platform_interface模块")
# except ImportError as e:
#     logger.error(f"导入open_platform_interface模块失败: {e}")
#     logger.error("请确保open_platform_interface.py文件与server.py在同一目录下")
#     raise

# 初始化FastMCP服务器
mcp = FastMCP("mcptool")

# 检查环境变量
env_api_key = os.getenv("API_KEY", "")  # 提供默认空字符串值
env_secret = os.getenv("SECRET_KEY", "")  # 提供默认空字符串值
env_version = os.getenv("VERSION", "")  # 提供默认空字符串值
env_url = os.getenv("ENV_URL", "")  # 提供默认空字符串值

@mcp.tool()
async def check_env_available() -> dict:
    """
    查看当前环境配置信息，用于检查环境变量是否正确设置。

    API_KEY: 密钥ID
    SECRET_KEY: 密钥密钥
    VERSION: API版本
    ENV_URL: 环境URL
    """
    # 检查环境变量是否设置
    if not env_api_key or not env_secret:
        logger.warning("API_KEY或SECRET_KEY环境变量未设置")
        return {
            "error": "环境变量未配置",
            "message": "请检查环境变量是否正确设置"
        }

    # 返回环境变量信息（不直接暴露敏感信息）
    return {
        "api_key": env_api_key,
        "secret_key": env_secret,
        "version": env_version,
        "url": env_url
    }

@mcp.tool()
async def get_org_subject_info(subject: str) -> dict:
    """
    获取机构主体信息
    """
    if not env_api_key or not env_secret or not env_url:
        return {
            "error": "环境变量未配置",
            "message": "请检查环境变量是否正确设置"
        }
    logger.info(f"开始查询机构主体信息: {subject}")
    try:
        req = {
            "subject_name": subject,
            "api_key": env_api_key,
            "version": env_version,
            "secret_key": env_secret,
            "env_url": env_url
        }
        result = open_platform_interface.get_org_subject_info(req)
        # 检查result是否已经是字典，如果不是才进行json.loads
        if isinstance(result, str):
            return json.loads(result)
        logger.info(f"成功获取机构主体信息: {subject}")
        return result
    except Exception as e:
        logger.error(f"获取机构主体信息失败: {str(e)}")
        return {"error": f"获取机构主体信息失败: {str(e)}"}

@mcp.tool()
async def query_ant_block_info(safe_id: str) -> dict:
    """
    区块链存证结果查询
    """
    if not env_api_key or not env_secret or not env_url:
        return {
            "error": "环境变量未配置",
            "message": "请检查环境变量是否正确设置"
        }
    logger.info(f"开始查询区块链存证信息: {safe_id}")
    try:
        req = {
            "safe_id": safe_id,
            "api_key": env_api_key,
            "version": env_version,
            "secret_key": env_secret,
            "env_url": env_url
        }
        result = open_platform_interface.query_ant_block_info(req)
        # 检查result是否已经是字典，如果不是才进行json.loads
        if isinstance(result, str):
            return json.loads(result)
        logger.info(f"成功获取区块链存证信息: {safe_id}")
        return result
    except Exception as e:
        logger.error(f"查询区块链存证结果失败: {str(e)}")
        return {"error": f"查询区块链存证结果失败: {str(e)}"}

def main():
    logger.info("启动MCP服务器...")
    mcp.run(transport='streamable-http', port=8099, path='/mcp')

# 直接运行时的示例用法
if __name__ == "__main__":
    main()