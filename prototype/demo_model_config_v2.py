#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
快速Demo v2 - 车型配置爬取（修正版）
正确解析数据结构：car_info.info包含实际配置值
"""
import requests
import json
import time
from json_extractor import JSONExtractor
from config import HEADERS, TIMEOUT, REQUEST_DELAY


def fetch_model_config(model_id):
    """获取车型配置数据"""
    url = f"https://www.dongchedi.com/auto/params-carIds-{model_id}"

    print(f"正在请求: {url}")
    time.sleep(REQUEST_DELAY)

    try:
        session = requests.Session()
        session.headers.update(HEADERS)
        response = session.get(url, timeout=TIMEOUT)
        response.raise_for_status()

        print(f"✓ 请求成功，状态码: {response.status_code}")
        return response.text

    except requests.RequestException as e:
        print(f"✗ 请求失败: {str(e)}")
        return None


def parse_config_data(page_props):
    """
    解析配置参数（修正版）
    正确的数据结构：
    - properties: 参数定义和分类
    - car_info[0].info: 实际配置值
    """
    extractor = JSONExtractor()

    raw_data = extractor.safe_get(page_props, 'rawData', default={})
    properties = extractor.safe_get(raw_data, 'properties', default=[])
    car_info_list = extractor.safe_get(raw_data, 'car_info', default=[])

    if not car_info_list:
        print("✗ 未找到car_info数据")
        return None

    car_info = car_info_list[0]

    # 提取车型基本信息
    model_info = {
        'car_id': extractor.safe_get(car_info, 'car_id'),
        'car_name': extractor.safe_get(car_info, 'car_name'),
        'series_id': extractor.safe_get(car_info, 'series_id'),
        'series_name': extractor.safe_get(car_info, 'series_name'),
        'official_price': extractor.safe_get(car_info, 'official_price'),
        'car_year': extractor.safe_get(car_info, 'car_year'),
    }

    print(f"\n车型信息:")
    print(f"  车型ID: {model_info['car_id']}")
    print(f"  车型名称: {model_info['series_name']} {model_info['car_name']}")
    print(f"  官方价格: {model_info['official_price']}")
    print(f"  年款: {model_info['car_year']}")

    # 获取实际配置值
    config_values = extractor.safe_get(car_info, 'info', default={})
    print(f"\n配置参数总数: {len(config_values)}")

    # 构建参数名称映射（从properties）
    param_name_map = {}
    for prop in properties:
        key = extractor.safe_get(prop, 'key')
        text = extractor.safe_get(prop, 'text')
        if key and text:
            param_name_map[key] = text

    # 分类存储配置
    config_data = {
        'model_info': model_info,
        'intelligent': {},      # 智能化配置
        'adas': {},            # 辅助驾驶配置
        'battery': {},         # 电池配置
        'motor': {},           # 电动机配置
        'body': {},            # 车身参数
        'other': {}            # 其他配置
    }

    # 智能化关键词
    intelligent_keywords = ['intelligent', 'chip', '芯片', '智能', 'ota', '车联网', '语音']
    adas_keywords = ['adas', '辅助', '驾驶', 'cruise', '巡航', '泊车', '车道']
    battery_keywords = ['battery', 'charge', '电池', '充电', '续航', 'cltc']
    motor_keywords = ['motor', 'power', 'torque', '电机', '功率', '扭矩']
    body_keywords = ['length', 'width', 'height', 'weight', '长', '宽', '高', '轴距', '重量']

    # 遍历所有配置值
    for param_key, param_data in config_values.items():
        if not isinstance(param_data, dict):
            continue

        value = extractor.safe_get(param_data, 'value', default='')
        icon_type = extractor.safe_get(param_data, 'icon_type', default=0)

        # 图标类型映射：1=标配(●) 2=选装(○) 3=无(-)
        icon_text = {1: '●标配', 2: '○选装', 3: '-无', 0: ''}.get(icon_type, '')

        # 获取参数中文名称
        param_name = param_name_map.get(param_key, param_key)

        # 分类存储
        param_lower = param_key.lower() + param_name.lower()

        if any(kw in param_lower for kw in intelligent_keywords):
            config_data['intelligent'][param_name] = {
                'key': param_key,
                'value': value,
                'icon_text': icon_text
            }
        elif any(kw in param_lower for kw in adas_keywords):
            config_data['adas'][param_name] = {
                'key': param_key,
                'value': value,
                'icon_text': icon_text
            }
        elif any(kw in param_lower for kw in battery_keywords):
            config_data['battery'][param_name] = {
                'key': param_key,
                'value': value,
                'icon_text': icon_text
            }
        elif any(kw in param_lower for kw in motor_keywords):
            config_data['motor'][param_name] = {
                'key': param_key,
                'value': value,
                'icon_text': icon_text
            }
        elif any(kw in param_lower for kw in body_keywords):
            config_data['body'][param_name] = {
                'key': param_key,
                'value': value,
                'icon_text': icon_text
            }
        else:
            config_data['other'][param_name] = {
                'key': param_key,
                'value': value,
                'icon_text': icon_text
            }

    return config_data


def main():
    """主函数"""
    print("="*70)
    print("       快速Demo v2 - 车型配置爬取（修正版）")
    print("="*70)

    model_id = 250188
    print(f"\n目标车型ID: {model_id}")

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
        return

    page_props = extractor.get_page_props(nextjs_data)
    if not page_props:
        print("✗ 无法获取pageProps")
        return

    print("✓ JSON数据提取成功")

    # 3. 解析配置数据
    print("\n【步骤3】解析配置数据...")
    config_data = parse_config_data(page_props)

    if not config_data:
        print("✗ 解析失败")
        return

    # 4. 输出关键结果
    print("\n" + "="*70)
    print("【重点：智能化配置】")
    print("="*70)
    if config_data['intelligent']:
        for param_name, param_data in config_data['intelligent'].items():
            value = param_data['value']
            icon = param_data['icon_text']
            print(f"  {param_name}: {value} {icon}")

        # 特别标记智驾芯片
        print("\n" + "-"*70)
        chip_found = False
        for param_name, param_data in config_data['intelligent'].items():
            if '芯片' in param_name or 'chip' in param_name.lower():
                print(f"  ★★★ 找到智驾芯片: {param_name} = {param_data['value']} ★★★")
                chip_found = True

        if not chip_found:
            print("  ⚠ 未找到明确的芯片字段")
    else:
        print("  ⚠ 未找到智能化配置数据")

    print("\n" + "="*70)
    print("【辅助驾驶配置】")
    print("="*70)
    if config_data['adas']:
        count = 0
        for param_name, param_data in config_data['adas'].items():
            if count >= 10:  # 只显示前10个
                print(f"  ... (还有 {len(config_data['adas']) - 10} 项)")
                break
            value = param_data['value']
            icon = param_data['icon_text']
            print(f"  {param_name}: {value} {icon}")
            count += 1
    else:
        print("  ⚠ 未找到辅助驾驶配置数据")

    print("\n" + "="*70)
    print("【电池配置】")
    print("="*70)
    if config_data['battery']:
        for param_name, param_data in config_data['battery'].items():
            value = param_data['value']
            icon = param_data['icon_text']
            print(f"  {param_name}: {value} {icon}")
    else:
        print("  ⚠ 未找到电池配置数据")

    print("\n" + "="*70)
    print("【电动机配置】")
    print("="*70)
    if config_data['motor']:
        for param_name, param_data in config_data['motor'].items():
            value = param_data['value']
            icon = param_data['icon_text']
            print(f"  {param_name}: {value} {icon}")

    print("\n" + "="*70)
    print("【车身参数】")
    print("="*70)
    if config_data['body']:
        count = 0
        for param_name, param_data in config_data['body'].items():
            if count >= 10:
                print(f"  ... (还有 {len(config_data['body']) - 10} 项)")
                break
            value = param_data['value']
            print(f"  {param_name}: {value}")
            count += 1

    # 5. 统计汇总
    print("\n" + "="*70)
    print("【配置统计】")
    print("="*70)
    print(f"  智能化配置: {len(config_data['intelligent'])} 项")
    print(f"  辅助驾驶配置: {len(config_data['adas'])} 项")
    print(f"  电池配置: {len(config_data['battery'])} 项")
    print(f"  电动机配置: {len(config_data['motor'])} 项")
    print(f"  车身参数: {len(config_data['body'])} 项")
    print(f"  其他配置: {len(config_data['other'])} 项")

    # 6. 保存完整数据
    output_file = '/home/user/dongchedi/prototype/logs/demo_config_v2_output.json'
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(config_data, f, ensure_ascii=False, indent=2)
    print(f"\n✓ 完整配置数据已保存到: {output_file}")

    print("\n" + "="*70)
    print("✓ Demo验证完成！")
    print("="*70)

    # 总结
    print("\n【技术验证结论】")
    print("✓ 成功提取车型基本信息")
    if config_data['intelligent']:
        print(f"✓ 成功提取智能化配置 ({len(config_data['intelligent'])} 项)")
    if config_data['adas']:
        print(f"✓ 成功提取辅助驾驶配置 ({len(config_data['adas'])} 项)")
    if config_data['battery']:
        print(f"✓ 成功提取电池配置 ({len(config_data['battery'])} 项)")

    print("\n✅ 技术路线验证成功！可以进行完整实现。")


if __name__ == '__main__':
    main()
