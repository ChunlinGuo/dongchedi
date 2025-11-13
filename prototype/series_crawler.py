#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
车系爬虫模块 - 获取车系下的车型ID列表
"""
import requests
import time
from json_extractor import JSONExtractor
from config import HEADERS, TIMEOUT, REQUEST_DELAY


class SeriesCrawler:
    """车系爬虫类 - 负责爬取车系页面，获取车型ID列表"""

    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update(HEADERS)
        self.extractor = JSONExtractor()

    def get_series_url(self, series_id):
        """构建车系页面URL"""
        return f"https://www.dongchedi.com/auto/series/{series_id}"

    def fetch_series_page(self, series_id):
        """
        获取车系页面HTML
        :param series_id: 车系ID
        :return: HTML文本
        """
        url = self.get_series_url(series_id)

        try:
            time.sleep(REQUEST_DELAY)
            response = self.session.get(url, timeout=TIMEOUT)
            response.raise_for_status()
            return response.text
        except requests.RequestException as e:
            print(f"✗ 请求车系页面失败 (ID: {series_id}): {str(e)}")
            return None

    def parse_car_models(self, html):
        """
        解析车系页面，提取车型ID列表
        :param html: 页面HTML
        :return: 车型列表 [{car_id, car_name, official_price, ...}, ...]
        """
        # 1. 提取JSON数据
        nextjs_data = self.extractor.extract_nextjs_data(html)
        if not nextjs_data:
            print("  ✗ 未找到__NEXT_DATA__")
            return []

        page_props = self.extractor.get_page_props(nextjs_data)
        if not page_props:
            print("  ✗ 未找到pageProps")
            return []

        # 2. 获取车型数据
        car_models_data = self.extractor.safe_get(page_props, 'carModelsData', default={})
        tab_list = self.extractor.safe_get(car_models_data, 'tab_list', default=[])

        if not tab_list:
            print("  ⚠ 未找到车型数据")
            return []

        # 3. 解析车型列表
        car_list = []

        for tab in tab_list:
            tab_key = self.extractor.safe_get(tab, 'tab_key', default='')

            # 只处理在售车型（可以根据需要调整）
            if tab_key not in ['online_all']:  # online_all = 在售
                continue

            tab_data = self.extractor.safe_get(tab, 'data', default=[])

            for item in tab_data:
                item_type = self.extractor.safe_get(item, 'type')
                info = self.extractor.safe_get(item, 'info', default={})

                # type=1115 表示实际车型
                # type=1137 表示年款分组标签（跳过）
                if item_type == '1115':
                    car_id = self.extractor.safe_get(info, 'car_id')

                    if car_id:
                        car_info = {
                            'car_id': car_id,
                            'car_name': self.extractor.safe_get(info, 'car_name', default=''),
                            'official_price': self.extractor.safe_get(info, 'official_price', default='暂无报价'),
                            'brand_id': self.extractor.safe_get(info, 'brand_id'),
                            'brand_name': self.extractor.safe_get(info, 'brand_name', default=''),
                            'series_id': self.extractor.safe_get(info, 'series_id'),
                            'series_name': self.extractor.safe_get(info, 'series_name', default=''),
                        }
                        car_list.append(car_info)

        return car_list

    def crawl_series(self, series_id, series_name=''):
        """
        爬取指定车系的车型列表
        :param series_id: 车系ID
        :param series_name: 车系名称（用于日志）
        :return: 车型列表
        """
        print(f"\n  → 正在爬取车系: {series_name} (ID: {series_id})")

        # 1. 获取页面
        html = self.fetch_series_page(series_id)
        if not html:
            return []

        # 2. 解析车型列表
        car_list = self.parse_car_models(html)

        if car_list:
            print(f"  ✓ 找到 {len(car_list)} 个车型")
        else:
            print(f"  ⚠ 未找到车型数据")

        return car_list

    def crawl_multiple_series(self, series_list):
        """
        批量爬取多个车系的车型
        :param series_list: 车系列表 [{series_id, series_name, ...}, ...]
        :return: 所有车型列表
        """
        all_cars = []

        print(f"\n开始爬取 {len(series_list)} 个车系的车型数据...")
        print("="*70)

        for i, series in enumerate(series_list, 1):
            series_id = series.get('series_id')
            series_name = series.get('series_name', f'车系{series_id}')

            print(f"\n[{i}/{len(series_list)}] {series_name}")

            cars = self.crawl_series(series_id, series_name)

            # 为每个车型添加车系信息
            for car in cars:
                car['series_official_price'] = series.get('official_price', '')
                car['series_dcd_score'] = series.get('dcd_score', 0)

            all_cars.extend(cars)

        print("\n" + "="*70)
        print(f"✓ 完成！总共获取到 {len(all_cars)} 个车型")

        return all_cars


if __name__ == '__main__':
    """测试模块"""
    print("="*70)
    print("       车系爬虫模块测试")
    print("="*70)

    # 测试单个车系
    crawler = SeriesCrawler()

    test_series = {
        'series_id': 9266,
        'series_name': '零跑B01',
        'official_price': '8.98-11.98万',
        'dcd_score': 376
    }

    cars = crawler.crawl_series(
        test_series['series_id'],
        test_series['series_name']
    )

    print("\n获取到的车型:")
    for car in cars:
        print(f"  {car['car_id']} - {car['car_name']} - {car['official_price']}万")
