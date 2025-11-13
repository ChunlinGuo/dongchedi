# 懂车帝爬虫实施路线图 - 详细执行计划

## 🎯 项目目标
创建一个可以爬取懂车帝网站品牌车型库的爬虫系统，支持三级数据提取（品牌→车系→车型配置）

---

## 📋 总体架构概览

```
dongchedi_scraper/
├── core/                    # 核心爬虫模块
│   ├── __init__.py
│   ├── base_crawler.py      # 基础爬虫类
│   ├── brand_crawler.py     # 品牌爬虫
│   ├── series_crawler.py    # 车系爬虫
│   └── model_crawler.py     # 车型配置爬虫
├── parsers/                 # 数据解析器
│   ├── __init__.py
│   ├── json_parser.py       # JSON数据解析
│   ├── brand_parser.py      # 品牌信息解析
│   ├── series_parser.py     # 车系信息解析
│   └── config_parser.py     # 配置信息解析
├── utils/                   # 工具模块
│   ├── __init__.py
│   ├── selenium_helper.py   # Selenium工具
│   ├── request_helper.py    # Requests工具
│   ├── anti_spider.py       # 反爬虫策略
│   ├── data_cleaner.py      # 数据清洗
│   └── logger.py            # 日志工具
├── storage/                 # 数据存储模块
│   ├── __init__.py
│   ├── json_exporter.py     # JSON导出
│   ├── csv_exporter.py      # CSV导出
│   └── db_manager.py        # 数据库管理（可选）
├── config/                  # 配置文件
│   ├── __init__.py
│   ├── settings.py          # 全局配置
│   └── urls.py              # URL模板
├── data/                    # 数据输出目录
├── logs/                    # 日志目录
├── tests/                   # 测试文件
│   ├── test_crawler.py
│   └── test_parser.py
├── main.py                  # 主入口
├── requirements.txt         # 依赖包
└── README.md               # 使用文档
```

---

## 🚀 阶段一：项目初始化与基础框架（Day 1-2）

### Step 1.1: 创建项目目录结构 ⏱️ 15分钟

**操作步骤**：
```bash
# 创建主目录结构
mkdir -p dongchedi_scraper/{core,parsers,utils,storage,config,data,logs,tests}

# 创建__init__.py文件
touch dongchedi_scraper/{core,parsers,utils,storage,config,tests}/__init__.py

# 创建主要Python文件
touch dongchedi_scraper/core/{base_crawler,brand_crawler,series_crawler,model_crawler}.py
touch dongchedi_scraper/parsers/{json_parser,brand_parser,series_parser,config_parser}.py
touch dongchedi_scraper/utils/{selenium_helper,request_helper,anti_spider,data_cleaner,logger}.py
touch dongchedi_scraper/storage/{json_exporter,csv_exporter,db_manager}.py
touch dongchedi_scraper/config/{settings,urls}.py
touch dongchedi_scraper/{main,requirements,README}.{py,txt,md}
```

**验证**：
```bash
tree dongchedi_scraper -L 2
```

---

### Step 1.2: 创建 requirements.txt ⏱️ 10分钟

**文件内容**：
```txt
# 核心爬虫库
selenium==4.15.2
requests==2.31.0
beautifulsoup4==4.12.2
lxml==4.9.3

# 数据处理
pandas==2.1.3
numpy==1.26.2

# 浏览器驱动管理
webdriver-manager==4.0.1

# 反爬虫
fake-useragent==1.4.0

# 数据存储（可选）
openpyxl==3.1.2          # Excel支持

# 工具库
python-dotenv==1.0.0     # 环境变量
loguru==0.7.2            # 日志库
retry==0.9.2             # 重试装饰器
tqdm==4.66.1             # 进度条

# 开发工具
pytest==7.4.3
pytest-cov==4.1.0
```

**安装命令**：
```bash
cd dongchedi_scraper
pip install -r requirements.txt
```

**验证**：
```bash
python -c "import selenium, requests, bs4, pandas; print('依赖安装成功')"
```

---

### Step 1.3: 配置文件 - settings.py ⏱️ 20分钟

**文件路径**：`dongchedi_scraper/config/settings.py`

