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


        # 合并两个列表
        all_series = []

        # 解析category_list
        if isinstance(category_list, list):
            for i, category in enumerate(category_list):
                # 注意：这里字段是'list'而不是'series_list'
                series_list = self.extractor.safe_get(category, 'list', default=[])
                category_name = self.extractor.safe_get(category, 'category_name', default='未知')
                if len(series_list) > 0:
                    print(f"  处理分类: {category_name}, 原始项数: {len(series_list)}")

                for series in series_list:
                    parsed = self._parse_single_series(series, category_name)
                    if parsed:  # 过滤掉None（标签项）
                        all_series.append(parsed)

        # 也可以尝试innerList和outerList
        for list_name, series_type in [('innerList', inner_list), ('outerList', outer_list)]:
            if isinstance(series_type, list):
                for category in series_type:
                    series_list = self.extractor.safe_get(category, 'series_list', default=[])
                    if series_list:
                        print(f"  处理 {list_name}, 车系数: {len(series_list)}")
                        for series in series_list:
                            parsed = self._parse_single_series(series, list_name)
                            if parsed:
                                all_series.append(parsed)

        return all_series

    def _parse_single_series(self, series, origin_type=''):
        """
        解析单个车系信息
        :param series: 车系数据
        :param origin_type: 车型来源（分类名称）
        :return: 车系信息字典
        """
        # 跳过标签类型（type=1075, 1076等）
        item_type = self.extractor.safe_get(series, 'type')
        if item_type in [1075, 1076]:
            return None

        # 真实车系数据在info字段里（type=1002）
        info = self.extractor.safe_get(series, 'info', default={})

        series_info = {
            'series_id': self.extractor.safe_get(info, 'series_id'),
            'series_name': self.extractor.safe_get(info, 'series_name'),
            'sub_brand_name': self.extractor.safe_get(info, 'sub_brand_name', default=''),
            'category': origin_type,
            'official_price': self.extractor.safe_get(info, 'official_price', default=''),
            'dealer_price': self.extractor.safe_get(info, 'dealer_price', default=''),
            'price': self.extractor.safe_get(info, 'price', default=''),
            'dcd_score': self.extractor.safe_get(info, 'dcd_score'),
            'image_url': self.extractor.safe_get(info, 'image_url', default=''),
            'motor_id': self.extractor.safe_get(info, 'motor_id'),
            'business_status': self.extractor.safe_get(info, 'business_status'),
        }

        # 提取top_tag信息
        top_tag = self.extractor.safe_get(info, 'top_tag', default={})
        if top_tag:
            series_info['top_tag'] = self.extractor.safe_get(top_tag, 'text', default='')

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
                name = series.get('series_name', '未知')
                price = series.get('official_price') or series.get('price') or series.get('dealer_price', '未知价格')
                score = series.get('dcd_score', '-')
                print(f"  {i}. {name} | 价格: {price} | 懂车分: {score}")
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
