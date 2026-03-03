import requests
import datetime
import random
import json
import os
import sys
import time
import hashlib
from urllib.parse import urlencode, urlparse, urlunparse, parse_qsl
from typing import Optional, Dict, List, Tuple

# ========== 配置区 (请修改为你的配置) ==========
# Server酱配置 - 支持两个SendKey，用逗号分隔
SERVERCHAN_SENDKEYS_STR = os.getenv("SERVERCHAN_SENDKEYS", "SCT316026Tl8kRVxrcgR4s4hlkxMQWmvcK,SCT316183TP3Wi6OZhBBqpd6EvqUu9jCHz")
# 将字符串转换为列表
SERVERCHAN_SENDKEYS = [key.strip() for key in SERVERCHAN_SENDKEYS_STR.split(",") if key.strip()]

# API配置
DEEPSEEK_API_KEY = os.getenv("DEEPSEEK_API_KEY", "sk-b577b49ba9204af8a1865d31958d87d7")
OPENWEATHER_API_KEY = os.getenv("OPENWEATHER_API_KEY", "141785f0e77812755c9480d53959081a")

# 双城市配置
CITIES = [
    {"query": "Kumamoto,JP", "name": "日本熊本", "emoji": "🇯🇵"},
    {"query": "Guangzhou,CN", "name": "广东广州", "emoji": "🇨🇳"}
]

# 纪念日配置
ANNIVERSARIES = [
    {"name": "第一次相遇", "date": "2026-02-04"},
]

# ========== 天气模块 ==========
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
            "units": "metric",
            "lang": "zh_cn"
        }
        
        response = requests.get(url, params=params, timeout=10)
        data = response.json()
        
        if response.status_code == 200:
            # 解析数据
            main_data = data["main"]
            weather_data = data["weather"][0]
            
            temp = main_data["temp"]
            description = weather_data["description"]
            
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
            
            return f"{city_emoji} {city_name}: {weather_emoji} {description} {temp:.1f}°C"
            
        else:
            return get_single_city_fallback(city_name, city_emoji)
            
    except Exception as e:
        print(f"{city_name}天气获取异常: {e}")
        return get_single_city_fallback(city_name, city_emoji)

def get_single_city_fallback(city_name: str, city_emoji: str) -> str:
    """单个城市天气备用数据"""
    if "熊本" in city_name:
        weather_options = [
            ("晴", "☀️", 22, 65),
            ("多云", "⛅", 20, 70),
            ("小雨", "🌦️", 18, 85),
        ]
    else:
        weather_options = [
            ("晴", "☀️", 28, 70),
            ("多云", "⛅", 26, 75),
            ("雷阵雨", "⛈️", 24, 90),
        ]
    
    description, emoji, temp, humidity = random.choice(weather_options)
    return f"{city_emoji} {city_name}: {emoji} {description} {temp}°C"

def get_local_dual_weather_fallback() -> str:
    """双城市本地备用天气数据"""
    kumamoto = f"🇯🇵 日本熊本: ☀️ 晴 22°C"
    guangzhou = f"🇨🇳 广东广州: ☀️ 晴 28°C"
    return f"{kumamoto}\n{guangzhou}"

# ========== 纪念日模块 ==========
def calculate_anniversaries() -> str:
    """计算纪念日距离今天的天数"""
    today = datetime.date.today()
    
    if not ANNIVERSARIES:
        return "📅 今天没有特殊纪念日"
    
    ann = ANNIVERSARIES[0]
    
    try:
        anniversary_date = datetime.datetime.strptime(ann["date"], "%Y-%m-%d").date()
        days_passed = (today - anniversary_date).days
        
        if days_passed == 0:
            return f"🎉 今天是【{ann['name']}】！缘分开始的时刻！✨"
        elif days_passed > 0:
            if days_passed == 1:
                return f"📅 昨天是我们【{ann['name']}】的日子，美好的开始！"
            elif days_passed <= 7:
                return f"📅 我们已经相遇 {days_passed} 天了，每一天都值得纪念！"
            elif days_passed <= 30:
                return f"📅 我们已经相遇 {days_passed} 天了，时间过得真快！"
            else:
                weeks = days_passed // 7
                months = days_passed // 30
                return f"📅 已经相遇 {days_passed} 天 ({weeks}周{months}月)"
        else:
            days_until = abs(days_passed)
            if days_until <= 7:
                return f"📅 距离我们【{ann['name']}】还有 {days_until} 天，倒计时开始！"
            else:
                months_until = days_until // 30
                return f"📅 距离我们【{ann['name']}】还有 {months_until} 个月"
                
    except Exception as e:
        print(f"纪念日计算错误: {e}")
        return "📅 纪念日计算出错"

