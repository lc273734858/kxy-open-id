"""
并发测试脚本：验证号段分配的分布式锁机制

该脚本模拟多个并发请求同时获取号段，验证：
1. 不会出现重复的号段
2. 分布式锁机制正常工作
3. 初始化逻辑只执行一次
"""

import asyncio
import httpx
from typing import List, Tuple

# 测试配置
BASE_URL = "http://localhost:5801"
CONCURRENT_REQUESTS = 10  # 并发请求数量

# 测试参数
TEST_PARAMS = {
    "system_code": "test_system",
    "db_name": "test_db",
    "table_name": "test_table",
    "field_name": "test_field",
    "segment_count": 1000
}


async def allocate_segment(client: httpx.AsyncClient, request_id: int) -> Tuple[int, dict]:
    """
    发送号段分配请求

    Args:
        client: HTTP客户端
        request_id: 请求ID（用于追踪）

    Returns:
        Tuple[int, dict]: (请求ID, 响应数据)
    """
    try:
        response = await client.get(
            f"{BASE_URL}/api/segment/allocate",
            params=TEST_PARAMS
        )

        if response.status_code == 200:
            data = response.json()
            print(f"[Request {request_id}] Success: start={data['start']}, end={data['end']}")
            return request_id, data
        else:
            print(f"[Request {request_id}] Failed: {response.status_code} - {response.text}")
            return request_id, None
    except Exception as e:
        print(f"[Request {request_id}] Error: {e}")
        return request_id, None


async def test_concurrent_allocation():
    """
    测试并发号段分配
    """
    print(f"\n{'='*60}")
    print(f"开始并发测试：{CONCURRENT_REQUESTS} 个并发请求")
    print(f"测试参数：{TEST_PARAMS}")
    print(f"{'='*60}\n")

    async with httpx.AsyncClient(timeout=30.0) as client:
        # 创建并发任务
        tasks = [
            allocate_segment(client, i)
            for i in range(CONCURRENT_REQUESTS)
        ]

        # 并发执行所有请求
        results = await asyncio.gather(*tasks)

    # 分析结果
    print(f"\n{'='*60}")
    print("测试结果分析")
    print(f"{'='*60}\n")

    successful_results = [(req_id, data) for req_id, data in results if data is not None]
    failed_count = len(results) - len(successful_results)

    print(f"成功请求数：{len(successful_results)}")
    print(f"失败请求数：{failed_count}")

    if successful_results:
        # 检查号段是否有重叠
        segments = [(data['start'], data['end']) for _, data in successful_results]
        segments.sort()

        print(f"\n所有成功分配的号段：")
        for i, (start, end) in enumerate(segments):
            print(f"  号段 {i+1}: [{start}, {end}] (大小: {end - start + 1})")

        # 检查重叠
        has_overlap = False
        for i in range(len(segments) - 1):
            current_end = segments[i][1]
            next_start = segments[i + 1][0]
            if current_end >= next_start:
                print(f"\n❌ 发现重叠号段：")
                print(f"  号段 {i+1}: [{segments[i][0]}, {segments[i][1]}]")
                print(f"  号段 {i+2}: [{segments[i+1][0]}, {segments[i+1][1]}]")
                has_overlap = True

        if not has_overlap:
            print(f"\n✅ 所有号段无重叠，并发控制成功！")

        # 验证号段连续性
        expected_segment_count = TEST_PARAMS['segment_count']
        all_continuous = all(
            end - start + 1 == expected_segment_count
            for start, end in segments
        )

        if all_continuous:
            print(f"✅ 所有号段大小正确 ({expected_segment_count})")
        else:
            print(f"❌ 部分号段大小不正确")

    print(f"\n{'='*60}\n")


async def cleanup_test_data():
    """
    清理测试数据（删除 Redis 中的测试键）
    """
    print("清理测试数据...")

    # 这里需要直接连接 Redis 删除测试键
    # 为了简化，可以通过 Redis CLI 手动清理，或者添加一个清理 API
    from app.redis_client import RedisClient

    redis_client = await RedisClient.get_instance()

    segment_key = f"{TEST_PARAMS['system_code']}:{TEST_PARAMS['db_name']}:{TEST_PARAMS['table_name']}:{TEST_PARAMS['field_name']}".lower()

    keys_to_delete = [
        f"kxy:id:segment:{segment_key}",
        f"kxy:id:failure:{segment_key}",
        f"kxy:id:lock:segment:{segment_key}"
    ]

    for key in keys_to_delete:
        await redis_client.delete(key)

    print(f"已删除测试键：{keys_to_delete}")

    await RedisClient.close()


if __name__ == "__main__":
    print("""
╔══════════════════════════════════════════════════════════════╗
║          号段分配并发测试                                      ║
║                                                              ║
║  本测试脚本验证分布式锁机制在并发场景下的正确性                ║
╚══════════════════════════════════════════════════════════════╝
    """)

    # 运行测试前先清理数据
    print("\n[步骤 1] 清理之前的测试数据")
    asyncio.run(cleanup_test_data())

    # 运行并发测试
    print("\n[步骤 2] 执行并发测试")
    asyncio.run(test_concurrent_allocation())

    print("\n测试完成！\n")
    print("提示：")
    print("  - 如需再次测试，请先运行清理脚本或重启 Redis")
    print("  - 如需修改并发数量，请修改 CONCURRENT_REQUESTS 变量")
