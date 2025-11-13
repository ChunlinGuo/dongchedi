# 车型详细配置爬取 - 扩展方案

## 📋 需求分析

**目标**：扩展现有爬虫，爬取每个车型的详细配置参数（如智驾域控芯片等）

**示例URL**：https://www.dongchedi.com/auto/params-carIds-250188

---

## 🔍 技术分析

### 1. 页面结构确认

✅ **配置页面使用Next.js**：数据在 `__NEXT_DATA__` 中
✅ **数据路径**：`pageProps.rawData.properties`
✅ **参数组织**：分层结构（20+个配置分类）

### 2. 数据结构示例

```json
{
  "props": {
    "pageProps": {
      "rawData": {
        "properties": [
          {
            "text": "智能化配置",
            "key": "intelligent_config",
            "type": "category",
            "items": [
              {
                "text": "车载智能芯片",
                "key": "car_intelligent_chip",
                "value": "高通骁龙8155",
                "symbol": "●"  // ●标配 ○选装 -无
              }
            ]
          }
        ]
      }
    }
  }
}
```

### 3. 关键配置分类

| 分类 | 包含参数示例 |
|------|-------------|
| **智能化配置** | 车载智能芯片、OTA升级、智能语音系统 |
| **辅助/操控配置** | L2级驾驶辅助、自适应巡航、自动泊车 |
| **电动机** | 电机类型、最大功率、最大扭矩 |
| **电池/充电** | 电池容量、充电时间、续航里程 |
| **车身** | 长宽高、轴距、整备质量 |
| **基本信息** | 厂商指导价、上市时间、能源类型 |

---

## 🚀 实施方案

### 方案架构（三级爬取）

```
品牌页面
  ↓ 爬取车系列表
车系页面
  ↓ 爬取车型列表（新增）
车型配置页面（新增）
  ↓ 爬取详细配置
Excel输出
```

---

## 📝 详细实施步骤

### **阶段一：扩展车系爬虫** ⏱️ 1-2小时

#### Step 1.1: 修改车系页面爬取逻辑
当前我们有 `series_id`，需要进一步获取该车系下的所有车型ID。

**车系页面URL**：`https://www.dongchedi.com/auto/series/{series_id}`

**新增功能**：
- 从车系页面提取车型列表
- 获取每个车型的 `model_id`（car_id）

**预期数据结构**：
```python
{
  'series_id': 9266,
  'series_name': '零跑B01',
  'models': [
    {'model_id': 250188, 'model_name': '2025款 430舒享版', 'price': '8.98万'},
    {'model_id': 250189, 'model_name': '2025款 510智享版', 'price': '9.98万'},
    ...
  ]
}
```

---

### **阶段二：创建车型配置爬虫** ⏱️ 2-3小时

#### Step 2.1: 创建 `model_config_crawler.py`

**核心功能**：
```python
class ModelConfigCrawler:
    def crawl(self, model_id):
        """
        爬取车型详细配置
        :param model_id: 车型ID（如250188）
        :return: 配置字典
        """
        url = f"https://www.dongchedi.com/auto/params-carIds-{model_id}"
        html = self.fetch_page(url)

        # 提取__NEXT_DATA__
        nextjs_data = self.extractor.extract_from_html(html)
        page_props = self.extractor.get_page_props(nextjs_data)

        # 解析配置参数
        config_data = self.parse_config_params(page_props)

        return config_data
```

#### Step 2.2: 配置参数解析器

**解析逻辑**：
```python
def parse_config_params(self, page_props):
    """解析配置参数"""
    raw_data = page_props.get('rawData', {})
    properties = raw_data.get('properties', [])

    config = {
        'basic_info': {},      # 基本信息
        'body': {},            # 车身参数
        'motor': {},           # 电动机
        'battery': {},         # 电池/充电
        'intelligent': {},     # 智能化配置 ← 智驾芯片在这里
        'adas': {},            # 辅助驾驶配置
        # ... 其他分类
    }

    for category in properties:
        category_key = category.get('key')
        category_items = category.get('items', [])

        for item in category_items:
            param_key = item.get('key')
            param_value = item.get('value')
            param_symbol = item.get('symbol')  # ●/○/-

            # 存储到对应分类
            if category_key == 'intelligent_config':
                config['intelligent'][param_key] = {
                    'name': item.get('text'),
                    'value': param_value,
                    'type': param_symbol  # 标配/选装/无
                }

    return config
```

