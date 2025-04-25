"""
Symbol Data Generation Module

此模組用於生成符號記憶體配置的模擬資料，主要功能包括：
- 產生模擬的符號資料
- 設定記憶體配置規則
- 產生符合實際情況的記憶體使用分布

Author: swchen.tw
Version: 1.0.0
"""

import pandas as pd
import numpy as np
import random
import os
import csv
import logging

def setup_logging():
    """
    設定logging配置。

    Returns:
        logging.Logger: 配置好的logger物件

    Note:
        - 預設輸出等級為 INFO
        - 格式包含時間戳記、等級和訊息
    """
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s %(levelname)s %(message)s',
        handlers=[logging.StreamHandler()]
    )
    return logging.getLogger("data_gen")

# 新增 folder_name 列表
FOLDER_NAMES = [
    "customer", "custom/system",
    "core/mlm", "core/rlm", "core/system", "core/middle",
    "open_core/mlm", "open_core/rlm", "open_core/system", "open_core/middle",
    "base/hal", "base/prj_ram", "base/exthal",
    "open_base/hal", "open_base/prj_ram", "open_base/exthal"
]

def generate_symbol_data(num_symbols=1500, outfile="data/symbols.csv", day=1, prev_data=None):
    """
    產生模擬的符號記憶體配置資料。

    Args:
        num_symbols (int, optional): 要產生的符號數量. 預設為1500.
        outfile (str, optional): 輸出CSV檔案路徑. 預設為"data/symbols.csv".
        day (int, optional): 第幾天的資料. 預設為1.
        prev_data (pd.DataFrame, optional): 前一天的資料. 預設為None.

    Returns:
        pd.DataFrame: 包含以下欄位的DataFrame：
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
            - symbol_access_count: 存取次數
            - symbol_hw_usage: 硬體使用標記
            - symbol_folder_name_for_file: 資料夾路徑

    記憶體限制:
        - ilm: 64KB
        - dlm: 64KB
        - sysram: 256KB
        - ext_memory1: 1MB
        - ext_memory2: 1MB
    """
    logger = setup_logging()
    logger.info(f"Generating {num_symbols} synthetic symbols for day {day}...")

    # 記憶體配置與權重定義
    memory_weights = {
        "ilm": 10, "dlm": 10,
        "sysram": 8,
        "ext_memory1": 2, "ext_memory2": 2
    }
    memory_types = list(memory_weights.keys())

    # 各記憶體區域大小限制
    memory_max_size = {
        "ilm": 64 * 1024,      # 64KB
        "dlm": 64 * 1024,      # 64KB
        "sysram": 256 * 1024,  # 256KB
        "ext_memory1": 1024 * 1024,  # 1MB
        "ext_memory2": 1024 * 1024   # 1MB
    }

    # 資料欄位定義
    modules = [f"module_{i}" for i in range(1, random.randint(10, 20))]
    filenames = [f"file_{i}.c" for i in range(1, random.randint(50, 100))]
    realtime_levels = ["High", "Medium", "Low"]
    output_section_types = ["code", "data", "init", "always_power_on", "ro_after_write"]
    
    records = []
    memory_usage = {mem: 0 for mem in memory_types}
    
    if prev_data is not None:
        # 第二天開始：只修改 size，其他屬性保持不變
        for _, row in prev_data.iterrows():
            variation = random.uniform(0, 0.02)  # 0% to 2%
            new_size = int(row['symbol_size'] * (1 + variation))
            new_size = max(16, min(2048, new_size))  # 確保在合理範圍內
            
            # 檢查記憶體限制
            if memory_usage[row['symbol_physical_memory']] + new_size > memory_max_size[row['symbol_physical_memory']]:
                continue
                
            memory_usage[row['symbol_physical_memory']] += new_size
            
            new_record = row.to_dict()
            new_record['symbol_size'] = new_size
            records.append(new_record)
    else:
        # 第一天：產生初始資料
        for i in range(num_symbols):
            symbol_name = f"symbol_{i}"
            module = random.choice(modules)
            filename = random.choice(filenames)
            size = np.random.randint(16, 2048)  # 16B ~ 2KB
            memory = random.choices(memory_types, weights=[memory_weights[m] for m in memory_types])[0]
            
            # 檢查記憶體限制
            if memory_usage[memory] + size > memory_max_size[memory]:
                continue
            memory_usage[memory] += size
            
            input_section = random.choice(["code", "data", "bss"])
            out_section = f"{memory}_{'code' if input_section == 'code' else 'data'}"
            address = hex(np.random.randint(0x80000000, 0x8FFFFFFF))
            output_section = random.choice(output_section_types)
            realtime = random.choices(realtime_levels, weights=[2, 3, 5])[0]
            access_count = np.random.randint(0, 101)
            hw_usage = random.choice(["Yes", "No"])
            
            records.append({
                "symbol_name": symbol_name,
                "symbol_module": module,
                "symbol_filename": filename,
                "input_section": input_section,
                "symbol_size": size,
                "symbol_address": address,
                "symbol_physical_memory": memory,
                "symbol_out_section": out_section,
                "symbol_output_section": output_section,
                "symbol_realtime": realtime,
                "symbol_access_count": access_count,
                "symbol_hw_usage": hw_usage,
                "symbol_folder_name_for_file": random.choice(FOLDER_NAMES)
            })

    os.makedirs(os.path.dirname(outfile), exist_ok=True)
    df = pd.DataFrame(records)
    df.to_csv(outfile, index=False, quoting=csv.QUOTE_NONNUMERIC)
    logger.info(f"✅ Generated {len(df)} symbols → {outfile}")
    logger.info("Memory usage summary:")
    for mem, usage in memory_usage.items():
        logger.info(f"{mem}: {usage/1024:.1f}KB / {memory_max_size[mem]/1024:.1f}KB")
    
    return df

