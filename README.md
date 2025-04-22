# Symbol Memory Cost Analysis Dashboard

針對 RISC-V 裸機映像檔的 ELF 符號配置分析的 Streamlit 儀表板。

## 功能特點

已實現功能：
- ✅ 多維度篩選（記憶體區域、模組、資料夾、檔案、Section、即時性、硬體使用）
- ✅ 成本分析（模組排行、記憶體佔比、資料夾分析）
- ✅ 記憶體分布 TreeMap 視覺化
- ✅ 異常檢測（即時性配置、硬體使用）
- ✅ 詳細資料查看與匯出
- ✅ CSV 和 Markdown 報告產生

## 安裝需求

- Python 3.7+
- Streamlit
- Plotly
- Pandas

## 快速開始

1. 克隆專案：
```bash
git clone https://github.com/yourusername/memory_tree.git
cd memory_tree
```

2. 安裝依賴：
```bash
pip install -r requirements.txt
```

3. 執行應用：
```bash
streamlit run app.py
```

## 執行測試

1. 安裝測試依賴：
```bash
pip install pytest pytest-cov
```

2. 設定 Python 路徑：
```bash
# Linux/macOS
export PYTHONPATH=$PYTHONPATH:/path/to/memory_tree

# Windows
set PYTHONPATH=%PYTHONPATH%;C:\path\to\memory_tree
```

3. 執行所有測試：
```bash
# 在專案根目錄執行
pytest

# 顯示詳細測試過程
pytest -v

# 顯示 print 輸出
pytest -s

# 同時顯示詳細過程和輸出
pytest -vs
```

4. 執行特定測試：
```bash
# 執行特定測試檔案
pytest tests/test_data_generation.py

# 執行特定測試函式
pytest tests/test_data_generation.py::test_generate_output_file_exists

# 執行符合特定名稱的測試
pytest -k "test_memory"
```

5. 測試覆蓋率報告：
```bash
# 產生覆蓋率報告
pytest --cov=.

# 產生 HTML 格式覆蓋率報告
pytest --cov=. --cov-report=html
```

6. 故障排除：
- 確認在專案根目錄執行測試
- 確認已建立 data 目錄
- 檢查 Python 路徑設定

測試案例說明：
- 資料生成測試：確認可正確產生測試資料
- 欄位完整性測試：確認必要欄位存在
- 記憶體限制測試：確認不超過各區域容量
- 成本計算測試：驗證計算公式正確性

測試檢查項目：
- 資料生成功能
- 符號成本計算
- 記憶體限制檢查
- 必要欄位驗證
- CSV 匯出功能

## 資料模型

分析基於以下符號屬性：
- 符號名稱和大小
- 輸入/輸出區段
- 記憶體保護類型
- 實時優先級
- 硬體使用情況
- 模組和檔案資訊

## 主要功能

1. 記憶體成本分析
   - 模組級別成本統計（自動計算 symbol_cost = size × memory_weight）
   - 記憶體權重：ILM/DLM=10, SYSRAM=8, EXT_MEMORY=2
   - 符號級別詳細分析與排序
   - 記憶體區域使用率監控

2. 視覺化圖表
   - 記憶體分配樹狀圖（物理記憶體 > 模組 > 符號）
   - Top 10 模組成本柱狀圖
   - 記憶體區域成本佔比圓餅圖
   - 異常檢測熱力圖（模組 × 規則違規）

3. 自動異常檢測
   - High Realtime 符號誤置於外部記憶體
   - Low Realtime 符號誤置於高速記憶體
   - 硬體存取符號誤置於外部記憶體
   - 異常統計與詳細列表

4. KPI 指標監控
   - 符號總數統計
   - 總記憶體用量（KB）
   - 總成本計算
   - High Realtime 符號數量
   - 異常配置筆數

5. 報告輸出
   - 完整符號資料 CSV 匯出
   - 異常檢測報告 CSV 匯出
   - Markdown 格式異常摘要報告

## 授權資訊

待定

## 貢獻指南

歡迎提交 Pull Request 或建立 Issue。

## 聯絡方式

待定