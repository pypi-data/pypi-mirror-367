---
title: 測試覆蓋範圍
type: docs
weight: 88
prev: docs/developer-guide/experiment-name-in-reporter
next: docs/developer-guide/docker-development
---


## PETsARD 端到端功能測試

### `PETsARD 功能工作流程`

> tests/test_petsard.py

測試完整的 PETsARD 端到端工作流程，使用真實的 YAML 配置。這些測試驗證整個系統從資料載入到合成和評估的正確運作。

#### 核心工作流程測試

**`test_default_synthesis_workflow`**：測試基本資料合成管道
- **YAML 配置**：
  - `Loader`：載入基準 adult-income 資料集
  - `Preprocessor`：使用預設預處理方法
  - `Synthesizer`：使用預設合成方法
  - `Postprocessor`：使用預設後處理方法
  - `Reporter`：將合成資料儲存到輸出目錄
- **預期結果**：
  - 執行成功完成，`is_execution_completed() == True`
  - 合成資料包含所有 15 個預期欄位（age、workclass、fnlwgt、education 等）
  - 輸出資料是有效的 pandas DataFrame，行數 >0
  - 資料維持 adult-income 資料集結構

**`test_data_preprocessing_workflow`**：測試含缺失值處理的資料預處理
- **YAML 配置**：
  - `Loader`：載入含自定義空值（'?'）的 adult-income
  - `Preprocessor`：含缺失值處理和編碼的自定義序列
  - `Synthesizer`：預設合成方法
  - `Postprocessor`：預設後處理
  - `Reporter`：儲存處理後的資料
- **預期結果**：
  - 缺失值在合成前得到適當處理
  - 編碼應用於類別變數
  - 最終合成資料維持資料品質

**`test_data_constraining_workflow`**：測試含資料約束的合成
- **YAML 配置**：
  - `Loader`：標準 adult-income 資料集
  - `Preprocessor`：預設預處理
  - `Synthesizer`：預設合成
  - `Postprocessor`：預設後處理
  - `Constrainer`：欄位約束（年齡 18-65、每週工時 20-60）和教育欄位比例
  - `Reporter`：儲存約束後的資料
- **預期結果**：
  - 年齡值約束在 18-65 範圍內
  - 每週工時值約束在 20-60 範圍內
  - 教育欄位比例在容忍度內維持
  - 約束正確應用於合成資料

**`test_evaluation_workflow`**：測試含評估指標的合成
- **YAML 配置**：
  - `Loader`：Adult-income 資料集
  - `Splitter`：80/20 訓練/測試分割，1 個樣本
  - `Preprocessor`：預設預處理
  - `Synthesizer`：預設合成
  - `Postprocessor`：預設後處理
  - `Evaluator`：SDMetrics 品質報告評估
  - `Reporter`：儲存全域粒度的評估報告
- **預期結果**：
  - 資料正確分割以進行評估
  - 品質指標計算完成且可用
  - 時間資訊被捕獲且可存取
  - 評估報告成功生成

**`test_minimal_workflow`**：測試僅含資料載入的最小管道
- **YAML 配置**：
  - `Loader`：僅 Adult-income 資料集
  - `Reporter`：直接儲存載入的資料
- **預期結果**：
  - 資料成功載入，無需處理
  - 原始資料集結構得到保留
  - 展示最小可行的 PETsARD 工作流程

**`test_custom_sequence_preprocessing`**：測試自定義預處理管道
- **YAML 配置**：
  - `Loader`：Adult-income 資料集
  - `Preprocessor`：自定義 4 步序列（missing → outlier → scaler → encoder）
  - `Synthesizer`：預設合成
  - `Postprocessor`：預設後處理
  - `Reporter`：儲存最終處理的資料
- **預期結果**：
  - 所有預處理步驟按正確順序執行
  - 資料轉換依序應用
  - 最終資料準備好進行下游分析

#### 參數化模組執行測試

**`test_workflow_module_execution`**：測試不同工作流程配置
- **測試案例**：
  - `default-synthesis`：完整管道（Loader → Preprocessor → Synthesizer → Postprocessor）
  - `minimal`：基本管道（僅 Loader）
  - `with-splitter`：擴展管道（Loader → Splitter → Preprocessor → Synthesizer → Postprocessor）
- **預期結果**：每個工作流程執行預期的模組並產生有效結果

#### 配置驗證測試

**`test_invalid_yaml_config`**：測試無效配置的錯誤處理
- **YAML 配置**：包含不存在的無效模組（InvalidModule）
- **預期結果**：適當拋出 NameError、ValueError、KeyError 或 AttributeError

**`test_missing_required_config`**：測試空配置的錯誤處理
- **YAML 配置**：空配置檔案
- **預期結果**：對缺少必要組件拋出適當錯誤

#### 主要特色

- **Executor API 整合**：測試使用新的 `is_execution_completed()` 方法檢查執行狀態
- **結果提取**：使用輔助方法 `_extract_module_data()` 處理嵌套結果結構
- **真實資料測試**：使用實際基準資料集（adult-income）進行真實測試
- **配置多樣性**：測試多種 YAML 配置模式和模組組合
- **錯誤處理**：驗證無效配置的適當錯誤處理
- **端到端驗證**：確保從配置到最終輸出的完整工作流程運作

> **架構說明**：這些測試使用新的 Executor API 與 `is_execution_completed()` 狀態追蹤來驗證完整的 PETsARD 系統。`run()` 方法在當前版本返回 `None`，計劃在 v2.0.0 中返回成功/失敗狀態碼。結果透過 `get_result()` 方法存取，並透過嵌套工作流程結構處理。

### `Executor`

> tests/test_executor.py

測試 Executor 的主要功能：

- `test_default_values`：驗證預設配置值是否正確設定
- `test_update_config`：測試透過 update 方法更新配置值
- `test_validation_log_output_type`：測試日誌輸出類型設定的驗證：
  - 有效值（stdout、file、both）被接受
  - 無效值引發 ConfigError
- `test_validation_log_level`：測試日誌等級的驗證：
  - 有效等級（DEBUG、INFO、WARNING、ERROR、CRITICAL）被接受
  - 無效等級引發 ConfigError
- `test_executor_default_config`：測試使用不含 Executor 部分的 YAML 初始化時使用預設值
- `test_executor_custom_config`：驗證 YAML 中的自定義日誌設定是否正確應用
- `test_logger_setup`：測試日誌初始化的正確性：
  - 日誌等級
  - 多個處理器（檔案和控制台）
  - 處理器類型
- `test_logger_file_creation`：測試日誌檔案是否在指定目錄中創建並正確替換時間戳
- `test_logger_reconfiguration`：測試日誌器能否在初始設置後重新配置
- `test_get_config`：測試從檔案載入 YAML 配置



## 資料讀取

### `Loader`

> tests/loader/test_loader.py

測試 Loader 的主要功能：

- `test_loader_init_no_config`：驗證無配置初始化時會觸發 ConfigError
- `test_loader_init_with_filepath`：測試以檔案路徑初始化，檢查配置路徑和副檔名是否正確設定
- `test_handle_filepath_with_complex_name`：測試各種檔案路徑模式，包含：
  - 含多個點的路徑
  - 相對路徑 (./ 和 ../)
  - 絕對路徑
  - 混合大小寫的副檔名
