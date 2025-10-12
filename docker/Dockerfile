# 使用官方 Python 镜像
FROM python:3.11-slim

# 设置环境变量
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

# 设置工作目录
WORKDIR /app

# 安装系统依赖（包括 LDAP 编译所需的库）
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    netcat-traditional \
    libpq-dev \
    libldap2-dev \
    libsasl2-dev \
    libssl-dev \
    && rm -rf /var/lib/apt/lists/*

# 升级 pip
RUN pip install --upgrade pip

# 复制依赖文件
COPY requirements.txt pyproject.toml ./

# 安装 Python 依赖
RUN pip install --no-cache-dir -r requirements.txt

# 复制项目文件
COPY . .

# 复制 Docker 相关文件
COPY docker/entrypoint.sh /app/entrypoint.sh

# 创建必要的目录
RUN mkdir -p /app/logs /app/staticfiles /app/media

# 赋予启动脚本执行权限
RUN chmod +x /app/entrypoint.sh

# 创建非 root 用户
RUN useradd -m -u 1000 appuser && \
    chown -R appuser:appuser /app

USER appuser

# 暴露端口
EXPOSE 8000

# 入口脚本
ENTRYPOINT ["/app/entrypoint.sh"]

# 默认命令（可以在 docker-compose 中覆盖）
CMD ["gunicorn", "pc_info_record.wsgi:application", "--bind", "0.0.0.0:8000", "--workers", "4", "--timeout", "120", "--access-logfile", "-", "--error-logfile", "-"]