**完整代码**：
```python
"""
全局配置文件
"""
import os
from pathlib import Path

# ==================== 项目路径配置 ====================
BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / 'data'
LOGS_DIR = BASE_DIR / 'logs'

# 确保目录存在
DATA_DIR.mkdir(exist_ok=True)
LOGS_DIR.mkdir(exist_ok=True)

# ==================== 爬虫配置 ====================
CRAWLER_CONFIG = {
    # 延时设置（秒）
    'delay_min': 2,
    'delay_max': 5,

    # 重试设置
    'retry_times': 3,
    'retry_delay': 2,  # 重试间隔（秒）

    # 超时设置
    'timeout': 30,
    'page_load_timeout': 60,

    # 浏览器设置
    'use_selenium': True,
    'headless': True,  # 无头模式
    'window_size': (1920, 1080),

    # 并发设置（暂不支持，预留）
    'max_workers': 1,
}

# ==================== Selenium配置 ====================
SELENIUM_CONFIG = {
    'browser': 'chrome',  # chrome/firefox
    'options': [
        '--disable-blink-features=AutomationControlled',
        '--disable-dev-shm-usage',
        '--no-sandbox',
        '--disable-gpu',
        '--disable-extensions',
        '--disable-infobars',
        'user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
    ],
}

# ==================== 请求头配置 ====================
DEFAULT_HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
    'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8',
    'Accept-Encoding': 'gzip, deflate, br',
    'Connection': 'keep-alive',
    'Referer': 'https://www.dongchedi.com/',
}

# User-Agent池（用于轮换）
USER_AGENT_POOL = [
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36',
    'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.1 Safari/605.1.15',
    'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
]

# ==================== 数据存储配置 ====================
STORAGE_CONFIG = {
    'output_formats': ['json', 'csv'],  # 可选：json, csv, excel, sqlite
    'save_images': False,  # 是否保存图片
    'encoding': 'utf-8',

    # 目录结构
    'brand_dir_pattern': '{data_dir}/brands/{brand_name}',
    'series_dir_pattern': '{brand_dir}/series',
    'models_dir_pattern': '{brand_dir}/models',
}

# ==================== 日志配置 ====================
LOGGING_CONFIG = {
    'level': 'INFO',  # DEBUG, INFO, WARNING, ERROR
    'format': '<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level: <8}</level> | <cyan>{name}</cyan>:<cyan>{function}</cyan> - <level>{message}</level>',
    'rotation': '10 MB',  # 日志文件大小
    'retention': '30 days',  # 保留时间
    'log_file': LOGS_DIR / 'crawler_{time}.log',
}

# ==================== URL配置 ====================
# 见 urls.py

# ==================== 反爬虫配置 ====================
ANTI_SPIDER_CONFIG = {
    'enable_proxy': False,  # 是否启用代理
    'proxy_pool': [],  # 代理池
    'enable_cookie': True,  # 是否保持Cookie
    'max_retry_on_403': 3,  # 403错误最大重试次数
}

# ==================== 数据字段配置 ====================
# 品牌信息字段
BRAND_FIELDS = [
    'brand_id',
    'brand_name',
    'brand_name_en',
    'brand_logo',
    'description',
    'country',
    'founded_year',
    'official_website',
    'series_count',
    'crawl_time',
]

# 车系信息字段
SERIES_FIELDS = [
    'series_id',
    'series_name',
    'brand_id',
    'brand_name',
    'price_min',
    'price_max',
    'dongche_score',
    'vehicle_type',  # 轿车/SUV/MPV等
    'energy_type',   # 燃油/纯电/混动
    'on_sale',       # 是否在售
    'image_url',
    'crawl_time',
]

# 车型配置字段（动态，由实际数据决定）
MODEL_CONFIG_CATEGORIES = [
    '基本参数',
    '车身参数',
    '发动机',
    '变速箱',
    '底盘转向',
    '车轮制动',
    '主/被动安全配置',
    '辅助/操控配置',
    '外部/防盗配置',
    '内部配置',
    '座椅配置',
    '多媒体配置',
    '灯光配置',
    '玻璃/后视镜',
    '空调/冰箱',
]
```

**要点说明**：
- ✅ 所有配置集中管理
- ✅ 路径自动创建
- ✅ 灵活的参数调整
- ✅ 支持多种输出格式

---

### Step 1.4: URL配置 - urls.py ⏱️ 15分钟

**文件路径**：`dongchedi_scraper/config/urls.py`

**完整代码**：
```python
"""
URL配置和模板
"""

# ==================== 基础URL ====================
BASE_URL = 'https://www.dongchedi.com'

# ==================== 品牌相关URL ====================
# 品牌列表页
BRAND_LIST_URL = f'{BASE_URL}/auto/library'

# 品牌详情页（品牌ID: {brand_id}）
BRAND_DETAIL_URL = f'{BASE_URL}/auto/library-brand/{{brand_id}}'

# 示例：https://www.dongchedi.com/auto/library-brand/207

# ==================== 车系相关URL ====================
# 车系详情页（车系ID: {series_id}）
SERIES_DETAIL_URL = f'{BASE_URL}/auto/series/{{series_id}}'

# 车系参数配置对比页
SERIES_PARAMS_URL = f'{BASE_URL}/auto/params-carIds-{{series_id}}'

# 示例：https://www.dongchedi.com/auto/series/4272

# ==================== 车型相关URL ====================
# 车型详细配置页（车型ID: {model_id}）
MODEL_CONFIG_URL = f'{BASE_URL}/auto/params-carIds-x-{{model_id}}'

# 车型参数对比页（多个车型ID）
MODELS_COMPARE_URL = f'{BASE_URL}/auto/params-carIds-{{model_ids}}'  # model_ids用逗号分隔

# 示例：https://www.dongchedi.com/auto/params-carIds-x-123456

# ==================== 图片相关URL ====================
# 车型图片库
MODEL_IMAGES_URL = f'{BASE_URL}/auto/{{series_id}}/picture'

# ==================== API相关URL（备用）====================
# 注意：这些API可能需要通过抓包分析获得
# 品牌列表API（推测）
BRAND_LIST_API = f'{BASE_URL}/motor/car_library/get_brand_list'

# 车系列表API（推测）
SERIES_LIST_API = f'{BASE_URL}/motor/car_library/get_series_list'

# 车型配置API（推测）
MODEL_CONFIG_API = f'{BASE_URL}/motor/car_library/get_model_config'

# ==================== URL构建函数 ====================
def build_brand_url(brand_id):
    """构建品牌详情页URL"""
    return BRAND_DETAIL_URL.format(brand_id=brand_id)

def build_series_url(series_id):
    """构建车系详情页URL"""
    return SERIES_DETAIL_URL.format(series_id=series_id)

def build_model_config_url(model_id):
    """构建车型配置页URL"""
    return MODEL_CONFIG_URL.format(model_id=model_id)

def build_models_compare_url(model_ids):
    """
    构建多车型对比URL
    :param model_ids: list或逗号分隔的字符串
    """
    if isinstance(model_ids, list):
        model_ids = ','.join(map(str, model_ids))
    return MODELS_COMPARE_URL.format(model_ids=model_ids)

# ==================== URL解析函数 ====================
def extract_brand_id(url):
    """从URL提取品牌ID"""
    import re
    match = re.search(r'/library-brand/(\d+)', url)
    return match.group(1) if match else None

def extract_series_id(url):
    """从URL提取车系ID"""
    import re
    match = re.search(r'/series/(\d+)', url)
    return match.group(1) if match else None

def extract_model_id(url):
    """从URL提取车型ID"""
    import re
    match = re.search(r'/params-carIds-x-(\d+)', url)
    return match.group(1) if match else None
```

