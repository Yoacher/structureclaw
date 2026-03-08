# StructureClaw

> 开源建筑结构分析与设计平台原型，包含 Web 前端、Node.js API 和 Python 分析引擎。

## 当前状态

这个仓库目前已经整理成可运行的多服务原型，包含：

- `frontend`: Next.js 14 前端
- `backend`: Fastify + Prisma + Redis/Postgres 接入的 API 服务
- `core`: FastAPI 结构分析引擎
- `docker-compose.yml`: 编排数据库、缓存、前后端和 Nginx

目前更接近“可运行的项目骨架”而不是完整产品，部分接口是可用的最小实现，用于保证工程链路能跑通。

## 技术架构

```text
Browser
  -> Next.js frontend (:3000)
  -> Fastify backend (:8000)
  -> FastAPI analysis engine (:8001)
  -> PostgreSQL / Redis
  -> Nginx reverse proxy (Docker only)
```

## 目录结构

```text
structureclaw/
├── backend/                 # Fastify API + Prisma
├── core/                    # FastAPI 分析引擎
├── frontend/                # Next.js 前端
├── docker/                  # Nginx 配置
├── docs/                    # 预留文档目录
├── plugins/                 # 预留插件目录
├── services/                # 预留微服务目录
├── tests/                   # 预留测试目录
├── .env.example             # Docker Compose 用环境变量示例
├── Makefile                 # 常用开发命令
└── docker-compose.yml
```

## 环境要求

推荐直接使用 Docker（门槛最低）：

- Docker Engine / Docker Desktop
- Docker Compose v2

本地源码开发（非 Docker）时需要：

- Node.js >= 18
- `uv`（推荐，用于自动创建 Python 3.11 环境）
- Python >= 3.10（未使用 `uv` 时）
- PostgreSQL >= 14（必须）
- Redis >= 7（可选，不启用时自动降级内存缓存）

## 快速开始

### 先做自检

第一次打开仓库，先跑：

```bash
make check-startup
```

它会检查：

- backend 编译、lint、Prisma schema
- frontend 类型检查、lint
- core 是否能导入并完成一次简化分析

说明：

- `frontend build` 也会被执行，但仅作为可选项
- 如果看到 `EXDEV`，通常是当前文件系统挂载方式导致的 Next.js 生产构建问题，不影响 `next dev`

### 方式一：本地源码启动（推荐给新手）

推荐直接使用 `uv`，它会自动创建 `core/.venv` 的 Python 3.11 环境：

```bash
make local-up-uv
```

如果需要完整分析依赖：

```bash
make local-up-full-uv
```

停止服务：

```bash
make local-down
```

查看状态：

```bash
make local-status
```

启动后访问：

- Web: `http://localhost:3000`
- API: `http://localhost:8000`
- API Docs: `http://localhost:8000/docs`
- Analysis Engine: `http://localhost:8001`

`make local-up-uv` 会自动：

- 补齐缺失的环境变量文件
- 安装前后端依赖
- 创建 `core/.venv`
- 启动 `postgres` 和 `redis`（Docker）
- 初始化数据库
- 启动 frontend、backend、core

如果本机没有 `uv`，再退回传统方式：

```bash
make local-up
```

### 方式二：Docker Compose

适合想直接起完整容器栈的情况：

```bash
cp .env.example .env
make up
```

### 方式三：手动分步启动

1. 安装前后端依赖：

```bash
make install
```

2. 准备后端环境变量：

```bash
cp backend/.env.example backend/.env
```

3. 启动数据库和 Redis：

```bash
make db-up
```

4. 初始化数据库结构和种子数据：

```bash
make db-init
```

5. 准备 Python 分析引擎环境：

轻量模式，仅用于本地跑通接口和简化分析：

```bash
make setup-core-lite-uv
```

传统 `venv` 写法：

```bash
make setup-core-lite
```

完整模式，安装全部分析依赖：

```bash
make setup-core-full-uv
```

传统 `venv` 写法：

```bash
make setup-core-full
```

6. 分别启动三个服务：

```bash
make dev-backend
```

```bash
make dev-frontend
```

```bash
make dev-core-lite
```

如果你装的是完整依赖，也可以使用：

```bash
make dev-core-full
```

## 最常用命令

```bash
make check-startup
make local-up-uv
make local-down
make local-status
```

## 环境变量

### 根目录 `.env`

用于 `docker compose`：

```bash
OPENAI_API_KEY=
```

### `backend/.env`

复制自 `backend/.env.example`，主要字段：

- `DATABASE_URL`
- `REDIS_URL`
- `JWT_SECRET`
- `ANALYSIS_ENGINE_URL`
- `OPENAI_API_KEY`

说明：

- `OPENAI_API_KEY` 是可选的，未配置时聊天接口自动降级提示
- `REDIS_URL=disabled` 表示禁用 Redis，后端自动降级为内存缓存

### Prisma 初始化

后端现在已经包含：

- `backend/prisma/migrations/20260308000100_init/migration.sql`
- `backend/prisma/seed.ts`

常用命令：

```bash
npm run db:validate --prefix backend
npm run db:deploy --prefix backend
npm run db:seed --prefix backend
npm run db:init --prefix backend
```

### `frontend/.env.local`

可参考 `frontend/.env.example`：

```bash
NEXT_PUBLIC_API_URL=http://localhost:8000
```

## 已验证的运行状态

2026-03-08 在当前环境已验证：

- 后端可成功编译
- 后端 lint 可运行
- 后端测试命令可运行（当前无测试用例）
- Prisma schema 校验通过
- 前端类型检查通过
- 前端 lint 通过
- `uv 0.10.8` 可创建 Python 3.11 环境
- `core` 可在 lite 依赖下导入并执行简化静力分析
- `make check-startup` 可通过

说明：

- 在当前机器上 Docker daemon 无访问权限，因此未能在本机完成 `make local-up` 的全链路实启；如你的环境 Docker 可用，该流程应可直接跑通。
- 前端 `next build` 在当前文件系统上触发 `EXDEV`（跨设备 rename）错误；这通常与宿主文件系统挂载方式有关，不影响 `next dev` 本地开发启动。
- 当前沙箱不允许本地监听端口，因此这里未直接完成 `uvicorn` 端口绑定验证；已通过导入和分析调用确认 `core` 进程本身可启动。

## 当前已实现的主要接口

### Backend

- `GET /health`
- `GET /docs`
- `GET /api/v1`
- `GET /api/v1/users/*`
- `GET /api/v1/projects/*`
- `GET /api/v1/skills/*`
- `GET /api/v1/community/*`
- `GET /api/v1/analysis/*`

### Core

- `GET /`
- `GET /health`
- `POST /analyze`
- `POST /code-check`
- `POST /design/beam`
- `POST /design/column`

## 已知说明

- 当前部分后端业务实现属于“最小可运行版本”，用于确保启动链路、数据流和接口结构可用
- 如果未配置 Redis，后端会使用内存缓存降级模式
- `core/requirements.txt` 包含较重的工程分析依赖，首次安装可能较慢
- `core/requirements-lite.txt` 适合本地快速起服务，但不代表具备完整分析能力
- 对新手来说，最省事的路径是先 `make check-startup`，再 `make local-up-uv`

## 后续建议

适合下一步继续完善的方向：

1. 为后端补充 Prisma migration 和初始化 seed
2. 为主要 API 增加自动化测试
3. 给前端补更多真实页面，而不仅是首页
4. 把当前最小实现逐步替换成真实业务逻辑

## 许可证

本项目采用 MIT 许可证，详见 `LICENSE`。
