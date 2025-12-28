#!/usr/bin/env python3
"""
清除认证相关的Redis数据，用于重置系统初始化状态
"""
import asyncio
from app.redis_client import RedisClient


async def reset_auth_data():
    print("=" * 60)
    print("重置系统认证数据")
    print("=" * 60)

    try:
        redis_client = await RedisClient.get_instance()

        # 定义需要删除的keys
        keys_to_delete = [
            "kxy:id:system:init",
            "kxy:id:system:username",
            "kxy:id:system:password"
        ]

        print("\n检查并删除认证相关的Redis键:")
        for key in keys_to_delete:
            value = await redis_client.get(key)
            if value:
                print(f"  - {key}: 存在 (值: {value[:50]}{'...' if len(str(value)) > 50 else ''})")
                await redis_client.delete(key)
                print(f"    ✓ 已删除")
            else:
                print(f"  - {key}: 不存在")

        print("\n" + "=" * 60)
        print("重置完成！现在可以重新初始化系统了。")
        print("=" * 60)

    except Exception as e:
        print(f"\n✗ 错误: {e}")
        import traceback
        traceback.print_exc()
    finally:
        await RedisClient.close()


if __name__ == "__main__":
    asyncio.run(reset_auth_data())