**要点说明**：
- ✅ 所有URL集中管理
- ✅ 提供构建和解析函数
- ✅ 支持动态参数替换
- ✅ 预留API地址（待验证）

---

### Step 1.5: 日志工具 - logger.py ⏱️ 20分钟

**文件路径**：`dongchedi_scraper/utils/logger.py`

**完整代码**：
```python
"""
日志工具模块
"""
import sys
from loguru import logger
from pathlib import Path
from config.settings import LOGGING_CONFIG, LOGS_DIR

def setup_logger(name='dongchedi_scraper'):
    """
    初始化日志配置
    :param name: 日志器名称
    :return: logger实例
    """
    # 移除默认handler
    logger.remove()

    # 添加控制台输出（彩色）
    logger.add(
        sys.stdout,
        format=LOGGING_CONFIG['format'],
        level=LOGGING_CONFIG['level'],
        colorize=True,
    )

    # 添加文件输出
    logger.add(
        LOGGING_CONFIG['log_file'],
        format=LOGGING_CONFIG['format'],
        level=LOGGING_CONFIG['level'],
        rotation=LOGGING_CONFIG['rotation'],
        retention=LOGGING_CONFIG['retention'],
        encoding='utf-8',
        enqueue=True,  # 异步写入
    )

    return logger

# 创建全局logger实例
log = setup_logger()

# 便捷函数
def debug(msg, *args, **kwargs):
    log.debug(msg, *args, **kwargs)

def info(msg, *args, **kwargs):
    log.info(msg, *args, **kwargs)

def warning(msg, *args, **kwargs):
    log.warning(msg, *args, **kwargs)

def error(msg, *args, **kwargs):
    log.error(msg, *args, **kwargs)

def success(msg, *args, **kwargs):
    log.success(msg, *args, **kwargs)

def critical(msg, *args, **kwargs):
    log.critical(msg, *args, **kwargs)

# 装饰器：记录函数执行
def log_function_call(func):
    """装饰器：记录函数调用"""
    from functools import wraps

    @wraps(func)
    def wrapper(*args, **kwargs):
        log.debug(f"调用函数: {func.__name__}, args={args}, kwargs={kwargs}")
        try:
            result = func(*args, **kwargs)
            log.debug(f"函数 {func.__name__} 执行成功")
            return result
        except Exception as e:
            log.error(f"函数 {func.__name__} 执行失败: {str(e)}")
            raise
    return wrapper

# 使用示例
if __name__ == '__main__':
    log.debug("这是调试信息")
    log.info("这是普通信息")
    log.warning("这是警告信息")
    log.error("这是错误信息")
    log.success("这是成功信息")
```

**测试**：
```bash
python dongchedi_scraper/utils/logger.py
# 应该看到彩色日志输出
```

---

### Step 1.6: 反爬虫工具 - anti_spider.py ⏱️ 30分钟

**文件路径**：`dongchedi_scraper/utils/anti_spider.py`