- `test_loader_init_with_column_types`：驗證欄位型態設定是否正確存入配置
- `test_benchmark_loader`：使用模擬配置測試基準資料集初始化
- `test_load_csv`：測試 CSV 檔案載入是否返回正確的 DataFrame 和 Metadata 元組
- `test_load_excel`：測試 Excel 檔案載入是否返回正確的 DataFrame 和 Metadata 元組
- `test_benchmark_data_load`：使用模擬數據測試完整的基準資料載入流程
- `test_custom_na_values`：測試自定義空值的處理
- `test_custom_header_names`：測試使用自定義欄位標題載入資料

#### 邏輯型態系統測試

測試全面的邏輯型態推斷和驗證系統：

**重新設計的邏輯型態系統（2025 更新）：**
我們的邏輯型態系統已完全重新設計，避免與基本資料型態重疊，並提供清晰的語意意義檢測。

**可用的邏輯型態：**
- **文字型態**：`email`, `url`, `uuid`, `categorical`, `ip_address`（需要字串資料型態）
- **數值型態**：`percentage`, `currency`, `latitude`, `longitude`（需要數值資料型態）
- **識別碼型態**：`primary_key`（需要唯一性驗證）
- **已移除**：`datetime`, `date`, `time`, `duration`, `integer`, `decimal`, `text`, `foreign_key`（避免型態重疊）

**邏輯型態檢測測試（`tests/metadater/field/test_field_functions.py`）：**
- `test_email_logical_type_detection`：測試電子郵件模式檢測與正則表達式驗證（80% 閾值）
- `test_url_logical_type_detection`：測試網址模式檢測與 HTTP/HTTPS 協定驗證（80% 閾值）
- `test_uuid_logical_type_detection`：測試 8-4-4-4-12 十六進位格式的 UUID 格式檢測（95% 閾值）
- `test_ip_address_detection`：測試 IPv4/IPv6 模式識別與全面位址驗證（90% 閾值）
- `test_categorical_detection_via_cardinality`：測試使用動態閾值的 ASPL 基數分析分類檢測
- `test_primary_key_uniqueness_validation`：測試主鍵的 100% 唯一性要求與重複檢測
- `test_percentage_range_validation`：測試百分比值的 0-100 範圍驗證（95% 閾值）
- `test_currency_symbol_detection`：測試貨幣符號檢測與正值驗證的金額值檢測（80% 閾值）
- `test_latitude_longitude_detection`：測試地理座標範圍驗證（緯度 -90/90，經度 -180/180，95% 閾值）

**型態相容性系統測試：**
- `test_compatible_type_logical_combinations`：測試有效組合：
  - `string` + `email`, `url`, `uuid`, `categorical`, `ip_address` ✅
  - `numeric` + `percentage`, `currency`, `latitude`, `longitude` ✅
  - `int/string` + `primary_key` ✅
- `test_incompatible_type_logical_combinations`：測試觸發警告的無效組合：
  - `numeric` + `email`, `url`, `uuid`, `ip_address` ❌
  - `string` + `percentage`, `currency`, `latitude`, `longitude` ❌
- `test_logical_type_fallback_on_conflict`：測試型態衝突時自動回退到推斷
- `test_logical_type_priority_handling`：測試優先級系統（資料型態約束 > 邏輯型態提示）

**邏輯型態配置測試：**
- `test_logical_type_never_mode`：測試使用 "never" 設定停用邏輯型態推斷
- `test_logical_type_infer_mode`：測試使用 "infer" 設定的自動推斷
- `test_logical_type_explicit_specification`：測試透過配置強制指定特定邏輯型態與相容性驗證
- `test_logical_type_validation_thresholds`：測試信心閾值（文字模式 80%，數值範圍 90-95%）

**模式匹配和驗證測試：**
- `test_regex_pattern_validation`：測試更新的電子郵件、網址、UUID、IP 位址檢測正則表達式模式
- `test_numeric_range_validation`：測試緯度、經度、百分比值的範圍驗證
- `test_special_validator_functions`：測試地理座標的自定義驗證函數
- `test_pattern_confidence_scoring`：測試信心評分和基於閾值的分類
- `test_primary_key_duplicate_detection`：測試主鍵驗證的重複檢測機制

**錯誤處理和衝突解決測試：**
- `test_compatibility_warning_generation`：測試不相容 type/logical_type 組合的警告產生
- `test_automatic_fallback_mechanism`：測試衝突發生時的自動回退機制
- `test_logging_incompatibility_messages`：測試不相容原因的詳細記錄

> **重新設計的邏輯型態系統**：我們的專有邏輯型態推斷系統已重新設計，專注於語意意義檢測而不與基本資料型態重疊。系統使用模式識別、統計分析和驗證函數，具有嚴格的型態相容性規則和完整的衝突解決機制。

#### Schema 參數測試

測試 schema 參數系統的全面功能：

**全域參數測試（`TestSchemaGlobalParameters`）：**
- `test_compute_stats_parameter`：測試 `compute_stats` 全域參數的布林值驗證
- `test_optimize_dtypes_parameter`：測試 `optimize_dtypes` 全域參數的布林值驗證
- `test_sample_size_parameter`：測試 `sample_size` 全域參數的正整數驗證
- `test_sample_size_null`：測試 `sample_size` 參數接受 null 值
- `test_leading_zeros_parameter`：測試 `leading_zeros` 全域參數的有效值（"never", "num-auto", "leading_n"）
- `test_leading_zeros_invalid`：測試 `leading_zeros` 參數的無效值處理
- `test_nullable_int_parameter`：測試 `nullable_int` 全域參數的布林值驗證
- `test_nullable_int_invalid`：測試 `nullable_int` 參數的無效值處理
- `test_infer_logical_types_parameter`：測試 `infer_logical_types` 全域參數的布林值驗證
- `test_descriptive_parameters`：測試描述性參數（`title`, `description`, `version`）的字串驗證

**欄位參數測試（`TestSchemaFieldParameters`）：**
- `test_logical_type_parameter`：測試欄位層級 `logical_type` 參數的有效值驗證
- `test_leading_zeros_field_level`：測試欄位層級 `leading_zeros` 參數覆蓋全域設定
- `test_leading_zeros_field_invalid`：測試欄位層級 `leading_zeros` 參數的無效值處理

**參數衝突測試（`TestSchemaParameterConflicts`）：**
- `test_infer_logical_types_conflict`：測試 `infer_logical_types=true` 與欄位層級 `logical_type` 的衝突檢測

**Loader Schema 參數測試（`tests/loader/test_loader.py`）：**
- `TestLoaderSchemaParameters`：測試 Loader 中全域 schema 參數
- `TestLoaderSchemaFieldParameters`：測試 Loader 中欄位層級 schema 參數
- `TestLoaderSchemaParameterConflicts`：測試 Loader 中參數衝突檢測
- `TestLoaderSchemaEdgeCases`：測試 Loader 中 schema 邊界情況

**SchemaConfig 驗證測試（`tests/metadater/test_schema_types.py`）：**
- `test_schema_config_with_parameters`：測試 SchemaConfig 使用參數的初始化
- `test_schema_config_invalid_leading_zeros`：測試 SchemaConfig 無效 `leading_zeros` 值的錯誤處理
- `test_schema_config_invalid_nullable_int`：測試 SchemaConfig 無效 `nullable_int` 值的錯誤處理
- `test_schema_config_logical_type_conflict`：測試 SchemaConfig 中邏輯類型衝突的檢測