# ========== AI情话生成模块 ==========
def generate_love_cheer() -> str:
    """生成情侣加油打气情话"""
    ai_line = try_deepseek_api()
    if ai_line and len(ai_line) > 5:
        return ai_line
    
    return get_local_cheer_line()

def try_deepseek_api() -> Optional[str]:
    """使用DeepSeek API"""
    if not DEEPSEEK_API_KEY or DEEPSEEK_API_KEY == "你的DeepSeek_API_Key":
        return None
    
    try:
        url = "https://api.deepseek.com/chat/completions"
        headers = {
            "Authorization": f"Bearer {DEEPSEEK_API_KEY}",
            "Content-Type": "application/json"
        }
        
        themes = [
            "为今天的工作加油",
            "鼓励对方坚持努力",
            "温馨的日常关心",
            "提醒对方照顾自己",
        ]
        
        data = {
            "model": "deepseek-chat",
            "messages": [
                {
                    "role": "system",
                    "content": "你是温暖贴心的恋人，专门为伴侣创作甜甜的情话。要求：1.简短有力，15-25字；2.温暖积极有爱；3.避免陈词滥调；4.直接使用'你''我们'等人称。"
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
            
            if 5 < len(text) < 35 and "情话" not in text:
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
    ]
    
    now = datetime.datetime.now()
    weekday = now.weekday()
    day_of_month = now.day
    index = (weekday * 7 + day_of_month) % len(local_lines)
    
    if random.random() < 0.1:
        return random.choice(local_lines)
    
    return local_lines[index]

# ========== 实时游戏新闻模块 ==========
def get_gaming_news() -> str:
    """获取实时游戏热点新闻 - 只使用实时API"""
    news_sources = [
        ("小黑盒API", try_heiyou_api),
        ("备用游戏API", try_backup_gaming_api),
        ("知乎游戏热榜", try_zhihu_gaming),
        ("B站游戏资讯", try_bilibili_gaming),
    ]
    
    for source_name, api_func in news_sources:
        print(f"尝试{source_name}...")
        try:
            news = api_func()
            if news and news.strip():
                print(f"✅ 成功从{source_name}获取新闻")
                return news
        except Exception as e:
            print(f"❌ {source_name}调用异常: {e}")
            continue
    
    # 所有实时API都失败，返回实时API错误消息
    return "🎮 实时游戏新闻获取中..."

def try_heiyou_api() -> Optional[str]:
    """尝试小黑盒API"""
    api_dict = "JKMNPQRTX1234OABCDFG56789H"

    def convert_byte(value: int) -> int:
        value = value & 0xFF
        if value & 0x80:
            return ((value << 1) ^ 0x1B) & 0xFF
        return (value << 1) & 0xFF

    def c3(value: int) -> int:
        return convert_byte(value) ^ (value & 0xFF)

    def c2(value: int) -> int:
        return c3(convert_byte(value))

    def c1(value: int) -> int:
        return c2(c3(convert_byte(value)))

    def c0(value: int) -> int:
        return c1(value) ^ c2(value) ^ c3(value)

    def checksum(data: List[int]) -> int:
        values = [
            c0(data[0]) ^ c1(data[1]) ^ c2(data[2]) ^ c3(data[3]),
            c3(data[0]) ^ c0(data[1]) ^ c1(data[2]) ^ c2(data[3]),
            c2(data[0]) ^ c3(data[1]) ^ c0(data[2]) ^ c1(data[3]),
            c1(data[0]) ^ c2(data[1]) ^ c3(data[2]) ^ c0(data[3]),
        ]
        return sum(values) % 100

    def build_signed_url(raw_url: str) -> str:
        timestamp = int(time.time())
        nonce = hashlib.md5(str(random.random()).encode("utf-8")).hexdigest().upper()
        parsed = urlparse(raw_url)
        normalized_path = "/" + "/".join([segment for segment in parsed.path.split("/") if segment]) + "/"
        ts = timestamp + 1

        nonce_digits = "".join(char for char in (nonce + api_dict) if char.isdigit())
        nonce_hash = hashlib.md5(nonce_digits.encode("utf-8")).hexdigest().lower()

        rnd_source = hashlib.md5(f"{ts}{normalized_path}{nonce_hash}".encode("utf-8")).hexdigest()
        rnd_digits = "".join(char for char in rnd_source if char.isdigit())[:9].ljust(9, "0")

        cursor = int(rnd_digits)
        hkey_core = ""
        for _ in range(5):
            idx = cursor % len(api_dict)
            cursor = cursor // len(api_dict)
            hkey_core += api_dict[idx]

        suffix = str(checksum([ord(char) for char in hkey_core[-4:]])).zfill(2)
        query_items = parse_qsl(parsed.query, keep_blank_values=True)
        query_items.extend([
            ("hkey", f"{hkey_core}{suffix}"),
            ("_time", str(timestamp)),
            ("nonce", nonce),
        ])
        signed_query = urlencode(query_items)
        return urlunparse((parsed.scheme, parsed.netloc, parsed.path, parsed.params, signed_query, parsed.fragment))

    def parse_articles(payload: Dict) -> List[Dict]:
        result = payload.get("result", {}) if isinstance(payload, dict) else {}
        data_root = payload.get("data", {}) if isinstance(payload, dict) else {}
        candidates = [
            result.get("links"),
            result.get("articles"),
            result.get("data", {}).get("articles") if isinstance(result.get("data"), dict) else None,
            data_root.get("list") if isinstance(data_root, dict) else None,
            data_root.get("articles") if isinstance(data_root, dict) else None,
            payload.get("articles") if isinstance(payload, dict) else None,
        ]

        for candidate in candidates:
            if isinstance(candidate, list) and candidate:
                return [item for item in candidate if isinstance(item, dict)]
        return []

    try:
        new_api_url = (
            "https://api.xiaoheihe.cn/bbs/app/feeds/news?"
            "os_type=web&app=heybox&client_type=mobile&version=999.0.3"
            "&x_client_type=web&x_os_type=Mac&x_app=heybox&heybox_id=-1"
            "&appid=900018355&offset=0&limit=20"
        )
        legacy_api_url = "https://api.xiaoheihe.cn/v3/bbs/app/api/web/index/feed"
        legacy_params = {"limit": 20, "offset": 0, "catid": "new", "os_type": "web"}

        request_urls = [
            ("signed_news", build_signed_url(new_api_url)),
            ("legacy_feed", f"{legacy_api_url}?{urlencode(legacy_params)}"),
        ]
        
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36 ApiMaxJia/1.0",
            "Referer": "https://www.xiaoheihe.cn/",
            "Accept": "application/json, text/plain, */*",
            "Accept-Language": "zh-CN,zh;q=0.9,en;q=0.8",
        }

        debug_news_api = os.getenv("DEBUG_NEWS_API", "0") == "1"

        for source_name, request_url in request_urls:
            response = requests.get(request_url, headers=headers, timeout=8)
            if response.status_code != 200:
                if debug_news_api:
                    print(f"小黑盒{source_name}状态码: {response.status_code}")
                continue

            try:
                data = response.json()
            except json.JSONDecodeError:
                if debug_news_api:
                    print(f"小黑盒{source_name}JSON解析失败: {response.text[:180]}")
                continue

            articles = parse_articles(data)
            if not articles:
                if debug_news_api:
                    top_level_keys = list(data.keys()) if isinstance(data, dict) else []
                    print(f"小黑盒{source_name}无文章，顶层字段: {top_level_keys}")
                continue

            filtered_articles: List[Dict] = []
            for article in articles[:20]:
                title = str(article.get("title") or article.get("link_title") or "").strip()
                if not title:
                    continue
                if len(title) < 4:
                    continue
                if "抽奖" in title:
                    continue
                filtered_articles.append(article)

            if filtered_articles:
                title = str(filtered_articles[0].get("title") or filtered_articles[0].get("link_title") or "").strip()
                title = clean_news_title(title)
                if len(title) > 40:
                    title = title[:37] + "..."
                return f"🎮 {title}"

            if debug_news_api:
                print(f"小黑盒{source_name}有文章但被过滤，样例标题: {articles[0].get('title', '')}")
    except Exception as e:
        print(f"小黑盒API错误: {e}")
    
    return None

def try_backup_gaming_api() -> Optional[str]:
    """尝试备用游戏新闻API"""
    try:
        url = "https://api.oioweb.cn/api/news/game"
        response = requests.get(url, timeout=8)
        
        if response.status_code == 200:
            data = response.json()
            if data.get("result"):
                news_list = data["result"]
                if news_list:
                    # 获取最新的新闻（列表第一个）
                    news = news_list[0]
                    title = news.get("title", "").strip()
                    
                    if title:
                        title = clean_news_title(title)
                        
                        if len(title) > 40:
                            title = title[:37] + "..."
                        return f"🎮 {title}"
    except Exception as e:
        print(f"备用游戏API错误: {e}")
    
    return None

def try_zhihu_gaming() -> Optional[str]:
    """尝试知乎游戏热榜 - 获取实时热门游戏话题"""
    try:
        url = "https://www.zhihu.com/api/v3/feed/topstory/hot-lists/game"
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
            "Referer": "https://www.zhihu.com/hot"
        }
        
        response = requests.get(url, headers=headers, timeout=8)
        
        if response.status_code == 200:
            data = response.json()
            items = data.get("data", [])
            
            if items:
                # 获取最热门的游戏话题
                for item in items[:5]:
                    target = item.get("target", {})
                    title = target.get("title", "").strip()
                    
                    if title and len(title) > 5:
                        title = clean_news_title(title)
                        if len(title) > 40:
                            title = title[:37] + "..."
                        return f"🎮 知乎热榜: {title}"
    except Exception as e:
        print(f"知乎热榜错误: {e}")
    
    return None

