import os
from dotenv import load_dotenv

# 加载 .env 文件中的环境变量
load_dotenv()

# API配置
API_URL = "https://api.pipecdn.app/api/points"
# Token配置 - 支持动态扩展用户数量
TOKENS_CONFIG = [
    {
        'name': str(i), 
        'token': os.getenv(f'USER{i}_TOKEN')
    } 
    for i in range(1, 11)  # 修改这里的数字来增减用户数量
]
# Webhook配置
WEBHOOK_URL = os.getenv('WEBHOOK_URL')

# 应用名称
APP_NAME = 'PipeCDN'

# 代理配置
PROXY_URL = 'http://localhost:7890'
USE_PROXY = False
ALWAYS_NOTIFY = True
SHOW_DETAIL = True
# 时间配置
INTERVAL = 28800  # 8小时检查一次
TIME_OFFSET = 0 

