import hashlib
import json
from collections import OrderedDict


class SignUtil:
    @staticmethod
    def get_sign(data, app_key):
        """
        生成签名
        
        :param data: 包含待签名数据的字典
        :param app_key: 应用密钥
        :return: 签名字符串
        """
        # 对数据进行排序
        sorted_data = SignUtil._get_sort_dict(data)
        # 验证并收集签名字段
        verify_list = []
        for key, value in sorted_data.items():
            if key == "sign":
                continue
            if value is not None:
                verify_list.append(str(value))
        
        # 添加app_key
        verify_list.append(app_key)
        
        # 排序
        verify_list.sort()
        
        # 拼接字符串
        plain_text = "".join(verify_list)
        # 生成MD5签名
        sign = SignUtil._encryption(plain_text)
        
        # 注释掉敏感信息打印
        print(f"获取签名 明文={plain_text}，密文={sign}")
        
        return sign
    
    @staticmethod
    def _encryption(plain_text):
        """
        MD5加密
        
        :param plain_text: 明文
        :return: MD5密文
        """
        md5 = hashlib.md5()
        md5.update(plain_text.encode('utf-8'))
        return md5.hexdigest()
    
    @staticmethod
    def _get_sort_dict(data):
        """
        对字典进行排序
        
        :param data: 待排序的字典
        :return: 排序后的有序字典
        """
        if data is None:
            return OrderedDict()
        
        # 创建有序字典
        sorted_map = OrderedDict()
        
        # 对键进行排序
        for key in sorted(data.keys()):
            value = data[key]
            
            # 如果值是列表类型
            if isinstance(value, list):
                json_array = []
                for item in value:
                    if isinstance(item, dict):
                        # 递归处理字典元素
                        sort_json = SignUtil._get_sort_dict(item)
                        json_array.append(sort_json)
                    else:
                        json_array.append(item)
                sorted_map[key] = json_array
            
            # 如果值是字典类型
            elif isinstance(value, dict):
                sort_json = SignUtil._get_sort_dict(value)
                sorted_map[key] = sort_json
            
            # 其他类型直接赋值
            else:
                sorted_map[key] = value
        
        return sorted_map
