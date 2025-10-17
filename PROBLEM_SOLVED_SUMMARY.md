# 问题解决总结 - 2025-10-17

## 🎯 问题概述

### 问题 1：LDAP 登录问题
**症状**：用户（bob, alice）使用 LDAP 账号登录后，被重定向回登录页面

**表面原因**：Session cookie 问题、CSRF token 问题

**真正原因**：旧的数据库状态/会话数据冲突

**解决方案**：
```bash
docker compose down -v  # 清除所有数据卷
docker compose up -d    # 重新创建干净环境
```

**结论**：代码本身没有问题，是数据状态问题。

---

### 问题 2：数据库迁移不同步（生产环境主要问题）
**症状**：
- Admin 后台添加记录报错：`column "user_name" does not exist`
- API 调用返回 500 Internal Server Error
- 日志显示：`Your models have changes that are not yet reflected in a migration`

**根本原因**：
- 旧迁移文件（0001_initial.py）创建的表结构包含 `Department` 和 `Employee` 模型
- 当前代码已简化模型，直接在 `Computer` 中存储 `user_name`, `computer_name` 等字段
- 缺少迁移文件来同步这些变化

**解决方案**：
```bash
# 在生产服务器上执行
cd /home/ubuntu/PC_info_record
docker compose exec web python manage.py makemigrations
docker compose exec web python manage.py migrate
docker compose restart web
```

**迁移内容**（0003）：
- ✅ 删除 `Department` 模型和表
- ✅ 删除 `Employee` 模型和表
- ✅ 删除 `Computer.employee` 外键字段
- ✅ 添加 `Computer.user_name` 字段
- ✅ 添加 `Computer.computer_name` 字段
- ✅ 添加 `Computer.execution_log` 字段（Base64 编码的完整日志）
- ✅ 添加 `Computer.log_size` 字段
- ✅ 添加 `Computer.error_log` 字段
- ✅ 添加 `Computer.has_errors` 字段（带索引）
- ✅ 修改 `Computer.asset_code` 从 `unique=True` 改为 `db_index=True`

---

## 📊 修改的文件

### 新增文件
1. **computers/migrations/0003_remove_employee_department_remove_computer_employee_and_more.py**
   - 数据库迁移文件
   - 同步模型变化到数据库表结构

### 代码状态
- ✅ 模型代码（computers/models.py）：正常
- ✅ 视图代码（computers/views.py, api/views.py）：正常
- ✅ 配置文件（settings.py）：正常
- ✅ LDAP 认证配置：正常

---

## 🧪 验证结果

### 生产环境（10.65.37.238）
- ✅ LDAP 用户可以正常登录
- ✅ Admin 后台可以添加/编辑记录
- ✅ API 端点可以正常接收数据
- ✅ 数据库表结构与模型同步

### 测试项目
1. ✅ LDAP 登录（bob, alice 等用户）
2. ✅ Admin 后台操作
3. ✅ API 调用（从 Windows 客户端）
4. ✅ 日志记录（execution_log 字段）

---

## 💡 经验教训

### 1. LDAP 登录问题的教训
- 问题不一定是代码本身
- 旧的 session/cookie/数据库状态可能导致问题
- `docker compose down -v` 是重置环境的好方法
- 浏览器缓存也可能是问题根源

### 2. 数据库迁移的教训
- **迁移文件必须与代码同步**
- 修改模型后必须立即运行 `makemigrations`
- 部署到生产环境前要确保迁移文件已提交
- 日志中的警告信息很重要：`Your models have changes...`

### 3. 调试流程
1. ✅ 查看详细日志（docker compose logs）
2. ✅ 检查数据库表结构（\d table_name）
3. ✅ 验证迁移状态（showmigrations）
4. ✅ 对比模型定义和实际表结构

---

## 📋 最佳实践

### 开发环境
```bash
# 修改模型后立即执行
python manage.py makemigrations
python manage.py migrate
git add computers/migrations/
git commit -m "更新数据库迁移"
```

### 部署到生产环境
```bash
# 1. 拉取最新代码
git pull origin main

# 2. 检查是否有新迁移
docker compose exec web python manage.py showmigrations

# 3. 应用迁移
docker compose exec web python manage.py migrate

# 4. 重启容器（如果需要）
docker compose restart web
```

### 遇到问题时
```bash
# 1. 查看日志
docker compose logs -f web

# 2. 检查数据库连接
docker compose exec db psql -U postgres -d pc_info_record

# 3. 检查表结构
\d computers_computer

# 4. 检查迁移状态
docker compose exec web python manage.py showmigrations
```

---

## 🔄 未来改进

### 1. CI/CD 集成
- [ ] 自动检测未应用的迁移
- [ ] 部署前自动运行迁移
- [ ] 迁移失败时自动回滚

### 2. 监控和告警
- [ ] 添加数据库健康检查
- [ ] 监控 API 错误率
- [ ] LDAP 认证失败告警

### 3. 文档完善
- [x] 添加故障排查指南到 README
- [ ] 创建运维手册
- [ ] 记录常见问题和解决方案

---

## ✅ 当前状态

### 开发环境
- 状态：正常
- 迁移：已同步
- 代码：最新

### 生产环境（10.65.37.238）
- 状态：✅ 正常运行
- 迁移：✅ 已应用
- 功能：✅ 全部可用
  - LDAP 登录正常
  - Admin 后台正常
  - API 调用正常

---

## 📞 后续支持

如果遇到问题，请检查：
1. Docker 容器状态：`docker compose ps`
2. 应用日志：`docker compose logs -f web`
3. 数据库日志：`docker compose logs -f db`
4. 迁移状态：`docker compose exec web python manage.py showmigrations`

---

**问题解决日期**：2025-10-17  
**服务器**：10.65.37.238  
**状态**：🟢 已解决  
**版本**：v1.0.4