**完整代码**：
```python
"""
反爬虫策略模块
"""
import time
import random
from retry import retry
from config.settings import (
    CRAWLER_CONFIG,
    USER_AGENT_POOL,
    DEFAULT_HEADERS,
    ANTI_SPIDER_CONFIG
)
from utils.logger import log

class AntiSpiderStrategy:
    """反爬虫策略类"""

    def __init__(self):
        self.user_agent_pool = USER_AGENT_POOL
        self.default_headers = DEFAULT_HEADERS.copy()
        self.request_count = 0
        self.last_request_time = 0

    def get_random_user_agent(self):
        """获取随机User-Agent"""
        return random.choice(self.user_agent_pool)

    def get_random_headers(self, extra_headers=None):
        """
        获取随机请求头
        :param extra_headers: 额外的请求头字典
        :return: 完整的请求头字典
        """
        headers = self.default_headers.copy()
        headers['User-Agent'] = self.get_random_user_agent()

        if extra_headers:
            headers.update(extra_headers)

        return headers

    def random_delay(self, min_sec=None, max_sec=None):
        """
        随机延时
        :param min_sec: 最小延时（秒）
        :param max_sec: 最大延时（秒）
        """
        min_sec = min_sec or CRAWLER_CONFIG['delay_min']
        max_sec = max_sec or CRAWLER_CONFIG['delay_max']

        delay = random.uniform(min_sec, max_sec)
        log.debug(f"随机延时 {delay:.2f} 秒")
        time.sleep(delay)

    def smart_delay(self):
        """
        智能延时：根据请求频率动态调整
        """
        current_time = time.time()

        # 如果上次请求距离现在太近，增加延时
        if self.last_request_time > 0:
            elapsed = current_time - self.last_request_time
            if elapsed < CRAWLER_CONFIG['delay_min']:
                additional_delay = CRAWLER_CONFIG['delay_min'] - elapsed
                time.sleep(additional_delay)

        # 正常随机延时
        self.random_delay()

        # 更新状态
        self.last_request_time = time.time()
        self.request_count += 1

        # 每N次请求后增加额外延时（模拟人类行为）
        if self.request_count % 10 == 0:
            extra_delay = random.uniform(5, 10)
            log.info(f"第{self.request_count}次请求，额外休息 {extra_delay:.2f} 秒")
            time.sleep(extra_delay)

    @retry(tries=3, delay=2, backoff=2, logger=log)
    def safe_request(self, request_func, *args, **kwargs):
        """
        安全请求装饰器：自动重试
        :param request_func: 请求函数
        :return: 响应结果
        """
        log.debug(f"执行请求: {request_func.__name__}")

        # 智能延时
        self.smart_delay()

        # 执行请求
        try:
            response = request_func(*args, **kwargs)

            # 检查响应状态
            if hasattr(response, 'status_code'):
                if response.status_code == 403:
                    log.warning("遇到403错误，可能被反爬虫检测")
                    raise Exception("403 Forbidden")
                elif response.status_code == 429:
                    log.warning("请求过于频繁（429），增加延时")
                    time.sleep(10)
                    raise Exception("429 Too Many Requests")
                elif response.status_code != 200:
                    log.warning(f"响应状态码异常: {response.status_code}")

            return response

        except Exception as e:
            log.error(f"请求失败: {str(e)}")
            raise

    def get_random_proxy(self):
        """
        获取随机代理（如果启用）
        :return: 代理字典或None
        """
        if not ANTI_SPIDER_CONFIG['enable_proxy']:
            return None

        if not ANTI_SPIDER_CONFIG['proxy_pool']:
            log.warning("代理池为空")
            return None

        proxy = random.choice(ANTI_SPIDER_CONFIG['proxy_pool'])
        log.debug(f"使用代理: {proxy}")
        return {
            'http': proxy,
            'https': proxy
        }

    def simulate_human_behavior(self):
        """模拟人类浏览行为"""
        # 随机滚动页面、移动鼠标等（需要Selenium）
        pass

# 创建全局实例
anti_spider = AntiSpiderStrategy()

# 便捷函数
def get_headers():
    """快捷获取请求头"""
    return anti_spider.get_random_headers()

def delay():
    """快捷延时"""
    anti_spider.smart_delay()

# 使用示例
if __name__ == '__main__':
    print("测试随机User-Agent:")
    for i in range(3):
        print(f"  {i+1}. {anti_spider.get_random_user_agent()}")

    print("\n测试随机延时:")
    for i in range(3):
        start = time.time()
        anti_spider.random_delay()
        print(f"  延时: {time.time() - start:.2f}秒")
```

**测试**：
```bash
python dongchedi_scraper/utils/anti_spider.py
```

---

## 🔍 阶段二：数据解析器开发（Day 2-3）

### Step 2.1: JSON解析器 - json_parser.py ⏱️ 45分钟

**文件路径**：`dongchedi_scraper/parsers/json_parser.py`

