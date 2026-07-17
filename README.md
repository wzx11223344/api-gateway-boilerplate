# API Gateway Boilerplate

![CI](https://github.com/your-org/api-gateway-boilerplate/actions/workflows/ci.yml/badge.svg)

一个生产级的 FastAPI 后端脚手架项目，包含 JWT 认证、用户管理、Item CRUD、异步数据库操作和 Docker 部署支持。

---

## 目录

- [快速开始](#快速开始)
- [项目结构](#项目结构)
- [API 端点](#api-端点)
- [测试](#测试)
- [Docker 部署](#docker-部署)
- [环境变量](#环境变量)

---

## 快速开始

### 1. 克隆项目

```bash
git clone https://github.com/your-org/api-gateway-boilerplate.git
cd api-gateway-boilerplate
```

### 2. 创建虚拟环境

```bash
python -m venv .venv
source .venv/bin/activate   # Linux / macOS
.venv\Scripts\activate      # Windows
```

### 3. 安装依赖

```bash
pip install -r requirements.txt
```

### 4. 配置环境变量

复制 `.env.example` 为 `.env` 并填写配置（默认使用 SQLite，可直接启动）：

```bash
# .env
DATABASE_URL=sqlite+aiosqlite:///./app.db
SECRET_KEY=your-secret-key-here
```

### 5. 启动开发服务器

```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

访问 http://localhost:8000/docs 查看 Swagger 文档。

---

## 项目结构

```
api-gateway-boilerplate/
├── app/
│   ├── main.py           # FastAPI 应用入口
│   ├── config.py         # 配置管理 (pydantic-settings)
│   ├── models/           # SQLAlchemy ORM 模型
│   ├── schemas/          # Pydantic v2 请求/响应模型
│   ├── routers/          # API 路由 (auth / users / items)
│   ├── services/         # 业务逻辑层 (JWT, CRUD)
│   └── utils/            # 工具 (database, dependencies)
├── tests/                # pytest 测试
├── alembic/              # 数据库迁移目录
├── Dockerfile            # 多阶段 Docker 构建
├── docker-compose.yml    # App + PostgreSQL 编排
└── requirements.txt      # Python 依赖
```

---

## API 端点

| Method | Path                     | Auth | 说明             |
|--------|--------------------------|------|------------------|
| GET    | `/health`                | No   | 健康检查         |
| POST   | `/api/v1/auth/register`  | No   | 用户注册         |
| POST   | `/api/v1/auth/login`     | No   | 用户登录（JWT）  |
| POST   | `/api/v1/auth/refresh`   | Yes  | 刷新 Token       |
| GET    | `/api/v1/auth/me`        | Yes  | 当前用户信息     |
| GET    | `/api/v1/users/`         | No   | 用户列表（分页） |
| GET    | `/api/v1/users/{id}`     | No   | 查询单个用户     |
| PUT    | `/api/v1/users/{id}`     | Yes  | 更新用户         |
| DELETE | `/api/v1/users/{id}`     | Yes  | 删除用户         |
| POST   | `/api/v1/items`          | Yes  | 创建 Item        |
| GET    | `/api/v1/items`          | No   | Item 列表（分页）|
| GET    | `/api/v1/items/{id}`     | No   | 查询 Item        |
| PUT    | `/api/v1/items/{id}`     | Yes  | 更新 Item        |
| DELETE | `/api/v1/items/{id}`     | Yes  | 删除 Item        |

---

## 测试

```bash
pytest --verbose --tb=short -x
```

测试使用内存 SQLite 数据库，无需外部依赖。

---

## Docker 部署

### 使用 SQLite（快速启动）

```bash
docker build -t api-gateway .
docker run -p 8000:8000 api-gateway
```

### 使用 PostgreSQL（生产推荐）

```bash
docker-compose up --build -d
```

首次启动前设置 `.env`：

```
DATABASE_URL=postgresql+asyncpg://app_user:app_password@postgres:5432/api_gateway
```

---

## 环境变量

| 变量名                    | 默认值        | 说明                   |
|---------------------------|---------------|------------------------|
| `DATABASE_URL`            | SQLite 内存   | 数据库连接字符串       |
| `SECRET_KEY`              | —             | JWT 签名密钥           |
| `ALGORITHM`               | `HS256`       | JWT 签名算法           |
| `ACCESS_TOKEN_EXPIRE_MINUTES` | `30`      | Token 过期时间（分钟） |
| `API_V1_PREFIX`           | `/api/v1`     | API 版本前缀           |

---

## 技术栈

- **Python 3.10+** — 语言
- **FastAPI** — Web 框架
- **SQLAlchemy 2.0** — ORM（异步）
- **Pydantic v2** — 数据验证
- **python-jose** — JWT
- **passlib + bcrypt** — 密码哈希
- **pytest + httpx** — 测试
- **Docker** — 容器化