def try_bilibili_gaming() -> Optional[str]:
    """尝试B站游戏资讯 - 获取实时游戏动态"""
    try:
        url = "https://api.bilibili.com/x/web-interface/ranking/v2"
        params = {
            "rid": 4,  # 游戏区
            "type": "all"
        }
        
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
            "Referer": "https://www.bilibili.com/"
        }
        
        response = requests.get(url, params=params, headers=headers, timeout=8)
        
        if response.status_code == 200:
            data = response.json()
            videos = data.get("data", {}).get("list", [])
            
            if videos:
                # 获取热门游戏视频
                video = videos[0]
                title = video.get("title", "").strip()
                
                if title:
                    # 清理标题
                    title = clean_news_title(title)
                    title = title.replace("《", "").replace("》", "")
                    
                    if len(title) > 40:
                        title = title[:37] + "..."
                    return f"🎮 B站热门: {title}"
    except Exception as e:
        print(f"B站API错误: {e}")
    
    return None

def clean_news_title(title: str) -> str:
    """清理新闻标题中的特殊字符"""
    if not title:
        return ""
    
    replacements = {
        "&quot;": '"',
        "&#039;": "'",
        "&amp;": "&",
        "&lt;": "<",
        "&gt;": ">",
        "&nbsp;": " ",
        "【": "",
        "】": "",
        "[]": "",
        "()": "",
    }
    
    for old, new in replacements.items():
        title = title.replace(old, new)
    
    return title.strip()