**FieldConfig 驗證測試（`tests/metadater/field/test_field_types.py`）：**
- `test_field_config_with_parameters`：測試 FieldConfig 使用參數的初始化
- `test_field_config_invalid_logical_type`：測試 FieldConfig 無效 `logical_type` 值的錯誤處理
- `test_field_config_invalid_leading_zeros`：測試 FieldConfig 無效 `leading_zeros` 值的錯誤處理
- `test_field_config_invalid_category_method`：測試 FieldConfig 無效 `category_method` 值的錯誤處理
- `test_field_config_invalid_datetime_precision`：測試 FieldConfig 無效 `datetime_precision` 值的錯誤處理

**邊界情況測試（`TestEdgeCases`）：**
- `test_empty_schema`：測試空 schema 的處理
- `test_schema_with_only_global_params`：測試僅含全域參數的 schema
- `test_invalid_global_parameter`：測試無效全域參數的錯誤處理
- `test_invalid_field_parameter`：測試無效欄位參數的錯誤處理
- `test_mixed_legacy_and_schema`：測試混合舊版和 schema 語法的相容性

**主要特色：**
- **兩層架構驗證**：測試全域參數與欄位參數的分層結構
- **參數衝突檢測**：自動檢測並報告邏輯衝突（如 `infer_logical_types` 與欄位 `logical_type`）
- **向後相容性**：確保參數系統與舊版 schema 語法完全相容
- **全面驗證**：涵蓋參數值範圍、型別、邏輯一致性檢查
- **邊界情況覆蓋**：測試空 schema、混合語法、無效參數組合等極端情況

> **Schema 參數系統**：實現了基於兩層架構的 schema 參數系統，提供全域參數（如 `compute_stats`, `optimize_dtypes`, `sample_size`）和欄位層級參數（如 `logical_type`, `leading_zeros`）的靈活配置，同時具備完整的參數衝突檢測和向後相容性保證。

#### 容易誤判資料類型處理功能

測試處理容易誤判、型別判斷模糊的資料：

- `test_preserve_raw_data_feature`：測試 preserve_raw_data 功能阻止 pandas 自動類型推斷：
  - 驗證當 preserve_raw_data=True 時使用 dtype=object
  - 測試與其他容易誤判資料處理功能的整合
  - 驗證原始資料保留的資料載入流程
- `test_leading_zero_detection_config`：測試 auto_detect_leading_zeros 配置：
  - 驗證配置是否正確儲存
  - 測試啟用和停用狀態
- `test_nullable_integer_config`：測試 force_nullable_integers 配置：
  - 驗證配置是否正確儲存
  - 測試啟用和停用狀態
- `test_ambiguous_data_config_combination`：測試所有容易誤判資料處理配置的組合：
  - preserve_raw_data + auto_detect_leading_zeros + force_nullable_integers
  - 驗證所有設定能正確協同運作
- `test_backward_compatibility`：測試新功能不會破壞現有功能：
  - 驗證新參數的預設值
  - 測試功能停用時的正常載入行為

#### 壓力測試

測試大型檔案處理和邊緣情況型別推斷：

**TestLoaderStress** - 逐步檔案大小測試，包含超時機制：
- `test_small_file_100mb`：測試 100MB 檔案（30秒超時）
- `test_medium_file_1gb`：測試 1GB 檔案（120秒超時）
- `test_large_file_3gb`：測試 3GB 檔案（300秒超時）
- `test_xlarge_file_5gb`：測試 5GB 檔案（600秒超時）

**TestLoaderTypeInference** - 邊緣情況型別推斷，99.9% 正常資料，0.1% 例外在最後：
- `test_int_with_string_exception`：測試整數資料含字串例外
- `test_float_with_null_exception`：測試浮點數資料含空值例外
- `test_string_with_numeric_exception`：測試字串資料含數值例外

**主要特色：**
- **記憶體監控**：使用 psutil 進行即時記憶體使用追蹤
- **超時保護**：載入超過時間限制時自動測試失敗
- **型別推斷驗證**：確保 99.9% 正常資料，0.1% 例外放置在檔案末尾
- **效能指標**：處理速度測量（MB/秒）和記憶體效率追蹤

**使用方式：**
```bash
# 執行所有壓力測試
pytest tests/loader/ -m stress -v

# 執行特定壓力測試類別
pytest tests/loader/test_loader.py::TestLoaderStress -v
pytest tests/loader/test_loader.py::TestLoaderTypeInference -v

# 執行壓力測試示範
python -c "from tests.loader.test_loader import run_stress_demo; run_stress_demo()"
```

### `Benchmarker`

> tests/loader/test_benchmarker.py

測試基準資料集處理：

- `test_basebenchmarker_init`：驗證 BaseBenchmarker 作為抽象類別無法被實例化
- `test_benchmarker_requests_init`：使用模擬的檔案系統操作測試 BenchmarkerRequests 初始化
- `test_download_success`：測試成功下載的情境，包含：
  - 模擬 HTTP 請求
  - 模擬檔案操作
  - SHA256 驗證檢查
- `test_verify_file_mismatch`：使用模擬的檔案內容測試 SHA256 驗證失敗的處理
- `test_download_request_fails`：測試下載請求失敗（HTTP 404 等）的處理方式
- `test_file_already_exists_hash_match`：測試檔案已存在且哈希值匹配的情境，確認直接使用本地檔案
- `test_verify_file_remove_fails`：測試在驗證過程中刪除檔案失敗的處理機制
- `test_init_file_exists_hash_match`：測試初始化時檔案存在且哈希值匹配的處理邏輯
- `test_file_content_change`：測試檔案內容變更後的哈希驗證機制，確保能正確檢測變更

#### `BenchmarkerConfig`

> tests/loader/test_loader.py::TestBenchmarkerConfig

測試管理基準資料集配置的 BenchmarkerConfig 類別：

- `test_benchmarker_config_requires_benchmark_name`：測試初始化時需要 benchmark_name 參數
- `test_benchmarker_config_initialization`：測試 BenchmarkerConfig 初始化與正確的屬性設定：
  - 基準名稱、檔案名稱、存取類型
  - 區域名稱、儲存桶名稱、SHA256 雜湊值
  - 與基準 YAML 配置載入的整合
- `test_benchmarker_config_get_benchmarker_config`：測試 get_benchmarker_config 方法：
  - 為 BenchmarkerRequests 返回正確的字典格式
  - 包含所有必要的鍵值（benchmark_filename、benchmark_bucket_name、benchmark_sha256、filepath）
  - 構建正確的本地基準檔案路徑
- `test_benchmarker_config_unsupported_benchmark`：測試不支援的基準資料集的錯誤處理
- `test_benchmarker_config_private_access_unsupported`：測試私有基準存取嘗試的錯誤處理

> **架構重構**：BenchmarkerConfig 已從 LoaderConfig 中提取出來，提供清晰的關注點分離。LoaderConfig 現在包含一個可選的 benchmarker_config 屬性，允許兩種不同的狀態：有或沒有基準功能。這種重構提高了程式碼的可維護性，並遵循單一職責原則。

## 資料處理

### `Processor`

#### 缺失值處理器

> tests/processor/test_missing.py

測試缺失值處理的全面類型相容性：

