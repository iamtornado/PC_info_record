# PC信息记录系统

一个基于 Django 的企业级 PC 信息记录和管理系统，集成 LDAP/Active Directory 认证，支持自动收集和管理 Windows 计算机信息。

## ✨ 功能特性

- 🖥️ **自动信息收集**：通过客户端自动收集 Windows 计算机的硬件、系统信息
- 📊 **数据管理**：提供 Web 界面进行数据查看、搜索、筛选
- 🔐 **LDAP/AD 认证**：集成企业 Active Directory，统一用户认证
- 🔍 **高级搜索**：支持多条件组合搜索和筛选
- 📡 **REST API**：提供完整的 REST API 接口
- 🔧 **管理后台**：功能强大的 Django Admin 后台
- 📱 **响应式设计**：支持桌面和移动设备访问
- 🐳 **Docker 支持**：完整的容器化部署方案，已发布到 Docker Hub

## 🛠️ 技术栈

### 后端
- **框架**: Django 5.2.7
- **数据库**: PostgreSQL 17.6
- **API**: Django REST Framework 3.16+
- **认证**: django-auth-ldap + python-ldap
- **应用服务器**: Gunicorn 23.0 (生产环境)
- **Web 服务器**: Nginx (生产环境)

### 前端
- Django 模板引擎
- 原生 CSS + 响应式设计

### 客户端
- PowerShell 5.1+ (Windows 信息采集)