# ========== Server酱消息发送模块（支持双人） ==========
def send_serverchan_message(content: str) -> Dict[str, bool]:
    """
    通过Server酱发送微信消息给两个用户
    
    参数:
        content: 消息内容（支持Markdown）
    返回:
        Dict[str, bool]: 每个用户的发送结果
    """
    results = {}
    
    if not SERVERCHAN_SENDKEYS or len(SERVERCHAN_SENDKEYS) == 0:
        print("❌ 错误: Server酱SendKey未配置")
        print("请在环境变量中设置 SERVERCHAN_SENDKEYS")
        return {"no_keys": False}
    
    # 从消息中提取标题
    lines = content.split('\n')
    title = lines[0] if len(lines) > 0 else "每日推送"
    if len(title) > 30:
        title = title[:27] + "..."
    
    print(f"📤 开始向 {len(SERVERCHAN_SENDKEYS)} 个用户发送消息...")
    
    for i, sendkey in enumerate(SERVERCHAN_SENDKEYS, 1):
        if not sendkey or sendkey == "你的Server酱SendKey":
            print(f"  ❌ 用户{i}: SendKey无效，跳过")
            results[f"user{i}_invalid"] = False
            continue
        
        try:
            # 隐藏SendKey显示，只显示前几位
            masked_key = f"{sendkey[:6]}...{sendkey[-4:]}" if len(sendkey) > 10 else "***"
            print(f"  📨 用户{i} ({masked_key})...")
            
            # 避免请求频率过高，添加短暂延迟
            if i > 1:
                time.sleep(1)
            
            # Server酱 API URL
            url = f"https://sctapi.ftqq.com/{sendkey}.send"
            
            # 请求数据
            data = {
                "title": title,
                "desp": content,
                "channel": "9"  # 默认推送渠道：微信
            }
            
            # 发送请求
            response = requests.post(url, data=data, timeout=10)
            result = response.json()
            
            # 解析响应
            if result.get("code") == 0 or result.get("errno") == 0:
                print(f"    ✅ 发送成功")
                results[f"user{i}"] = True
            else:
                error_msg = result.get("message", "未知错误")
                print(f"    ❌ 发送失败: {error_msg}")
                results[f"user{i}"] = False
                
        except requests.exceptions.Timeout:
            print(f"    ⏱️  用户{i}: 请求超时")
            results[f"user{i}_timeout"] = False
        except Exception as e:
            print(f"    ❌ 用户{i}: 发送异常 - {str(e)[:50]}")
            results[f"user{i}_error"] = False
    
    return results

