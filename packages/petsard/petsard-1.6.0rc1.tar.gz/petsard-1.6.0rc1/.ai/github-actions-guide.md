# GitHub Actions AI 輔助開發自動化指南

## 🎯 概述

我們設計了一個完整的 GitHub Actions 工作流程來自動化 AI 輔助開發流程，確保團隊成員在提交 Pull Request 時自動獲得：

1. **代碼變更分析**：自動檢測修改的模組
2. **文檔同步提醒**：提醒更新相關的功能設計文檔
3. **架構合規檢查**：驗證是否遵循既定的架構原則
4. **互動式建議**：在 PR 中留言提供具體的改進建議

## 🔧 工作流程架構

### 主要組件

1. **[`.github/workflows/ai-assisted-development.yml`](../.github/workflows/ai-assisted-development.yml)**
   - GitHub Actions 工作流程定義
   - 在 PR 創建/更新時自動觸發

2. **[`.ai/scripts/development-assistant.py`](scripts/development-assistant.py)**
   - 核心分析腳本，支援多種執行模式
   - CI 模式、報告模式、合規性檢查模式

3. **功能設計文檔映射**
   - 自動檢測代碼變更對應的文檔
   - 提供具體的架構檢查清單

## 🚀 自動化流程

### 觸發條件
```yaml
on:
  pull_request:
    types: [opened, synchronize, reopened]
    paths:
      - 'petsard/**'
      - '.ai/functional_design/**'
      - 'tests/**'
```

### 執行步驟

1. **代碼變更分析**
   ```bash
   python .ai/scripts/development-assistant.py --mode=ci --pr-number=$PR_NUMBER
   ```

2. **生成分析報告**
   ```bash
   python .ai/scripts/development-assistant.py --mode=report
   ```

3. **PR 留言互動**
   - 自動在 PR 中留言分析結果
   - 更新現有留言而非創建新留言
   - 提供具體的改進建議

4. **合規性檢查**（可選）
   ```bash
   python .ai/scripts/development-assistant.py --mode=compliance --strict
   ```

## 📋 實際使用範例

### PR 留言範例

當開發者修改 `petsard/loader/` 模組時，GitHub Actions 會自動留言：

```markdown
# 🤖 AI 輔助開發分析報告

## 📊 變更分析 Change Analysis

**分析時間**: 2025-01-15 10:30:00 UTC
**PR 編號**: #123
**分支**: feature/loader-enhancement

## 🔍 檢測到的模組變更 Detected Module Changes

### 🔄 `loader` 模組

**📚 對應文檔**: [functional_design/loader.md](.ai/functional_design/loader.md)

**📝 變更檔案**: 3 個
  - `petsard/loader/base.py`
  - `petsard/loader/csv_loader.py`
  - `petsard/loader/__init__.py`

**🔍 架構檢查清單**:
- [ ] 確認 load() 方法回傳 tuple[pd.DataFrame, SchemaMetadata]
- [ ] 檢查是否正確使用 Metadater.create_schema()
- [ ] 驗證向後相容性

## 🤖 AI 輔助開發建議

1. **使用 Roo 時請載入相關的功能設計文檔**
2. **確保代碼變更與文檔保持同步**
3. **運行相關的測試確保功能正常**
4. **考慮向後相容性影響**

---
*此留言由 AI 輔助開發系統自動生成*
```

## 🎛️ 配置選項

### 強制模式 vs 警告模式

在 [`.github/workflows/ai-assisted-development.yml`](../.github/workflows/ai-assisted-development.yml) 中：

```yaml
- name: ❌ Fail if Non-Compliant (Optional)
  if: steps.compliance.outputs.compliance_status != '0'
  run: |
    echo "::warning::AI 輔助開發合規性檢查失敗。請檢查 PR 留言中的建議。"
    echo "::notice::這是警告模式，不會阻止 PR 合併。如需強制模式，請修改工作流程設定。"
    # exit 1  # 取消註解以啟用強制模式
```

- **警告模式**（預設）：提供建議但不阻止 PR 合併
- **強制模式**：合規性檢查失敗時阻止 PR 合併

### 自訂檢查規則

在 [`development-assistant.py`](scripts/development-assistant.py) 中修改 `architecture_rules`：

```python
self.architecture_rules = {
    "petsard/loader/": [
        "確認 load() 方法回傳 tuple[pd.DataFrame, SchemaMetadata]",
        "檢查是否正確使用 Metadater.create_schema()",
        "驗證向後相容性",
        # 添加新的檢查規則
    ],
    # 添加新模組的規則
}
```

## 🔄 與現有工具整合

### 與 Roo AI 助手整合

1. **自動載入上下文**
   - Roo 會自動載入 [`.roo/project.yaml`](../.roo/project.yaml) 配置
   - 包含專案上下文和架構規則

2. **開發提示生成**
   ```bash
   python .ai/scripts/development-assistant.py --mode=interactive
   ```

### 與 Pre-commit Hook 整合

[`.ai/scripts/pre-commit-hook.sh`](scripts/pre-commit-hook.sh) 會在本地提交前執行檢查：

```bash
#!/bin/bash
# 執行 AI 輔助開發檢查
python .ai/scripts/development-assistant.py --mode=compliance

if [ $? -ne 0 ]; then
    echo "⚠️  建議檢查相關的功能設計文檔"
    echo "是否繼續提交？ (y/N)"
    read -r response
    if [[ ! "$response" =~ ^[Yy]$ ]]; then
        exit 1
    fi
fi
```

## 📈 業界最佳實踐對比

### 我們的方案 vs 業界標準

| 功能 | 我們的方案 | 業界常見做法 | 優勢 |
|------|------------|--------------|------|
| **自動化檢查** | ✅ GitHub Actions | ✅ CI/CD 整合 | 專為 AI 輔助開發設計 |
| **互動式提醒** | ✅ PR 留言 Bot | ✅ Slack/Teams 通知 | 直接在代碼審查流程中 |
| **文檔同步** | ✅ 自動檢測映射 | ❌ 手動維護 | 自動化程度更高 |
| **架構合規** | ✅ 可配置規則 | ✅ Linting 工具 | 針對功能設計文檔 |
| **AI 整合** | ✅ Roo 專用配置 | ❌ 通用工具 | 專為 AI 助手優化 |

### 參考的業界實踐

1. **Dependabot**：自動化依賴更新和 PR 留言
2. **CodeClimate**：代碼品質分析和 PR 集成
3. **Renovate**：配置驅動的自動化更新
4. **Semantic Release**：自動化版本管理和發佈

## 🎯 使用建議

### 團隊導入策略

1. **階段一：警告模式**
   - 啟用自動檢查但不阻止合併
   - 讓團隊熟悉工作流程

2. **階段二：互動優化**
   - 根據團隊反饋調整檢查規則
   - 優化 PR 留言內容

3. **階段三：強制模式**
   - 啟用強制合規檢查
   - 確保架構一致性

### 維護注意事項

1. **定期更新規則**：根據專案演進調整架構檢查規則
2. **監控效果**：追蹤 PR 留言的有效性和團隊採用率
3. **性能優化**：大型專案可能需要優化 git diff 範圍

## 🔗 相關資源

- [AI 輔助開發總覽](README.md)
- [開發流程文檔](development-workflow.md)
- [專案上下文配置](roo-config/project-context.md)
- [架構規則配置](roo-config/architecture-rules.md)