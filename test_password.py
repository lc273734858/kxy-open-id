#!/usr/bin/env python3
"""
测试密码哈希功能，诊断问题
"""
from app.utils.auth_utils import hash_password, verify_password
import asyncio
from app.redis_client import RedisClient

async def test_password_operations():
    print("=" * 50)
    print("测试密码哈希功能")
    print("=" * 50)

    # 测试1: 基本哈希功能
    test_password = "123456"
    print(f"\n1. 测试密码: {test_password}")
    print(f"   密码长度: {len(test_password)} 字符 / {len(test_password.encode('utf-8'))} 字节")

    try:
        hashed = hash_password(test_password)
        print(f"   ✓ 哈希成功")
        print(f"   哈希值: {hashed}")
        print(f"   哈希值长度: {len(hashed)} 字符 / {len(hashed.encode('utf-8'))} 字节")
    except Exception as e:
        print(f"   ✗ 哈希失败: {e}")
        return

    # 测试2: 验证功能
    print(f"\n2. 测试密码验证")
    try:
        result = verify_password(test_password, hashed)
        print(f"   ✓ 验证成功: {result}")
    except Exception as e:
        print(f"   ✗ 验证失败: {e}")
        return

    # 测试3: 检查Redis中存储的值
    print(f"\n3. 检查Redis中存储的密码")
    try:
        redis_client = await RedisClient.get_instance()
        stored_password = await redis_client.get("kxy:id:system:password")

        if stored_password:
            print(f"   找到存储的密码哈希")
            print(f"   存储值: {stored_password}")
            print(f"   存储值长度: {len(stored_password)} 字符 / {len(stored_password.encode('utf-8'))} 字节")
            print(f"   存储值类型: {type(stored_password)}")

            # 尝试验证
            try:
                result = verify_password(test_password, stored_password)
                print(f"   ✓ 使用'123456'验证: {result}")
            except Exception as e:
                print(f"   ✗ 验证失败: {e}")
                print(f"\n   问题诊断:")
                print(f"   - 存储的值可能不是有效的bcrypt哈希")
                print(f"   - 建议删除并重新初始化")
        else:
            print(f"   未找到存储的密码 (系统未初始化)")

    except Exception as e:
        print(f"   ✗ Redis操作失败: {e}")

    print("\n" + "=" * 50)

if __name__ == "__main__":
    asyncio.run(test_password_operations())