**MissingMean 測試（4 個測試）：**
- `test_mean_no_missing_values`：測試無缺失值的平均值填補
- `test_mean_with_missing_values`：測試有缺失值的平均值填補
- `test_mean_with_integer_dtype`：測試 pandas 可空整數類型（Int32、Int64）的平均值填補：
  - 驗證整數資料類型的正確處理，不會出現 TypeError
  - 測試平均值的自動四捨五入以符合整數相容性
  - 驗證轉換後的資料類型保持
- `test_mean_with_integer_dtype_fractional_mean`：測試平均值有小數部分時的填補：
  - 測試整數類型的銀行家舍入法（20.5 → 20）
  - 確保小數平均值的正確類型轉換

**MissingMedian 測試（4 個測試）：**
- `test_median_no_missing_values`：測試無缺失值的中位數填補
- `test_median_with_missing_values`：測試有缺失值的中位數填補
- `test_median_with_integer_dtype`：測試 pandas 可空整數類型（Int32、Int64）的中位數填補：
  - 驗證整數資料類型的正確處理，不會出現 TypeError
  - 測試中位數的自動四捨五入以符合整數相容性
  - 驗證轉換後的資料類型保持
- `test_median_with_integer_dtype_fractional_median`：測試中位數有小數部分時的填補：
  - 測試整數類型的銀行家舍入法（20.5 → 20）
  - 確保小數中位數的正確類型轉換

**MissingSimple 測試（2 個測試）：**
- `test_simple_no_missing_values`：測試無缺失值的簡單值填補
- `test_simple_with_missing_values`：測試有缺失值的簡單值填補

**MissingDrop 測試（2 個測試）：**
- `test_drop_no_missing_values`：測試無缺失值的刪除策略
- `test_drop_with_missing_values`：測試有缺失值的刪除策略

> **整數類型相容性**：增強的缺失值處理器現在正確支援 pandas 可空整數類型（Int8、Int16、Int32、Int64），透過自動將浮點填補值四捨五入為整數，防止 fillna 操作期間的 TypeError。這確保與 schema 指定的整數類型無縫整合，同時維持資料完整性。

#### 異常值檢測處理器

增強異常值檢測，具有 pandas 可空整數陣列相容性：

**OutlierHandler 基礎類別：**
- 增強 `fit()` 和 `transform()` 方法，使用 `np.asarray()` 轉換
- 正確處理 pandas 可空整數陣列，防止廣播錯誤
- 維持與異常值檢測演算法中 numpy 操作的相容性

> **Pandas 陣列相容性**：異常值處理器現在使用 `np.asarray()` 而非 `.values`，確保 pandas 可空整數陣列正確轉換為 numpy 陣列，防止異常值檢測演算法中邏輯操作期間的 ValueError。

### `Metadater`

#### 欄位函數

> tests/metadater/field/test_field_functions.py

測試欄位級別的資料處理和類型分析：

##### 完整類型分析

- `test_leading_zero_detection`：測試前導零檢測和保留：
  - 識別含前導零的資料（如 "001"、"002"）
  - 保留為字串類型以維持前導零
- `test_float_detection`：測試浮點數檢測：
  - 識別字串格式的小數
  - 轉換為適當的 float32/float64 類型
- `test_integer_with_nulls`：測試含空值的整數資料：
  - 使用可空整數類型（Int8、Int16、Int32、Int64）
  - 防止轉換為會添加 .0 後綴的 float64
- `test_integer_without_nulls`：測試純整數資料：
  - 使用一般整數類型（int8、int16、int32、int64）
  - 優化為最小適合的整數類型
- `test_mixed_non_numeric_data`：測試混合非數值資料：
  - 文字資料回退為 category 類型
- `test_numeric_conversion_threshold`：測試 80% 數值轉換門檻：
  - 少於 80% 數值的資料視為分類資料
- `test_integer_dtype_handling`：測試 pd.to_numeric 整數結果的處理：
  - 正確處理 int64 與 float64 類型檢測

##### 前導零檢測

- `test_has_leading_zeros_positive`：測試正面檢測案例：
  - 超過 30% 的值具有前導零模式
- `test_has_leading_zeros_negative`：測試負面檢測案例：
  - 少於 30% 的值具有前導零模式
- `test_has_leading_zeros_empty_data`：測試空資料處理
- `test_has_leading_zeros_all_na`：測試全空值資料處理
- `test_has_leading_zeros_mixed_types`：測試混合資料類型處理

##### 欄位元資料整合

- `test_build_field_metadata_with_leading_zeros`：測試含前導零檢測的欄位元資料建立：
  - 啟用與停用前導零檢測
  - 與類型分析流程的整合
- `test_build_field_metadata_with_nullable_integers`：測試可空整數整合：
  - 啟用與停用可空整數處理
  - 根據空值存在選擇適當類型
- `test_build_field_metadata_dtype_optimization`：測試資料類型優化：
  - 記憶體效率的類型選擇（int8 vs int64）
  - 浮點精度優化（float32 vs float64）

##### 容易誤判資料情境

- `test_id_code_preservation`：測試識別代號保留：
  - 前導零識別代號（001、002 等）
  - 維持官方識別碼的資料完整性
- `test_demographic_data_with_missing_values`：測試含缺失值的人口統計資料：
  - 使用可空整數避免 .0 後綴
  - 維持資料類型一致性
- `test_financial_amount_detection`：測試金額資料處理：
  - 金額值的正確浮點檢測
  - 財務計算的精度保留
- `test_score_integer_detection`：測試評分資料：
  - 測試分數、評級的整數檢測
- `test_categorical_data_detection`：測試分類資料：
  - 等級分類、狀態分類

##### 邊界情況

- `test_empty_series`：測試空資料序列處理
- `test_all_null_series`：測試全空值資料處理
- `test_single_value_series`：測試單值資料
- `test_mixed_numeric_string_data`：測試混合資料類型
- `test_config_none_handling`：測試預設配置處理

### `Metadata`

> tests/loader/test_metadata.py

測試 metadata 處理和型態推斷：

- `test_metadata_init`：驗證 Metadata 類別的空初始化
- `test_build_metadata`：測試 metadata 建立，樣本 DataFrame 包含：
  - 數值型態
  - 類別型態
  - 日期時間型態
  - 布林型態
  - 缺失值 (None/NaN)
- `test_invalid_dataframe`：測試錯誤處理：
  - 非 DataFrame 輸入
  - 空的 DataFrame
- `test_set_col_infer_dtype`：測試欄位型態推斷：
  - 設定有效型態
  - 處理無效欄位
  - 處理無效型態
- `test_to_sdv`：測試轉換為 SDV 格式時的型態對應
- `test_convert_dtypes`：測試型態轉換：
  - 數值型態 (int/float)
  - 類別型態
  - 日期時間型態
  - 布林型態
  - 無效型態

### `Splitter`

> tests/loader/test_splitter.py

測試資料分割功能：

#### 基本功能測試

- `test_splitter_init_normal`：測試正常初始化，包含預設參數設定
- `test_splitter_init_invalid_ratio`：測試無效分割比例的處理
- `test_splitter_init_custom_data_valid`：測試自定義資料方法的有效配置
- `test_splitter_init_custom_data_invalid_method`：測試無效自定義方法的錯誤處理
- `test_splitter_init_custom_data_invalid_filepath`：測試無效檔案路徑的錯誤處理

#### 分割方法測試

