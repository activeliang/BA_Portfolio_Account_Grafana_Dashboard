#!/bin/bash
# 创建日志文件以确保 tail 命令可以正常工作
touch /var/log/cron.log

cat >/app/docker/cron_task.sh<<EOF
#!/bin/bash
export \$(grep '^[^CRONTAB]' /app/vars.env | xargs)
/usr/local/bin/python /app/main.py >> /var/log/cron.log 2>&1
EOF

chmod +x /app/docker/cron_task.sh

# 创建一个 cron 任务
crontab -r
CURRENT_CRONTAB_SCHEDULE="$(grep '^CRONTAB_SCHEDULE=' /app/vars.env | cut -d '=' -f 2)"

(crontab -l 2>/dev/null; echo -e "${CURRENT_CRONTAB_SCHEDULE} /app/docker/cron_task.sh") | crontab -

# 启动 cron 服务
cron

# 保持容器运行
tail -f /var/log/cron.log