**完整代码**：
```python
"""
JSON数据解析器 - 提取Next.js页面数据
"""
import json
import re
from bs4 import BeautifulSoup
from utils.logger import log

class NextJSDataExtractor:
    """Next.js数据提取器"""

    @staticmethod
    def extract_from_html(html):
        """
        从HTML中提取__NEXT_DATA__
        :param html: HTML字符串
        :return: 解析后的JSON数据，如果失败返回None
        """
        try:
            soup = BeautifulSoup(html, 'lxml')

            # 方法1：查找<script id="__NEXT_DATA__">标签
            script_tag = soup.find('script', {'id': '__NEXT_DATA__'})

            if script_tag and script_tag.string:
                data = json.loads(script_tag.string)
                log.debug("成功从__NEXT_DATA__标签提取数据")
                return data

            # 方法2：正则表达式查找（备用）
            pattern = r'<script id="__NEXT_DATA__"[^>]*>(.*?)</script>'
            match = re.search(pattern, html, re.DOTALL)

            if match:
                data = json.loads(match.group(1))
                log.debug("成功通过正则表达式提取数据")
                return data

            log.warning("未找到__NEXT_DATA__数据")
            return None

        except json.JSONDecodeError as e:
            log.error(f"JSON解析失败: {str(e)}")
            return None
        except Exception as e:
            log.error(f"数据提取失败: {str(e)}")
            return None

    @staticmethod
    def get_page_props(nextjs_data):
        """
        获取pageProps数据
        :param nextjs_data: __NEXT_DATA__数据
        :return: pageProps字典
        """
        if not nextjs_data:
            return None

        try:
            page_props = nextjs_data.get('props', {}).get('pageProps', {})
            if page_props:
                log.debug(f"成功获取pageProps，包含 {len(page_props)} 个键")
            return page_props
        except Exception as e:
            log.error(f"获取pageProps失败: {str(e)}")
            return None

    @staticmethod
    def extract_json_from_script(html, pattern=None):
        """
        提取页面中的JSON数据（通用方法）
        :param html: HTML字符串
        :param pattern: 正则表达式模式
        :return: JSON数据列表
        """
        if not pattern:
            pattern = r'<script[^>]*>(.*?window\.__INITIAL_STATE__\s*=\s*)({.*?})</script>'

        matches = re.findall(pattern, html, re.DOTALL)
        results = []

        for match in matches:
            try:
                # match可能是tuple，取最后一个元素
                json_str = match[-1] if isinstance(match, tuple) else match
                data = json.loads(json_str)
                results.append(data)
            except:
                continue

        return results

    @staticmethod
    def safe_get(data, *keys, default=None):
        """
        安全获取嵌套字典的值
        :param data: 字典
        :param keys: 键路径
        :param default: 默认值
        :return: 值或默认值

        示例：safe_get(data, 'props', 'pageProps', 'brand', default={})
        """
        result = data
        for key in keys:
            if isinstance(result, dict):
                result = result.get(key)
                if result is None:
                    return default
            else:
                return default
        return result if result is not None else default


class JSONCleaner:
    """JSON数据清洗工具"""

    @staticmethod
    def remove_null_values(data):
        """移除None/null值"""
        if isinstance(data, dict):
            return {k: JSONCleaner.remove_null_values(v)
                    for k, v in data.items() if v is not None}
        elif isinstance(data, list):
            return [JSONCleaner.remove_null_values(item)
                    for item in data if item is not None]
        return data

    @staticmethod
    def flatten_dict(data, parent_key='', sep='_'):
        """
        展平嵌套字典
        示例：{'a': {'b': 1}} -> {'a_b': 1}
        """
        items = []
        for k, v in data.items():
            new_key = f"{parent_key}{sep}{k}" if parent_key else k
            if isinstance(v, dict):
                items.extend(JSONCleaner.flatten_dict(v, new_key, sep=sep).items())
            else:
                items.append((new_key, v))
        return dict(items)

    @staticmethod
    def extract_fields(data, field_mapping):
        """
        按字段映射提取数据
        :param data: 原始数据
        :param field_mapping: 字段映射 {'新字段名': '原字段路径'}
        :return: 提取后的数据

        示例：
        field_mapping = {
            'id': 'brand.id',
            'name': 'brand.name'
        }
        """
        result = {}
        extractor = NextJSDataExtractor()

        for new_field, old_path in field_mapping.items():
            keys = old_path.split('.')
            value = extractor.safe_get(data, *keys)
            result[new_field] = value

        return result


# 使用示例
if __name__ == '__main__':
    # 测试HTML
    test_html = '''
    <html>
    <head>
        <script id="__NEXT_DATA__" type="application/json">
        {
            "props": {
                "pageProps": {
                    "brand": {
                        "id": 207,
                        "name": "零跑汽车",
                        "description": "创新型智能电动汽车品牌"
                    },
                    "seriesList": [
                        {"id": 4272, "name": "零跑T03"},
                        {"id": 5831, "name": "零跑C11"}
                    ]
                }
            }
        }
        </script>
    </head>
    <body></body>
    </html>
    '''

    # 提取数据
    extractor = NextJSDataExtractor()
    data = extractor.extract_from_html(test_html)
    page_props = extractor.get_page_props(data)

    print("PageProps数据:")
    print(json.dumps(page_props, indent=2, ensure_ascii=False))

    # 安全获取
    brand_name = extractor.safe_get(page_props, 'brand', 'name', default='未知品牌')
    print(f"\n品牌名称: {brand_name}")
```

**测试**：
```bash
python dongchedi_scraper/parsers/json_parser.py
```

**预期输出**：
```
PageProps数据:
{
  "brand": {
    "id": 207,
    "name": "零跑汽车",
    "description": "创新型智能电动汽车品牌"
  },
  "seriesList": [...]
}

品牌名称: 零跑汽车
```

---

### Step 2.2: 品牌解析器 - brand_parser.py ⏱️ 30分钟

**文件路径**：`dongchedi_scraper/parsers/brand_parser.py`

