#!/bin/bash
set -e

echo "=========================================="
echo "  PC Info Record - Django Application"
echo "=========================================="

# 等待 PostgreSQL 就绪
echo ""
echo "⏳ Waiting for PostgreSQL..."
attempt=0
max_attempts=30

while ! nc -z $DB_HOST $DB_PORT; do
  attempt=$((attempt + 1))
  if [ $attempt -ge $max_attempts ]; then
    echo "❌ Failed to connect to PostgreSQL after $max_attempts attempts"
    exit 1
  fi
  echo "   Attempt $attempt/$max_attempts - PostgreSQL is unavailable, sleeping..."
  sleep 2
done

echo "✅ PostgreSQL is ready!"

# 运行数据库迁移
echo ""
echo "🔄 Running database migrations..."
python manage.py migrate --noinput

if [ $? -eq 0 ]; then
  echo "✅ Migrations completed successfully"
else
  echo "❌ Migrations failed"
  exit 1
fi

# 收集静态文件
echo ""
echo "📦 Collecting static files..."
python manage.py collectstatic --noinput --clear

if [ $? -eq 0 ]; then
  echo "✅ Static files collected successfully"
else
  echo "❌ Failed to collect static files"
  exit 1
fi

# 检查是否需要创建超级用户（仅在开发环境）
if [ "$DEBUG" = "True" ] || [ "$DEBUG" = "true" ]; then
  echo ""
  echo "🔐 Checking for superuser..."
  python manage.py shell << END
from django.contrib.auth import get_user_model
User = get_user_model()
if not User.objects.filter(username='admin').exists():
    print('ℹ️  No superuser found. You can create one with: python manage.py createsuperuser')
else:
    print('✅ Superuser already exists')
END
fi

echo ""
echo "=========================================="
echo "🚀 Starting application..."
echo "=========================================="
echo ""

# 执行传入的命令
exec "$@"

