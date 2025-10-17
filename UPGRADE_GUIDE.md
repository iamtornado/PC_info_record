# 升级指南

本文档说明如何从旧版本升级到最新版本。

---

## 升级到 v1.0.4

**发布日期**: 2025-10-17

### 🎯 重要变更

此版本修复了关键的数据库迁移问题，包含**数据库架构变更**，升级时需要特别注意。

### 📋 变更摘要

#### 数据库架构变更
- ✅ 删除了 `computers_department` 表
- ✅ 删除了 `computers_employee` 表
- ✅ `computers_computer` 表新增字段：
  - `user_name` (VARCHAR 100)
  - `computer_name` (VARCHAR 100)
  - `execution_log` (TEXT, nullable)
  - `log_size` (INTEGER, default 0)
  - `error_log` (TEXT, nullable)
  - `has_errors` (BOOLEAN, default False, indexed)
- ✅ `asset_code` 从 `UNIQUE` 改为 `INDEX`（支持历史记录）

#### 配置变更
- ✅ 更新 Docker Compose 使用具体版本号（v1.0.4）而非 `latest`
- ✅ 改进 `.env.example` 的 DEBUG 模式说明
- ✅ 优化 Admin 后台分页设置

---

### 🚀 升级步骤

#### 方式 1：Docker Hub 部署（推荐）

**适用于**：使用 Docker Compose 从 Docker Hub 拉取镜像的生产环境

```bash
# 1. 备份数据库（重要！）
docker compose exec db pg_dump -U postgres pc_info_record > backup_$(date +%Y%m%d_%H%M%S).sql

# 2. 进入项目目录
cd /home/ubuntu/PC_info_record

# 3. 拉取最新代码
git pull origin main

# 4. 更新配置文件（如果有本地修改）
# 检查 .env 文件，确保所有必需的环境变量都已设置

# 5. 拉取新镜像
docker compose pull

# 6. 停止并重新创建容器
docker compose up -d

# 7. 应用数据库迁移（关键步骤！）
docker compose exec web python manage.py migrate

# 8. 验证迁移状态
docker compose exec web python manage.py showmigrations computers

# 9. 重启容器以确保所有更改生效
docker compose restart web

# 10. 检查应用状态
docker compose ps
docker compose logs -f web  # 查看日志
```

#### 方式 2：本地构建部署

**适用于**：使用本地 Dockerfile 构建的开发或自定义环境

```bash
# 1. 备份数据库
docker compose exec db pg_dump -U postgres pc_info_record > backup_$(date +%Y%m%d_%H%M%S).sql

# 2. 拉取最新代码
git pull origin main

# 3. 重新构建镜像
docker compose build --no-cache

# 4. 重启服务
docker compose down
docker compose up -d

# 5. 应用迁移
docker compose exec web python manage.py migrate

# 6. 验证
docker compose exec web python manage.py showmigrations
```

#### 方式 3：非 Docker 环境

**适用于**：直接在服务器上运行的环境

```bash
# 1. 备份数据库
pg_dump -U postgres pc_info_record > backup_$(date +%Y%m%d_%H%M%S).sql

# 2. 拉取最新代码
git pull origin main

# 3. 更新依赖
uv sync  # 或 pip install -r requirements.txt

# 4. 应用迁移
python manage.py migrate

# 5. 收集静态文件
python manage.py collectstatic --noinput

# 6. 重启服务
sudo systemctl restart gunicorn  # 或您使用的服务管理器
```

---

### ✅ 升级验证

升级完成后，请执行以下验证：

#### 1. 检查迁移状态
```bash
docker compose exec web python manage.py showmigrations computers
```

**期望输出**：
```
computers
 [X] 0001_initial
 [X] 0002_auto_20251011_1006
 [X] 0003_remove_employee_department_remove_computer_employee_and_more
```

#### 2. 检查数据库表结构
```bash
docker compose exec db psql -U postgres -d pc_info_record -c "\d computers_computer"
```

应该能看到所有新字段：`user_name`, `computer_name`, `execution_log` 等

#### 3. 测试功能
- ✅ 访问 Admin 后台并添加一条记录
- ✅ 使用 LDAP 账号登录
- ✅ 从客户端调用 API 上传数据
- ✅ 查看计算机列表和详情

#### 4. 检查日志
```bash
docker compose logs -f web
```

确保没有错误信息。

---

### 🔄 回滚步骤

如果升级后出现问题，可以回滚到之前的版本：

```bash
# 1. 停止服务
docker compose down

# 2. 恢复数据库（如果做了架构变更）
docker compose up -d db
docker compose exec -T db psql -U postgres -d pc_info_record < backup_YYYYMMDD_HHMMSS.sql

# 3. 回退到旧版本
git checkout v1.0.3  # 或其他版本标签

# 4. 更新镜像版本（如果使用 Docker Hub）
# 编辑 docker-compose.yml，将镜像改为：
# image: tornadoami/pc-info-record:v1.0.3

# 5. 重新启动
docker compose up -d

# 6. 回退迁移（如果需要）
docker compose exec web python manage.py migrate computers 0002
```

---

### 📝 注意事项

#### 数据迁移注意事项
- ⚠️ 旧的 `Department` 和 `Employee` 数据将被删除
- ⚠️ 如果有重要数据，请在升级前导出备份
- ⚠️ `asset_code` 不再是唯一约束，允许重复记录（历史版本）

#### 配置注意事项
- ⚠️ 生产环境必须设置 `DEBUG=False`
- ⚠️ 确保 `ALLOWED_HOSTS` 包含所有访问域名/IP
- ⚠️ `SECRET_KEY` 必须保持不变，否则会话将失效

#### Docker 注意事项
- ⚠️ 使用 `docker compose pull` 前建议先备份
- ⚠️ 使用 `docker compose down -v` 会删除所有数据，慎用
- ⚠️ 生产环境建议使用具体版本号而非 `latest`

---

### 🆘 故障排查

#### 问题 1：迁移失败
**症状**：`python manage.py migrate` 报错

**解决**：
```bash
# 1. 检查数据库连接
docker compose exec db psql -U postgres -d pc_info_record -c "SELECT version();"

# 2. 查看迁移状态
docker compose exec web python manage.py showmigrations

# 3. 手动运行特定迁移
docker compose exec web python manage.py migrate computers 0003

# 4. 查看详细错误
docker compose logs web
```

#### 问题 2：字段不存在错误
**症状**：`column "user_name" does not exist`

**原因**：迁移未应用

**解决**：
```bash
docker compose exec web python manage.py migrate
docker compose restart web
```

#### 问题 3：无法访问 Admin
**症状**：Admin 页面 404 或 500 错误

**解决**：
```bash
# 1. 收集静态文件
docker compose exec web python manage.py collectstatic --noinput

# 2. 检查容器状态
docker compose ps

# 3. 重启所有服务
docker compose restart
```

---

### 📞 获取帮助

如果遇到问题：

1. 查看日志：`docker compose logs -f web`
2. 检查 [PROBLEM_SOLVED_SUMMARY.md](PROBLEM_SOLVED_SUMMARY.md) 中的类似问题
3. 查看 [README.md](README.md) 的故障排查章节
4. 提交 GitHub Issue

---

**最后更新**：2025-10-17  
**当前版本**：v1.0.4  
**上一版本**：v1.0.3