**完整代码**：
```python
"""
品牌信息解析器
"""
import datetime
from parsers.json_parser import NextJSDataExtractor
from config.settings import BRAND_FIELDS
from utils.logger import log

class BrandParser:
    """品牌信息解析器"""

    def __init__(self):
        self.extractor = NextJSDataExtractor()

    def parse_brand_page(self, html):
        """
        解析品牌页面
        :param html: 品牌页面HTML
        :return: 品牌信息字典和车系列表
        """
        # 1. 提取JSON数据
        nextjs_data = self.extractor.extract_from_html(html)
        if not nextjs_data:
            log.error("无法提取品牌页面数据")
            return None, []

        page_props = self.extractor.get_page_props(nextjs_data)

        # 2. 解析品牌信息
        brand_info = self._parse_brand_info(page_props)

        # 3. 解析车系列表
        series_list = self._parse_series_list(page_props)

        log.info(f"解析品牌: {brand_info.get('brand_name')}, 车系数量: {len(series_list)}")

        return brand_info, series_list

    def _parse_brand_info(self, page_props):
        """
        解析品牌基本信息
        :param page_props: pageProps数据
        :return: 品牌信息字典
        """
        brand_data = self.extractor.safe_get(page_props, 'brand', default={})

        # 提取字段（根据实际页面结构调整）
        brand_info = {
            'brand_id': self.extractor.safe_get(brand_data, 'id'),
            'brand_name': self.extractor.safe_get(brand_data, 'name'),
            'brand_name_en': self.extractor.safe_get(brand_data, 'name_en', default=''),
            'brand_logo': self.extractor.safe_get(brand_data, 'logo', default=''),
            'description': self.extractor.safe_get(brand_data, 'description', default=''),
            'country': self.extractor.safe_get(brand_data, 'country', default=''),
            'founded_year': self.extractor.safe_get(brand_data, 'founded_year'),
            'official_website': self.extractor.safe_get(brand_data, 'website', default=''),
            'series_count': 0,  # 稍后更新
            'crawl_time': datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
        }

        # 清理None值
        brand_info = {k: v for k, v in brand_info.items() if v is not None}

        return brand_info

    def _parse_series_list(self, page_props):
        """
        解析车系列表
        :param page_props: pageProps数据
        :return: 车系列表
        """
        # 可能的数据路径（根据实际情况调整）
        series_data = self.extractor.safe_get(page_props, 'seriesList', default=[])

        if not series_data:
            # 尝试其他可能的路径
            series_data = self.extractor.safe_get(page_props, 'data', 'seriesList', default=[])

        series_list = []
        for series in series_data:
            series_info = {
                'series_id': self.extractor.safe_get(series, 'id'),
                'series_name': self.extractor.safe_get(series, 'name'),
                'series_name_en': self.extractor.safe_get(series, 'name_en', default=''),
                'price_min': self.extractor.safe_get(series, 'price_min'),
                'price_max': self.extractor.safe_get(series, 'price_max'),
                'price_text': self.extractor.safe_get(series, 'price', default=''),
                'dongche_score': self.extractor.safe_get(series, 'score'),
                'vehicle_type': self.extractor.safe_get(series, 'vehicle_type', default=''),
                'energy_type': self.extractor.safe_get(series, 'energy_type', default=''),
                'on_sale': self.extractor.safe_get(series, 'on_sale', default=True),
                'image_url': self.extractor.safe_get(series, 'image', default=''),
            }

            # 清理None值
            series_info = {k: v for k, v in series_info.items() if v is not None}
            series_list.append(series_info)

        return series_list

    def parse_price_range(self, price_text):
        """
        解析价格文本
        :param price_text: "5.99-8.99万"
        :return: (min_price, max_price) 单位：万元
        """
        import re

        if not price_text:
            return None, None

        # 匹配价格范围
        match = re.search(r'([\d.]+)-([\d.]+)', price_text)
        if match:
            return float(match.group(1)), float(match.group(2))

        # 匹配单个价格
        match = re.search(r'([\d.]+)', price_text)
        if match:
            price = float(match.group(1))
            return price, price

        return None, None


# 使用示例
if __name__ == '__main__':
    parser = BrandParser()

    # 测试价格解析
    test_prices = [
        "5.99-8.99万",
        "15.58-18.58万",
        "15.99万",
        "暂无报价"
    ]

    for price_text in test_prices:
        min_p, max_p = parser.parse_price_range(price_text)
        print(f"{price_text} -> min={min_p}, max={max_p}")
```

---

### Step 2.3: 车系解析器 - series_parser.py ⏱️ 30分钟

**文件路径**：`dongchedi_scraper/parsers/series_parser.py`