---

### **阶段三：修改数据导出** ⏱️ 1-2小时

#### Step 3.1: 扩展Excel导出格式

**新增Sheet结构**：

| Sheet名称 | 内容 |
|-----------|------|
| 品牌信息 | 品牌ID、品牌名称、爬取时间 |
| 车系列表 | 车系ID、车系名称、价格区间 |
| **车型列表** ← 新增 | 车型ID、车型名称、具体价格 |
| **智能化配置** ← 新增 | 车型ID、车载芯片、OTA升级、语音系统 |
| **辅助驾驶** ← 新增 | 车型ID、驾驶辅助等级、巡航系统 |
| **电池配置** ← 新增 | 车型ID、电池容量、续航里程 |
| **完整配置** ← 新增 | 车型ID、所有配置参数（扁平化） |

#### Step 3.2: 配置参数扁平化

**示例输出（智能化配置Sheet）**：

| 车型ID | 车型名称 | 车载智能芯片 | 芯片类型 | OTA升级 | 智能语音 |
|--------|---------|-------------|---------|---------|---------|
| 250188 | 2025款 430舒享版 | 高通骁龙8155 | 标配 | 支持 | 标配 |
| 250189 | 2025款 510智享版 | 高通骁龙8155 | 标配 | 支持 | 标配 |

---

### **阶段四：整合完整流程** ⏱️ 1小时

#### Step 4.1: 更新主流程

```python
def crawl_brand_with_configs(brand_id):
    """爬取品牌完整信息（包含车型配置）"""

    # 1. 爬取品牌和车系
    brand_info, series_list = brand_crawler.crawl(brand_id)

    # 2. 遍历每个车系
    all_models_configs = []
    for series in series_list:
        series_id = series['series_id']

        # 2.1 获取车系下的车型列表
        models = series_crawler.get_models(series_id)

        # 2.2 爬取每个车型的配置
        for model in models:
            model_id = model['model_id']
            config = model_config_crawler.crawl(model_id)

            all_models_configs.append({
                'series_name': series['series_name'],
                'model_id': model_id,
                'model_name': model['model_name'],
                'config': config
            })

    # 3. 导出到Excel（多Sheet）
    exporter.export_full_data(brand_info, series_list, all_models_configs)
```

#### Step 4.2: 命令行参数扩展

```bash
# 基础模式（当前功能）
python main.py --brand-id 207

# 详细模式（新功能）
python main.py --brand-id 207 --detailed

# 只爬取指定车系的配置
python main.py --series-id 9266 --detailed

# 只爬取指定车型的配置
python main.py --model-id 250188
```

---

## 🎯 关键字段提取清单

### 优先级1（必须）

| 分类 | 字段名 | key值 | 示例值 |
|------|--------|-------|--------|
| **智能化配置** | 车载智能芯片 | car_intelligent_chip | 高通骁龙8155 |
| 智能化配置 | OTA升级 | ota_upgrade | 支持 |
| 智能化配置 | 车联网 | car_networking | 5G |
| **辅助驾驶** | 驾驶辅助等级 | adas_level | L2级 |
| 辅助驾驶 | 自适应巡航 | adaptive_cruise | 全速域 |
| 辅助驾�驶 | 自动泊车 | auto_parking | 支持 |

### 优先级2（重要）

| 分类 | 字段名 | key值 |
|------|--------|-------|
| 电池/充电 | 电池容量 | battery_capacity |
| 电池/充电 | CLTC续航里程 | cltc_range |
| 电池/充电 | 快充时间 | fast_charge_time |
| 电动机 | 最大功率 | max_power |
| 电动机 | 最大扭矩 | max_torque |
| 车身 | 长/宽/高 | length/width/height |

