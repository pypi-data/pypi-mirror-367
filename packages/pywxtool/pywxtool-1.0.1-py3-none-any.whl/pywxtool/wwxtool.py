# -*- coding: utf-8 -*-#
# -------------------------------------------------------------------------------
# Description:  获取好友、聊天记录、收藏夹 到 csv 文件
# -------------------------------------------------------------------------------
import ctypes
import os
import platform
from ctypes import c_ubyte, c_char_p, c_size_t, Structure, POINTER, c_void_p
import sys
import pkg_resources


# 定义 ByteArray 结构体，对应 DLL 中的结构
class ByteArray(Structure):
    _fields_ = [
        ('data', POINTER(c_ubyte)),  # 无符号字符指针
        ('size', c_size_t)  # 数据长度
    ]


class WxTool:
    def __init__(self, dll_path=pkg_resources.resource_filename('pywxtool', 'libs', "wxtool.dll"), activation_key=""):
        """
        初始化 WxTool 实例

        :param dll_path: wxtool.dll 的绝对路径
        """
        self.wxtool_dll_path = dll_path
        self.activation_key = activation_key
        self.dll = self.__load_dll()
        self.initialization()

    def __load_dll(self):
        """加载 DLL 并设置函数原型"""
        # 确保 DLL 目录在系统路径中
        dll_dir = os.path.dirname(self.wxtool_dll_path)
        if dll_dir not in os.environ['PATH']:
            os.environ['PATH'] = dll_dir + os.pathsep + os.environ['PATH']

        # 加载 DLL
        try:
            dll = ctypes.WinDLL(self.wxtool_dll_path, winmode=0)
        except OSError as e:
            raise RuntimeError(f"无法加载 DLL: {e}") from e

        # 注册初始化函数
        self.__register_initialization(dll)
        # 注册返回 ByteArray 的函数
        self.__register_byte_array_functions(dll)
        # 注册密钥和数据库操作函数
        self.__register_key_db_functions(dll)
        # 注册工具函数
        self.__register_util_functions(dll)
        # 注册测试函数
        self.__register_test_function(dll)

        return dll

    def __register_initialization(self, dll):
        """初始化函数"""
        dll.initialization.argtypes = [c_char_p]
        dll.initialization.restype = ctypes.c_int

    def __register_byte_array_functions(self, dll):
        """处理 ByteArray 相关函数"""
        # create_byte_array 和 free_byte_array
        dll.create_byte_array.argtypes = [POINTER(c_ubyte), c_size_t]
        dll.create_byte_array.restype = ByteArray
        dll.free_byte_array.argtypes = [POINTER(ByteArray)]
        dll.free_byte_array.restype = None

        # 返回 ByteArray 的函数（转换结果需用 free_byte_array 释放）
        byte_array_funcs = [
            'verify_key_fast_init',
            'convert_to_sqlcipher_rawkey',
            'hex_to_bytes_c'
        ]
        for func in byte_array_funcs:
            # 设置返回类型为 ByteArray
            getattr(dll, func).restype = ByteArray
            # 包装函数
            setattr(dll, func, self.__wrap_byte_array_function(getattr(dll, func)))

    def __wrap_byte_array_function(self, func):
        """包装返回 ByteArray 的函数：自动复制数据并释放内存"""

        def wrapper(*args):
            byte_arr = func(*args)
            if byte_arr.data is None or byte_arr.size == 0:
                return b""
            # 将 C 数组复制到 Python 字节对象
            result = bytes(byte_arr.data[:byte_arr.size])
            # 释放 DLL 分配的内存
            self.dll.free_byte_array(ctypes.pointer(byte_arr))
            return result

        return wrapper

    def __register_key_db_functions(self, dll):
        """密钥和数据库操作函数"""
        # verify_key_fast: 使用字节数组密钥和 blist
        dll.verify_key_fast.argtypes = [
            POINTER(c_ubyte), c_size_t,  # key, key_len
            POINTER(c_ubyte), c_size_t,  # blist, blist_len
            c_char_p  # version
        ]
        dll.verify_key_fast.restype = ctypes.c_int
        dll.verify_key_fast_init.argtypes = [
            c_char_p,  # wx_db_path
        ]
        # verify_key: 使用字节数组密钥和文件路径
        dll.verify_key.argtypes = [
            POINTER(c_ubyte), c_size_t,  # key, key_len
            c_char_p,  # wx_db_path
            c_char_p  # version
        ]
        dll.verify_key.restype = ctypes.c_int

        # decrypt_db: 解密数据库
        dll.decrypt_db.argtypes = [
            POINTER(c_ubyte), c_size_t,  # key, key_len
            c_char_p,  # wx_db_path
            c_char_p,  # output_path
            c_char_p  # version
        ]
        dll.decrypt_db.restype = ctypes.c_int

    def __register_util_functions(self, dll):
        """工具函数封装"""
        # bytes_to_hex_c: 返回字符串（需要释放内存）
        dll.bytes_to_hex_c.argtypes = [POINTER(c_ubyte), c_size_t]
        dll.bytes_to_hex_c.restype = ctypes.POINTER(ctypes.c_char)

        # 包装函数确保内存安全
        original_bytes_to_hex = dll.bytes_to_hex_c

        # def wrapped_bytes_to_hex(data, length):
        #     ptr = original_bytes_to_hex(data, length)
        #     result = ctypes.string_at(ptr)
        #     dll.free_byte_array(ByteArray(ptr, c_size_t(0)))  # 使用 free_byte_array 释放
        #     return result.decode('utf-8')
        def wrapped_bytes_to_hex(data, length):
            ptr = original_bytes_to_hex(data, length)
            result = ctypes.string_at(ptr)

            # 使用 free 函数释放内存
            try:
                # 尝试使用 msvcrt 中的 free
                msvcrt = ctypes.cdll.msvcrt
                free = msvcrt.free
                free.argtypes = [c_void_p]
                free.restype = None
                free(ptr)
            except:
                # 如果找不到 msvcrt，尝试使用 ctypes 自带的 free
                try:
                    free = ctypes.CDLL('msvcrt').free
                    free.argtypes = [c_void_p]
                    free.restype = None
                    free(ptr)
                except:
                    print("警告: 无法释放 bytes_to_hex_c 分配的内存")

            return result.decode('utf-8')

        dll.bytes_to_hex_c = wrapped_bytes_to_hex

    def __register_test_function(self, dll):
        """无参数测试函数"""
        dll.test.argtypes = []
        dll.test.restype = None

    # ========================================== 公开接口方法 ==========================================
    def initialization(self) -> int:
        """初始化激活密钥（必须在其他函数前调用）"""
        return self.dll.initialization(self.activation_key.encode('utf-8'))

    def verify_key_fast_init(self, wx_db_path: str) -> bytes:
        """快速初始化密钥验证 - 返回 blist 数据"""
        path_bytes = wx_db_path.encode('utf-8')
        return self.dll.verify_key_fast_init(path_bytes)

    def verify_key_fast(self, key: bytes, blist: bytes, version: str) -> int:
        """快速密钥验证（使用内存中的 blist 数据）"""
        return self.dll.verify_key_fast(
            (c_ubyte * len(key))(*key), len(key),
            (c_ubyte * len(blist))(*blist), len(blist),
            version.encode('utf-8')
        )

    def verify_key(self, key: bytes, wx_db_path: str, version: str) -> int:
        """完整密钥验证（直接读取数据库文件）"""
        return self.dll.verify_key(
            (c_ubyte * len(key))(*key), len(key),
            wx_db_path.encode('utf-8'),
            version.encode('utf-8')
        )

    def convert_to_sqlcipher_rawkey(self, key: bytes, blist: bytes, version: str) -> bytes:
        """转换为 SQLCipher 原始密钥"""
        return self.dll.convert_to_sqlcipher_rawkey(
            (c_ubyte * len(key))(*key), len(key),
            (c_ubyte * len(blist))(*blist), len(blist),
            version.encode('utf-8')
        )

    def decrypt_db(self, key: bytes, wx_db_path: str, output_path: str, version: str) -> int:
        """解密微信数据库"""
        return self.dll.decrypt_db(
            (c_ubyte * len(key))(*key), len(key),
            wx_db_path.encode('utf-8'),
            output_path.encode('utf-8'),
            version.encode('utf-8')
        )

    def bytes_to_hex(self, data: bytes) -> str:
        """字节数据转十六进制字符串"""
        array_type = (c_ubyte * len(data))(*data)
        return self.dll.bytes_to_hex_c(array_type, len(data))

    def hex_to_bytes(self, hex_str: str) -> bytes:
        """十六进制字符串转字节数据"""
        hex_bytes = hex_str.encode('utf-8')
        return self.dll.hex_to_bytes_c(hex_bytes)

    def test(self):
        """测试 DLL 是否工作正常"""
        self.dll.test()