**完整代码**：
```python
"""
车系信息解析器
"""
from parsers.json_parser import NextJSDataExtractor
from utils.logger import log

class SeriesParser:
    """车系信息解析器"""

    def __init__(self):
        self.extractor = NextJSDataExtractor()

    def parse_series_page(self, html):
        """
        解析车系详情页
        :param html: 车系页面HTML
        :return: 车系信息和车型列表
        """
        # 1. 提取JSON数据
        nextjs_data = self.extractor.extract_from_html(html)
        if not nextjs_data:
            log.error("无法提取车系页面数据")
            return None, []

        page_props = self.extractor.get_page_props(nextjs_data)

        # 2. 解析车系详细信息
        series_info = self._parse_series_detail(page_props)

        # 3. 解析车型列表
        models_list = self._parse_models_list(page_props)

        log.info(f"解析车系: {series_info.get('series_name')}, 车型数量: {len(models_list)}")

        return series_info, models_list

    def _parse_series_detail(self, page_props):
        """解析车系详细信息"""
        series_data = self.extractor.safe_get(page_props, 'series', default={})

        series_info = {
            'series_id': self.extractor.safe_get(series_data, 'id'),
            'series_name': self.extractor.safe_get(series_data, 'name'),
            'brand_id': self.extractor.safe_get(series_data, 'brand_id'),
            'brand_name': self.extractor.safe_get(series_data, 'brand_name'),
            'price_min': self.extractor.safe_get(series_data, 'price_min'),
            'price_max': self.extractor.safe_get(series_data, 'price_max'),
            'manufacturer': self.extractor.safe_get(series_data, 'manufacturer', default=''),
            'level': self.extractor.safe_get(series_data, 'level', default=''),
            'energy_type': self.extractor.safe_get(series_data, 'energy_type', default=''),
        }

        return {k: v for k, v in series_info.items() if v is not None}

    def _parse_models_list(self, page_props):
        """解析车型列表"""
        models_data = self.extractor.safe_get(page_props, 'models', default=[])

        if not models_data:
            models_data = self.extractor.safe_get(page_props, 'data', 'list', default=[])

        models_list = []
        for model in models_data:
            model_info = {
                'model_id': self.extractor.safe_get(model, 'id'),
                'model_name': self.extractor.safe_get(model, 'name'),
                'year': self.extractor.safe_get(model, 'year'),
                'price': self.extractor.safe_get(model, 'price'),
                'on_sale': self.extractor.safe_get(model, 'on_sale', default=True),
            }

            models_list.append({k: v for k, v in model_info.items() if v is not None})

        return models_list
```

---

### Step 2.4: 配置解析器 - config_parser.py ⏱️ 40分钟

**文件路径**：`dongchedi_scraper/parsers/config_parser.py`

**完整代码**：
```python
"""
车型配置信息解析器
"""
from parsers.json_parser import NextJSDataExtractor
from config.settings import MODEL_CONFIG_CATEGORIES
from utils.logger import log

class ConfigParser:
    """车型配置解析器"""

    def __init__(self):
        self.extractor = NextJSDataExtractor()

    def parse_config_page(self, html):
        """
        解析车型配置页面
        :param html: 配置页面HTML
        :return: 配置信息字典
        """
        # 1. 提取JSON数据
        nextjs_data = self.extractor.extract_from_html(html)
        if not nextjs_data:
            log.error("无法提取配置页面数据")
            return None

        page_props = self.extractor.get_page_props(nextjs_data)

        # 2. 解析配置信息
        config_data = self._parse_config_data(page_props)

        log.info(f"解析配置: {config_data.get('model_name', '未知车型')}")

        return config_data

    def _parse_config_data(self, page_props):
        """解析配置数据"""
        # 车型基本信息
        model_info = self.extractor.safe_get(page_props, 'model', default={})

        config_data = {
            'model_id': self.extractor.safe_get(model_info, 'id'),
            'model_name': self.extractor.safe_get(model_info, 'name'),
            'series_id': self.extractor.safe_get(model_info, 'series_id'),
            'series_name': self.extractor.safe_get(model_info, 'series_name'),
            'year': self.extractor.safe_get(model_info, 'year'),
            'price': self.extractor.safe_get(model_info, 'price'),
        }

        # 解析配置参数（按分类组织）
        params_data = self.extractor.safe_get(page_props, 'params', default={})

        config_categories = {}
        for category in MODEL_CONFIG_CATEGORIES:
            category_params = self._parse_category_params(params_data, category)
            if category_params:
                config_categories[category] = category_params

        config_data['config'] = config_categories

        return config_data

    def _parse_category_params(self, params_data, category):
        """解析单个配置分类"""
        category_data = params_data.get(category, {})

        if not category_data:
            return {}

        # 提取参数键值对
        params = {}
        for key, value in category_data.items():
            # 跳过空值
            if value is None or value == '' or value == '-':
                continue
            params[key] = value

        return params

    def normalize_config_value(self, value):
        """
        标准化配置值
        :param value: 原始值
        :return: 标准化后的值
        """
        if value is None:
            return None

        # 转字符串
        value = str(value).strip()

        # 标准化常见值
        normalize_map = {
            '●': '有',
            '○': '无',
            '-': '无',
            '': '无',
            '标配': '有',
            '选配': '可选',
        }

        return normalize_map.get(value, value)
```

---

## 🕷️ 阶段三：爬虫核心开发（Day 3-5）

### Step 3.1: Selenium助手 - selenium_helper.py ⏱️ 45分钟

*(由于篇幅限制，这里展示核心框架)*

**关键功能**：
1. 浏览器初始化（Chrome/Firefox）
2. 页面加载等待
3. 反检测设置
4. 截图保存
5. Cookie管理

### Step 3.2: 基础爬虫类 - base_crawler.py ⏱️ 1小时

**核心功能**：
1. 统一的请求接口
2. 错误处理和重试
3. 数据缓存
4. 日志记录

