# PETsARD Functional Design Document

## 🎯 整體架構設計原則

PETsARD 採用模組化設計，每個模組都遵循以下核心設計原則：

1. **Separation of Concerns**: 清楚分離資料載入、處理、合成、評估和報告功能
2. **Functional Programming**: 核心功能使用純函數和不可變資料結構
3. **Type Safety**: 強型別檢查和清晰的介面定義
4. **Backward Compatibility**: 保持向後相容性，確保現有程式碼可以無縫遷移
5. **Unified Interface**: 透過統一的公開介面提供功能，避免深層內部呼叫

## 📁 模組架構概覽

```
PETsARD/
├── petsard/
│   ├── loader/                 # 資料載入模組
│   │   ├── loader.py          # 主要載入器 (LoaderConfig, Loader)
│   │   ├── loader_base.py     # 載入器基底類別 (LoaderBase)
│   │   ├── loader_pandas.py   # Pandas 載入器實現
│   │   ├── splitter.py        # 資料分割器 (Splitter)
│   │   └── benchmarker.py     # 基準資料集管理 (BenchmarkerConfig, BaseBenchmarker, BenchmarkerRequests)
│   ├── metadater/             # 詮釋資料管理核心
│   │   ├── functional_design.md  # 模組功能設計文件
│   │   ├── __init__.py        # 公開 API 介面
│   │   ├── metadater.py       # 核心 Metadater 類別
│   │   ├── api.py             # 函數式 API 介面
│   │   ├── utils.py           # 工具函數
│   │   ├── metadata/          # Metadata 層 (多表格資料集)
│   │   ├── schema/            # Schema 層 (單表格結構)
│   │   ├── field/             # Field 層 (單欄位分析)
│   │   └── types/             # Types 層 (基礎資料型別)
│   ├── processor/             # 資料前處理模組
│   │   ├── functional_design.md  # 模組功能設計文件
│   │   └── ...
│   ├── synthesizer/           # 資料合成模組
│   │   ├── functional_design.md  # 模組功能設計文件
│   │   └── ...
│   ├── evaluator/             # 資料評估模組
│   │   ├── functional_design.md  # 模組功能設計文件
│   │   └── ...
│   ├── reporter/              # 結果報告模組
│   │   ├── functional_design.md  # 模組功能設計文件
│   │   └── ...
│   └── constrainer/           # 約束條件模組
│       ├── functional_design.md  # 模組功能設計文件
│       └── ...
├── functional_design.md       # 整體系統功能設計文件
└── tests/                     # 測試套件
```

### 📋 模組功能設計文件

每個維護的模組都有自己的 `functional_design.md` 文件，詳細描述：
- **模組職責**：明確定義模組的核心職責和功能範圍
- **公開 API**：只暴露必要的公開介面，避免深層內部呼叫
- **設計模式**：採用的設計模式和架構原則
- **模組互動**：與其他模組的清晰介面定義
- **使用範例**：具體的使用方式和最佳實踐

這種設計確保：
1. **模組獨立性**：每個模組都有清晰的邊界和職責
2. **介面簡潔**：模組間只透過公開 API 互動
3. **可維護性**：每個模組可以獨立開發和維護
4. **文檔完整**：每個模組都有完整的功能說明

## 🔧 核心模組設計

### 1. Loader 模組 (資料載入)

**設計理念**: 統一的資料載入介面，支援多種資料格式和來源

**核心功能**:
- 檔案格式支援 (CSV, Excel, JSON 等)
- 基準資料集管理
- 資料分割功能
- 詮釋資料自動生成

**架構特點**:
```python
# 函數式 API 設計
data, metadata = loader.load()  # 回傳 (data, metadata) 元組
split_data, split_metadata = splitter.split(data, metadata=metadata)
```

**與 Metadater 整合**:
- `Metadata` 類別內部使用 `Metadater.create_schema()`
- 保持向後相容的 API 介面
- 增強的型別推斷和詮釋資料生成

### 2. Metadater 模組 (詮釋資料管理核心)

**設計理念**: 函數式程式設計的詮釋資料管理系統

**核心功能**:
- 四層架構: Metadata → Schema → Field → Types
- 函數式 API 和管線處理
- 型別推斷和資料驗證
- 統一的公開介面

