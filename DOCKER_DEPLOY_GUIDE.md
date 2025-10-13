# Docker 快速部署指南

## 🚀 3分钟快速部署

### 前置要求
- Docker 20.10+
- Docker Compose v2.0+

### 步骤 1: 克隆项目

```bash
git clone https://github.com/iamtornado/PC_info_record.git
cd PC_info_record
```

### 步骤 2: 配置环境变量（重要！）

```bash
# 复制环境变量模板
cp .env.example .env

# 编辑配置文件
nano .env  # 或使用 vim、vi 等编辑器
```

### 必须修改的配置项：

```bash
# 1. Django 密钥（必须修改为随机值）
SECRET_KEY=your-secret-key-here-CHANGE-THIS

# 2. 数据库密码（必须修改）
DB_PASSWORD=your-strong-password-here

# 3. 调试模式（生产环境必须为 False）
DEBUG=False

# 4. 数据库主机（Docker 环境使用 db）
DB_HOST=db

# 5. 允许访问的主机名（添加你的域名或IP）
ALLOWED_HOSTS=yourdomain.com,www.yourdomain.com,localhost,127.0.0.1,your_server_ip
```

### 生成 Django SECRET_KEY：

```bash
# 方法1: 使用 Python
python3 -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"

# 方法2: 使用 openssl
openssl rand -base64 50
```

### 步骤 3: 启动服务

```bash
cd docker
docker compose up -d
```

Docker Compose 会自动：
- ✅ 从 Docker Hub 拉取 `tornadoami/pc-info-record:v1.0.0` 镜像
- ✅ 启动 PostgreSQL 数据库
- ✅ 运行数据库迁移
- ✅ 启动 Django 应用（Gunicorn）
- ✅ 启动 Nginx 反向代理

### 步骤 4: 创建管理员账号

```bash
docker compose exec web python manage.py createsuperuser
```

按提示输入用户名、邮箱和密码。

### 步骤 5: 访问应用

- **主页**: http://your_server_ip 或 http://yourdomain.com
- **管理后台**: http://your_server_ip/admin/
- **API**: http://your_server_ip/api/

---

## 📋 常见问题排查

### 问题 1: 密码认证失败

**错误信息**:
```
psycopg2.OperationalError: password authentication failed for user "postgres"
```

**原因**: `.env` 文件配置不正确或未加载

**解决方案**:
```bash
# 1. 确保 .env 文件存在
ls -la .env

# 2. 检查 .env 文件中的数据库密码
cat .env | grep DB_PASSWORD

# 3. 确保 DB_HOST=db（不是 localhost）
cat .env | grep DB_HOST

# 4. 停止并删除旧容器和数据卷（会删除数据！）
cd docker
docker compose down -v

# 5. 重新启动
docker compose up -d
```

### 问题 2: Web 服务一直重启

```bash
# 查看 web 服务日志
cd docker
docker compose logs web

# 常见原因:
# - 数据库连接失败 → 检查 .env 配置
# - SECRET_KEY 未设置 → 检查 .env 中的 SECRET_KEY
# - ALLOWED_HOSTS 配置错误 → 添加你的域名/IP
```

### 问题 3: 无法访问网站（502 Bad Gateway）

```bash
# 1. 检查服务状态
docker compose ps

# 2. 确保所有服务都是 healthy 状态
# 如果 web 服务不健康，查看日志:
docker compose logs web

# 3. 检查 Nginx 日志
docker compose logs nginx
```

---

## 🔧 管理命令

### 服务管理

```bash
cd docker

# 启动服务
docker compose up -d

# 停止服务
docker compose down

# 重启服务
docker compose restart

# 查看服务状态
docker compose ps

# 查看日志
docker compose logs -f web     # Web 服务日志
docker compose logs -f db      # 数据库日志
docker compose logs -f nginx   # Nginx 日志
```

### 数据库管理

```bash
cd docker

# 运行迁移
docker compose exec web python manage.py migrate

# 创建超级用户
docker compose exec web python manage.py createsuperuser

# 进入数据库 shell
docker compose exec db psql -U postgres -d pc_info_record

# 备份数据库
docker compose exec db pg_dump -U postgres pc_info_record > backup_$(date +%Y%m%d).sql

# 恢复数据库
cat backup.sql | docker compose exec -T db psql -U postgres -d pc_info_record
```

### 应用管理

```bash
cd docker

# Django shell
docker compose exec web python manage.py shell

# 收集静态文件（通常不需要，镜像已包含）
docker compose exec web python manage.py collectstatic --noinput

# 测试 LDAP 连接
docker compose exec web python test_ldap_connection.py
```

---

## 🔄 更新应用

当有新版本发布时：

```bash
cd docker

# 1. 拉取新镜像
docker compose pull

# 2. 停止旧容器
docker compose down

# 3. 启动新版本
docker compose up -d

# 4. 查看日志确认启动成功
docker compose logs -f web
```

---

## 🔒 生产环境安全检查清单

- [ ] 修改了 `SECRET_KEY` 为随机值
- [ ] 修改了 `DB_PASSWORD` 为强密码
- [ ] 设置 `DEBUG=False`
- [ ] 配置了正确的 `ALLOWED_HOSTS`
- [ ] 配置了防火墙，只开放 80 和 443 端口
- [ ] 配置了 SSL/TLS 证书（推荐使用 Let's Encrypt）
- [ ] 配置了数据库定期备份
- [ ] 配置了日志轮转和监控

---

## 📞 获取帮助

如果遇到问题：
1. 查看服务日志: `docker compose logs -f`
2. 检查 [README.md](README.md) 中的故障排除部分
3. 提交 Issue 到 GitHub

---

**祝部署顺利！** 🎉

