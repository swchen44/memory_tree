"""
Symbol Data Generation Test Module

此測試模組用於確保符號資料產生器的功能正確性，測試項目包括：
- 檔案產生與存在性
- 資料筆數正確性
- 資料大小對齊
- 必要欄位存在性
- 欄位值合法性

Author: swchen.tw
Version: 1.0.0
"""

import sys
import os

# 將專案根目錄加入 Python 路徑
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from data_generation import generate_symbol_data
import pandas as pd
import pytest

def test_generate_output_file_exists():
    """
    測試產生的輸出檔案是否存在。
    
    步驟:
    1. 產生測試資料檔案
    2. 確認檔案是否成功建立
    """
    test_file = "data/test_symbols.csv"
    generate_symbol_data(num_symbols=100, outfile=test_file)
    assert os.path.exists(test_file), "CSV 檔案未建立"

def test_output_row_count():
    """
    測試產生的資料筆數是否符合預期。
    
    步驟:
    1. 讀取測試資料檔案
    2. 驗證資料筆數是否為100筆
    """
    test_file = "data/test_symbols.csv"
    df = pd.read_csv(test_file)
    assert len(df) == 100, "資料筆數應為 100"

def test_output_size_1k_alignment():
    """
    測試產生的符號大小總和是否合理。
    
    步驟:
    1. 計算所有符號大小總和
    2. 轉換為 KB 單位
    3. 確認總大小為正值
    """
    test_file = "data/test_symbols.csv"
    df = pd.read_csv(test_file)
    total_size = df['symbol_size'].sum()
    nearest_k = round(total_size / 1024)
    print(f"Total size ≈ {total_size} bytes ({nearest_k} KB)")
    assert nearest_k > 0, "總 size 應大於 0"

def test_required_columns_present():
    """
    測試產生的資料是否包含所有必要欄位。
    
    必要欄位:
    - symbol_name: 符號名稱
    - symbol_module: 所屬模組
    - symbol_filename: 來源檔案
    - input_section: 輸入段落
    - symbol_size: 符號大小
    - symbol_address: 記憶體位址
    - symbol_physical_memory: 實體記憶體位置
    - symbol_out_section: 輸出段落
    - symbol_output_section: 輸出區段類型
    - symbol_realtime: 即時性需求
    - symbol_hw_usage: 硬體使用標記
    """
    test_file = "data/test_symbols.csv"
    df = pd.read_csv(test_file)
    required_cols = [
        "symbol_name", "symbol_module", "symbol_filename",
        "input_section", "symbol_size", "symbol_address",
        "symbol_physical_memory", "symbol_out_section",
        "symbol_output_section", "symbol_realtime", "symbol_hw_usage"
    ]
    for col in required_cols:
        assert col in df.columns, f"缺少欄位: {col}"

def test_output_section_values():
    """
    測試輸出區段的值是否符合預期範圍。
    
    合法的輸出區段值:
    - code
    - data
    - init
    - always_power_on
    - ro_after_write
    """
    test_file = "data/test_symbols.csv"
    df = pd.read_csv(test_file)
    valid_output_sections = ["code", "data", "init", "always_power_on", "ro_after_write"]
    assert df["symbol_output_section"].isin(valid_output_sections).all(), \
        "symbol_output_section 包含非法值"