**架構特點**:
```python
# 函數式 API
field_metadata = analyze_field(data, field_name, config)

# 類別方法介面 (推薦使用)
schema = Metadater.create_schema(data, schema_id)
field = Metadater.create_field(series, field_name)
metadata = Metadater.create_metadata(metadata_id)
```

**設計模式**:
- **Pure Functions**: 核心業務邏輯使用純函數
- **Builder Pattern**: 複雜物件建構
- **Adapter Pattern**: 外部系統整合
- **Pipeline Pattern**: 資料處理管線

### 3. Processor 模組 (資料前處理)

**設計理念**: 可組合的資料前處理管線

**核心功能**:
- 缺失值處理
- 資料型別轉換
- 特徵編碼
- 資料標準化

**與 Metadater 整合**:
- 使用 Metadater 的型別推斷功能
- 基於詮釋資料的智慧處理決策

### 4. Synthesizer 模組 (資料合成)

**設計理念**: 多演算法支援的合成資料生成

**核心功能**:
- 多種合成演算法支援 (SDV, 自定義等)
- 條件合成
- 多表格合成
- 自定義合成器支援

**架構特點**:
- 使用 `petsard.metadater.types.SchemaMetadata` 進行詮釋資料管理
- SDV 轉換邏輯與 Metadater 架構整合

### 5. Evaluator 模組 (資料評估)

**設計理念**: 多維度的合成資料品質評估

**核心功能**:
- 統計相似性評估
- 機器學習效用評估
- 隱私風險評估
- 自定義評估器支援

**架構特點**:
- 使用 `petsard.metadater.types.data_types.safe_round` 進行數值處理
- 使用 `petsard.metadater.types.data_types.EvaluationScoreGranularityMap` 管理評估粒度
- 使用 `petsard.utils.load_external_module` 載入外部模組
- 使用 `Metadater.apply_schema_transformations` 進行資料型別對齊
- 使用 `petsard.metadater.Metadater` 進行詮釋資料管理
- **外部模組載入**:
  - **核心功能**: `petsard.utils.load_external_module` 提供通用的外部模組載入功能
  - **智能回退**: CustomSynthesizer 和 CustomEvaluator 優先使用 demo 功能，回退至核心功能

### 6. Reporter 模組 (結果報告)

**設計理念**: 靈活的結果匯出和報告生成

**核心功能**:
- 資料匯出 (save_data)
- 評估報告生成 (save_report)
- 多粒度報告 (global, columnwise, pairwise)
- 實驗結果比較

**架構特點**:
- 使用 `petsard.metadater.safe_round` 進行數值處理
- 使用 `petsard.utils.load_external_module` 載入外部模組
- `petsard.loader.metadata.Metadata` 內部使用 Metadater 進行詮釋資料管理
- 使用增強的 `_safe_merge` 方法處理 columnwise 和 pairwise 資料

### 7. Constrainer 模組 (約束條件)

**設計理念**: 靈活的資料約束和驗證系統

**核心功能**:
- 欄位約束 (範圍、型別等)
- 欄位組合約束
- NaN 值處理約束
- 自定義約束邏輯

## 🎯 設計模式應用

### 1. Adapter Pattern (適配器模式)
- **用途**: 整合外部系統和保持向後相容性
- **實例**: 
  - `petsard.metadater.adapters.legacy_adapter` - 舊版 API 相容
  - `petsard.metadater.adapters.pandas_adapter` - Pandas 整合

### 2. Builder Pattern (建構器模式)
- **用途**: 建構複雜的詮釋資料物件
- **實例**: 
  - `SchemaBuilder` - 建構 Schema 物件
  - `FieldBuilder` - 建構 Field 物件

### 3. Strategy Pattern (策略模式)
- **用途**: 支援多種演算法和處理策略
- **實例**: 
  - Synthesizer 的多演算法支援
  - Evaluator 的多評估方法

### 4. Pipeline Pattern (管線模式)
- **用途**: 資料處理流程組合
- **實例**: 
  - `FieldPipeline` - 欄位處理管線
  - Processor 的處理鏈

### 5. Factory Pattern (工廠模式)
- **用途**: 物件建立和配置
- **實例**: 
  - `create_field_analyzer()` - 建立欄位分析器
  - `create_schema_from_dataframe()` - 建立 Schema

