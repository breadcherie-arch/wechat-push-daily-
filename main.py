import requests
import datetime
import random
import json
import os
from typing import Optional, Dict, List

# ========== 配置区 (请修改为你的配置) ==========
# 企业微信配置
CORP_ID = os.getenv("ww501bda5f38352e79", "你的企业ID")
AGENT_ID = os.getenv("1000002", "你的应用AgentId")
AGENT_SECRET = os.getenv("iyYfsscluT0XBcVMZpFOSZhw0mCoxk_gTudgf1PGeCg", "你的应用Secret")
TO_USER = "@all"  # 发送给所有人，或指定成员如"ZhangSan"

# API配置
DEEPSEEK_API_KEY = os.getenv("sk-b577b49ba9204af8a1865d31958d87d7", "你的DeepSeek_API_Key")

#天气api配置
OPENWEATHER_API_KEY = os.getenv("141785f0e77812755c9480d53959081a","你的openweathermap_API_KEY")

#双城市配置
CITIES = [
    {"query": "Kumamoto,JP", "name": "日本熊本", "emoji": "🇯🇵"},
    {"query": "Guangzhou,CN", "name": "广东广州", "emoji": "🇨🇳"}
]

# 纪念日配置 (修改为你的纪念日)
ANNIVERSARIES = [
    {"name": "第一次相遇", "date": "2026-02-04"},
]

# ========== 双城市天气模块 ==========
def get_dual_city_weather() -> str:
    """同时获取熊本和广州的天气"""
    if not OPENWEATHER_API_KEY or OPENWEATHER_API_KEY == "你的OpenWeatherMap_API_Key":
        return get_local_dual_weather_fallback()
    
    weather_results = []
    
    for city in CITIES:
        weather = get_single_city_weather(city["query"], city["name"], city["emoji"])
        weather_results.append(weather)
    
    return "\n".join(weather_results)

def get_single_city_weather(city_query: str, city_name: str, city_emoji: str) -> str:
    """获取单个城市的天气"""
    try:
        url = "https://api.openweathermap.org/data/2.5/weather"
        params = {
            "q": city_query,
            "appid": OPENWEATHER_API_KEY,
            "units": "metric",  # 摄氏度
            "lang": "zh_cn"     # 中文
        }
        
        response = requests.get(url, params=params, timeout=10)
        data = response.json()
        
        if response.status_code == 200:
            # 解析数据
            main_data = data["main"]
            weather_data = data["weather"][0]
            wind_data = data.get("wind", {})
            
            temp = main_data["temp"]
            feels_like = main_data["feels_like"]
            humidity = main_data["humidity"]
            description = weather_data["description"]
            wind_speed = wind_data.get("speed", 0)
            
            # 天气图标映射
            weather_icons = {
                "01d": "☀️", "01n": "🌙",
                "02d": "⛅", "02n": "⛅",
                "03d": "☁️", "03n": "☁️",
                "04d": "☁️", "04n": "☁️",
                "09d": "🌧️", "09n": "🌧️",
                "10d": "🌦️", "10n": "🌧️",
                "11d": "⛈️", "11n": "⛈️",
                "13d": "❄️", "13n": "❄️",
                "50d": "🌫️", "50n": "🌫️",
            }
            
            icon_code = weather_data.get("icon", "01d")
            weather_emoji = weather_icons.get(icon_code, "🌤️")
            
            # 构建天气字符串
            return f"{city_emoji} {city_name}: {weather_emoji} {description} {temp:.1f}°C"
            
        else:
            return get_single_city_fallback(city_name, city_emoji)
            
    except Exception as e:
        print(f"{city_name}天气获取异常: {e}")
        return get_single_city_fallback(city_name, city_emoji)

