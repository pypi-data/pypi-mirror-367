import json
import time
import random
import requests

from sign_util import SignUtil


# 模拟常量配置
class Constant:
    BQ_ANT_BLOCK_INFO_URL = "/bqserver/v2/queryAntBlockInfo"  # 区块链存证结果查询接口路径
    JGZT_INFO_URL = "/organization/findSysOrgSubjectInfo"


def get_org_subject_info(param):
    """
    获取机构主体信息
    
    :param subject_name: 主体名称
    :return: API响应结果
    """
    timestamp = str(int(time.time() * 1000))  # 当前时间戳(毫秒)
    nonce = f"{random.randint(0, 99999999):08d}"  # 8位随机整数

    # 业务参数
    body = {
        "subjectName": param.get("subject_name")
    }

    # 安全参数
    body["appId"] = param.get("api_key")
    body["version"] = param.get("version")
    body["timestamp"] = timestamp
    body["nonce"] = nonce
    body["sign"] = SignUtil.get_sign(body, param.get("secret_key"))

    # 发送HTTP请求
    url = param.get("env_url") + Constant.JGZT_INFO_URL
    headers = {
        "Content-Type": "application/json; charset=utf-8"
    }
    try:
        response = requests.post(url, headers=headers, data=json.dumps(body), timeout=(60, 60))
        response.raise_for_status()  # 如果响应状态码不是200会抛出异常
        # 正确处理响应对象
        response_data = response.json()  # 先解析JSON
        return response_data
    except requests.exceptions.RequestException as e:
        return {"error": f"请求发生错误: {e}"}
    except json.JSONDecodeError as e:
        return {"error": f"响应数据解析失败: {e}"}


def query_ant_block_info(param):
    """
    区块链存证结果查询
    
    :param safe_id: 存证ID
    :return: API响应结果
    """
    timestamp = str(int(time.time() * 1000))  # 当前时间戳(毫秒)
    nonce = f"{random.randint(0, 99999999):08d}"  # 8位随机整数

    # 业务参数
    body = {
        "safeId": param.get("safe_id")
    }

    # 安全参数
    body["appId"] = param.get("api_key")
    body["version"] = param.get("version")
    body["timestamp"] = timestamp
    body["nonce"] = nonce
    body["sign"] = SignUtil.get_sign(body, param.get("secret_key"))

    # 发送HTTP请求
    url = param.get("env_url") + Constant.BQ_ANT_BLOCK_INFO_URL
    headers = {
        "Content-Type": "application/json; charset=utf-8"
    }
    
    try:
        response = requests.get(url, headers=headers, data=json.dumps(body), timeout=(60, 60))
        response.raise_for_status()  # 如果响应状态码不是200会抛出异常
        # 正确处理响应对象
        response_data = response.json()  # 先解析JSON
        return response_data
    except requests.exceptions.RequestException as e:
        return {"error": f"请求发生错误: {e}"}
    except json.JSONDecodeError as e:
        return {"error": f"响应数据解析失败: {e}"}


def main():
    # 敏感信息建议从配置文件或环境变量读取
    response_data = get_org_subject_info("测试机构")
    print(response_data)


if __name__ == "__main__":
    main()