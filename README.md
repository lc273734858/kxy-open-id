# KXY ID 生成器

基于 FastAPI 和 Redis 构建的分布式 ID 段分配服务,支持多种数据库类型(MySQL、PostgreSQL、SQL Server、Oracle),配备 Vue 3 前端管理界面。

## 功能特性

- **多数据库支持**: 连接 MySQL、PostgreSQL、SQL Server 和 Oracle 数据库
- **分布式 ID 分配**: 使用 Redis 实现原子化的段式 ID 生成
- **自动发现**: 后台扫描器自动检测新表
- **Web 管理**: Vue 3 + Element Plus 前端,便于配置管理
- **JWT 认证**: 基于令牌的安全 API 端点
- **RESTful API**: 简洁的 API 设计,端点完善

## 架构

**单体应用** - 前端和后端集成为一个可部署单元。

```
FastAPI 应用程序 (端口 5801)
├── API 路由 (/api/*)
│   ├── 认证服务 (JWT)
│   ├── 数据库配置服务 (CRUD)
│   ├── 段分配服务 (原子化 ID 生成)
│   ├── 数据库连接器 (多数据库支持)
│   └── 后台扫描器 (表发现)
└── 静态前端服务 (/)
    ├── Vue 3 + Element Plus
    ├── 登录页面 (初始化/登录)
    ├── 数据库列表页面 (管理)
    └── 组件 (表单、导航)

数据存储
└── Redis
```

当你访问 http://localhost:5801 时,后端提供 Vue 前端服务,前端随后向同一服务器上的 `/api/*` 端点发起 API 调用。

## 前置要求

- Python 3.8+
- Redis 服务器
- Node.js 16+ (用于前端构建)

### 可选数据库驱动

应用程序支持多种数据库类型,但驱动程序按需安装:

- **MySQL** (默认包含): `aiomysql`
- **PostgreSQL**: `pip install asyncpg`
- **SQL Server**: `pip install pyodbc` + [ODBC Driver 17](https://docs.microsoft.com/en-us/sql/connect/odbc/download-odbc-driver-for-sql-server)
- **Oracle**: `pip install cx_Oracle` + [Oracle Instant Client](https://www.oracle.com/database/technologies/instant-client.html)

仅安装你需要的数据库驱动。

## 安装

### 1. 克隆仓库

```bash
cd /myspace/source/workspace/yudao-python/kxy-open-id
```

### 2. 后端设置

```bash
# 创建虚拟环境
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate

# 安装核心依赖 (默认包含 MySQL 驱动)
pip install -r requirements.txt

# 可选: 安装额外的数据库驱动
# PostgreSQL:
pip install asyncpg==0.30.0
# SQL Server (需要系统已安装 ODBC Driver 17):
pip install pyodbc==5.2.0
# Oracle (需要系统已安装 Oracle Instant Client):
pip install cx-Oracle==8.3.0

# 复制并配置环境变量
cp .env.example .env
# 使用你的 Redis 配置编辑 .env 文件
```

### 3. 前端设置

```bash
cd frontend
npm install
```

### 4. 启动 Redis

确保 Redis 在你的系统上运行:

```bash
# Ubuntu/Debian
sudo systemctl start redis

# macOS
brew services start redis

# 或直接运行
redis-server
```

## 配置

编辑 `.env` 文件:

```env
# Redis 配置
REDIS_HOST=127.0.0.1
REDIS_PORT=6379
REDIS_PASSWORD=
REDIS_DB=0

# JWT 配置
JWT_SECRET_KEY=your-secret-key-change-in-production
JWT_ALGORITHM=HS256
JWT_EXPIRE_HOURS=24
```

## 运行应用

### 生产模式 (推荐)

**一次性设置:**
```bash
# 构建前端静态文件
cd frontend
npm install
npm run build
cd ..
```

**启动应用:**
```bash
# 运行统一服务器
uvicorn app.main:app --reload --host 0.0.0.0 --port 5801

# 或使用 VSCode 调试配置 (F5)
```

**访问应用:**
- Web 界面: http://localhost:5801
- API 文档: http://localhost:5801/docs
- 健康检查: http://localhost:5801/health

### 开发模式 (前端开发)

如果你需要修改前端并启用热重载:

**终端 1 - 后端:**
```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 5801
```

**终端 2 - 前端开发服务器:**
```bash
cd frontend
npm run dev
```

**访问:**
- 前端 (带热重载): http://localhost:3000
- 后端 API: http://localhost:5801/docs

**注意:** 前端修改后,使用 `npm run build` 重新构建以更新生产版本。

### 生产部署

```bash
# 构建前端
cd frontend && npm run build && cd ..

# 使用多个工作进程运行
uvicorn app.main:app --host 0.0.0.0 --port 5801 --workers 4
```

## 使用说明

### 首次设置

1. 打开 http://localhost:5801
2. 系统将检测到首次设置
3. 创建管理员账户 (用户名 + 密码)
4. 使用创建的凭据登录

### 管理数据库配置

1. **添加数据库**:
   - 点击 "添加数据库" 按钮
   - 填写: 系统代码、数据库类型、地址 (host:port)、用户名、密码
   - 点击 "添加"

2. **初始化数据库**:
   - 点击数据库的 "初始化" 按钮
   - 系统将扫描所有表并存储最大 ID
   - 只有具有数字主键的表会被初始化

3. **添加自定义配置**:
   - 用于非表的 ID
   - 点击 "添加配置" 按钮
   - 指定字段名和初始值

4. **查看/编辑/删除**:
   - 使用操作列中的相应按钮

### 分配 ID 段 (API)

**端点:** `POST /api/segment/allocate` (无需认证)

**请求:**
```json
{
  "system_code": "my_system",
  "db_name": "my_database",
  "table_name": "users",
  "field_name": "id",
  "segment_count": 10000
}
```

**响应:**
```json
{
  "code": 0,
  "msg": "Allocated segment: 1 to 10000",
  "data": {
    "start": 1,
    "end": 10000
  }
}
```

**使用示例 (Python requests):**

```python
import requests

response = requests.post('http://localhost:5801/api/segment/allocate', json={
    'system_code': 'my_system',
    'db_name': 'my_database',
    'table_name': 'users',
    'field_name': 'id',
    'segment_count': 10000
})

data = response.json()
if data['code'] == 0:
    start = data['data']['start']
    end = data['data']['end']
    print(f"Allocated IDs: {start} to {end}")
```

**使用示例 (Python 客户端库 - 推荐):**

为了更方便的集成,使用官方 Python 客户端库 `kxy-open-id-client`:

```bash
# 安装客户端
cd ../kxy-open-id-client
pip install -e .
```

```python
from kxy_open_id_client import SegmentClient

# 创建客户端
client = SegmentClient(base_url="http://localhost:5801")

# 分配段
segment = client.allocate_segment(
    system_code="my_system",
    db_name="my_database",
    table_name="users",
    field_name="id",
    segment_count=10000
)

print(f"Allocated IDs: {segment.start} to {segment.end}")
```

查看 [kxy-open-id-client](../kxy-open-id-client/README.md) 获取完整文档。

## API 端点

### 认证 (无需认证)

- `GET /api/auth/check-init` - 检查系统是否已初始化
- `POST /api/auth/init-user` - 使用管理员用户初始化系统
- `POST /api/auth/login` - 登录并获取 JWT 令牌

### 数据库管理 (需要认证)

- `GET /api/database/list` - 获取所有数据库配置
- `POST /api/database/add` - 添加新数据库配置
- `GET /api/database/{guid}` - 获取单个数据库配置
- `PUT /api/database/{guid}` - 更新数据库配置
- `DELETE /api/database/{guid}` - 删除数据库配置
- `POST /api/database/initialize/{guid}` - 初始化数据库
- `POST /api/database/{guid}/add-config` - 添加自定义段配置
- `GET /api/database/{guid}/discovered-tables` - 获取发现的新表

### 段分配 (无需认证)

- `POST /api/segment/allocate` - 分配 ID 段

## Redis 键结构

```
kxy:id:db_config:{guid}                          → 数据库配置 (JSON)
kxy:id:segment:{system}:{db}:{table}:{field}     → 当前最大 ID (整数)
kxy:id:discovered_tables:{guid}                  → 已发现表的集合
kxy:id:system:init                               → 如已初始化则为 "1"
kxy:id:system:username                           → 管理员用户名
kxy:id:system:password                           → 哈希密码
```

## 后台扫描器

后台扫描器每 60 秒运行一次:
1. 扫描所有配置的数据库
2. 检测具有数字主键的新表
3. 将它们存储在 `kxy:id:discovered_tables:{guid}` 中
4. 需要通过 "初始化" 按钮手动批准

## 安全考虑

1. **密码哈希**: 使用 bcrypt 存储密码
2. **JWT 令牌**: 24 小时后过期 (可配置)
3. **HTTPS**: 生产环境使用 HTTPS
4. **数据库凭据**: 存储在 Redis 中 (考虑静态加密)
5. **JWT 密钥**: 生产环境更改默认密钥

## 故障排除

### Redis 连接错误

```
Failed to connect to Redis: [Errno 111] Connection refused
```

**解决方案:** 确保 Redis 正在运行,并且可以在配置的主机/端口访问。

### 数据库连接错误

```
Failed to initialize database: ...
```

**解决方案:**
- 验证数据库凭据
- 检查网络连接
- 确保已安装数据库驱动

### 前端 401 错误

**解决方案:**
- 令牌已过期 - 重新登录
- 检查令牌是否存储在 localStorage 中
- 验证后端 JWT_SECRET_KEY 匹配

## 开发

### 项目结构

```
kxy-open-id/
├── app/                      # 后端
│   ├── models/              # Pydantic 模型
│   ├── services/            # 业务逻辑
│   ├── routers/             # API 端点
│   ├── utils/               # 工具
│   ├── config.py            # 配置
│   ├── redis_client.py      # Redis 单例
│   └── main.py              # FastAPI 应用
├── frontend/                # 前端
│   └── src/
│       ├── views/           # 页面
│       ├── components/      # 组件
│       ├── router/          # Vue Router
│       └── utils/           # Axios 配置
├── requirements.txt         # Python 依赖
└── README.md               # 本文件
```

### 运行测试

```bash
# 后端测试 (待实现)
pytest

# 前端测试 (待实现)
cd frontend && npm test
```

## 许可证

专有 - 驿氪 (Ezr) 内部使用

## 支持

如有问题或疑问,请联系开发团队。
