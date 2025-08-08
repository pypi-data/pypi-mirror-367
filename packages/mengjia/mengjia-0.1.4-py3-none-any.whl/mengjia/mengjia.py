import random
import string
import datetime
from datetime import date
from typing import Optional

seed = 1

def shuffle_string(s: str, seed: int) -> str:
    """打乱字符串，基于固定种子可还原"""
    random.seed(seed)
    chars = list(s)
    random.shuffle(chars)
    return ''.join(chars)

def unshuffle_string(shuffled: str, seed: int) -> str:
    """还原被打乱的字符串"""
    random.seed(seed)
    # 生成相同的排列顺序
    indices = list(range(len(shuffled)))
    random.shuffle(indices)
    
    # 创建逆排列
    reverse_indices = [0] * len(indices)
    for i, pos in enumerate(indices):
        reverse_indices[pos] = i
    
    # 按原始顺序重建字符串
    return ''.join(shuffled[i] for i in reverse_indices)

def generate_random_string(length: int) -> str:
    """生成指定长度的随机字符串(大小写字母+数字)"""
    random.seed()  # 重置随机种子为系统时间
    chars = string.ascii_letters + string.digits
    return ''.join(random.choice(chars) for _ in range(length))

def encode_date(date_str: str) -> str:
    """将日期字符串编码为8字符的编码"""
    # 简单实现：将每个数字转换为字母(A=0, B=1,... J=9)
    mapping = {str(i): chr(65 + i) for i in range(10)}
    # for key, value in mapping.items():
    #     print(f"{key}: {value}")
    encoded = []
    for c in date_str:
        encoded.append(mapping[c])
    return ''.join(encoded)

def decode_date(encoded_date: str) -> Optional[str]:
    """将8字符的编码解码为日期字符串"""
    mapping = {chr(65 + i): str(i) for i in range(10)}
    try:
        decoded = []
        for c in encoded_date:
            decoded.append(mapping[c])
        return ''.join(decoded)
    except KeyError:
        return None

def calculate_checksum(api_key_part: str) -> str:
    """计算API Key部分的校验码"""
    # 简单实现：取字符ASCII码的和，然后模36，转换为字母或数字
    total = sum(ord(c) for c in api_key_part)
    checksum_value = total % 36
    if checksum_value < 10:
        return str(checksum_value)
    else:
        return chr(55 + checksum_value)  # 10->A, 11->B,... 35->Z

def generate_api_key(expiry_date: str = "20250901") -> str:
    """
    生成包含有效期的API Key

    参数:
        expiry_date: 有效期日期，格式为YYYYMMDD

    返回:
        生成的API Key，格式为24字符的字符串
    """
    if len(expiry_date) != 8:
        raise ValueError("Expiry date must be in YYYYMMDD format")

    # 生成随机部分
    prefix = generate_random_string(8)
    suffix = generate_random_string(8)

    # 编码日期
    encoded_date = encode_date(expiry_date)

    # 组合并计算校验码
    main_part = prefix + encoded_date + suffix
    
    #打乱排列顺序
    #seed = 123456  # 可以是任意整数（如20250808）
    main_part_v2 = shuffle_string(main_part, seed)
    checksum = calculate_checksum(main_part_v2)
    return main_part_v2 + checksum

def validate_api_key(api_key: str) -> bool:
    """
    验证API Key是否有效(未过期)
    参数:
        api_key: 要验证的API Key
    返回:
        True如果API Key格式正确且未过期，False否则
    """
    
    # print("len(api_key)=",len(api_key))
    # 检查长度
    if len(api_key) != 25:
        return False

    # 提取各部分
    prefix = api_key[:8]
    encoded_date = api_key[8:16]
    suffix = api_key[16:24]
    checksum = api_key[24:]

    # 验证校验码
    main_part = prefix + encoded_date + suffix
    expected_checksum = calculate_checksum(main_part)
    
    if checksum != expected_checksum:  # 简单扩展校验码
        return False
        
    #seed = 123456
    sourcestr = unshuffle_string(main_part, seed)
    encoded_date = sourcestr[8:16]

    # 解码日期
    expiry_date_str = decode_date(encoded_date)

    if not expiry_date_str or len(expiry_date_str) != 8:
        return False


    # 获取当前日期
    current = date.today()  # 获取当前日期（date对象）
    # print("----current=",current)
        
    current_date_str = current.strftime("%Y%m%d")  # 格式化为20250807
    #print("----current_date_str=",current_date_str)

    # 检查是否过期
    return current_date_str <= expiry_date_str

