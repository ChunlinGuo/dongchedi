#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
懂车帝爬虫 - 完整版主程序
支持三级爬取：品牌 → 车系 → 车型配置
"""
import argparse
import datetime
from brand_crawler import BrandCrawler
from series_crawler import SeriesCrawler
from model_config_crawler import ModelConfigCrawler
from data_exporter import DataExporter


def main():
    parser = argparse.ArgumentParser(
        description='懂车帝完整爬虫 - 品牌/车系/车型配置',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog='''
示例:
  # 爬取零跑汽车的所有车型配置（包含智能芯片）
  python main_full.py --brand-id 207 --with-config

  # 只爬取品牌和车系（不爬配置）
  python main_full.py --brand-id 207

  # 限制爬取前2个车系的车型配置（用于测试）
  python main_full.py --brand-id 207 --with-config --limit-series 2
        '''
    )

    parser.add_argument('--brand-id', type=int, required=True,
                       help='品牌ID（如零跑汽车=207）')
    parser.add_argument('--with-config', action='store_true',
                       help='是否爬取车型详细配置（智能化、辅助驾驶等）')
    parser.add_argument('--limit-series', type=int, default=None,
                       help='限制爬取的车系数量（用于测试）')
    parser.add_argument('--output-dir', type=str, default='./data',
                       help='输出目录（默认: ./data）')

    args = parser.parse_args()

    print("="*70)
    print("       懂车帝完整爬虫 - 品牌/车系/车型配置")
    print("="*70)
    print(f"\n品牌ID: {args.brand_id}")
    print(f"爬取配置: {'是' if args.with_config else '否'}")
    if args.limit_series:
        print(f"限制车系数量: {args.limit_series}")
    print(f"输出目录: {args.output_dir}")

    # ============================================================
    # 第一步：爬取品牌和车系列表
    # ============================================================
    print("\n" + "="*70)
    print("【第一步】爬取品牌和车系列表")
    print("="*70)

    brand_crawler = BrandCrawler()
    brand_info, series_list = brand_crawler.crawl(args.brand_id)

    if not brand_info or not series_list:
        print("\n✗ 爬取品牌/车系失败，程序终止")
        return

    brand_name = brand_info.get('brand_name', '未知品牌')
    print(f"\n✓ 第一步完成：获取到 {brand_name} 的 {len(series_list)} 个车系")

    # 限制车系数量（用于测试）
    if args.limit_series:
        series_list = series_list[:args.limit_series]
        print(f"  (已限制为前 {len(series_list)} 个车系)")

    # 如果不需要配置，直接导出
    if not args.with_config:
        print("\n" + "="*70)
        print("【导出数据】品牌和车系列表")
        print("="*70)

        exporter = DataExporter(output_dir=args.output_dir)
        exporter.export_to_excel(brand_info, series_list)
        print("\n✓ 完成！")
        return

    # ============================================================
    # 第二步：爬取所有车系的车型列表
    # ============================================================
    print("\n" + "="*70)
    print("【第二步】爬取车型列表")
    print("="*70)

    series_crawler = SeriesCrawler()
    all_cars = series_crawler.crawl_multiple_series(series_list)

    if not all_cars:
        print("\n✗ 未获取到任何车型，程序终止")
        return

    print(f"\n✓ 第二步完成：获取到 {len(all_cars)} 个车型")

    # ============================================================
    # 第三步：爬取车型详细配置
    # ============================================================
    print("\n" + "="*70)
    print("【第三步】爬取车型详细配置（智能化、辅助驾驶、电池等）")
    print("="*70)

    config_crawler = ModelConfigCrawler()
    all_configs = config_crawler.crawl_multiple_models(all_cars)

    if not all_configs:
        print("\n⚠ 未获取到任何配置数据")
        # 即使没有配置，也导出车型列表
        print("\n" + "="*70)
        print("【导出数据】品牌/车系/车型列表（无配置）")
        print("="*70)

        exporter = DataExporter(output_dir=args.output_dir)
        exporter.export_with_configs(brand_info, series_list, all_cars, [])
        print("\n✓ 完成！")
        return

    print(f"\n✓ 第三步完成：获取到 {len(all_configs)} 个车型的配置")

    # ============================================================
    # 第四步：导出完整数据
    # ============================================================
    print("\n" + "="*70)
    print("【第四步】导出完整数据到Excel")
    print("="*70)

    exporter = DataExporter(output_dir=args.output_dir)
    filepath = exporter.export_with_configs(
        brand_info,
        series_list,
        all_cars,
        all_configs
    )

    # ============================================================
    # 统计汇总
    # ============================================================
    print("\n" + "="*70)
    print("【爬取统计】")
    print("="*70)
    print(f"  品牌: {brand_name} (ID: {args.brand_id})")
    print(f"  车系数量: {len(series_list)}")
    print(f"  车型数量: {len(all_cars)}")
    print(f"  配置数量: {len(all_configs)}")

    # 统计智能化配置
    total_intelligent = sum(len(c.get('intelligent', {})) for c in all_configs)
    print(f"  智能化配置参数: {total_intelligent}")

    # 统计有智能芯片的车型
    chip_count = 0
    for config in all_configs:
        intelligent = config.get('intelligent', {})
        for param_name in intelligent.keys():
            if '芯片' in param_name or 'chip' in param_name.lower():
                chip_count += 1
                break

    print(f"  包含智能芯片信息的车型: {chip_count}/{len(all_configs)}")

    print("\n" + "="*70)
    print("✓ 全部完成！")
    print(f"✓ 数据已保存到: {filepath}")
    print("="*70)


if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n用户中断，程序退出")
    except Exception as e:
        print(f"\n✗ 程序异常: {str(e)}")
        import traceback
        traceback.print_exc()
