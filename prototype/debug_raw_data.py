#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
调试脚本 - 查看原始数据结构
"""
import requests
import json
import time
from json_extractor import JSONExtractor
from config import HEADERS, TIMEOUT, REQUEST_DELAY


def main():
    """主函数"""
    model_id = 250188
    url = f"https://www.dongchedi.com/auto/params-carIds-{model_id}"

    print(f"正在请求: {url}")
    time.sleep(REQUEST_DELAY)

    session = requests.Session()
    session.headers.update(HEADERS)
    response = session.get(url, timeout=TIMEOUT)

    print(f"✓ 请求成功，状态码: {response.status_code}")

    # 提取JSON数据
    extractor = JSONExtractor()
    nextjs_data = extractor.extract_nextjs_data(response.text)
    page_props = extractor.get_page_props(nextjs_data)

    # 保存完整的pageProps
    output_file = '/home/user/dongchedi/prototype/logs/raw_pageprops.json'
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(page_props, f, ensure_ascii=False, indent=2)

    print(f"\n✓ 原始pageProps已保存到: {output_file}")

    # 打印pageProps的顶层键
    print(f"\npageProps包含的顶层键:")
    for key in page_props.keys():
        value = page_props[key]
        value_type = type(value).__name__
        if isinstance(value, (list, dict)):
            length = len(value)
            print(f"  - {key}: {value_type} (长度: {length})")
        else:
            print(f"  - {key}: {value_type} = {value}")

    # 检查rawData结构
    raw_data = page_props.get('rawData', {})
    if raw_data:
        print(f"\nrawData包含的键:")
        for key in raw_data.keys():
            value = raw_data[key]
            value_type = type(value).__name__
            if isinstance(value, (list, dict)):
                length = len(value)
                print(f"  - {key}: {value_type} (长度: {length})")
            else:
                print(f"  - {key}: {value_type}")

    # 查看properties结构
    properties = raw_data.get('properties', [])
    if properties:
        print(f"\nproperties是一个列表，长度: {len(properties)}")
        print(f"\n第一个property的结构:")
        if len(properties) > 0:
            first_prop = properties[0]
            print(json.dumps(first_prop, ensure_ascii=False, indent=2))

        # 查找包含'智能'的分类
        print(f"\n查找智能化相关分类:")
        for i, prop in enumerate(properties):
            text = prop.get('text', '')
            if '智能' in text or '芯片' in text:
                print(f"\n找到分类 #{i}: {text}")
                print(json.dumps(prop, ensure_ascii=False, indent=2)[:500])


if __name__ == '__main__':
    main()
