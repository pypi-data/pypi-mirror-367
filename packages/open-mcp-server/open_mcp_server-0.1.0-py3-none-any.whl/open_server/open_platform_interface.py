import json
import time
import random
import requests

from sign_util import SignUtil


# 模拟常量配置
class Constant:
    APP_ID = "ntCtwnQEU7KV"  # 应用 ID
    SECRET_KEY = "wrlXq5JXNlHq"  # 应用秘钥
    VERSION_1 = "1.0"  # 接口版本
    TEST_BASE_URL = "http://testyqt.easysign.cn:8028/APIService"  # 测试环境基础URL
    BQ_ANT_BLOCK_INFO_URL = "/bqserver/v2/queryAntBlockInfo"  # 区块链存证结果查询接口路径
    JGZT_INFO_URL = "/organization/findSysOrgSubjectInfo"


def get_org_subject_info(subject_name):
    """
    获取机构主体信息
    
    :param subject_name: 主体名称
    :return: API响应结果
    """
    # 敏感信息建议从配置文件或环境变量读取
    app_id = Constant.APP_ID
    app_secret = Constant.SECRET_KEY
    version = Constant.VERSION_1
    timestamp = str(int(time.time() * 1000))  # 当前时间戳(毫秒)
    nonce = f"{random.randint(0, 99999999):08d}"  # 8位随机整数

    # 业务参数
    body = {
        "subjectName": subject_name
    }

    # 安全参数
    body["appId"] = app_id
    body["version"] = version
    body["timestamp"] = timestamp
    body["nonce"] = nonce
    body["sign"] = SignUtil.get_sign(body, app_secret)

    # 发送HTTP请求
    url = Constant.TEST_BASE_URL + Constant.JGZT_INFO_URL
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


def query_ant_block_info(safe_id):
    """
    区块链存证结果查询
    
    :param safe_id: 存证ID
    :return: API响应结果
    """
    # 敏感信息建议从配置文件或环境变量读取
    app_id = Constant.APP_ID
    app_secret = Constant.SECRET_KEY
    version = Constant.VERSION_1
    timestamp = str(int(time.time() * 1000))  # 当前时间戳(毫秒)
    nonce = f"{random.randint(0, 99999999):08d}"  # 8位随机整数

    # 业务参数
    body = {
        "safeId": safe_id
    }

    # 安全参数
    body["appId"] = app_id
    body["version"] = version
    body["timestamp"] = timestamp
    body["nonce"] = nonce
    body["sign"] = SignUtil.get_sign(body, app_secret)

    # 发送HTTP请求
    url = Constant.TEST_BASE_URL + Constant.BQ_ANT_BLOCK_INFO_URL
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