## 📊 效益與優勢

### 1. 可維護性
- **模組化設計**: 清楚的職責分離
- **統一介面**: 避免深層內部呼叫
- **型別安全**: 編譯時期錯誤檢查

### 2. 可擴展性
- **函數式設計**: 易於組合和擴展
- **適配器模式**: 易於整合新系統
- **策略模式**: 易於添加新演算法

### 3. 可測試性
- **純函數**: 易於單元測試
- **依賴注入**: 易於模擬和測試
- **清楚介面**: 易於整合測試

### 4. 效能
- **不可變資料**: 支援快取和最佳化
- **函數式設計**: 天然支援並行處理
- **智慧型別推斷**: 減少不必要的計算

### 5. 向後相容性
- **適配器層**: 保持舊 API 可用
- **漸進式遷移**: 不破壞現有程式碼
- **統一介面**: 簡化升級過程

## 🚀 使用範例

### 完整工作流程
```python
from petsard import Executor

# 1. 載入和分割資料
executor = Executor('config.yaml')
executor.run()

# 2. 取得執行結果
results = executor.get_result()

# 3. 取得執行時間記錄
timing_data = executor.get_timing()  # 返回 pandas DataFrame
print(timing_data)  # 顯示各模組的執行時間統計

# 4. 使用函數式 API
from petsard.metadater import analyze_field, create_schema_from_dataframe

# 分析單一欄位
field_metadata = analyze_field(data['column'], 'column_name')

# 建立完整 Schema
schema = create_schema_from_dataframe(data, 'my_schema')

# 5. 使用類別方法
from petsard.metadater import Metadater

# 建立 Schema
schema = Metadater.create_schema(data, 'my_schema')

# 建立 Field
field = Metadater.create_field(data['column'], 'column_name')

# 建立 Metadata
metadata = Metadater.create_metadata('my_dataset')
```

### 自定義處理管線
```python
from petsard.metadater import FieldPipeline, analyze_field

# 建立處理管線
pipeline = (FieldPipeline()
    .with_stats(enabled=True)
    .with_logical_type_inference(enabled=True)
    .with_dtype_optimization(enabled=True))

# 處理欄位
initial_metadata = analyze_field(data, "field_name", compute_stats=False)
final_metadata = pipeline.process(data, initial_metadata)
```

## 🔮 未來發展方向

### 1. 效能最佳化
- 並行處理支援
- 記憶體使用最佳化
- 快取機制改善

### 2. 功能擴展
- 更多資料格式支援
- 進階約束條件
- 自動化調參

### 3. 生態系統整合
- 更多第三方工具整合
- 雲端服務支援
- 視覺化工具

### 4. 使用者體驗
- 更直觀的 API 設計
- 更好的錯誤訊息
- 更完整的文檔

## 📊 架構特點總結

### 模組架構
- **Config 模組**: 使用 SchemaMetadata 進行配置管理
- **Executor 模組**: 核心執行引擎，保持穩定的介面，提供執行時間記錄功能
- **Operator 模組**: 使用 SchemaMetadata 統一操作器介面
- **Evaluator 模組**: 使用 Metadater 架構進行評估
- **Reporter 模組**: 使用 Metadater 架構進行報告生成
- **Utils 模組**: 提供模組化的外部模組載入功能

### 架構優勢
- **型別統一**: 所有模組使用統一的 SchemaMetadata 格式
- **介面清晰**: 統一的公開 API，避免深層內部呼叫
- **模組化設計**: 核心功能與 demo 特定功能完全分離
- **智能回退**: CustomSynthesizer 和 CustomEvaluator 支援優雅降級
- **測試完整**: 每個模組都有完整的測試套件
- **文檔完善**: 每個模組都有詳細的功能設計文件

### 外部模組載入架構
- **核心功能**: `petsard.utils.load_external_module` 提供通用的外部模組載入
- **關注點分離**: 核心 utils 不包含 demo 特定的硬編碼路徑
- **智能回退**: CustomSynthesizer 和 CustomEvaluator 優先使用 demo 功能，失敗時回退至核心功能

PETsARD 採用現代的函數式和模組化設計，同時保持向後相容性和系統穩定性，提供清晰、可維護的模組架構。