- `test_split_normal_method`：測試正常分割方法，驗證返回格式為三元組
- `test_split_normal_method_no_data`：測試無資料情況下的分割
- `test_split_multiple_samples`：測試多重樣本分割，驗證每個樣本的獨立性
- `test_split_custom_data_method`：測試自定義資料分割方法
- `test_split_basic_functionality`：測試基本分割功能和資料完整性

#### 重疊控制功能測試

- `test_bootstrapping_with_exist_indices`：測試使用現有索引的拔靴法抽樣：
  - 驗證重疊比率計算的正確性
  - 測試重疊檢查機制
  - 確認索引集合的正確性
- `test_bootstrapping_overlap_control`：測試重疊控制參數：
  - `max_overlap_ratio` 參數的有效性
  - `max_attempts` 參數的重試機制
  - 重疊比率超過限制時的處理
- `test_bootstrapping_edge_cases`：測試邊界情況：
  - 空的現有索引集合
  - 極端重疊比率設定
  - 最大嘗試次數達到上限

#### 函數式編程架構測試

- `test_metadata_update_functional_approach`：測試函數式方法更新 metadata：
  - 驗證不修改原始物件狀態
  - 測試返回新的 metadata 物件
- `test_create_split_metadata`：測試建立分割 metadata 的純函數特性
- `test_split_return_format`：測試 split 方法的三元組返回格式：
  - `split_data` 字典結構驗證
  - `metadata_dict` 字典結構驗證
  - `train_indices_list` 列表格式驗證

#### 參數重構測試

- `test_exist_train_indices_parameter`：測試重構後的參數名稱：
  - 驗證 `exist_train_indices` 參數的正確處理
  - 測試與舊版本的相容性
- `test_overlap_parameters_validation`：測試重疊控制參數的驗證：
  - `max_overlap_ratio` 範圍檢查
  - `max_attempts` 正整數檢查

> **架構重構說明**：在 2025/6/18 的重構中，所有外部模組（Loader、Processor、Splitter、Benchmarker）已不再直接導入 Metadater 的內部 API（`metadater.api`、`metadater.core`、`metadater.types`），改為使用 Metadater 類別的公共方法。相關測試的 mock 路徑也已相應更新，確保架構的封裝性和一致性。

## 資料合成

### `Synthesizer`

> tests/synthesizer/test_synthesizer.py

測試 Synthesizer 的主要功能：

- `test_initialization`：驗證 Synthesizer 的初始化功能：
  - 檢查配置方法是否正確設定
  - 驗證初始狀態（_impl 為 None）
  - 測試自定義參數設定（如 sample_num_rows）
- `test_create_basic`：測試 create 方法的基本功能：
  - 使用 mock 物件模擬 SDV synthesizer
  - 驗證 _impl 在 create 前後的狀態變化
  - 測試 _determine_sample_configuration 方法的整合
- `test_fit_without_create`：測試在未呼叫 create 前呼叫 fit 會引發 UncreatedError
- `test_fit_without_data_raises_error`：測試非 CUSTOM_DATA 方法但無資料時引發 ConfigError
- `test_sample_without_create`：測試在未 create 時 sample 方法返回空 DataFrame



### `Constrainer`

> tests/constrainer/test_constrainer.py

測試主要約束器工廠類別（18 個測試）：

- `test_basic_initialization`：測試基本約束器初始化和配置儲存
- `test_nan_groups_constraints`：測試空值群組約束：
  - 刪除動作實作
  - 多目標的清除動作
  - 含型別檢查的複製動作
- `test_field_constraints`：測試欄位級別約束：
  - 數值範圍條件
  - 多重條件組合
- `test_field_combinations`：測試欄位組合規則：
  - 教育程度與績效對應
  - 多重值組合
- `test_all_constraints_together`：測試所有約束共同運作：
  - 約束之間的互動
  - 複雜的過濾情境
- `test_resample_functionality`：測試重複採樣直到滿足：
  - 達成目標列數
  - 合成資料生成
  - 約束條件滿足
- `test_error_handling`：測試錯誤情況：
  - 無效的配置格式
  - 缺少欄位
- `test_edge_cases`：測試邊界條件：
  - 空的資料框
  - 全部為空值
- `test_empty_config`：測試空配置的約束器
- `test_unknown_constraint_type_warning`：測試未知約束類型的警告
- `test_resample_trails_attribute`：測試重新採樣軌跡追蹤功能
- `test_register_custom_constraint`：測試自定義約束註冊
- `test_register_invalid_constraint_class`：測試無效約束類別的錯誤處理

**欄位比例整合測試（5 個測試）：**
- `test_field_proportions_integration`：測試新架構下的欄位比例約束器整合：
  - 更新配置格式的單一欄位比例
  - 缺失值比例維護
  - 欄位組合比例處理
- `test_field_proportions_with_other_constraints`：測試欄位比例與其他約束類型的協同運作：
  - 結合欄位比例和欄位約束
  - 多約束互動驗證
- `test_field_proportions_comprehensive_integration`：測試基於真實世界情境的全面欄位比例整合：
  - 教育程度、收入和工作類別資料分布維護
  - 多種約束模式（all、missing、欄位組合）
  - 使用 `target_rows` 參數的新架構驗證
- `test_field_proportions_multiple_modes`：測試多種約束模式的欄位比例：
  - 類別比例（'all' 模式）
  - 缺失值比例（'missing' 模式）
  - 區域比例驗證
- `test_field_proportions_edge_cases_integration`：測試欄位比例邊界情況：
  - 小資料集處理
  - 目標行數大於可用資料
  - 空欄位比例列表處理

#### `NaNGroupConstrainer`

> tests/constrainer/test_nan_group_constrainer.py

測試空值處理約束（18 個測試）：

- `test_invalid_config_initialization`：測試無效配置處理：
  - 非字典輸入
  - 無效的動作類型
  - 無效的目標設定
  - 刪除動作與其他動作的組合
- `test_valid_config_initialization`：測試有效配置：
  - 獨立的刪除動作
  - 多目標的清除動作
  - 單目標的複製動作
  - 不同目標格式
- `test_erase_action`：測試清除動作功能：
  - 當來源欄位為空值時設定目標欄位為空值
  - 處理多個目標欄位
- `test_copy_action_compatible_types`：測試相容類型間的值複製
- `test_copy_action_incompatible_types`：測試不相容類型複製的處理
- `test_multiple_constraints`：測試多個約束同時運作
- `test_delete_action_edge_case`：測試刪除動作邊界情況
- `test_erase_action_multiple_targets`：測試清除動作多目標欄位
- `test_copy_action_type_validation`：測試複製動作型別驗證
- `test_invalid_action_type`：測試無效動作類型處理
- `test_invalid_target_specification`：測試無效目標欄位設定
- `test_empty_config_handling`：測試空配置處理
- `test_mixed_action_validation`：測試混合動作配置驗證

#### `FieldConstrainer`

> tests/constrainer/test_field_constrainer.py

測試欄位級別約束（12 個測試）：

- `test_invalid_config_structure`：測試配置驗證：
  - 非列表輸入
  - 無效的約束格式
  - 空約束
- `test_invalid_constraint_syntax`：測試語法驗證：
  - 不匹配的括號
  - 無效的運算子
  - 缺少運算子
- `test_field_extraction`：測試欄位名稱提取：
  - 加法運算
  - 括號表達式
  - 空值檢查
  - 日期運算
