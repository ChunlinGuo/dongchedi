#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
探索车系详情页面 - 获取车型ID列表
"""
import requests
import json
import time
from json_extractor import JSONExtractor
from config import HEADERS, TIMEOUT, REQUEST_DELAY


def explore_series_page(series_id):
    """
    探索车系页面，查找车型ID列表
    可能的URL格式：
    1. /auto/series/{series_id}
    2. /motor/series/{series_id}
    3. /auto/library-series-{series_id}
    """

    # 尝试不同的URL格式
    url_patterns = [
        f"https://www.dongchedi.com/auto/series/{series_id}",
        f"https://www.dongchedi.com/motor/series/{series_id}",
        f"https://www.dongchedi.com/auto/library-series-{series_id}"
    ]

    extractor = JSONExtractor()

    for url in url_patterns:
        print(f"\n尝试访问: {url}")
        time.sleep(REQUEST_DELAY)

        try:
            session = requests.Session()
            session.headers.update(HEADERS)
            response = session.get(url, timeout=TIMEOUT)

            print(f"  状态码: {response.status_code}")

            if response.status_code == 200:
                print(f"  ✓ 成功! 响应大小: {len(response.text)} 字符")

                # 尝试提取JSON数据
                nextjs_data = extractor.extract_nextjs_data(response.text)
                if nextjs_data:
                    print(f"  ✓ 找到__NEXT_DATA__")

                    # 保存数据以供分析
                    output_file = f'/home/user/dongchedi/prototype/logs/series_{series_id}_data.json'
                    with open(output_file, 'w', encoding='utf-8') as f:
                        json.dump(nextjs_data, f, ensure_ascii=False, indent=2)
                    print(f"  ✓ 数据已保存: {output_file}")

                    # 查看pageProps结构
                    page_props = extractor.get_page_props(nextjs_data)
                    if page_props:
                        print(f"\n  pageProps包含的键:")
                        for key in list(page_props.keys())[:20]:  # 显示前20个键
                            value = page_props[key]
                            value_type = type(value).__name__
                            if isinstance(value, (list, dict)):
                                length = len(value)
                                print(f"    - {key}: {value_type} (长度: {length})")
                            else:
                                print(f"    - {key}: {value_type}")

                        # 查找可能包含车型列表的字段
                        print(f"\n  查找车型相关字段...")
                        for key, value in page_props.items():
                            if isinstance(value, list) and len(value) > 0:
                                # 查看第一个元素
                                first_item = value[0]
                                if isinstance(first_item, dict):
                                    # 检查是否包含car_id或类似字段
                                    if any(k in str(first_item.keys()).lower() for k in ['car', 'model', 'vehicle']):
                                        print(f"\n  ★ 可能是车型列表: {key}")
                                        print(f"    列表长度: {len(value)}")
                                        print(f"    第一个元素的键: {list(first_item.keys())[:10]}")

                                        # 保存车型列表样本
                                        sample_file = f'/home/user/dongchedi/prototype/logs/series_{series_id}_{key}_sample.json'
                                        with open(sample_file, 'w', encoding='utf-8') as f:
                                            json.dump(value[:3], f, ensure_ascii=False, indent=2)
                                        print(f"    样本已保存: {sample_file}")

                    return True
                else:
                    print(f"  ✗ 未找到__NEXT_DATA__")
                    # 保存HTML用于分析
                    html_file = f'/home/user/dongchedi/prototype/logs/series_{series_id}_page.html'
                    with open(html_file, 'w', encoding='utf-8') as f:
                        f.write(response.text)
                    print(f"  HTML已保存: {html_file}")
            else:
                print(f"  ✗ 请求失败")

        except Exception as e:
            print(f"  ✗ 错误: {str(e)}")

    return False


def main():
    """主函数"""
    print("="*70)
    print("       探索车系页面 - 查找车型ID列表")
    print("="*70)

    # 使用零跑B01作为测试（series_id=9266）
    series_id = 9266
    series_name = "零跑B01"

    print(f"\n测试车系: {series_name} (ID: {series_id})")
    print("目标：找到该车系下所有车型的ID列表")

    success = explore_series_page(series_id)

    if success:
        print("\n" + "="*70)
        print("✓ 成功找到车系页面！请查看保存的数据文件。")
        print("="*70)
    else:
        print("\n" + "="*70)
        print("✗ 所有URL格式都失败了")
        print("="*70)
        print("\n备选方案：")
        print("1. 可能需要从配置对比页面获取车型列表")
        print("2. 或者直接从品牌页面的__NEXT_DATA__中查找车型信息")
        print("3. 或者使用API接口（需要抓包分析）")


if __name__ == '__main__':
    main()