def test_decipher(wxtool):
    # 定义正确的和错误的密钥（十六进制字符串）
    key3_true = "8db6c56099ff4b92ba351155d2279a479cc04961b6334711978e22118d02431d"
    key3_false = "0db6c56099ff4b92ba351155d2279a479cc04961b6334711978e22118d024311"
    key4_true = "cc923e52bd9c41b2bd9b2bf2063ed3b8ed2bc8b1e21f4a0e9485c950720729bd"
    key4_false = "cc923e52bd9c41b2bd9b2bf2063ed3b8ed2bc8b1e21f4a0e9485c950720729ad"

    # 将十六进制密钥转换为字节数据
    key3_true_bytes = wxtool.hex_to_bytes(key3_true)
    key3_false_bytes = wxtool.hex_to_bytes(key3_false)
    key4_true_bytes = wxtool.hex_to_bytes(key4_true)
    key4_false_bytes = wxtool.hex_to_bytes(key4_false)

    # 数据库文件路径
    wx_db_path3 = r"D:\_code\c_code\wxtool_dll\test\MSG1.db"
    wx_db_path4 = r"D:\_code\c_code\wxtool_dll\test\contact.db"

    # 解密后的数据库输出路径
    out_wx_db_path3 = r"D:\_code\c_code\wxtool_dll\dist\MSG1_decrypted.db"
    out_wx_db_path4 = r"D:\_code\c_code\wxtool_dll\dist\contact_decrypted.db"

    print("====================== Testing verify_key TRUE... ======================")
    # # 测试用例1 - 正确密钥
    rc = wxtool.verify_key(key3_true_bytes, wx_db_path3, "3")
    print(f"1: {rc}")
    rc = wxtool.verify_key(key4_true_bytes, wx_db_path4, "4")
    print(f"2: {rc}")

    # 测试用例1 - 错误密钥
    rc = wxtool.verify_key(key3_false_bytes, wx_db_path3, "3")
    print(f"3: {rc}")
    rc = wxtool.verify_key(key4_false_bytes, wx_db_path4, "4")
    print(f"4: {rc}")

    print("====================== Testing verify_key_fast... ======================")
    # 获取blist数据
    blist3 = wxtool.verify_key_fast_init(wx_db_path3)
    blist4 = wxtool.verify_key_fast_init(wx_db_path4)

    # 测试用例2 - 正确密钥
    rc = wxtool.verify_key_fast(key3_true_bytes, blist3, "3")
    print(f"5: {rc}")
    rc = wxtool.verify_key_fast(key4_true_bytes, blist4, "4")
    print(f"6: {rc}")

    # 测试用例2 - 错误密钥
    rc = wxtool.verify_key_fast(key3_false_bytes, blist3, "3")
    print(f"7: {rc}")
    rc = wxtool.verify_key_fast(key4_false_bytes, blist4, "4")
    print(f"8: {rc}")

    print("====================== Testing convert_to_sqlcipher_rawkey... ======================")
    # 测试用例3 - 正确密钥
    sqlcipher_key3 = wxtool.convert_to_sqlcipher_rawkey(key3_true_bytes, blist3, "3")
    sqlcipher_key4 = wxtool.convert_to_sqlcipher_rawkey(key4_true_bytes, blist4, "4")
    print(f"9: {wxtool.bytes_to_hex(sqlcipher_key3)}")
    print(f"10: {wxtool.bytes_to_hex(sqlcipher_key4)}")

    # 测试用例3 - 错误密钥
    sqlcipher_key3_false = wxtool.convert_to_sqlcipher_rawkey(key3_false_bytes, blist3, "3")
    sqlcipher_key4_false = wxtool.convert_to_sqlcipher_rawkey(key4_false_bytes, blist4, "4")
    print(f"11: {wxtool.bytes_to_hex(sqlcipher_key3_false)}")
    print(f"12: {wxtool.bytes_to_hex(sqlcipher_key4_false)}")

    print("====================== Testing decrypt_db... ======================")
    # 测试用例4 - 正确密钥
    rc = wxtool.decrypt_db(key3_true_bytes, wx_db_path3, out_wx_db_path3, "3")
    print(f"13: {rc}")
    rc = wxtool.decrypt_db(key4_true_bytes, wx_db_path4, out_wx_db_path4, "4")
    print(f"14: {rc}")

    # 测试用例4 - 错误密钥
    rc = wxtool.decrypt_db(key3_false_bytes, wx_db_path3, out_wx_db_path3, "3")
    print(f"15: {rc}")
    rc = wxtool.decrypt_db(key4_false_bytes, wx_db_path4, out_wx_db_path4, "4")
    print(f"16: {rc}")


# 使用示例
if __name__ == "__main__":
    wxtool = WxTool(r"D:\_code\c_code\wxtool_dll\dist\wxtool.dll")
    # 1. 初始化
    # a = dll.test()
    test_decipher(wxtool)