- `test_complex_expression_validation`：測試複雜約束組合
- `test_empty_constraint_list`：測試空約束列表處理
- `test_null_check_operations`：測試空值檢查操作
- `test_date_operation_constraints`：測試日期約束操作
- `test_parentheses_validation`：測試括號匹配驗證
- `test_operator_validation`：測試運算子語法驗證

#### `FieldCombinationConstrainer`

> tests/constrainer/test_field_combination_constrainer.py

測試欄位組合約束（15 個測試）：

- `test_validate_config_existing_columns`：測試欄位存在性驗證
- `test_invalid_constraints_not_list`：測試非列表約束處理
- `test_invalid_constraint_structure`：測試無效的元組結構
- `test_invalid_field_map`：測試欄位映射驗證
- `test_invalid_source_fields`：測試來源欄位類型驗證
- `test_invalid_target_field`：測試目標欄位類型驗證
- `test_multi_field_source_value_length_mismatch`：測試多欄位值匹配
- `test_single_field_constraint`：測試單欄位約束驗證
- `test_multi_field_constraint`：測試多欄位約束情境
- `test_constraint_tuple_validation`：測試約束元組結構驗證
- `test_field_mapping_edge_cases`：測試欄位映射邊界情況
- `test_value_length_validation`：測試值長度匹配驗證
- `test_complex_field_combinations`：測試複雜欄位組合情境

#### `FieldProportionsConstrainer`

> tests/constrainer/test_field_proportions_constrainer.py

測試欄位比例維護約束（33 個測試）：

**FieldProportionsConfig 測試（6 個測試）：**
- `test_valid_config_initialization`：測試有效配置初始化，僅包含欄位比例
- `test_invalid_field_proportions_structure`：測試無效的欄位比例結構（缺少容忍度、無效模式）
- `test_invalid_tolerance_values`：測試無效的容忍度值（>1、<0）
- `test_verify_data_with_valid_data`：測試有效資料框的資料驗證和提供的 target_n_rows
- `test_verify_data_with_missing_columns`：測試資料中缺少欄位的錯誤處理
- `test_check_proportions`：測試良好和不良過濾資料的比例檢查

**FieldProportionsConstrainer 測試（14 個測試）：**
- `test_constrainer_initialization`：測試有效配置的約束器初始化
- `test_invalid_constrainer_config`：測試無效配置的約束器（無效模式）
- `test_apply_with_empty_dataframe`：測試空資料框的 apply 方法
- `test_apply_with_valid_data`：測試有效資料和已知比例的 apply 方法
- `test_field_combination_proportions`：測試使用元組欄位鍵的欄位組合比例
- `test_missing_value_proportions`：測試缺失值比例維護
- `test_edge_case_all_same_values`：測試所有值相同的邊界情況
- `test_edge_case_target_larger_than_data`：測試目標超過可用資料的邊界情況

**極端邊界情況測試（19 個測試）：**
- `test_extreme_case_single_row_data`：測試單列資料處理
- `test_extreme_case_very_large_tolerance`：測試極大容忍度值（0.9）
- `test_extreme_case_zero_tolerance`：測試零容忍度與完美比例
- `test_extreme_case_all_missing_values`：測試全缺失值情境
- `test_extreme_case_no_missing_values`：測試無缺失值情境
- `test_extreme_case_very_small_target`：測試極小目標列數（1 列）
- `test_extreme_case_huge_data_small_target`：測試大型資料集與小目標
- `test_extreme_case_many_unique_values`：測試多個唯一值（每個僅出現一次）
- `test_extreme_case_complex_field_combinations`：測試複雜多欄位組合
- `test_extreme_case_mixed_data_types`：測試混合資料類型（int、string、float、None、bool）
- `test_extreme_case_empty_field_proportions_list`：測試空欄位比例列表
- `test_extreme_case_duplicate_field_rules`：測試重複欄位規則處理
- `test_extreme_case_very_unbalanced_data`：測試極不平衡資料（99% vs 1%）
- `test_extreme_case_numerical_precision`：測試小容忍度的數值精度問題
- `test_extreme_case_unicode_and_special_characters`：測試 Unicode 和特殊字符
- `test_extreme_case_datetime_objects`：測試日期時間物件作為欄位值
- `test_extreme_case_large_string_values`：測試極大字串值（1000+ 字符）
- `test_extreme_case_nested_tuple_combinations`：測試深度嵌套元組組合（5 個欄位）
- `test_apply_without_target_rows_should_fail`：測試不提供 target_rows 參數時適當地失敗

**架構整合：**
- 欄位比例約束器現在遵循統一的 Constrainer 架構
- 目標行數由主要 Constrainer 在重新採樣過程中提供
- 移除日期名稱映射功能以簡化配置
- 所有測試已更新以反映新的參數傳遞機制

> **約束器測試總計**：97 個測試分佈在 5 個測試檔案中，涵蓋完整的約束功能，包括工廠模式實作、空值群組處理、欄位級別約束、欄位組合規則和欄位比例維護，具有廣泛的邊界情況覆蓋和整合測試。

## 資料評測

### `Evaluator`

#### `SDMetrics`

> tests/evaluator/test_sdmetrics.py

測試 SDMetrics 單表評估功能：

- `test_eval_diagnostic_report`：使用模擬 SDMetrics 組件測試 DiagnosticReport 評估
- `test_eval_quality_report`：使用全面模擬設定測試 QualityReport 評估
- `test_init`：測試 SDMetricsSingleTable 初始化和配置驗證
- `test_invalid_method`：測試不支援評估方法的錯誤處理

**主要特色：**
- **資料類型一致性**：增強的 BaseEvaluator 現在檢測資料集間的資料類型不匹配，並提供清楚的錯誤訊息，而非自動類型對齊
- **錯誤處理**：改進的錯誤訊息指導使用者在 Executor 層級處理類型對齊
- **模擬整合**：全面模擬 SDMetrics 組件以確保可靠測試

> **架構增強**：BaseEvaluator 已修改以移除自動資料類型對齊功能。不再靜默「修復」類型不匹配，而是拋出包含詳細不匹配資訊的 ValueError，確保 Data Structure 評估準確性並維持資料完整性。

#### `Stats`

> tests/evaluator/test_stats.py

測試統計評估功能：

- `test_eval_basic`：使用模擬欄位元資料建立測試基本統計評估
- `test_eval_with_different_data`：測試使用不同原始和合成資料集的評估
- `test_init`：測試 Stats 評估器初始化和配置驗證
- `test_invalid_compare_method`：測試無效比較方法的錯誤處理
- `test_invalid_stats_method`：測試無效統計方法的錯誤處理

**主要特色：**
- **Metadater 整合**：更新為使用 `Metadater.create_field` 進行欄位元資料建立
- **類型推斷**：透過模擬欄位元資料正確處理資料類型推斷
- **配置驗證**：統計方法配置的全面驗證

#### `CustomEvaluator`

> tests/evaluator/test_custom_evaluator.py

測試自定義評估器功能：

- `test_init`：測試 CustomEvaluator 使用外部模組載入的初始化
- `test_eval`：測試使用自定義評估器實例的評估方法執行
- `test_missing_module_path`：測試缺少模組路徑配置的錯誤處理

**主要特色：**
- **外部模組載入**：與 `petsard.utils.load_external_module` 整合以進行動態評估器載入
- **模擬整合**：全面模擬外部模組載入和自定義評估器執行
- **錯誤處理**：模組路徑和類別名稱需求的適當驗證

