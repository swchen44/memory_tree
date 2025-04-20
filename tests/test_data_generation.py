
# tests/test_data_generation.py
# Unit test for data_generation.py

import os
import pandas as pd
import pytest
from data_generation import generate_symbol_data

def test_generate_output_file_exists():
    test_file = "data/test_symbols.csv"
    generate_symbol_data(num_symbols=100, outfile=test_file)
    assert os.path.exists(test_file), "CSV 檔案未建立"

def test_output_row_count():
    test_file = "data/test_symbols.csv"
    df = pd.read_csv(test_file)
    assert len(df) == 100, "資料筆數應為 100"

def test_output_size_1k_alignment():
    test_file = "data/test_symbols.csv"
    df = pd.read_csv(test_file)
    total_size = df['symbol_size'].sum()
    nearest_k = round(total_size / 1024)
    print(f"Total size ≈ {total_size} bytes ({nearest_k} KB)")
    assert nearest_k > 0, "總 size 應大於 0"

def test_required_columns_present():
    test_file = "data/test_symbols.csv"
    df = pd.read_csv(test_file)
    required_cols = [
        "symbol_name", "symbol_module", "symbol_filename",
        "input_section", "symbol_size", "symbol_address",
        "symbol_physical_memory", "symbol_out_section",
        "symbol_protection", "symbol_realtime", "symbol_hw_usage"
    ]
    for col in required_cols:
        assert col in df.columns, f"缺少欄位: {col}"
