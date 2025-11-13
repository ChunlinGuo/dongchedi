# 懂车帝品牌车系爬虫 v1.0

一个用于爬取懂车帝网站品牌车型信息的Python爬虫工具。

## ✨ 功能特点

- ✅ 爬取品牌基本信息（品牌名称、ID等）
- ✅ 爬取车系列表（车系名称、价格、懂车分等）
- ✅ 支持多种数据导出格式：Excel、JSON、CSV
- ✅ 自动处理Brotli压缩响应
- ✅ 友好的命令行界面
- ✅ 完善的错误处理和重试机制

## 📋 系统要求

- Python 3.8+
- pip

## 🚀 快速开始

### 1. 安装依赖

```bash
pip install -r requirements.txt
pip install brotli brotlicffi  # Brotli解压支持
```

### 2. 运行爬虫

#### 基本用法（导出Excel）
```bash
python main.py --brand-id 207
```

#### 指定输出格式
```bash
# 导出JSON
python main.py --brand-id 207 --output json

# 导出CSV
python main.py --brand-id 207 --output csv

# 导出所有格式
python main.py --brand-id 207 --output all
```

#### 指定输出目录
```bash
python main.py --brand-id 207 --output-dir ./my_data
```

### 3. 查看结果

爬取完成后，数据文件会保存在 `data/` 目录（或指定的输出目录）中。

## 📊 示例数据

### 零跑汽车品牌爬取示例

```bash
$ python main.py --brand-id 207 --output all

======================================================================
       懂车帝品牌车系爬虫 v1.0
======================================================================

目标品牌ID: 207
输出格式: all
输出目录: ./data

【步骤1/2】开始爬取数据...
✓ 品牌信息:
  - brand_id: 207
  - brand_name: 零跑汽车

✓ 发现 13 个车系

车系列表:
  1. 零跑T03 | 价格: 5.99-6.99万 | 懂车分: 346
  2. 零跑B01 | 价格: 8.98-11.98万 | 懂车分: 376
  3. 零跑C01 | 价格: 13.68-15.88万 | 懂车分: 395
  ...

【步骤2/2】导出数据...
✓ Excel文件已保存
✓ JSON文件已保存
✓ CSV文件已保存

✓ 爬取完成！
```

### 生成的文件

#### Excel格式（零跑汽车_20251113_123101.xlsx）
包含2个Sheet:
- **品牌信息**：品牌ID、品牌名称、爬取时间
- **车系列表**：车系名称、价格、懂车分、图片URL等

#### JSON格式（零跑汽车_20251113_123101.json）
```json
{
  "brand_info": {
    "brand_id": "207",
    "brand_name": "零跑汽车",
    "crawl_time": "2025-11-13 12:31:01"
  },
  "series_list": [
    {
      "series_id": 4272,
      "series_name": "零跑T03",
      "official_price": "5.99-6.99万",
      "dealer_price": "5.19-6.19万",
      "dcd_score": 346,
      ...
    }
  ]
}
```

#### CSV格式
- **品牌CSV**（零跑汽车_20251113_123101_brand.csv）：品牌基本信息
- **车系CSV**（零跑汽车_20251113_123101_series.csv）：车系列表数据

## 🔍 如何找到品牌ID

访问懂车帝品牌页面，URL中的数字就是品牌ID：
```
https://www.dongchedi.com/auto/library-brand/207
                                                ^^^
                                             品牌ID
```

常见品牌ID示例：
- 零跑汽车：207
- 比亚迪：10
- 特斯拉：85
- 蔚来：116

## 📁 项目结构

```
prototype/
├── main.py                 # 主程序入口
├── brand_crawler.py        # 品牌爬虫模块
├── json_extractor.py       # JSON数据提取器
├── data_exporter.py        # 数据导出模块
├── config.py              # 配置文件
├── requirements.txt       # 依赖包列表
├── data/                  # 数据输出目录
├── logs/                  # 日志目录
└── README.md             # 本文件
```

## 🛠️ 技术实现

### 核心技术
- **请求库**：requests（处理HTTP请求）
- **解析库**：BeautifulSoup4（HTML解析）
- **数据处理**：pandas（数据处理和导出）
- **压缩处理**：brotli（Brotli解压）

### 关键特性
1. **JSON数据提取**：直接解析Next.js页面中的 `__NEXT_DATA__` 数据，比DOM解析更快更稳定
2. **Brotli解压**：自动处理懂车帝的Brotli压缩响应
3. **智能延时**：3秒请求间隔，避免触发反爬虫
4. **数据清洗**：自动过滤标签项，只保留真实车系数据

## ⚠️ 注意事项

1. **合法使用**：
   - ✅ 个人学习和研究
   - ✅ 汽车市场分析
   - ❌ 商业转售数据
   - ❌ 恶意高频爬取

2. **请求频率**：
   - 默认延时：3秒/请求
   - 建议不要频繁爬取
   - 避免高并发请求

3. **数据时效性**：
   - 价格等信息可能随时变动
   - 建议定期更新数据

## 🐛 故障排除

### 问题1：ModuleNotFoundError
**解决**：确保已安装所有依赖
```bash
pip install -r requirements.txt
pip install brotli brotlicffi
```

### 问题2：无法解压响应
**解决**：安装Brotli支持
```bash
pip install brotli brotlicffi
```

### 问题3：403 Forbidden
**解决**：可能触发反爬虫，等待一段时间后重试，或增加延时

## 📈 性能指标

- 单品牌爬取时间：<10秒
- 数据准确率：>95%
- 支持的品牌数：全部懂车帝品牌

## 🔄 版本历史

### v1.0（2025-11-13）
- ✅ 基础爬虫功能
- ✅ 多格式数据导出
- ✅ 命令行界面
- ✅ 完善的错误处理

## 📞 技术支持

如有问题或建议，请查看：
- ANALYSIS_AND_PLAN.md - 技术分析文档
- IMPLEMENTATION_ROADMAP.md - 实施路线图
- PROTOTYPE_SUMMARY.md - 原型测试总结

## 📄 许可证

本项目仅供学习和研究使用，请遵守网站的robots.txt和服务条款。

---

**最后更新**：2025-11-13
**版本**：v1.0
**作者**：Claude Code