def get_single_city_fallback(city_name: str, city_emoji: str) -> str:
    """单个城市天气备用数据"""
    # 根据不同城市生成不同的备用天气
    if "熊本" in city_name:
        # 日本熊本的典型天气
        weather_options = [
            ("晴", "☀️", 22, 65),
            ("多云", "⛅", 20, 70),
            ("小雨", "🌦️", 18, 85),
            ("阴", "☁️", 19, 75),
            ("阵雨", "🌧️", 21, 80)
        ]
    else:
        # 广州的典型天气
        weather_options = [
            ("晴", "☀️", 28, 70),
            ("多云", "⛅", 26, 75),
            ("雷阵雨", "⛈️", 24, 90),
            ("阴", "☁️", 25, 80),
            ("大雨", "🌧️", 23, 95)
        ]
    
    description, emoji, temp, humidity = random.choice(weather_options)
    return f"{city_emoji} {city_name}: {emoji} {description} {temp}°C (备用数据)"

def get_local_dual_weather_fallback() -> str:
    """双城市本地备用天气数据"""
    kumamoto = f"🇯🇵 日本熊本: ☀️ 晴 22°C (备用数据)"
    guangzhou = f"🇨🇳 广东广州: ☀️ 晴 28°C (备用数据)"
    return f"{kumamoto}\n{guangzhou}"


# ========== 纪念日模块（更新版本） ==========
def calculate_anniversaries() -> str:
    """计算纪念日距离今天的天数 - 专为第一次相遇纪念日设计"""
    today = datetime.date.today()
    
    if not ANNIVERSARIES:
        return "📅 今天没有特殊纪念日"
    
    # 只处理第一个纪念日（可以扩展为多个）
    ann = ANNIVERSARIES[0]
    
    try:
        # 解析纪念日日期
        anniversary_date = datetime.datetime.strptime(ann["date"], "%Y-%m-%d").date()
        
        # 计算距今多少天
        days_passed = (today - anniversary_date).days
        
        # 计算距离下一次纪念日还有多少天（基于周年）
        years_passed = today.year - anniversary_date.year
        
        # 下一个周年日期
        next_anniversary = anniversary_date.replace(year=today.year)
        
        # 如果今年的纪念日已经过去，计算明年的
        if today > next_anniversary:
            next_anniversary = next_anniversary.replace(year=today.year + 1)
            years_passed = years_passed + 1
        
        days_until_next = (next_anniversary - today).days
        
        # 根据天数生成不同的消息
        if days_passed == 0:
            return f"🎉 今天是【{ann['name']}】！缘分开始的时刻！✨"
        elif days_passed > 0:
            # 已经过去的天数
            if days_passed == 1:
                return f"📅 昨天是我们【{ann['name']}】的日子，美好的开始！"
            elif days_passed <= 7:
                return f"📅 我们已经相遇 {days_passed} 天了，每一天都值得纪念！"
            elif days_passed <= 30:
                return f"📅 我们已经相遇 {days_passed} 天了，时间过得真快！"
            else:
                # 计算周数和月数
                weeks = days_passed // 7
                months = days_passed // 30
                
                if days_until_next == 0:
                    # 正好是周年纪念日
                    if years_passed == 1:
                        return f"🎉 今天是我们相遇 {years_passed} 周年纪念日！❤️"
                    else:
                        return f"🎉 今天是我们相遇 {years_passed} 周年纪念日！🎊"
                elif days_until_next == 1:
                    return f"📅 明天就是我们相遇 {years_passed} 周年纪念日啦！准备好惊喜了吗？"
                elif days_until_next <= 7:
                    return f"📅 距离我们相遇 {years_passed} 周年还有 {days_until_next} 天，期待！"
                elif days_until_next <= 30:
                    return f"📅 距离我们相遇 {years_passed} 周年还有 {days_until_next} 天"
                else:
                    months_until = days_until_next // 30
                    return f"📅 已经相遇 {years_passed} 年，距离 {years_passed+1} 周年还有 {months_until} 个月"
        else:
            # 纪念日在未来（还没发生）
            days_until = abs(days_passed)
            if days_until <= 7:
                return f"📅 距离我们【{ann['name']}】还有 {days_until} 天，倒计时开始！"
            elif days_until <= 30:
                return f"📅 距离我们【{ann['name']}】还有 {days_until} 天"
            else:
                months_until = days_until // 30
                return f"📅 距离我们【{ann['name']}】还有 {months_until} 个月"
                
    except Exception as e:
        print(f"纪念日计算错误: {e}")
        return "📅 哎呀出错了，没关系，出错也不想搞了！代码太难了！"

