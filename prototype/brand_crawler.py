"""
快速原型 - 品牌信息爬虫
核心功能：爬取品牌基本信息和车系列表
"""
import requests
import time
import datetime
from json_extractor import JSONExtractor
from config import HEADERS, TIMEOUT, REQUEST_DELAY, BRAND_URL_TEMPLATE


class BrandCrawler:
    """品牌爬虫"""

    def __init__(self):
        self.extractor = JSONExtractor()
        self.session = requests.Session()
        self.session.headers.update(HEADERS)

    def fetch_page(self, url):
        """
        获取页面HTML
        :param url: 目标URL
        :return: HTML字符串
        """
        try:
            print(f"\n正在请求: {url}")
            time.sleep(REQUEST_DELAY)  # 延时，避免请求过快

            response = self.session.get(url, timeout=TIMEOUT)
            response.raise_for_status()

            # 设置正确的编码
            response.encoding = response.apparent_encoding or 'utf-8'

            print(f"✓ 请求成功，状态码: {response.status_code}")
            print(f"✓ Content-Type: {response.headers.get('Content-Type', 'Unknown')}")
            print(f"✓ Content-Encoding: {response.headers.get('Content-Encoding', 'None')}")
            print(f"✓ 响应大小: {len(response.text)} 字符")

            # 检查是否是HTML
            content_type = response.headers.get('Content-Type', '')
            if 'text/html' not in content_type:
                print(f"⚠ 警告: Content-Type不是HTML: {content_type}")

            return response.text

        except requests.RequestException as e:
            print(f"✗ 请求失败: {str(e)}")
            return None

    def parse_brand_info(self, page_props):
        """
        解析品牌基本信息
        :param page_props: pageProps数据
        :return: 品牌信息字典
        """
        # 从brandInfo.brand_simple_info获取品牌数据
        brand_simple_info = self.extractor.safe_get(page_props, 'brandInfo', 'brand_simple_info', default={})

        # 提取字段
        brand_info = {
            'brand_id': self.extractor.safe_get(page_props, 'brandId') or
                       self.extractor.safe_get(brand_simple_info, 'brand_id'),
            'brand_name': self.extractor.safe_get(brand_simple_info, 'brand_name'),
            'brand_name_en': self.extractor.safe_get(brand_simple_info, 'brand_name_en', default=''),
            'brand_logo': self.extractor.safe_get(brand_simple_info, 'brand_logo', default=''),
            'description': self.extractor.safe_get(brand_simple_info, 'description', default=''),
            'country': self.extractor.safe_get(brand_simple_info, 'country', default=''),
            'initial': self.extractor.safe_get(brand_simple_info, 'initial', default=''),
            'crawl_time': datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
        }

        # 清理None值和空字符串
        brand_info = {k: v for k, v in brand_info.items() if v}

        return brand_info

    def parse_series_list(self, page_props):
        """
        解析车系列表
        :param page_props: pageProps数据
        :return: 车系列表
        """
        # 尝试从多个位置获取车系数据
        inner_list = self.extractor.safe_get(page_props, 'innerList', default=[])
        outer_list = self.extractor.safe_get(page_props, 'outerList', default=[])

        # 也尝试从brandInfo获取
        brand_info = self.extractor.safe_get(page_props, 'brandInfo', default={})
        category_list = self.extractor.safe_get(brand_info, 'category_list', default=[])
        recommend_series_list = self.extractor.safe_get(brand_info, 'recommend_series_list', default=[])

        print(f"  innerList 长度: {len(inner_list) if isinstance(inner_list, list) else 'not a list'}")
        print(f"  outerList 长度: {len(outer_list) if isinstance(outer_list, list) else 'not a list'}")
        print(f"  category_list 长度: {len(category_list) if isinstance(category_list, list) else 'not a list'}")
        print(f"  recommend_series_list 长度: {len(recommend_series_list) if isinstance(recommend_series_list, list) else 'not a list'}")

        # 调试：打印第一个分类的键
        if isinstance(category_list, list) and len(category_list) > 0:
            print(f"  category_list[0] 的键: {list(category_list[0].keys()) if isinstance(category_list[0], dict) else 'not a dict'}")

        # 合并两个列表
        all_series = []

        # 解析category_list
        if isinstance(category_list, list):
            for category in category_list:
                # 注意：这里字段是'list'而不是'series_list'
                series_list = self.extractor.safe_get(category, 'list', default=[])
                category_name = self.extractor.safe_get(category, 'category_name', default='未知')
                print(f"  处理分类: {category_name}, 车系数: {len(series_list)}")
                for series in series_list:
                    all_series.append(self._parse_single_series(series, category_name))

        # 也可以尝试innerList和outerList
        for list_name, series_type in [('innerList', inner_list), ('outerList', outer_list)]:
            if isinstance(series_type, list):
                for category in series_type:
                    series_list = self.extractor.safe_get(category, 'series_list', default=[])
                    if series_list:
                        print(f"  处理 {list_name}, 车系数: {len(series_list)}")
                        for series in series_list:
                            all_series.append(self._parse_single_series(series, list_name))

        return all_series

    def _parse_single_series(self, series, origin_type=''):
        """
        解析单个车系信息
        :param series: 车系数据
        :param origin_type: 车型来源（国产/进口）
        :return: 车系信息字典
        """
        series_info = {
            'series_id': self.extractor.safe_get(series, 'series_id'),
            'series_name': self.extractor.safe_get(series, 'series_name'),
            'origin_type': origin_type,
            'price_text': self.extractor.safe_get(series, 'price_info', default=''),
            'min_price': self.extractor.safe_get(series, 'min_price'),
            'max_price': self.extractor.safe_get(series, 'max_price'),
            'series_score': self.extractor.safe_get(series, 'series_score'),
            'level_name': self.extractor.safe_get(series, 'level_name', default=''),
            'energy_type': self.extractor.safe_get(series, 'energy_type', default=''),
            'on_sale': self.extractor.safe_get(series, 'on_sale', default=True),
            'image_url': self.extractor.safe_get(series, 'image_url', default=''),
        }

        # 清理None值和空字符串
        series_info = {k: v for k, v in series_info.items() if v not in [None, '']}

        return series_info

    def crawl(self, brand_id):
        """
        爬取品牌信息
        :param brand_id: 品牌ID
        :return: (brand_info, series_list) 或 (None, None)
        """
        print(f"\n{'='*60}")
        print(f"开始爬取品牌 ID: {brand_id}")
        print(f"{'='*60}")

        # 1. 构建URL
        url = BRAND_URL_TEMPLATE.format(brand_id=brand_id)

        # 2. 获取页面HTML
        html = self.fetch_page(url)
        if not html:
            print("✗ 无法获取页面内容")
            return None, None

        # 3. 提取JSON数据
        print("\n正在提取JSON数据...")
        nextjs_data = self.extractor.extract_nextjs_data(html)
        if not nextjs_data:
            print("✗ 无法提取JSON数据")
            # 保存HTML以便调试
            debug_file = f"/home/user/dongchedi/prototype/logs/debug_{brand_id}.html"
            with open(debug_file, 'w', encoding='utf-8') as f:
                f.write(html)
            print(f"⚠ HTML已保存到: {debug_file}")
            return None, None

        page_props = self.extractor.get_page_props(nextjs_data)
        if not page_props:
            print("✗ 无法获取pageProps")
            return None, None

        # 打印pageProps的键（用于调试）
        print(f"\n页面数据包含的键: {list(page_props.keys())}")

        # 打印brandInfo结构
        if 'brandInfo' in page_props:
            print(f"\nbrandInfo包含的键: {list(page_props['brandInfo'].keys()) if isinstance(page_props['brandInfo'], dict) else 'not a dict'}")

        # 打印车系列表的位置
        for key in ['innerList', 'outerList', 'seriesList', 'series']:
            if key in page_props:
                data = page_props[key]
                if isinstance(data, list) and len(data) > 0:
                    print(f"\n{key} 是列表，长度={len(data)}, 第一项的键: {list(data[0].keys()) if isinstance(data[0], dict) else 'not a dict'}")
                else:
                    print(f"\n{key}: {type(data)}")

        # 4. 解析品牌信息
        print("\n正在解析品牌信息...")
        brand_info = self.parse_brand_info(page_props)
        if brand_info:
            print(f"✓ 品牌信息:")
            for key, value in brand_info.items():
                print(f"  - {key}: {value}")
        else:
            print("⚠ 未找到品牌信息")

        # 5. 解析车系列表
        print("\n正在解析车系列表...")
        series_list = self.parse_series_list(page_props)
        print(f"✓ 发现 {len(series_list)} 个车系")

        if series_list:
            print("\n车系列表:")
            for i, series in enumerate(series_list[:5], 1):  # 只显示前5个
                print(f"  {i}. {series.get('series_name', '未知')} - {series.get('price_text', '未知价格')}")
            if len(series_list) > 5:
                print(f"  ... (还有 {len(series_list) - 5} 个车系)")

        print(f"\n{'='*60}")
        print("✓ 爬取完成")
        print(f"{'='*60}")

        return brand_info, series_list


# 测试代码
if __name__ == '__main__':
    from config import TEST_BRAND_ID

    print("=== 测试品牌爬虫 ===")
    print(f"目标品牌: 零跑汽车 (ID: {TEST_BRAND_ID})")

    crawler = BrandCrawler()
    brand_info, series_list = crawler.crawl(TEST_BRAND_ID)

    if brand_info and series_list:
        print("\n\n=== 爬取结果摘要 ===")
        print(f"品牌: {brand_info.get('brand_name', '未知')}")
        print(f"车系数量: {len(series_list)}")
        print("\n✓ 测试成功")
    else:
        print("\n✗ 测试失败")