### Step 3.3: 品牌爬虫 - brand_crawler.py ⏱️ 1.5小时

**核心流程**：
```python
def crawl(brand_id):
    1. 构建URL
    2. 获取页面HTML
    3. 调用BrandParser解析
    4. 保存品牌信息
    5. 遍历车系列表
    6. 返回结果
```

### Step 3.4: 车系爬虫 - series_crawler.py ⏱️ 1.5小时

### Step 3.5: 车型爬虫 - model_crawler.py ⏱️ 1.5小时

---

## 💾 阶段四：数据存储模块（Day 6）

### Step 4.1: JSON导出 - json_exporter.py ⏱️ 30分钟
### Step 4.2: CSV导出 - csv_exporter.py ⏱️ 30分钟
### Step 4.3: 数据管理器 - db_manager.py ⏱️ 1小时

---

## 🎮 阶段五：主程序与CLI（Day 7）

### Step 5.1: 主入口 - main.py ⏱️ 2小时

**命令行参数**：
```python
python main.py --brand-id 207
python main.py --brand-list 207,209,210
python main.py --input brands.txt --output json,csv
python main.py --brand-id 207 --selenium --headless
```

---

## ✅ 阶段六：测试与优化（Day 8-9）

### Step 6.1: 单元测试 ⏱️ 3小时
### Step 6.2: 端到端测试（零跑品牌）⏱️ 2小时
### Step 6.3: 性能优化 ⏱️ 2小时
### Step 6.4: 异常处理完善 ⏱️ 2小时

---

## 📚 附录：关键代码模板

### 模板1：爬虫类基本结构
```python
class BrandCrawler(BaseCrawler):
    def __init__(self):
        super().__init__()
        self.parser = BrandParser()

    def crawl(self, brand_id):
        # 1. 获取页面
        url = build_brand_url(brand_id)
        html = self.fetch_page(url)

        # 2. 解析数据
        brand_info, series_list = self.parser.parse_brand_page(html)

        # 3. 保存数据
        self.save_data(brand_info, series_list)

        # 4. 爬取下级数据
        for series in series_list:
            series_crawler.crawl(series['series_id'])

        return brand_info, series_list
```

### 模板2：数据保存流程
```python
def save_brand_data(brand_info, series_list):
    # 1. 创建目录
    brand_dir = create_brand_directory(brand_info['brand_name'])

    # 2. 保存品牌信息
    save_json(brand_info, brand_dir / 'info.json')

    # 3. 保存车系列表
    save_csv(series_list, brand_dir / 'series_list.csv')

    log.success(f"数据已保存到: {brand_dir}")
```

---

## 🎯 执行检查清单

### 阶段一检查项
- [ ] 目录结构创建完成
- [ ] requirements.txt安装成功
- [ ] settings.py配置正确
- [ ] urls.py URL模板可用
- [ ] logger.py日志输出正常
- [ ] anti_spider.py延时功能正常

### 阶段二检查项
- [ ] json_parser.py能提取__NEXT_DATA__
- [ ] brand_parser.py解析逻辑正确
- [ ] series_parser.py解析逻辑正确
- [ ] config_parser.py解析逻辑正确

### 阶段三检查项
- [ ] selenium_helper.py浏览器启动成功
- [ ] base_crawler.py基础功能完善
- [ ] brand_crawler.py爬取成功
- [ ] series_crawler.py爬取成功
- [ ] model_crawler.py爬取成功

### 阶段四检查项
- [ ] JSON导出格式正确
- [ ] CSV导出格式正确
- [ ] 数据存储目录结构合理

### 阶段五检查项
- [ ] main.py命令行参数解析正确
- [ ] 完整流程跑通（零跑品牌测试）
- [ ] 输出数据完整

### 阶段六检查项
- [ ] 单元测试通过率>90%
- [ ] 端到端测试成功
- [ ] 错误处理完善
- [ ] 性能满足要求（单品牌<15分钟）

---

## 📊 预期交付物

### 代码交付
1. ✅ 完整的项目代码（符合PEP8规范）
2. ✅ 详细的代码注释
3. ✅ requirements.txt依赖列表
4. ✅ README.md使用文档

### 数据交付（零跑品牌示例）
1. ✅ 品牌信息JSON
2. ✅ 车系列表CSV
3. ✅ 所有车型配置JSON（预计30-50个文件）

### 文档交付
1. ✅ 技术文档（架构说明）
2. ✅ 使用手册（命令行说明）
3. ✅ 常见问题FAQ
4. ✅ 维护指南（如何应对网站结构变化）

---

## 🚨 风险应对预案

### 风险1：无法提取__NEXT_DATA__
**应对**：降级使用BeautifulSoup解析DOM

### 风险2：反爬虫触发403
**应对**：增加延时、切换代理、使用Selenium

### 风险3：页面结构变化
**应对**：版本检测机制、多种解析方式并存

### 风险4：数据字段缺失
**应对**：安全获取方法（safe_get）、默认值处理

---

## 📞 下一步行动

请确认是否按此详细计划开始实施？

我将从 **Step 1.1** 开始，逐步完成每个步骤，并在关键节点向你汇报进度。

预计完成时间：**9个工作日**