# ========== AI情话生成模块 ==========
def generate_love_cheer() -> str:
    """生成情侣加油打气情话（尝试API，失败则用本地库）"""
    
    # 尝试DeepSeek API
    ai_line = try_deepseek_api()
    if ai_line and len(ai_line) > 5:
        return ai_line
    
    
    # 使用本地库
    return get_local_cheer_line()

def try_deepseek_api() -> Optional[str]:
    """尝试使用DeepSeek API"""
    if not DEEPSEEK_API_KEY or DEEPSEEK_API_KEY == "你的DeepSeek_API_Key":
        return None
    
    try:
        url = "https://api.deepseek.com/chat/completions"
        headers = {
            "Authorization": f"Bearer {DEEPSEEK_API_KEY}",
            "Content-Type": "application/json"
        }
        
        # 随机选择不同主题
        themes = [
            "为今天的工作加油",
            "鼓励对方坚持努力",
            "表达无条件的支持",
            "温馨的日常关心",
            "对未来一起努力的期待",
            "提醒对方照顾自己",
            "为对方的小进步喝彩",
            "传递温暖和力量"
        ]
        
        data = {
            "model": "deepseek-chat",
            "messages": [
                {
                    "role": "system",
                    "content": "你是温暖贴心的恋人，专门为伴侣创作甜甜的情话。要求：1.简短有力，15-25字；2.温暖积极有爱；3.避免陈词滥调，不要油腻；4.结合日常场景；5.直接使用'你''我们'等人称；6.每次完全不同。示例风格：'今天也要加油哦，我的能量都分你一半。'"
                },
                {
                    "role": "user",
                    "content": f"请创作一句情侣间思念的甜甜的情话，主题：{random.choice(themes)}，直接输出句子不要解释。"
                }
            ],
            "temperature": 0.9,
            "max_tokens": 50
        }
        
        response = requests.post(url, headers=headers, json=data, timeout=8)
        
        if response.status_code == 200:
            result = response.json()
            text = result["choices"][0]["message"]["content"].strip()
            text = text.strip('"').strip("'").strip()
            
            # 验证结果质量
            if (5 < len(text) < 35 and 
                "情话" not in text and 
                "示例" not in text and
                "要求" not in text):
                return text
    except Exception as e:
        print(f"DeepSeek API错误: {e}")
    
    return None


def get_local_cheer_line() -> str:
    """本地备用鼓励情话库"""
    local_lines = [
        "今天也要加油哦，我的能量都分你一半。💪",
        "不管遇到什么，我都在你身后支持你。",
        "慢慢来，我们的未来还很长呢～",
        "你努力的样子，就是我喜欢的模样。",
        "累了就休息会，我的肩膀随时待命。",
        "每一天的你，都比昨天更让我心动。",
        "别太拼，你的健康最重要。❤️",
        "我们的爱情，就是彼此最好的充电宝。",
        "小事你搞定，大事有我在。",
        "今天也要做最闪亮的自己呀！✨",
        "你的进步，我看在眼里甜在心里。",
        "一起加油，为了我们的小未来。",
        "你是我的骄傲，永远都是。",
        "别怕失败，我陪你从头再来。",
        "今天工作辛苦啦，晚上给你按摩～",
        "你的笑容，就是我每天的动力源。",
        "一步一步来，我陪你走每一步。",
        "在我眼里，你永远是最棒的。",
        "累了就靠着我，我一直都在。",
        "今天的任务：好好爱自己，我监督！",
        "你是最棒的，我相信你！",
        "无论结果如何，你都是我的英雄。",
        "慢慢来，我陪你一起成长。",
        "你的努力，时间都会看见。",
        "今天也辛苦啦，晚上好好犒劳自己！",
        "记得多喝水，按时吃饭哦～",
        "你认真的样子特别迷人！",
        "我们的未来，一起努力～",
        "别给自己太大压力，你已经很棒了！",
        "加油，我在终点等你。"
    ]
    
    # 根据星期几和日期选择，增加随机性但又有一定规律
    now = datetime.datetime.now()
    weekday = now.weekday()
    day_of_month = now.day
    
    # 使用日期计算索引，确保每天不同但每月循环
    index = (weekday * 7 + day_of_month) % len(local_lines)
    
    # 10%概率随机选择，增加惊喜感
    if random.random() < 0.1:
        return random.choice(local_lines)
    
    return local_lines[index]

