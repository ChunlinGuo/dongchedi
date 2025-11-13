"""
快速原型 - 配置文件
"""
from pathlib import Path

# 项目路径
BASE_DIR = Path(__file__).resolve().parent
DATA_DIR = BASE_DIR / 'data'
LOGS_DIR = BASE_DIR / 'logs'

# 确保目录存在
DATA_DIR.mkdir(exist_ok=True)
LOGS_DIR.mkdir(exist_ok=True)

# 目标URL
BASE_URL = 'https://www.dongchedi.com'
BRAND_URL_TEMPLATE = f'{BASE_URL}/auto/library-brand/{{brand_id}}'

# 测试品牌ID（零跑汽车）
TEST_BRAND_ID = 207

# 请求配置
HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
    'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8',
    'Accept-Encoding': 'gzip, deflate, br',
    'Connection': 'keep-alive',
}

# 超时设置
TIMEOUT = 30

# 延时设置（秒）
REQUEST_DELAY = 3