> - 所有功能替換都使用 Metadater 的公共介面，完全避免調用深層內部功能
> - 保持了所有原有功能的完整性，確保向後相容性
> - 新的 Metadater 功能通過 `Metadater` 類的靜態方法提供統一介面

#### `MLUtility`

> tests/evaluator/test_mlutility.py

測試機器學習效用評估：

- `test_classification_of_single_value`：測試單一值分類目標的三種情境：
  - 原始資料有單一層級目標
  - 合成資料有單一層級目標
  - 兩個資料集都有單一層級目標
  - 驗證 NaN 分數和警告的正確處理
- `test_classification_normal_case`：測試正常多分類情況：
  - 驗證分數計算
  - 檢查分數範圍
  - 驗證統計指標
- `test_classification_empty_data`：測試空資料的行為：
  - 處理空資料的預處理
  - 驗證 NaN 分數
  - 檢查警告訊息

#### `MPUCCs`

> tests/evaluator/test_mpuccs.py

測試 mpUCCs（最大部分唯一欄位組合）隱私風險評估：

**基本功能測試（`TestMPUCCsBasic`）：**
- `test_initialization`：測試 MPUCCs 評估器初始化與配置參數
- `test_basic_evaluation`：測試使用簡單測試資料的基本評估功能
- `test_empty_data`：測試空資料集的處理

**精度處理測試（`TestMPUCCsPrecisionHandling`）：**
- `test_numeric_precision_auto_detection`：測試數值欄位精度的自動檢測（小數位數）
- `test_numeric_precision_manual_setting`：測試手動數值精度配置
- `test_datetime_precision_auto_detection`：測試日期時間欄位精度的自動檢測
- `test_datetime_precision_normalization`：測試大小寫不敏感的日期時間精度格式正規化

**熵計算測試（`TestMPUCCsEntropyCalculation`）：**
- `test_renyi_entropy_calculation`：測試不同資料分佈的 Rényi 熵（α=2，碰撞熵）計算：
 - 高熵（均勻分佈）
 - 中等熵（中度偏斜）
 - 低熵（高度偏斜）
 - 極低熵（極端偏斜）
- `test_entropy_gain_calculation`：測試欄位組合的條件熵增益計算

**剪枝邏輯測試（`TestMPUCCsPruningLogic`）：**
- `test_entropy_based_pruning`：測試可配置閾值的基於熵的剪枝機制
- `test_base_combo_pruning_propagation`：測試從基礎組合到超集的剪枝傳播

**整合測試（`TestMPUCCsIntegration`）：**
- `test_complete_workflow`：測試具有真實資料情境的完整 mpUCCs 工作流程
- `test_skip_ncols_configuration`：測試跳躍模式配置（如 n_cols=[1, 3]）
- `test_deduplication_functionality`：測試分析前的自動資料去重

**邊界情況測試（`TestMPUCCsEdgeCases`）：**
- `test_single_column_data`：測試單欄位資料集
- `test_all_unique_data`：測試所有值唯一但無碰撞的資料集
- `test_all_identical_data`：測試具有相同值的資料集

**理論驗證：**
- `test_renyi_vs_shannon_entropy`：展示 Rényi 熵與 Shannon 熵在隱私分析中的差異

> **mpUCCs 架構**：mpUCCs 實現基於最大部分唯一欄位組合理論（mpUCCs = QIDs）的先進指認性風險評估。主要特色包括漸進式樹狀搜尋、基於熵的剪枝、數值/日期時間欄位的精度處理，以及具有雙層進度條的全面進度追蹤。

## 資料報告

### `Reporter`

> tests/reporter/test_reporter.py

測試具有**函式化設計架構**和**命名策略支援**的主要 Reporter 功能：

- `test_method`：測試 Reporter 使用不同方法的初始化：
  - 'save_data' 方法使用 ReporterSaveData
  - 'save_report' 方法使用 ReporterSaveReport
  - 'save_timing' 方法使用 ReporterSaveTiming
  - 無效方法拋出 UnsupportedMethodError
- `test_method_save_data`：測試 save_data 方法驗證：
  - 未提供 source 時拋出 ConfigError
- `test_method_save_report`：測試 save_report 方法驗證：
  - 僅使用 granularity 的有效初始化
  - 缺少必要參數時拋出 ConfigError
- `test_method_save_timing`：測試 save_timing 方法驗證：
  - 使用可選參數的有效初始化
  - 正確處理 time_unit 和模組過濾

#### `TestReporterNamingStrategy`

測試命名策略功能（6 個測試）：

- `test_naming_strategy_parameter_validation`：測試 naming_strategy 參數驗證：
  - 接受有效值（'traditional'、'compact'）
  - 無效命名策略值拋出 ConfigError
- `test_traditional_naming_strategy`：測試傳統命名策略：
  - 維持與現有檔名格式的向後相容性
  - 產生含傳統方括號標記的檔案
- `test_compact_naming_strategy`：測試簡潔命名策略：
  - 產生簡化的檔名格式
  - 移除冗餘的方括號和標記
- `test_naming_strategy_with_different_methods`：測試不同 Reporter 方法的命名策略：
  - save_data 方法使用兩種策略
  - save_report 方法使用兩種策略
  - save_timing 方法（跨策略不變）
- `test_naming_strategy_integration`：測試命名策略與 Reporter 工作流程的整合：
  - 端到端檔名生成
  - 透過 Reporter 架構的適當參數傳遞
- `test_naming_strategy_default_behavior`：測試預設命名策略行為：
  - 未指定 naming_strategy 時使用傳統策略
  - 維持向後相容性

#### `ReporterSaveData`

測試具有函式化設計的資料儲存功能：

- `test_source`：測試 source 參數驗證：
  - 接受字串和字串列表
  - 無效類型（浮點數、混合列表、元組）拋出 ConfigError
- `test_functional_create_and_report`：測試函式化「拋出再拋回」模式：
  - `create()` 處理資料但不儲存在實例變數中
  - `report()` 接收處理後的資料並產生輸出檔案
  - 呼叫間不維護內部狀態

#### `ReporterSaveReport`

測試具有**多粒度支援**的報告生成功能：

- `test_granularity`：測試 granularity 參數驗證：
  - **單一粒度**：'global'、'columnwise'、'pairwise'、'details'、'tree'
  - **多重粒度**：['global', 'columnwise']、['details', 'tree']
  - 缺少或無效 granularity 拋出 ConfigError
  - 非字串/非列表類型拋出 ConfigError
- `test_multi_granularity_support`：測試多粒度功能：
  - 在單一操作中處理多個粒度
  - 為每個粒度產生個別報告
  - 正確處理粒度特定的資料結構
- `test_new_granularity_types`：測試新粒度類型（v2.0+）：
  - 'details'：詳細分解與額外指標
  - 'tree'：階層樹狀結構分析
- `test_eval`：測試 eval 參數驗證：
  - 接受字串、字串列表或 None
  - 無效類型拋出 ConfigError
- `test_create`：測試所有粒度的函式化報告建立：
  - Global 粒度報告生成
  - Columnwise 粒度報告生成
  - Pairwise 粒度報告生成
  - Details 粒度報告生成
  - Tree 粒度報告生成
  - 多粒度處理
- `test_functional_design_pattern`：測試函式化「拋出再拋回」模式：
  - `create()` 回傳處理後的資料但不內部儲存
  - `report()` 接受處理後的資料並產生檔案
  - 透過無狀態設計進行記憶體優化
