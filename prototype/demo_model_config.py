#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
快速Demo - 车型配置爬取
验证技术路线：爬取单个车型的详细配置参数（重点：智驾芯片）
"""
import requests
import json
import time
from json_extractor import JSONExtractor
from config import HEADERS, TIMEOUT, REQUEST_DELAY


def fetch_model_config(model_id):
    """
    获取车型配置数据
    :param model_id: 车型ID（如250188）
    :return: 配置数据字典
    """
    url = f"https://www.dongchedi.com/auto/params-carIds-{model_id}"

    print(f"正在请求: {url}")
    time.sleep(REQUEST_DELAY)

    try:
        session = requests.Session()
        session.headers.update(HEADERS)
        response = session.get(url, timeout=TIMEOUT)
        response.raise_for_status()

        print(f"✓ 请求成功，状态码: {response.status_code}")
        print(f"✓ 响应大小: {len(response.text)} 字符")

        return response.text

    except requests.RequestException as e:
        print(f"✗ 请求失败: {str(e)}")
        return None


def parse_config_data(page_props):
    """
    解析配置参数
    :param page_props: pageProps数据
    :return: 配置字典
    """
    extractor = JSONExtractor()

    # 获取rawData.properties
    raw_data = extractor.safe_get(page_props, 'rawData', default={})
    properties = extractor.safe_get(raw_data, 'properties', default=[])

    print(f"\n找到 {len(properties)} 个配置分类")

    config_data = {
        'basic_info': {},      # 基本信息
        'body': {},            # 车身参数
        'motor': {},           # 电动机
        'battery': {},         # 电池/充电
        'intelligent': {},     # 智能化配置 ← 智驾芯片在这里
        'adas': {},            # 辅助驾驶配置
        'all_categories': []   # 所有分类名称
    }

    # 遍历所有配置分类
    for category in properties:
        category_text = extractor.safe_get(category, 'text', default='未知分类')
        category_key = extractor.safe_get(category, 'key', default='')
        items = extractor.safe_get(category, 'items', default=[])

        config_data['all_categories'].append(category_text)

        print(f"\n【{category_text}】 ({len(items)} 项)")

        # 重点关注智能化配置
        if '智能' in category_text or 'intelligent' in category_key.lower():
            print("  ★ 这是智能化配置分类！")
            for item in items[:10]:  # 只显示前10项
                param_text = extractor.safe_get(item, 'text', default='')
                param_value = extractor.safe_get(item, 'value', default='')
                param_symbol = extractor.safe_get(item, 'symbol', default='')

                print(f"    - {param_text}: {param_value} {param_symbol}")

                # 存储到intelligent字典
                config_data['intelligent'][param_text] = {
                    'value': param_value,
                    'symbol': param_symbol,
                    'type': '标配' if param_symbol == '●' else ('选装' if param_symbol == '○' else '无')
                }

        # 也关注辅助驾驶配置
        elif '辅助' in category_text or '驾驶' in category_text or 'adas' in category_key.lower():
            print("  ★ 这是辅助驾驶配置分类！")
            for item in items[:10]:
                param_text = extractor.safe_get(item, 'text', default='')
                param_value = extractor.safe_get(item, 'value', default='')
                param_symbol = extractor.safe_get(item, 'symbol', default='')

                print(f"    - {param_text}: {param_value} {param_symbol}")

                config_data['adas'][param_text] = {
                    'value': param_value,
                    'symbol': param_symbol,
                    'type': '标配' if param_symbol == '●' else ('选装' if param_symbol == '○' else '无')
                }

        # 电池配置
        elif '电池' in category_text or '充电' in category_text or 'battery' in category_key.lower():
            for item in items[:5]:
                param_text = extractor.safe_get(item, 'text', default='')
                param_value = extractor.safe_get(item, 'value', default='')
                print(f"    - {param_text}: {param_value}")

                config_data['battery'][param_text] = param_value

    return config_data


def main():
    """主函数"""
    print("="*70)
    print("       快速Demo - 车型配置爬取（验证智驾芯片提取）")
    print("="*70)

    # 测试车型：零跑B01 2025款 430舒享版
    model_id = 250188
    print(f"\n目标车型ID: {model_id}")
    print("示例URL: https://www.dongchedi.com/auto/params-carIds-250188")

    # 1. 获取页面HTML
    print("\n【步骤1】获取页面HTML...")
    html = fetch_model_config(model_id)
    if not html:
        print("✗ 获取页面失败")
        return

    # 2. 提取JSON数据
    print("\n【步骤2】提取JSON数据...")
    extractor = JSONExtractor()
    nextjs_data = extractor.extract_nextjs_data(html)

    if not nextjs_data:
        print("✗ 无法提取JSON数据")
        # 保存HTML用于调试
        with open('/home/user/dongchedi/prototype/logs/debug_model_config.html', 'w', encoding='utf-8') as f:
            f.write(html)
        print("⚠ HTML已保存到: prototype/logs/debug_model_config.html")
        return

    page_props = extractor.get_page_props(nextjs_data)
    if not page_props:
        print("✗ 无法获取pageProps")
        return

    print("✓ JSON数据提取成功")

    # 3. 解析配置数据
    print("\n【步骤3】解析配置数据...")
    config_data = parse_config_data(page_props)

    # 4. 输出关键结果
    print("\n" + "="*70)
    print("【验证结果】")
    print("="*70)

    print(f"\n总共发现 {len(config_data['all_categories'])} 个配置分类:")
    for i, cat in enumerate(config_data['all_categories'], 1):
        print(f"  {i}. {cat}")

    print("\n" + "="*70)
    print("【重点：智能化配置】")
    print("="*70)
    if config_data['intelligent']:
        for param_name, param_data in config_data['intelligent'].items():
            value = param_data['value']
            param_type = param_data['type']
            print(f"  {param_name}: {value} ({param_type})")

        # 特别检查智驾芯片
        print("\n" + "-"*70)
        chip_keywords = ['芯片', 'chip', '域控']
        chip_found = False
        for param_name, param_data in config_data['intelligent'].items():
            if any(keyword in param_name.lower() for keyword in chip_keywords):
                print(f"  ★ 找到智驾芯片: {param_name} = {param_data['value']}")
                chip_found = True

        if not chip_found:
            print("  ⚠ 未在智能化配置中找到明确的芯片字段")
    else:
        print("  ⚠ 未找到智能化配置数据")

    print("\n" + "="*70)
    print("【辅助驾驶配置】")
    print("="*70)
    if config_data['adas']:
        for param_name, param_data in config_data['adas'].items():
            value = param_data['value']
            param_type = param_data['type']
            print(f"  {param_name}: {value} ({param_type})")
    else:
        print("  ⚠ 未找到辅助驾驶配置数据")

    print("\n" + "="*70)
    print("【电池配置】")
    print("="*70)
    if config_data['battery']:
        for param_name, value in config_data['battery'].items():
            print(f"  {param_name}: {value}")
    else:
        print("  ⚠ 未找到电池配置数据")

    # 5. 保存完整数据为JSON
    output_file = '/home/user/dongchedi/prototype/logs/demo_config_output.json'
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(config_data, f, ensure_ascii=False, indent=2)
    print(f"\n✓ 完整配置数据已保存到: {output_file}")

    print("\n" + "="*70)
    print("✓ Demo验证完成！")
    print("="*70)

    # 总结
    print("\n【技术验证结论】")
    if config_data['intelligent']:
        print("✓ 成功提取智能化配置数据")
        print(f"✓ 智能化配置包含 {len(config_data['intelligent'])} 个参数")
    if config_data['adas']:
        print(f"✓ 辅助驾驶配置包含 {len(config_data['adas'])} 个参数")
    if config_data['battery']:
        print(f"✓ 电池配置包含 {len(config_data['battery'])} 个参数")

    print("\n技术路线可行！可以进行完整实现。")


if __name__ == '__main__':
    main()
