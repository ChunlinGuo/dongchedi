"""
数据导出模块 - 支持Excel、JSON、CSV格式
"""
import pandas as pd
import json
from pathlib import Path
import datetime


class DataExporter:
    """数据导出器"""

    def __init__(self, output_dir='./data'):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(exist_ok=True)

    def export_to_excel(self, brand_info, series_list, filename=None):
        """
        导出为Excel文件（多个Sheet）
        :param brand_info: 品牌信息字典
        :param series_list: 车系列表
        :param filename: 文件名（可选）
        :return: 保存的文件路径
        """
        if not filename:
            brand_name = brand_info.get('brand_name', 'unknown')
            timestamp = datetime.datetime.now().strftime('%Y%m%d_%H%M%S')
            filename = f"{brand_name}_{timestamp}.xlsx"

        filepath = self.output_dir / filename

        # 创建Excel写入器
        with pd.ExcelWriter(filepath, engine='openpyxl') as writer:
            # Sheet 1: 品牌信息
            brand_df = pd.DataFrame([brand_info])
            brand_df.to_excel(writer, sheet_name='品牌信息', index=False)

            # Sheet 2: 车系列表
            if series_list:
                series_df = pd.DataFrame(series_list)
                series_df.to_excel(writer, sheet_name='车系列表', index=False)

        print(f"✓ Excel文件已保存: {filepath}")
        return str(filepath)

    def export_to_json(self, brand_info, series_list, filename=None):
        """
        导出为JSON文件
        :param brand_info: 品牌信息字典
        :param series_list: 车系列表
        :param filename: 文件名（可选）
        :return: 保存的文件路径
        """
        if not filename:
            brand_name = brand_info.get('brand_name', 'unknown')
            timestamp = datetime.datetime.now().strftime('%Y%m%d_%H%M%S')
            filename = f"{brand_name}_{timestamp}.json"

        filepath = self.output_dir / filename

        data = {
            'brand_info': brand_info,
            'series_list': series_list,
            'total_series': len(series_list),
            'export_time': datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        }

        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)

        print(f"✓ JSON文件已保存: {filepath}")
        return str(filepath)

    def export_to_csv(self, brand_info, series_list, filename_prefix=None):
        """
        导出为CSV文件（品牌和车系分开保存）
        :param brand_info: 品牌信息字典
        :param series_list: 车系列表
        :param filename_prefix: 文件名前缀（可选）
        :return: 保存的文件路径列表
        """
        if not filename_prefix:
            brand_name = brand_info.get('brand_name', 'unknown')
            timestamp = datetime.datetime.now().strftime('%Y%m%d_%H%M%S')
            filename_prefix = f"{brand_name}_{timestamp}"

        filepaths = []

        # 品牌信息CSV
        brand_filepath = self.output_dir / f"{filename_prefix}_brand.csv"
        brand_df = pd.DataFrame([brand_info])
        brand_df.to_csv(brand_filepath, index=False, encoding='utf-8-sig')  # utf-8-sig for Excel
        filepaths.append(str(brand_filepath))
        print(f"✓ 品牌CSV已保存: {brand_filepath}")

        # 车系列表CSV
        if series_list:
            series_filepath = self.output_dir / f"{filename_prefix}_series.csv"
            series_df = pd.DataFrame(series_list)
            series_df.to_csv(series_filepath, index=False, encoding='utf-8-sig')
            filepaths.append(str(series_filepath))
            print(f"✓ 车系CSV已保存: {series_filepath}")

        return filepaths

    def export_all_formats(self, brand_info, series_list):
        """
        导出所有格式（Excel + JSON + CSV）
        :param brand_info: 品牌信息字典
        :param series_list: 车系列表
        :return: 所有文件路径字典
        """
        brand_name = brand_info.get('brand_name', 'unknown')
        timestamp = datetime.datetime.now().strftime('%Y%m%d_%H%M%S')
        base_name = f"{brand_name}_{timestamp}"

        results = {
            'excel': self.export_to_excel(brand_info, series_list, f"{base_name}.xlsx"),
            'json': self.export_to_json(brand_info, series_list, f"{base_name}.json"),
            'csv': self.export_to_csv(brand_info, series_list, base_name)
        }

        print(f"\n✓ 所有格式导出完成！")
        return results


# 测试代码
if __name__ == '__main__':
    # 测试数据
    test_brand = {
        'brand_id': 207,
        'brand_name': '零跑汽车',
        'crawl_time': '2025-11-13 12:00:00'
    }

    test_series = [
        {
            'series_id': 4272,
            'series_name': '零跑T03',
            'official_price': '5.99-6.99万',
            'dcd_score': 346
        },
        {
            'series_id': 5831,
            'series_name': '零跑C11',
            'official_price': '14.88-20.98万',
            'dcd_score': 395
        }
    ]

    # 测试导出
    exporter = DataExporter()
    print("=== 测试Excel导出 ===")
    exporter.export_to_excel(test_brand, test_series, 'test_export.xlsx')

    print("\n=== 测试JSON导出 ===")
    exporter.export_to_json(test_brand, test_series, 'test_export.json')

    print("\n=== 测试CSV导出 ===")
    exporter.export_to_csv(test_brand, test_series, 'test_export')

    print("\n✓ 测试完成")
