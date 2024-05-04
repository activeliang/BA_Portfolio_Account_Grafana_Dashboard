# 使用官方 Python 镜像
FROM python:3.9-slim

# 安装 cron 和其他必需的包
RUN apt-get update && apt-get install -y cron

# 设置工作目录
WORKDIR /app

# 将 Python 脚本复制到容器中
COPY main.py .
COPY requirements.txt .

# 安装任何需要的依赖
RUN pip install -r requirements.txt

# 设置时区，如果你的脚本依赖于特定时区
ENV TZ=Asia/Shanghai

# 运行 cron 任务
# 这里我们使用 `entrypoint.sh` 来启动 cron 服务
COPY ./docker/entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh
ENTRYPOINT ["/entrypoint.sh"]
CMD ["cron", "-f"]