def generate_small_symbol(size, memory, memory_weights, modules, filenames):
    """
    產生一個小型符號的資料記錄。

    Args:
        size (int): 符號大小
        memory (str): 指定的記憶體區域
        memory_weights (dict): 記憶體權重字典
        modules (list): 可用的模組列表
        filenames (list): 可用的檔案名稱列表

    Returns:
        dict: 包含單一符號所有屬性的字典
    """
    output_section_types = ["code", "data", "init", "always_power_on", "ro_after_write"]
    return {
        "symbol_name": f"small_symbol_{random.randint(1000, 9999)}",
        "symbol_module": random.choice(modules),
        "symbol_filename": random.choice(filenames),
        "input_section": random.choice(["code", "data", "bss"]),
        "symbol_size": size,
        "symbol_address": hex(np.random.randint(0x80000000, 0x8FFFFFFF)),
        "symbol_physical_memory": memory,
        "symbol_out_section": f"{memory}_data",
        "symbol_output_section": random.choice(output_section_types),
        "symbol_realtime": "Low",
        "symbol_access_count": np.random.randint(0, 33),
        "symbol_hw_usage": "No",
        "symbol_folder_name_for_file": random.choice(FOLDER_NAMES)
    }

def generate_daily_data(project_name, start_date="2024-01-01", end_date="2024-01-07", num_symbols=1500):
    """
    產生指定專案和日期範圍的符號資料。

    Args:
        project_name (str): 專案名稱
        start_date (str): 開始日期 (YYYY-MM-DD格式)
        end_date (str): 結束日期 (YYYY-MM-DD格式)
        num_symbols (int): 每天的符號數量

    Returns:
        dict: 包含所有產生的DataFrame的字典，以日期為key
    """
    from datetime import datetime, timedelta

    # 轉換日期字串為datetime物件
    start = datetime.strptime(start_date, "%Y-%m-%d")
    end = datetime.strptime(end_date, "%Y-%m-%d")
    
    base_path = os.path.join("data", project_name)
    all_data = {}
    prev_data = None
    current_date = start

    # 逐日產生資料
    day_count = 1
    while current_date <= end:
        date_str = current_date.strftime("%Y-%m-%d")
        # 為每天建立獨立資料夾
        daily_path = os.path.join(base_path, date_str)
        os.makedirs(daily_path, exist_ok=True)
        
        outfile = os.path.join(daily_path, "symbols.csv")
        df = generate_symbol_data(num_symbols, outfile, day_count, prev_data)
        all_data[date_str] = df
        prev_data = df
        
        current_date += timedelta(days=1)
        day_count += 1

    return all_data

if __name__ == "__main__":
    import argparse
    
    # 建立說明文件
    description = '''
生成符號記憶體配置的模擬資料

使用範例:
    # 基本用法 - 使用預設日期範圍
    python data_generation.py -p project1
    
    # 指定日期範圍
    python data_generation.py -p project2 -s 2024-02-01 -e 2024-02-28
    
    # 完整參數使用
    python data_generation.py -p project3 -s 2024-03-01 -e 2024-03-31 -n 2000

輸出結構:
    data/
    └── project_name/
        ├── 2024-01-01/
        │   └── symbols.csv
        ├── 2024-01-02/
        │   └── symbols.csv
        └── ...
    '''
    
    parser = argparse.ArgumentParser(
        description=description,
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    
    parser.add_argument('--project', '-p', required=True, help='專案名稱')
    parser.add_argument('--start', '-s', default='2024-01-01', help='開始日期 (YYYY-MM-DD)')
    parser.add_argument('--end', '-e', default='2024-01-07', help='結束日期 (YYYY-MM-DD)')
    parser.add_argument('--symbols', '-n', type=int, default=1500, help='每天的符號數量')
    
    args = parser.parse_args()
    generate_daily_data(
        project_name=args.project,
        start_date=args.start,
        end_date=args.end,
        num_symbols=args.symbols
    )