### 优先级3（可选）

- 座椅配置
- 多媒体配置
- 灯光配置
- 空调配置

---

## ⏱️ 时间估算

| 阶段 | 任务 | 预计时间 |
|------|------|---------|
| 阶段一 | 扩展车系爬虫（获取车型列表） | 1-2小时 |
| 阶段二 | 创建车型配置爬虫 | 2-3小时 |
| 阶段三 | 修改数据导出（多Sheet） | 1-2小时 |
| 阶段四 | 整合测试 | 1小时 |
| **总计** | | **5-8小时** |

---

## 📊 预期输出示例

### Excel文件结构（零跑汽车_详细配置_20251113.xlsx）

**Sheet 1: 品牌信息**
| brand_id | brand_name | crawl_time |
|----------|-----------|------------|
| 207 | 零跑汽车 | 2025-11-13 |

**Sheet 2: 车系列表**
| series_id | series_name | price_range | model_count |
|-----------|------------|-------------|-------------|
| 9266 | 零跑B01 | 8.98-11.98万 | 5 |

**Sheet 3: 车型列表**
| series_id | model_id | model_name | price |
|-----------|----------|-----------|-------|
| 9266 | 250188 | 2025款 430舒享版 | 8.98万 |
| 9266 | 250189 | 2025款 510智享版 | 9.98万 |

**Sheet 4: 智能化配置** ← 核心关注
| model_id | model_name | 车载智能芯片 | OTA升级 | 车联网 | 智能语音 |
|----------|-----------|-------------|---------|--------|---------|
| 250188 | 2025款 430舒享版 | 高通骁龙8155 | 支持 | 5G | 标配 |
| 250189 | 2025款 510智享版 | 高通骁龙8155 | 支持 | 5G | 标配 |

**Sheet 5: 辅助驾驶配置**
| model_id | 驾驶辅助等级 | 自适应巡航 | 自动泊车 | 车道保持 |
|----------|-------------|-----------|---------|---------|
| 250188 | L2级 | 全速域 | 支持 | 支持 |

**Sheet 6: 电池配置**
| model_id | 电池容量(kWh) | CLTC续航(km) | 快充时间 |
|----------|--------------|-------------|---------|
| 250188 | 42.8 | 430 | 0.5小时 |

---

## 🚨 注意事项

### 1. 性能考虑
- **请求量增加**：每个车型一次请求
  - 零跑B01有5个车型 → 5次额外请求
  - 零跑汽车13个车系，假设平均每个车系5个车型 → 65次请求
  - 建议延时：3-5秒/请求
  - **总耗时**：约3-5分钟/品牌

### 2. 数据量考虑
- 每个车型约100+配置参数
- Excel单Sheet建议不超过10000行
- 建议分Sheet存储不同配置分类

### 3. 反爬虫策略
- 增加随机延时（3-8秒）
- 每10个请求休息30秒
- 监控403/429错误

---

## 🎯 实施优先级建议

### 方案A：最小实现（推荐先做）⏱️ 2-3小时
1. 只爬取1个车型的配置（验证技术可行性）
2. 只提取智能化配置分类
3. 输出JSON验证数据结构

### 方案B：完整实现 ⏱️ 5-8小时
1. 爬取所有车型配置
2. 提取所有配置分类
3. 多Sheet Excel输出

### 方案C：优化版本 ⏱️ 额外2-3小时
1. 并发请求（谨慎使用）
2. 增量更新（只爬取新增车型）
3. 数据对比分析

---

## 🤔 下一步行动

请告诉我你的选择：

**选项1**：从方案A开始，先验证单个车型配置爬取
**选项2**：直接实施方案B，完整实现所有车型配置
**选项3**：让我先写一个快速demo验证技术路线

我的建议：**选项1**，先实现最小版本验证可行性，然后再扩展到完整版本。

---

**预计下一步**：
1. 创建 `model_config_crawler.py`
2. 实现单个车型配置爬取
3. 验证数据结构和字段
4. 输出到Excel验证

准备好了吗？ 🚀