- `test_process_report_data`：測試資料處理功能：
  - 使用評估名稱前綴重命名欄位
  - 不同粒度的索引處理
  - 非 Evaluator/Describer 模組的跳過標記
- `test_safe_merge`：測試 DataFrame 合併功能：
  - 具有重疊欄位的純資料合併
  - 所有粒度的處理資料合併
  - 正確處理包括 'column'、'column1'、'column2' 的共同欄位
  - 合併結果中的正確行順序

#### `ReporterSaveTiming`

測試時間資訊報告功能：

- `test_timing_data_processing`：測試時間資料處理：
  - 時間單位轉換（秒、分鐘、小時、天）
  - 模組過濾功能
  - 時間詮釋資料提取
- `test_functional_timing_workflow`：測試函式化時間工作流程：
  - 處理時間資料但不內部儲存
  - 產生適當格式的時間報告

#### `Reporter Utils`

測試工具函數：

- `test_convert_full_expt_tuple_to_name`：測試實驗元組到名稱的轉換
- `test_convert_full_expt_name_to_tuple`：測試實驗名稱到元組的轉換
- `test_convert_eval_expt_name_to_tuple`：測試評估實驗名稱解析

> **函式化設計架構**：Reporter 已完全重構為使用函式化「拋出再拋回」設計模式以進行記憶體優化。`create()` 方法處理資料但不將其儲存在實例變數中（`self.result`、`self._processed_data`），而 `report()` 接收處理後的資料並產生輸出檔案。這種無狀態方法顯著減少記憶體消耗，同時保持完全向後相容性。

> **多粒度支援**：Reporter 現在支援單一粒度（`str`）和多粒度（`list[str]`）配置，允許使用者在單一操作中處理多個粒度。新的粒度類型 'details' 和 'tree' 已與傳統的 'global'、'columnwise' 和 'pairwise' 選項一起添加。

## 系統組件

### `Config`

> tests/test_config.py

配置管理和 BaseConfig 功能測試：

**Config 測試：**
- `test_init_basic_config`：測試基本配置初始化，包含模組序列和佇列設定
- `test_config_validation_error`：測試含有 "_[xxx]" 後綴的無效實驗名稱的配置驗證
- `test_splitter_handler`：測試 Splitter 配置的多樣本擴展
- `test_set_flow`：測試流程設定的正確佇列順序和內容
- `test_complete_workflow_setup`：測試完整多模組工作流程配置
- `test_operator_creation`：測試從配置實例化操作器

**BaseConfig 測試（已整合）：**
- `test_init_and_get`：測試初始化和 get 方法，包含所有屬性和日誌器
- `test_update`：測試配置更新，包含現有屬性的驗證和類型檢查
- `test_get_params_include`：測試使用 INCLUDE 動作的參數提取和重命名
- `test_get_params_merge`：測試使用 MERGE 動作的參數合併和字典驗證
- `test_get_params_combined`：測試多個動作的組合參數操作
- `test_get_params_validation`：測試不存在屬性、重複和衝突的驗證
- `test_from_dict`：測試從字典建立配置，包含參數驗證
- `test_config_get_param_action_map`：測試 ConfigGetParamActionMap 枚舉功能

**Status 測試（已整合）：**
- `test_init`：測試 Status 初始化，包含配置、序列和屬性設定
- `test_put_and_get_result`：測試狀態儲存和結果檢索，包含詮釋資料追蹤
- `test_metadata_management`：測試詮釋資料設定、檢索和不存在模組的錯誤處理
- `test_get_pre_module`：測試執行序列中前一個模組的檢索
- `test_get_full_expt`：測試實驗配置檢索（完整和部分）
- `test_report_management`：測試報告資料管理和 DataFrame 比較
- `test_status_renewal`：測試模組重新執行時的狀態更新機制

### `Status`

> tests/test_status.py

測試整合 Metadater 的增強 Status 快照系統：

- `test_snapshot_creation`：測試 ExecutionSnapshot 和 MetadataChange 建立，具有適當的資料類別結構
- `test_change_tracking`：測試跨管線階段的詮釋資料變更追蹤
- `test_metadata_evolution`：測試透過多個操作的詮釋資料演化追蹤
- `test_status_summary`：測試狀態摘要生成，包含執行歷史
- `test_snapshot_retrieval`：測試快照檢索和篩選功能

> **增強的 Status 架構**：Status 系統已重新設計，以 Metadater 為核心，提供全面的進度追蹤、詮釋資料快照和變更歷史，同時保持與現有介面的完全向後相容性。Status 現在是一個獨立模組（`petsard/status.py`），具有專用的快照功能。

## 系統組件

### `Config`

> tests/test_config.py

配置管理和 BaseConfig 功能測試：

**Config 測試：**
- `test_init_basic_config`：測試基本配置初始化，包含模組序列和佇列設定
- `test_config_validation_error`：測試含有 "_[xxx]" 後綴的無效實驗名稱的配置驗證
- `test_splitter_handler`：測試 Splitter 配置的多樣本擴展
- `test_set_flow`：測試流程設定的正確佇列順序和內容
- `test_complete_workflow_setup`：測試完整多模組工作流程配置
- `test_operator_creation`：測試從配置實例化操作器

**BaseConfig 測試（已整合）：**
- `test_init_and_get`：測試初始化和 get 方法，包含所有屬性和日誌器
- `test_update`：測試配置更新，包含現有屬性的驗證和類型檢查
- `test_get_params_include`：測試使用 INCLUDE 動作的參數提取和重命名
- `test_get_params_merge`：測試使用 MERGE 動作的參數合併和字典驗證
- `test_get_params_combined`：測試多個動作的組合參數操作
- `test_get_params_validation`：測試不存在屬性、重複和衝突的驗證
- `test_from_dict`：測試從字典建立配置，包含參數驗證
- `test_config_get_param_action_map`：測試 ConfigGetParamActionMap 枚舉功能

**Status 測試（已整合）：**
- `test_init`：測試 Status 初始化，包含配置、序列和屬性設定
- `test_put_and_get_result`：測試狀態儲存和結果檢索，包含詮釋資料追蹤
- `test_metadata_management`：測試詮釋資料設定、檢索和不存在模組的錯誤處理
- `test_get_pre_module`：測試執行序列中前一個模組的檢索
- `test_get_full_expt`：測試實驗配置檢索（完整和部分）
- `test_report_management`：測試報告資料管理和 DataFrame 比較
- `test_status_renewal`：測試模組重新執行時的狀態更新機制

### `Status`

> tests/test_status.py

測試整合 Metadater 的增強 Status 快照系統：

- `test_snapshot_creation`：測試 ExecutionSnapshot 和 MetadataChange 建立，具有適當的資料類別結構
- `test_change_tracking`：測試跨管線階段的詮釋資料變更追蹤
- `test_metadata_evolution`：測試透過多個操作的詮釋資料演化追蹤
- `test_status_summary`：測試狀態摘要生成，包含執行歷史
- `test_snapshot_retrieval`：測試快照檢索和篩選功能

> **增強的 Status 架構**：Status 系統已重新設計，以 Metadater 為核心，提供全面的進度追蹤、詮釋資料快照和變更歷史，同時保持與現有介面的完全向後相容性。Status 現在是一個獨立模組（`petsard/status.py`），具有專用的快照功能。