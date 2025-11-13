#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
车型配置爬虫模块 - 获取车型详细配置（重点：智能化配置）
"""
import requests
import time
from json_extractor import JSONExtractor
from config import HEADERS, TIMEOUT, REQUEST_DELAY


class ModelConfigCrawler:
    """车型配置爬虫类 - 负责爬取车型详细配置"""

    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update(HEADERS)
        self.extractor = JSONExtractor()

    def get_config_url(self, car_id):
        """构建车型配置页面URL"""
        return f"https://www.dongchedi.com/auto/params-carIds-{car_id}"

    def fetch_config_page(self, car_id):
        """
        获取车型配置页面HTML
        :param car_id: 车型ID
        :return: HTML文本
        """
        url = self.get_config_url(car_id)

        try:
            time.sleep(REQUEST_DELAY)
            response = self.session.get(url, timeout=TIMEOUT)
            response.raise_for_status()
            return response.text
        except requests.RequestException as e:
            print(f"    ✗ 请求配置页面失败 (车型ID: {car_id}): {str(e)}")
            return None

    def parse_intelligent_config(self, html):
        """
        解析车型配置页面，提取智能化配置
        :param html: 页面HTML
        :return: 配置字典 {model_info, intelligent_config, adas_config, ...}
        """
        # 1. 提取JSON数据
        nextjs_data = self.extractor.extract_nextjs_data(html)
        if not nextjs_data:
            return None

        page_props = self.extractor.get_page_props(nextjs_data)
        if not page_props:
            return None

        # 2. 获取原始数据
        raw_data = self.extractor.safe_get(page_props, 'rawData', default={})
        car_info_list = self.extractor.safe_get(raw_data, 'car_info', default=[])

        if not car_info_list:
            return None

        car_info = car_info_list[0]

        # 3. 提取车型基本信息
        model_info = {
            'car_id': self.extractor.safe_get(car_info, 'car_id'),
            'car_name': self.extractor.safe_get(car_info, 'car_name'),
            'series_id': self.extractor.safe_get(car_info, 'series_id'),
            'series_name': self.extractor.safe_get(car_info, 'series_name'),
            'official_price': self.extractor.safe_get(car_info, 'official_price'),
            'car_year': self.extractor.safe_get(car_info, 'car_year'),
        }

        # 4. 获取配置参数
        config_values = self.extractor.safe_get(car_info, 'info', default={})

        # 5. 构建参数名称映射
        properties = self.extractor.safe_get(raw_data, 'properties', default=[])
        param_name_map = {}
        for prop in properties:
            key = self.extractor.safe_get(prop, 'key')
            text = self.extractor.safe_get(prop, 'text')
            if key and text:
                param_name_map[key] = text

        # 6. 分类提取配置
        config_data = {
            'model_info': model_info,
            'intelligent': {},      # 智能化配置 ⭐ 重点
            'adas': {},            # 辅助驾驶配置
            'battery': {},         # 电池配置
            'motor': {},           # 电动机配置
        }

        # 关键词定义
        intelligent_keywords = ['intelligent', 'chip', '芯片', '智能', 'ota', '车联网', '语音', '系统']
        adas_keywords = ['adas', '辅助', '驾驶', 'cruise', '巡航', '泊车', '车道', '刹车']
        battery_keywords = ['battery', 'charge', '电池', '充电', '续航', 'cltc']
        motor_keywords = ['motor', 'power', 'torque', '电机', '功率', '扭矩']

        # 遍历所有配置值
        for param_key, param_data in config_values.items():
            if not isinstance(param_data, dict):
                continue

            value = self.extractor.safe_get(param_data, 'value', default='')
            icon_type = self.extractor.safe_get(param_data, 'icon_type', default=0)

            # 跳过空值
            if not value:
                continue

            # 图标类型映射：1=标配(●) 2=选装(○) 3=无(-)
            icon_text = {1: '●', 2: '○', 3: '-', 0: ''}.get(icon_type, '')

            # 获取参数中文名称
            param_name = param_name_map.get(param_key, param_key)

            # 分类存储
            param_lower = param_key.lower() + param_name.lower()

            param_info = {
                'key': param_key,
                'value': value,
                'icon': icon_text,
                'type': '标配' if icon_type == 1 else ('选装' if icon_type == 2 else ('无' if icon_type == 3 else ''))
            }

            if any(kw in param_lower for kw in intelligent_keywords):
                config_data['intelligent'][param_name] = param_info
            elif any(kw in param_lower for kw in adas_keywords):
                config_data['adas'][param_name] = param_info
            elif any(kw in param_lower for kw in battery_keywords):
                config_data['battery'][param_name] = param_info
            elif any(kw in param_lower for kw in motor_keywords):
                config_data['motor'][param_name] = param_info

        return config_data

    def crawl_model_config(self, car_id, car_name=''):
        """
        爬取指定车型的配置
        :param car_id: 车型ID
        :param car_name: 车型名称（用于日志）
        :return: 配置字典
        """
        print(f"    → 爬取车型配置: {car_name} (ID: {car_id})")

        # 1. 获取页面
        html = self.fetch_config_page(car_id)
        if not html:
            return None

        # 2. 解析配置
        config_data = self.parse_intelligent_config(html)

        if config_data:
            intelligent_count = len(config_data.get('intelligent', {}))
            adas_count = len(config_data.get('adas', {}))
            battery_count = len(config_data.get('battery', {}))
            motor_count = len(config_data.get('motor', {}))

            print(f"    ✓ 智能化: {intelligent_count} | 辅助驾驶: {adas_count} | 电池: {battery_count} | 电机: {motor_count}")

            # 特别显示智能芯片
            intelligent = config_data.get('intelligent', {})
            for param_name, param_info in intelligent.items():
                if '芯片' in param_name or 'chip' in param_name.lower():
                    print(f"    ★ {param_name}: {param_info['value']}")
        else:
            print(f"    ✗ 解析配置失败")

        return config_data

    def crawl_multiple_models(self, car_list):
        """
        批量爬取多个车型的配置
        :param car_list: 车型列表 [{car_id, car_name, ...}, ...]
        :return: 配置列表
        """
        all_configs = []

        print(f"\n开始爬取 {len(car_list)} 个车型的配置数据...")
        print("="*70)

        for i, car in enumerate(car_list, 1):
            car_id = car.get('car_id')
            car_name = car.get('car_name', f'车型{car_id}')
            series_name = car.get('series_name', '')

            print(f"\n  [{i}/{len(car_list)}] {series_name} - {car_name}")

            config_data = self.crawl_model_config(car_id, car_name)

            if config_data:
                # 添加车型基本信息
                config_data['brand_id'] = car.get('brand_id')
                config_data['brand_name'] = car.get('brand_name', '')
                config_data['series_id'] = car.get('series_id')

                all_configs.append(config_data)

        print("\n" + "="*70)
        print(f"✓ 完成！成功获取 {len(all_configs)}/{len(car_list)} 个车型的配置")

        return all_configs


if __name__ == '__main__':
    """测试模块"""
    print("="*70)
    print("       车型配置爬虫模块测试")
    print("="*70)

    # 测试单个车型
    crawler = ModelConfigCrawler()

    test_car = {
        'car_id': 250188,
        'car_name': '430舒享版',
        'series_name': '零跑B01',
        'brand_id': 207,
        'brand_name': '零跑汽车',
        'series_id': 9266
    }

    config = crawler.crawl_model_config(
        test_car['car_id'],
        test_car['car_name']
    )

    if config:
        print("\n智能化配置:")
        for param_name, param_info in config['intelligent'].items():
            print(f"  {param_name}: {param_info['value']} {param_info['icon']}")
