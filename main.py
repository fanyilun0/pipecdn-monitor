import asyncio
import aiohttp
from datetime import datetime, timedelta
import random
import logging

# 导入配置
from config import (
    API_URL,  # 分数API
    WEBHOOK_URL, 
    PROXY_URL, 
    USE_PROXY, 
    INTERVAL, 
    TIME_OFFSET,
    ALWAYS_NOTIFY,
    APP_NAME,
    TOKENS_CONFIG
)

# 配置logging
def setup_logging():
    """配置日志格式和级别"""
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    return logging.getLogger(__name__)

logger = setup_logging()

# 随机延迟函数
async def random_delay():
    """生成随机延迟时间（10-20秒）"""
    delay = random.uniform(10, 20)
    logger.info(f"等待 {delay:.2f} 秒...")
    await asyncio.sleep(delay)

async def fetch_points(session, api_url, api_token):
    """获取分数数据"""
    headers = {
        "accept": "application/json",
        "authorization": f"Bearer {api_token}",
        "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
    }
    
    try:
        async with session.get(api_url, headers=headers, ssl=False) as response:
            if response.status == 200:
                data = await response.json()
                return data.get('points', 0)
            else:
                logger.error(f"获取分数失败: {response.status}")
                return None
    except Exception as e:
        logger.error(f"获取分数出错: {str(e)}")
        return None

def build_message(tokens_points):
    """构建包含所有token分数的通知消息"""
    adjusted_time = datetime.now() + timedelta(hours=TIME_OFFSET)
    timestamp = adjusted_time.strftime('%Y-%m-%d %H:%M:%S')
    
    message = f"🔍 【{APP_NAME} 状态报告】\n⏰ 时间: {timestamp}\n\n"
    
    for token_name, points in tokens_points.items():
        message += f"👤 账户: {token_name}\n💰 当前分数: {points}\n\n"
    
    return message.strip()

async def send_message_async(webhook_url, message_content, use_proxy, proxy_url):
    """发送消息到webhook"""
    headers = {'Content-Type': 'application/json'}
    payload = {
        "msgtype": "text",
        "text": {
            "content": message_content
        }
    }
    
    proxy = proxy_url if use_proxy else None
    async with aiohttp.ClientSession() as session:
        async with session.post(webhook_url, json=payload, headers=headers, proxy=proxy) as response:
            if response.status == 200:
                logger.info("消息发送成功!")
            else:
                logger.error(f"发送消息失败: {response.status}")

async def monitor_single_token(session, token_config):
    """获取单个token的分数"""
    try:
        logger.info(f"开始检查Token: {token_config['name']}")
        
        points = await fetch_points(session, API_URL, token_config['token'])
        logger.info(f"获取到分数: {points}")
        
        return token_config['name'], points
        
    except Exception as e:
        logger.error(f"❌ 监控Token {token_config['name']} 时出错: {str(e)}")
        return token_config['name'], None
    finally:
        logger.info(f"检查完成: {token_config['name']}")

async def monitor_points(interval, webhook_url, use_proxy, proxy_url):
    """主监控函数"""
    iteration = 1
    while True:
        try:
            logger.info(f"\n开始第 {iteration} 轮检查...")
            tokens_points = {}
            
            async with aiohttp.ClientSession() as session:
                for token_config in TOKENS_CONFIG:
                    token_name, points = await monitor_single_token(session, token_config)
                    if points is not None:
                        tokens_points[token_name] = points
                    await random_delay()
            
            if tokens_points and ALWAYS_NOTIFY:
                message = build_message(tokens_points)
                await send_message_async(webhook_url, message, use_proxy, proxy_url)
                logger.info("✅ 消息发送成功")
            
            logger.info(f"第 {iteration} 轮检查完成\n")
            iteration += 1
            
        except Exception as e:
            logger.error(f"监控过程出错: {str(e)}")
            await asyncio.sleep(5)
            continue
            
        await asyncio.sleep(interval)

if __name__ == "__main__":
    asyncio.run(monitor_points(
        interval=INTERVAL,
        webhook_url=WEBHOOK_URL,
        use_proxy=USE_PROXY,
        proxy_url=PROXY_URL
    ))