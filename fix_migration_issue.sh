#!/bin/bash
# 修复数据库迁移问题的脚本
# 在生产服务器 (10.65.37.238) 上运行

set -e

echo "========================================"
echo "  修复数据库迁移问题"
echo "========================================"
echo ""

# 确保在正确的目录
cd /home/ubuntu/PC_info_record

echo "1️⃣  检查当前迁移状态..."
docker compose exec web python manage.py showmigrations computers
echo ""

echo "2️⃣  查看 Computer 模型定义..."
docker compose exec web python manage.py shell -c "
from computers.models import Computer
print('Computer 模型字段:')
for field in Computer._meta.get_fields():
    print(f'  - {field.name}: {field.__class__.__name__}')
"
echo ""

echo "3️⃣  检查数据库表结构..."
docker compose exec db psql -U postgres -d pc_info_record -c "\d computers_computer" || echo "表可能不存在或有问题"
echo ""

echo "4️⃣  生成新的迁移文件..."
docker compose exec web python manage.py makemigrations
echo ""

echo "5️⃣  应用迁移..."
docker compose exec web python manage.py migrate
echo ""

echo "6️⃣  验证表结构..."
docker compose exec db psql -U postgres -d pc_info_record -c "\d computers_computer"
echo ""

echo "========================================"
echo "  ✅ 修复完成！"
echo "========================================"
echo ""
echo "现在可以测试："
echo "  1. 访问 http://10.65.37.238/admin/ 添加记录"
echo "  2. 测试 API 调用"
echo ""

