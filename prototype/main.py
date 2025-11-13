#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
懂车帝爬虫 - 主程序入口
用法：python main.py --brand-id 207
"""
import argparse
from brand_crawler import BrandCrawler
from data_exporter import DataExporter


def main():
    """主函数"""
    # 解析命令行参数
    parser = argparse.ArgumentParser(description='懂车帝品牌车系爬虫')
    parser.add_argument('--brand-id', type=int, required=True, help='品牌ID（如：207表示零跑汽车）')
    parser.add_argument('--output', type=str, default='excel', choices=['excel', 'json', 'csv', 'all'],
                       help='输出格式：excel/json/csv/all（默认：excel）')
    parser.add_argument('--output-dir', type=str, default='./data', help='输出目录（默认：./data）')

    args = parser.parse_args()

    print("="*70)
    print("       懂车帝品牌车系爬虫 v1.0")
    print("="*70)
    print(f"\n目标品牌ID: {args.brand_id}")
    print(f"输出格式: {args.output}")
    print(f"输出目录: {args.output_dir}\n")

    try:
        # 1. 爬取数据
        print("【步骤1/2】开始爬取数据...")
        crawler = BrandCrawler()
        brand_info, series_list = crawler.crawl(args.brand_id)

        if not brand_info or not series_list:
            print("\n✗ 爬取失败：未获取到有效数据")
            return 1

        # 2. 导出数据
        print("\n【步骤2/2】导出数据...")
        exporter = DataExporter(output_dir=args.output_dir)

        if args.output == 'excel':
            filepath = exporter.export_to_excel(brand_info, series_list)
            print(f"\n✓ 数据已导出：{filepath}")

        elif args.output == 'json':
            filepath = exporter.export_to_json(brand_info, series_list)
            print(f"\n✓ 数据已导出：{filepath}")

        elif args.output == 'csv':
            filepaths = exporter.export_to_csv(brand_info, series_list)
            print(f"\n✓ 数据已导出：")
            for fp in filepaths:
                print(f"  - {fp}")

        elif args.output == 'all':
            results = exporter.export_all_formats(brand_info, series_list)
            print(f"\n✓ 所有格式已导出：")
            print(f"  - Excel: {results['excel']}")
            print(f"  - JSON: {results['json']}")
            for fp in results['csv']:
                print(f"  - CSV: {fp}")

        # 3. 总结
        print("\n" + "="*70)
        print("✓ 爬取完成！")
        print(f"  品牌：{brand_info.get('brand_name', '未知')}")
        print(f"  车系数量：{len(series_list)}")
        print("="*70)

        return 0

    except KeyboardInterrupt:
        print("\n\n✗ 用户中断")
        return 1
    except Exception as e:
        print(f"\n✗ 发生错误: {str(e)}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == '__main__':
    exit(main())
