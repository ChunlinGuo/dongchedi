"""
快速原型 - JSON数据提取器
核心功能：从懂车帝Next.js页面提取__NEXT_DATA__
"""
import json
import re
from bs4 import BeautifulSoup


class JSONExtractor:
    """JSON数据提取器"""

    @staticmethod
    def extract_nextjs_data(html):
        """
        从HTML中提取__NEXT_DATA__
        :param html: HTML字符串
        :return: 解析后的JSON数据，如果失败返回None
        """
        try:
            # 方法1：使用BeautifulSoup查找<script id="__NEXT_DATA__">
            soup = BeautifulSoup(html, 'html.parser')
            script_tag = soup.find('script', {'id': '__NEXT_DATA__', 'type': 'application/json'})

            if script_tag and script_tag.string:
                data = json.loads(script_tag.string)
                print("✓ 成功从__NEXT_DATA__标签提取数据")
                return data

            # 方法2：正则表达式（备用）
            pattern = r'<script id="__NEXT_DATA__"[^>]*>(.*?)</script>'
            match = re.search(pattern, html, re.DOTALL)

            if match:
                data = json.loads(match.group(1))
                print("✓ 成功通过正则表达式提取数据")
                return data

            print("✗ 未找到__NEXT_DATA__数据")
            return None

        except json.JSONDecodeError as e:
            print(f"✗ JSON解析失败: {str(e)}")
            return None
        except Exception as e:
            print(f"✗ 数据提取失败: {str(e)}")
            return None

    @staticmethod
    def get_page_props(nextjs_data):
        """
        获取pageProps数据（实际业务数据所在位置）
        :param nextjs_data: __NEXT_DATA__数据
        :return: pageProps字典
        """
        if not nextjs_data:
            return None

        try:
            page_props = nextjs_data.get('props', {}).get('pageProps', {})
            if page_props:
                print(f"✓ 成功获取pageProps，包含 {len(page_props)} 个键")
            return page_props
        except Exception as e:
            print(f"✗ 获取pageProps失败: {str(e)}")
            return None

    @staticmethod
    def safe_get(data, *keys, default=None):
        """
        安全获取嵌套字典的值
        :param data: 字典
        :param keys: 键路径
        :param default: 默认值
        :return: 值或默认值

        示例：
        safe_get(data, 'props', 'pageProps', 'brand', 'name', default='未知品牌')
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


# 测试代码
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
                    }
                }
            }
        }
        </script>
    </head>
    <body></body>
    </html>
    '''

    print("=== 测试JSON提取器 ===\n")

    extractor = JSONExtractor()

    # 测试提取
    data = extractor.extract_nextjs_data(test_html)
    if data:
        print(f"\n提取的数据: {json.dumps(data, indent=2, ensure_ascii=False)}")

    # 测试获取pageProps
    page_props = extractor.get_page_props(data)
    if page_props:
        print(f"\nPageProps: {json.dumps(page_props, indent=2, ensure_ascii=False)}")

    # 测试安全获取
    brand_name = extractor.safe_get(page_props, 'brand', 'name', default='未知品牌')
    print(f"\n品牌名称: {brand_name}")

    print("\n✓ 测试完成")
