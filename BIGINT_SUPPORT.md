# 64位长整型支持说明

本服务已全面支持64位长整型（BIGINT）ID，以满足大规模分布式系统的需求。

## 支持范围

### 1. 后端支持

- **SegmentRequest.segment_count**: 最大值从 1,000,000 提升至 9,223,372,036,854,775,807 (2^63-1)
- **SegmentResponse.start/end**: 支持完整的64位长整型范围
- **所有 ID 相关字段**: initial_value, max_id 等均支持64位长整型

### 2. JSON 序列化

由于 JavaScript 的 Number 类型只能安全表示到 2^53-1 (9,007,199,254,740,991)，超过此范围的整数会丢失精度。

**解决方案**:
- 后端会自动将超过 JavaScript 安全范围的整数序列化为字符串
- 在 9,007,199,254,740,991 以内的整数仍以数字形式返回
- 超过此范围的整数会以字符串形式返回

**示例响应**:

```json
{
  "code": 0,
  "msg": "Success",
  "data": {
    "start": "9007199254740992",
    "end": "9007199254741991"
  }
}
```

## 数据库配置要求

### MySQL

使用 **BIGINT** 类型存储 ID 字段：

```sql
CREATE TABLE your_table (
  id BIGINT NOT NULL AUTO_INCREMENT PRIMARY KEY,
  -- 其他字段...
);
```

**BIGINT 范围**:
- 有符号: -9,223,372,036,854,775,808 到 9,223,372,036,854,775,807
- 无符号: 0 到 18,446,744,073,709,551,615

### PostgreSQL

使用 **BIGINT** 或 **BIGSERIAL** 类型：

```sql
CREATE TABLE your_table (
  id BIGSERIAL PRIMARY KEY,
  -- 或者
  id BIGINT NOT NULL PRIMARY KEY
);
```

### SQL Server

使用 **BIGINT** 类型：

```sql
CREATE TABLE your_table (
  id BIGINT IDENTITY(1,1) PRIMARY KEY,
  -- 其他字段...
);
```

### Oracle

使用 **NUMBER(19,0)** 类型：

```sql
CREATE TABLE your_table (
  id NUMBER(19,0) PRIMARY KEY,
  -- 其他字段...
);
```

## 前端处理

### JavaScript/TypeScript

对于大整数（超过安全范围），后端会返回字符串。前端需要相应处理：

```typescript
interface SegmentResponse {
  start: number | string;  // 可能是数字或字符串
  end: number | string;
}

// 处理响应
const response = await fetch('/api/segment/allocate', {
  method: 'POST',
  body: JSON.stringify(request)
});

const result = await response.json();
const start = BigInt(result.data.start);  // 使用 BigInt 处理
const end = BigInt(result.data.end);
```

### 使用 BigInt

对于需要计算的场景，使用 JavaScript 的 BigInt：

```javascript
// 转换为 BigInt
const id = BigInt("9007199254740992");

// 进行运算
const nextId = id + 1n;

// 转回字符串发送给后端
const idStr = nextId.toString();
```

### 仅用于显示

如果只是显示 ID，可以直接使用字符串：

```javascript
// 直接显示
console.log(`ID range: ${result.data.start} - ${result.data.end}`);
```

## API 示例

### 请求

```bash
POST /api/segment/allocate
Content-Type: application/json

{
  "system_code": "order-service",
  "db_name": "order_db",
  "table_name": "orders",
  "field_name": "id",
  "segment_count": 1000000000000
}
```

### 响应（小范围ID）

```json
{
  "code": 0,
  "msg": "Allocated segment: 1000 to 11000",
  "data": {
    "start": 1000,
    "end": 11000
  }
}
```

### 响应（大范围ID）

```json
{
  "code": 0,
  "msg": "Allocated segment: 9007199254740992 to 10007199254740991",
  "data": {
    "start": "9007199254740992",
    "end": "10007199254740991"
  }
}
```

## 性能考虑

1. **Redis 存储**: Redis 支持64位有符号整数 (-2^63 到 2^63-1)
2. **原子操作**: 使用 Redis INCRBY 确保线程安全的 ID 分配
3. **序列化开销**: 大整数转字符串的性能影响可忽略不计

## 注意事项

1. **数据库迁移**: 如果现有表使用 INT (32位)，需要迁移到 BIGINT
2. **索引重建**: 修改字段类型后需要重建相关索引
3. **备份**: 进行结构变更前务必备份数据
4. **前端兼容**: 确保前端代码能正确处理字符串形式的大整数

## 测试

可以使用以下 segment_count 值测试大整数支持：

```bash
# 测试小范围（返回数字）
"segment_count": 10000

# 测试大范围（返回字符串）
"segment_count": 9007199254750000
```
