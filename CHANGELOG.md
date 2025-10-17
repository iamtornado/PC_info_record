# 更新日志

## [v1.0.4] - 2025-10-17

### 🐛 重要修复
- ✅ **数据库迁移同步问题**: 修复了模型和数据库表结构不一致的问题
  - 症状：Admin 后台添加记录报错 `column "user_name" does not exist`
  - 症状：API 调用返回 500 错误
  - 原因：旧迁移文件创建的表结构与当前模型不匹配
  - 解决：生成并应用 0003 迁移文件
  
- ✅ **LDAP 登录循环问题**: 修复了用户登录后被重定向回登录页的问题
  - 原因：旧的数据库/会话状态冲突
  - 解决：清理环境数据（docker compose down -v）
  
### 🔧 技术改进
- ✅ **数据库模型简化**:
  - 删除了 `Department` 和 `Employee` 模型
  - 直接在 `Computer` 模型中存储 `user_name` 和 `computer_name`
  - 添加了完整的日志字段（execution_log, error_log）
  - 将 `asset_code` 从 unique 改为 db_index（支持历史记录）

- ✅ **迁移管理**:
  - 添加了迁移 0003：同步模型变化到数据库
  - 改进了生产环境部署流程
  - 添加了迁移状态检查工具

### 📋 数据库变更
- ✅ 删除表：`computers_department`, `computers_employee`
- ✅ 新增字段：`user_name`, `computer_name`, `execution_log`, `log_size`, `error_log`, `has_errors`
- ✅ 修改字段：`asset_code` (unique → db_index)

### 📚 文档更新
- ✅ 添加了完整的问题解决总结（PROBLEM_SOLVED_SUMMARY.md）
- ✅ 更新了 README 故障排查章节
- ✅ 添加了迁移问题的诊断和解决方案

### 🚀 部署说明
**重要**：升级到此版本需要应用数据库迁移：
```bash
docker compose exec web python manage.py migrate
docker compose restart web
```

---

## [v1.0.3] - 2025-10-16

### 🎉 新功能
- ✅ 完整的中文字符支持
- ✅ 增强的 PowerShell 脚本调试功能
- ✅ 详细的 API 调用日志记录

### 🐛 修复
- ✅ **中文字符显示问题**: 修复了操作系统版本中中文字符显示为问号的问题
- ✅ **HTTP 编码问题**: 修复了 PowerShell HTTP 请求的编码问题
- ✅ **空字符处理**: 修复了日志中的空字符（\x00）导致的验证错误
- ✅ **JSON 解析错误**: 修复了大型日志文件的 JSON 传输问题
- ✅ **无人值守环境**: 修复了无人值守环境中的文件锁定问题

### 🔧 技术改进
- ✅ **PowerShell 脚本增强**:
  - 添加了详细的系统信息获取调试
  - 增强了 JSON 编码处理
  - 添加了中文字符检测和修复机制
  - 分离了 API 调用日志记录
  - 改进了错误处理和诊断功能

- ✅ **Django API 增强**:
  - 添加了详细的请求日志记录
  - 增强了 Base64 解码处理
  - 添加了空字符过滤
  - 改进了错误响应处理

- ✅ **Docker 配置优化**:
  - 更新了所有依赖包版本
  - 优化了容器构建过程
  - 改进了健康检查配置

### 📦 依赖更新
- Django: 5.2.7
- Django REST Framework: 3.16.1
- django-auth-ldap: 5.2.0
- python-ldap: 3.4.5
- gunicorn: 23.0.0
- psycopg2-binary: 2.9.11

### 🚀 部署
- Docker 镜像: `tornadoami/pc-info-record:v1.0.3`
- 同时提供 `latest` 标签
- 完整的向后兼容性

---

## [v1.0.2] - 2025-10-15

### 🐛 修复
- ✅ 修复了 Base64 编码的日志传输问题
- ✅ 修复了空字符串验证错误
- ✅ 改进了无人值守环境的稳定性

### 🔧 技术改进
- ✅ 增强了 PowerShell 脚本的错误处理
- ✅ 改进了 Django API 的数据验证
- ✅ 优化了 Docker 容器配置

---

## [v1.0.1] - 2025-10-14

### 🎉 新功能
- ✅ 添加了 LDAP/Active Directory 认证支持
- ✅ 实现了完整的 REST API 接口
- ✅ 添加了 Docker 容器化部署

### 🔧 技术改进
- ✅ 集成了 django-auth-ldap
- ✅ 配置了 PostgreSQL 数据库
- ✅ 添加了 Nginx 反向代理

---

## [v1.0.0] - 2025-10-13

### 🎉 初始版本
- ✅ 基础的 PC 信息记录功能
- ✅ Windows PowerShell 客户端
- ✅ Django Web 界面
- ✅ 基本的 CRUD 操作