# ========== 游戏新闻模块 ==========
def get_gaming_news() -> str:
    """获取游戏热点新闻"""
    
    # 尝试小黑盒API
    news = try_heiyou_api()
    if news:
        return news
    
    # 尝试备用API
    news = try_backup_gaming_api()
    if news:
        return news
    
    # 使用本地库
    return get_local_gaming_news()

def try_heiyou_api() -> Optional[str]:
    """尝试小黑盒API"""
    try:
        url = "https://api.xiaoheihe.cn/v3/bbs/app/api/web/index/feed"
        params = {
            "limit": 10,
            "offset": 0,
            "catid": "new",
            "os_type": "web"
        }
        
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
            "Referer": "https://www.xiaoheihe.cn/"
        }
        
        response = requests.get(url, params=params, headers=headers, timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            articles = data.get("result", {}).get("articles", [])
            
            if articles:
                # 过滤并随机选择
                valid_articles = []
                for article in articles[:10]:  # 只看前10条
                    title = article.get("title", "")
                    # 过滤太短或包含特定关键词的标题
                    if (len(title) > 8 and 
                        "抽奖" not in title and 
                        "活动" not in title and
                        len(title) < 50):
                        valid_articles.append(article)
                
                if valid_articles:
                    article = random.choice(valid_articles)
                    title = article.get("title", "")
                    
                    # 清理标题
                    title = title.replace("&quot;", '"').replace("&#039;", "'")
                    
                    # 截取合适长度
                    if len(title) > 40:
                        title = title[:37] + "..."
                    
                    return f"🎮 {title}"
    except Exception as e:
        print(f"小黑盒API错误: {e}")
    
    return None

    
    # 根据日期选择
    today = datetime.datetime.now()
    index = (today.day * today.month) % len(gaming_news)
    
    return f"🎮 {gaming_news[index]}"

# ========== 消息发送模块 ==========
def get_access_token() -> Optional[str]:
    """获取企业微信访问令牌"""
    try:
        url = f"https://qyapi.weixin.qq.com/cgi-bin/gettoken?corpid={CORP_ID}&corpsecret={AGENT_SECRET}"
        response = requests.get(url, timeout=5)
        
        if response.status_code == 200:
            data = response.json()
            return data.get("access_token")
        else:
            print(f"获取token失败: {response.status_code}")
            return None
    except Exception as e:
        print(f"获取token错误: {e}")
        return None

def send_wechat_message(content: str) -> bool:
    """发送消息到企业微信应用"""
    try:
        token = get_access_token()
        if not token:
            print("获取企业微信token失败")
            return False
        
        url = f"https://qyapi.weixin.qq.com/cgi-bin/message/send?access_token={token}"
        
        data = {
            "touser": TO_USER,
            "msgtype": "markdown",
            "agentid": int(AGENT_ID),
            "markdown": {"content": content},
            "safe": 0
        }
        
        response = requests.post(url, json=data, timeout=10)
        result = response.json()
        
        if result.get("errcode") == 0:
            print("企业微信消息发送成功！")
            return True
        else:
            print(f"企业微信消息发送失败: {result}")
            return False
            
    except Exception as e:
        print(f"发送消息错误: {e}")
        return False

# ========== 主函数模块 ==========
def format_daily_message() -> str:
    """生成完整的每日推送消息"""
    now = datetime.datetime.now()
    
    # 获取各个部分
    date_str = now.strftime("%Y年%m月%d日 星期") + ["一", "二", "三", "四", "五", "六", "日"][now.weekday()]
    
    # 早上还是晚上问候
    hour = now.hour
    if 5 <= hour < 12:
        greeting = "🌅 清晨问候"
    elif 12 <= hour < 18:
        greeting = "☀️ 午后时光"
    else:
        greeting = "🌙 夜晚安好"
    
    weather_str = get_weather()
    anniversary_str = calculate_anniversaries()
    cheer_line = generate_love_cheer()
    gaming_news = get_gaming_news()
    
    # 添加随机emoji装饰
    emojis = ["✨", "💖", "🌟", "🎈", "🌸", "🍀", "🎉", "💕", "🌼", "⭐"]
    random_emoji = random.choice(emojis)
    
    # 构建Markdown格式消息
    message = f"""{greeting} | {date_str} {random_emoji}

🌤️ 今日天气
{weather_str}

📅 纪念日提醒
{anniversary_str}

💌 每日加油
{cheer_line}

{gaming_news}

---
⏰ 推送时间 {now.strftime('%H:%M:%S')}
💝 美好的一天，从我的问候开始"""
    
    return message

def main_handler(event=None, context=None):
    """主函数 - 云函数入口"""
    print("=" * 50)
    print(f"开始执行每日推送任务 - {datetime.datetime.now()}")
    print("=" * 50)
    
    try:
        # 生成消息
        print("1. 生成每日消息...")
        message = format_daily_message()
        print("✓ 消息生成成功")
        print(f"消息长度: {len(message)} 字符")
        print(f"消息预览:\n{message[:200]}...")
        
        # 发送消息
        print("\n2. 发送到企业微信...")
        success = send_wechat_message(message)
        
        if success:
            print("✓ 推送发送成功！")
            return {
                "statusCode": 200,
                "body": json.dumps({
                    "status": "success",
                    "message": "推送发送成功",
                    "timestamp": datetime.datetime.now().isoformat()
                })
            }
        else:
            print("✗ 推送发送失败")
            return {
                "statusCode": 500,
                "body": json.dumps({
                    "status": "error",
                    "message": "企业微信发送失败",
                    "timestamp": datetime.datetime.now().isoformat()
                })
            }
            
    except Exception as e:
        print(f"✗ 推送任务异常: {str(e)}")
        
        # 尝试发送错误通知
        try:
            error_msg = f"""⚠️ 每日推送生成失败

错误信息: {str(e)[:100]}
时间: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

请检查配置或查看日志。"""
            send_wechat_message(error_msg)
        except:
            pass
            
        return {
            "statusCode": 500,
            "body": json.dumps({
                "status": "error",
                "message": str(e),
                "timestamp": datetime.datetime.now().isoformat()
            })
        }

def local_test():
    """本地测试函数"""
    print("=" * 50)
    print("本地测试模式")
    print("=" * 50)
    
    print("\n1. 测试天气获取...")
    weather = get_weather()
    print(f"天气: {weather}")
    
    print("\n2. 测试纪念日计算...")
    anniversaries = calculate_anniversaries()
    print(f"纪念日: {anniversaries}")
    
    print("\n3. 测试AI情话生成...")
    for i in range(3):
        cheer = generate_love_cheer()
        print(f"情话{i+1}: {cheer}")
    
    print("\n4. 测试游戏新闻获取...")
    gaming_news = get_gaming_news()
    print(f"游戏新闻: {gaming_news}")
    
    print("\n5. 生成完整消息...")
    message = format_daily_message()
    print(f"\n完整消息:\n{message}")
    
    # 询问是否发送测试消息
    send_test = input("\n是否发送测试消息到企业微信？(y/n): ")
    if send_test.lower() == 'y':
        success = send_wechat_message(f"🔧 测试消息\n\n{message}")
        if success:
            print("✓ 测试消息发送成功！")
        else:
            print("✗ 测试消息发送失败")

# ========== 执行入口 ==========
if __name__ == "__main__":
    # 本地运行测试
    local_test()
else:
    # 云函数环境
    pass