### 开发工具
- **包管理**: uv (开发环境) / pip (Docker)
- **容器化**: Docker + Docker Compose
- **镜像仓库**: Docker Hub ([tornadoami/pc-info-record](https://hub.docker.com/r/tornadoami/pc-info-record)) - v1.0.4
- **最新版本**: v1.0.4 (2025-10-17) - 修复数据库迁移同步问题
- **数据库工具**: pgcli

## 📁 项目结构

```
PC_info_record/
├── docker/                      # Docker 配置文件目录
│   ├── Dockerfile               # 容器镜像配置
│   ├── .dockerignore            # 构建忽略文件
│   ├── entrypoint.sh            # 容器启动脚本
│   └── nginx.conf               # Nginx 配置
│
├── docker-compose.yml           # 生产环境 Docker 编排 ⭐
├── docker-compose.dev.yml       # 开发环境 Docker 编排
├── .env                         # 环境变量配置（不提交Git）
├── .env.example                 # 环境变量模板
│
├── pc_info_record/              # Django 项目配置
│   ├── settings.py              # 设置（含 LDAP 配置）
│   ├── urls.py
│   └── wsgi.py
│
├── computers/                   # 计算机管理应用
│   ├── models.py                # 数据模型
│   ├── views.py
│   ├── admin.py
│   └── migrations/
│
├── api/                         # REST API
│   ├── views.py
│   └── urls.py
│
├── client/                      # Windows 客户端
│   └── collect_computer_info.ps1  # PowerShell 信息采集脚本
│
├── templates/                   # Django 模板
├── static/                      # 静态文件
├── logs/                        # 日志文件（开发环境）
│
├── requirements.txt             # Python 依赖列表
├── pyproject.toml               # 项目配置
├── manage.py                    # Django 管理脚本
├── test_ldap_connection.py      # LDAP 测试工具
└── README.md                    # 本文件
```

## 🚀 快速开始

### 方式一：Docker Hub 快速部署（推荐）⭐⭐

**🎉 最快最简单的方式，无需构建镜像，3 分钟内启动完整系统！**

本项目已发布到 Docker Hub：[tornadoami/pc-info-record](https://hub.docker.com/r/tornadoami/pc-info-record)

```bash
# 1. 克隆项目（只需要配置文件）
git clone https://github.com/iamtornado/PC_info_record.git
cd PC_info_record

# 2. 配置环境变量
cp .env.example .env
nano .env  # 修改数据库密码、LDAP 配置、生产环境设置等

# 3. 启动服务（自动从 Docker Hub 拉取镜像）
docker compose up -d

# 4. 创建超级用户
docker compose exec web python manage.py createsuperuser

# 5. 访问应用
# 浏览器打开: http://your_server_ip_or_domain
```

**优势**：
- ✅ 无需本地构建，直接使用预构建镜像
- ✅ 更快的部署速度
- ✅ 节省磁盘空间和构建时间
- ✅ 确保使用经过测试的稳定版本

---

### 方式二：Docker 本地构建部署

如果需要修改代码或自定义构建：

```bash
# 1. 克隆项目
git clone https://github.com/iamtornado/PC_info_record.git
cd PC_info_record

# 2. 修改 docker-compose.yml，使用本地构建
nano docker-compose.yml
# 将 web 服务的 image: tornadoami/pc-info-record:v1.0.4 注释掉
# 取消注释 build 配置：
#   build:
#     context: .
#     dockerfile: docker/Dockerfile

# 3. 配置环境变量
cp .env.example .env
nano .env

# 4. 构建并启动
docker compose up -d --build

# 5. 创建超级用户
docker compose exec web python manage.py createsuperuser
```

---

### 方式三：本地开发环境

适合开发和调试。

#### 1. 环境准备

确保已安装：
- Python 3.11+
- PostgreSQL 17.6+
- uv (Python 包管理器)

#### 2. 安装 uv

```bash
# macOS/Linux
curl -LsSf https://astral.sh/uv/install.sh | sh

# Windows
powershell -c "irm https://astral.sh/uv/install.ps1 | iex"
```

#### 3. 克隆项目并安装依赖

```bash
git clone https://github.com/iamtornado/PC_info_record.git
cd PC_info_record

# 同步依赖（自动创建虚拟环境）
uv sync
```

#### 4. 配置环境变量

```bash
cp .env.example .env
nano .env  # 编辑配置
```

**必须配置**：
```env
# 数据库配置
DB_NAME=pc_info_record
DB_USER=postgres
DB_PASSWORD=your-password
DB_HOST=localhost
DB_PORT=5432

# LDAP 配置（如果使用 AD 认证）
LDAP_SERVER_URI=ldap://your-ldap-server:389
LDAP_BIND_DN=CN=service_account,OU=Users,DC=example,DC=com
LDAP_BIND_PASSWORD=your-ldap-password
LDAP_USER_BASE_DN=OU=Users,DC=example,DC=com
```

#### 5. 创建数据库

```bash
# 使用 pgcli 或 psql
createdb pc_info_record
```

#### 6. 运行迁移

```bash
# 运行数据库迁移
uv run python manage.py migrate

# 创建超级用户
uv run python manage.py createsuperuser
```

#### 7. 启动开发服务器

```bash
uv run python manage.py runserver
```

访问 http://localhost:8000

---

### 🧪 测试 LDAP 连接（可选）

```bash
# 本地开发
uv run python test_ldap_connection.py

# Docker 环境
docker compose exec -it web python test_ldap_connection.py
```

## 📖 使用说明

### Web 界面

**本地开发环境**：
- **管理后台**：http://localhost:8000/admin/
- **API 浏览器**：http://localhost:8000/api/

**Docker 生产环境**：
- **管理后台**：http://localhost/admin/
- **API 端点**：http://localhost/api/
- **健康检查**：http://localhost/health/

### 🔐 用户认证

系统支持两种认证方式：

1. **LDAP/AD 认证**（主要）
   - 使用企业域账号登录
   - 首次登录自动创建用户
   - 用户信息从 LDAP 同步

2. **Django 本地认证**（备用）
   - 超级用户账号
   - 用于管理和应急访问

### 📡 REST API

#### 提交计算机信息
```bash
POST http://localhost/api/computers/create/
Content-Type: application/json
X-CSRFToken: <token>

{
  "asset_code": "PC-001",
  "sn_code": "SN123456",
  "model": "Dell OptiPlex 7090",
  "device_type": "Desktop",
  "cpu_model": "Intel i7-11700",
  "memory_size": 16,
  "os_version": "Windows 11 Pro",
  "os_internal_version": "22H2",
  "user_name": "zhangsan",
  "computer_name": "DESKTOP-ABC123",
  "execution_log": "脚本执行日志...",
  "log_size": 1024,
  "error_log": "",
  "has_errors": false,
  "uploader": "robot"
}
```

**注意**: POST 请求需要 CSRF Token，可以从 `/login/` 页面获取。

#### 查询计算机列表
```bash
GET http://localhost/api/computers/
```

#### 获取单个计算机详情
```bash
GET http://localhost/api/computers/{id}/
```

#### 健康检查
```bash
GET http://localhost/health/
```

### 💻 Windows 客户端使用

系统提供 PowerShell 脚本，用于自动收集 Windows 计算机信息并提交到服务器。

#### 信息采集脚本

`collect_computer_info.ps1` - PowerShell 信息采集脚本

```powershell
# 进入客户端目录
cd client

# 运行采集脚本（带详细日志和验证）
.\collect_computer_info.ps1

# 自定义服务器地址
.\collect_computer_info.ps1 -ServerUrl "http://your-server-ip"
```

**功能特点**：
- ✅ 完整的信息收集（硬件、系统、用户信息）
- ✅ 本地备份（JSON 格式）
- ✅ 详细的执行步骤显示
- ✅ 自动获取 CSRF Token
- ✅ 自动上传到服务器 API
- ✅ 自动验证上传结果
- ✅ 适合手动运行、测试或计划任务

**收集的信息**：
- **基本信息**：资产编码、SN 序列号、设备型号、设备类型
- **硬件信息**：CPU 型号、内存大小
- **系统信息**：操作系统版本、内部版本号
- **用户信息**：用户名、计算机名
- **日志信息**：执行日志、错误日志

**部署方式**：
- 手动运行（管理员权限）
- Windows 任务计划程序（定期采集）
- 组策略登录脚本（域环境）
- 命令行参数支持自定义服务器地址

## 📋 数据模型

### Computer (计算机)

**基本信息**：
- `asset_code` - 资产编码（有索引）
- `sn_code` - SN 序列号
- `model` - 型号
- `device_type` - 设备类型

**硬件信息**：
- `cpu_model` - CPU 型号
- `memory_size` - 内存大小 (GB)

**系统信息**：
- `os_version` - 操作系统版本
- `os_internal_version` - 操作系统内部版本

**用户信息**：
- `user_name` - 用户名
- `computer_name` - 计算机名

**日志信息**：
- `execution_log` - PowerShell 脚本执行日志
- `log_size` - 日志大小（字节）
- `error_log` - 错误日志
- `has_errors` - 是否有错误（有索引）

**元数据**：
- `uploader` - 上传者（默认 "Robot"）
- `upload_time` - 上传时间（自动）
- `last_update` - 最后更新时间（自动）

## 🚢 生产环境部署

### Docker Hub 部署（推荐）⭐⭐

完整的生产级部署方案，包含 Nginx + Gunicorn + PostgreSQL。

**使用预构建镜像，无需本地编译！**

```bash
# 1. 下载配置文件
git clone https://github.com/iamtornado/PC_info_record.git
cd PC_info_record

# 2. 配置环境变量
cp .env.example .env
nano .env  # 修改为生产配置（重要：DEBUG=False, SECRET_KEY, DB_PASSWORD）

# 3. 启动服务（自动从 Docker Hub 拉取 tornadoami/pc-info-record:v1.0.4）
docker compose up -d

# 4. 创建超级用户
docker compose exec web python manage.py createsuperuser

# 访问: http://your_domain_or_ip
```

**技术架构**：
- ✅ Nginx - 反向代理 + 静态文件服务
- ✅ Gunicorn - WSGI 应用服务器（4 workers）
- ✅ PostgreSQL 17.6 - 数据库
- ✅ 健康检查 - 自动重启
- ✅ 日志管理 - Docker logs
- ✅ Docker Hub - 预构建镜像 (`tornadoami/pc-info-record`)

**镜像版本**：

- `tornadoami/pc-info-record:v1.0.4` - 最新稳定版（推荐，修复数据库迁移问题）⭐
- `tornadoami/pc-info-record:v1.0.3` - 稳定版本（含 Base64 日志支持和中文字符修复）
- `tornadoami/pc-info-record:latest` - 最新版本（自动跟踪 v1.0.4）

**更新镜像**：
```bash
docker compose pull      # 拉取最新镜像
docker compose up -d     # 重启服务应用新镜像
```

---


## 🔧 LDAP/Active Directory 配置

系统集成了企业 Active Directory 认证。配置方法：

### 1. 环境变量配置

在 `.env` 文件中配置：

```env
LDAP_SERVER_URI=ldap://your-ldap-server.com:389
LDAP_BIND_DN=CN=service_account,OU=ServiceAccounts,DC=example,DC=com
LDAP_BIND_PASSWORD=your-service-password
LDAP_USER_BASE_DN=OU=Users,DC=example,DC=com
```

### 2. 测试 LDAP 连接

```bash
# 本地环境
uv run python test_ldap_connection.py

# Docker 环境
docker compose exec -it web python test_ldap_connection.py
```

### 3. 用户属性映射

系统自动将 LDAP 属性映射到 Django 用户：
- `sAMAccountName` → `username`
- `givenName` → `first_name`
- `sn` → `last_name`
- `mail` → `email`

详细配置请查看 `pc_info_record/settings.py` 中的 LDAP 配置部分。

---

## 👨‍💻 开发指南

### 开发环境设置

```bash
# 安装开发依赖
uv sync --group dev

# 启动开发服务器
uv run python manage.py runserver

# 运行测试
uv run python manage.py test

# 创建迁移
uv run python manage.py makemigrations
```

### Docker 开发环境

支持代码热重载的开发环境（使用本地构建）：

```bash
docker compose -f docker-compose.dev.yml up
```

**说明**：
- `docker-compose.dev.yml` 使用本地构建，挂载代码目录
- 支持代码修改实时生效（热重载）
- 使用 Django runserver（开发模式）
- `docker-compose.yml` 使用 Docker Hub 预构建镜像（生产模式）

### 代码规范

- ✅ 遵循 PEP 8 代码风格
- ✅ 添加适当的注释和文档字符串
- ✅ 使用 Django 最佳实践
- ✅ 编写单元测试（推荐）

## 🆘 故障排除

### Docker 环境

```bash
# 查看服务状态
docker compose ps

# 查看日志
docker compose logs -f web

# 重启服务
docker compose restart web

# 完全重置（会删除数据）
docker compose down -v
docker compose up -d
```

### 本地开发环境

#### 1. 数据库连接失败
```bash
# 检查 PostgreSQL 服务
sudo systemctl status postgresql

# 测试连接
psql -U postgres -d pc_info_record
```

#### 2. LDAP 认证失败
```bash
# 运行 LDAP 测试工具
uv run python test_ldap_connection.py

# 检查配置
# - LDAP_SERVER_URI 是否正确
# - LDAP_BIND_DN 和密码是否正确
# - LDAP_USER_BASE_DN 是否正确
```

#### 3. 静态文件无法加载
```bash
# 开发环境（不需要 collectstatic）
DEBUG=True  # 确保 DEBUG 开启

# 生产环境
python manage.py collectstatic --noinput
```

#### 4. 系统依赖缺失（LDAP）
```bash
# Ubuntu/Debian
sudo apt-get install libldap2-dev libsasl2-dev libssl-dev

# 重新安装 Python 依赖
uv sync
```


## 🔧 常用命令

### Docker 环境

```bash
# 服务管理
docker compose up -d          # 启动
docker compose down           # 停止
docker compose restart        # 重启
docker compose ps             # 状态
docker compose logs -f web    # 日志

# 数据库管理
docker compose exec web python manage.py migrate
docker compose exec web python manage.py createsuperuser
docker compose exec db pg_dump -U postgres pc_info_record > backup.sql

# 应用管理
docker compose exec web python manage.py shell
docker compose exec -it web python test_ldap_connection.py
```

### 本地开发

```bash
# 启动开发服务器
uv run python manage.py runserver

# 数据库操作
uv run python manage.py makemigrations
uv run python manage.py migrate
uv run python manage.py createsuperuser

# Django shell
uv run python manage.py shell

# 测试 LDAP
uv run python test_ldap_connection.py
```

---

## 🤝 贡献指南

1. Fork 项目
2. 创建功能分支 (`git checkout -b feature/AmazingFeature`)
3. 提交更改 (`git commit -m 'Add some AmazingFeature'`)
4. 推送到分支 (`git push origin feature/AmazingFeature`)
5. 创建 Pull Request

---

## 📄 许可证

MIT License

---

## 💬 联系方式

如有问题或建议：
- 📧 提交 Issue
- 📝 查看文档
- 🔍 查看故障排查部分

---

## 🙏 致谢

- Django 社区
- PostgreSQL 团队
- Astral (uv 开发团队)
- 所有贡献者

---

**祝使用愉快！** 🎉