# ========== 主函数模块 ==========
def format_daily_message() -> str:
    """生成完整的每日推送消息"""
    now = datetime.datetime.now()
    
    # 获取各个部分
    date_str = now.strftime("%Y年%m月%d日 星期") + ["一", "二", "三", "四", "五", "六", "日"][now.weekday()]
    
    greeting = "🌅 清晨问候"
    
    # 获取天气、纪念日、情话
    weather_str = get_dual_city_weather()
    anniversary_str = calculate_anniversaries()
    cheer_line = generate_love_cheer()
    
    # 获取实时游戏新闻
    print("\n4. 获取实时游戏新闻...")
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
👥 接收人数: {len(SERVERCHAN_SENDKEYS)}
🎮 游戏新闻均为实时获取
🤖 由 Server酱 自动推送"""
    
    return message

def main_handler(event=None, context=None):
    """主函数 - GitHub Actions入口"""
    print("=" * 50)
    print(f"开始执行 Server酱 双人推送任务 - {datetime.datetime.now()}")
    print("=" * 50)
    
    # 显示配置的用户数量
    print(f"📊 配置用户数: {len(SERVERCHAN_SENDKEYS)}")
    for i, key in enumerate(SERVERCHAN_SENDKEYS, 1):
        if len(key) > 10:
            masked_key = f"{key[:6]}...{key[-4:]}"
        else:
            masked_key = "***"
        print(f"  用户{i}: {masked_key}")
    
    try:
        # 生成消息
        print("\n1. 生成每日消息...")
        message = format_daily_message()
        print("✓ 消息生成成功")
        print(f"消息长度: {len(message)} 字符")
        print(f"消息预览:\n{message[:200]}...")
        
        # 发送消息
        print("\n2. 向两个用户发送消息...")
        results = send_serverchan_message(message)
        
        # 统计结果
        success_count = sum(1 for r in results.values() if r)
        total_count = len(results)
        
        print(f"\n📈 发送统计:")
        print(f"  总计: {total_count} 个发送任务")
        print(f"  成功: {success_count}")
        print(f"  失败: {total_count - success_count}")
        
        if success_count > 0:
            print(f"\n✅ Server酱推送完成，成功发送给 {success_count}/{total_count} 个用户")
            return {
                "statusCode": 200,
                "body": json.dumps({
                    "status": "success",
                    "message": f"推送成功发送给 {success_count}/{total_count} 个用户",
                    "success_count": success_count,
                    "total_count": total_count,
                    "timestamp": datetime.datetime.now().isoformat()
                })
            }
        else:
            print(f"\n❌ Server酱推送失败，所有发送都失败")
            return {
                "statusCode": 500,
                "body": json.dumps({
                    "status": "error",
                    "message": "所有发送都失败",
                    "success_count": 0,
                    "total_count": total_count,
                    "timestamp": datetime.datetime.now().isoformat()
                })
            }
            
    except Exception as e:
        print(f"\n❌ 推送任务异常: {str(e)}")
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
    print("Server酱 双人本地测试模式")
    print("=" * 50)
    
    # 显示当前配置
    print(f"当前配置 {len(SERVERCHAN_SENDKEYS)} 个用户:")
    for i, key in enumerate(SERVERCHAN_SENDKEYS, 1):
        if key and key != "你的Server酱SendKey":
            masked = f"{key[:6]}...{key[-4:]}" if len(key) > 10 else "***"
            print(f"  用户{i}: {masked}")
        else:
            print(f"  用户{i}: 未配置")
    
    try:
        # 1. 测试天气获取
        print("\n1. 测试天气获取...")
        weather = get_dual_city_weather()
        print(f"天气:\n{weather}")
        
        # 2. 测试纪念日计算
        print("\n2. 测试纪念日计算...")
        anniversary = calculate_anniversaries()
        print(f"纪念日: {anniversary}")
        
        # 3. 测试AI情话生成
        print("\n3. 测试AI情话生成...")
        for i in range(3):
            cheer = generate_love_cheer()
            print(f"情话{i+1}: {cheer}")
        
        # 4. 测试实时游戏新闻获取
        print("\n4. 测试实时游戏新闻获取...")
        gaming_news = get_gaming_news()
        print(f"游戏新闻: {gaming_news}")
        
        # 5. 生成完整消息
        print("\n5. 生成完整消息...")
        message = format_daily_message()
        print(f"\n完整消息:\n{message}")
        
        # 检查是否在 GitHub Actions 环境中
        is_github_actions = os.getenv('GITHUB_ACTIONS', False)
        
        if is_github_actions:
            # 在 GitHub Actions 中，自动发送
            print("\n检测到 GitHub Actions 环境，自动发送消息...")
            test_message = f"🔧 Server酱双人测试消息\n\n{message}"
            results = send_serverchan_message(test_message)
            
            # 统计结果
            success_count = sum(1 for r in results.values() if r)
            total_count = len(results)
            
            if success_count > 0:
                print(f"✅ 测试消息发送成功给 {success_count}/{total_count} 个用户")
                return True
            else:
                print("❌ 所有测试消息发送失败")
                return False
        else:
            # 本地环境，询问用户
            send_test = input("\n是否发送测试消息到两个Server酱用户？(y/n): ")
            if send_test.lower() == 'y':
                test_message = f"🔧 Server酱双人测试消息\n\n{message}"
                results = send_serverchan_message(test_message)
                
                # 统计结果
                success_count = sum(1 for r in results.values() if r)
                total_count = len(results)
                
                if success_count > 0:
                    print(f"✅ 测试消息发送成功给 {success_count}/{total_count} 个用户")
                    return True
                else:
                    print("❌ 所有测试消息发送失败")
                    return False
            else:
                print("测试完成，未发送消息。")
                return True
                
    except Exception as e:
        print(f"❌ 测试过程中发生错误: {e}")
        import traceback
        traceback.print_exc()
        return False

# ========== 执行入口 ==========
if __name__ == "__main__":
    # 检查是否在 GitHub Actions 环境中
    is_github_actions = os.getenv('GITHUB_ACTIONS', False)
    
    if is_github_actions:
        # 在 GitHub Actions 中，直接运行主推送函数
        print("检测到 GitHub Actions 环境，执行双人推送任务...")
        result = main_handler()
        if result.get("statusCode") == 200:
            print("✅ 双人推送执行成功")
            sys.exit(0)
        else:
            print("❌ 双人推送执行失败")
            sys.exit(1)
    else:
        # 本地环境，运行测试函数
        local_test()
else:
    # 云函数环境
    pass
