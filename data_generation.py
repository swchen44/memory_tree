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

def generate_symbol_data(num_symbols=1500, outfile="data/symbols.csv"):
    """
    產生模擬的符號記憶體配置資料。

    Args:
        num_symbols (int, optional): 要產生的符號數量. 預設為1500.
        outfile (str, optional): 輸出CSV檔案路徑. 預設為"data/symbols.csv".

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
            - symbol_cost: 記憶體成本
            - symbol_folder_name_for_file: 資料夾路徑

    記憶體限制:
        - ilm: 64KB
        - dlm: 64KB
        - sysram: 256KB
        - ext_memory1: 1MB
        - ext_memory2: 1MB
    """
    logger = setup_logging()
    logger.info(f"Generating {num_symbols} synthetic symbols...")

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
    
    # 產生符號資料
    records = []
    memory_usage = {mem: 0 for mem in memory_types}
    
    for i in range(num_symbols):
        # 基本符號資訊
        symbol_name = f"symbol_{i}"
        module = random.choice(modules)
        filename = random.choice(filenames)
        
        # 記憶體配置相關
        size = np.random.randint(16, 2048)  # 16B ~ 2KB
        memory = random.choices(memory_types, weights=[memory_weights[m] for m in memory_types])[0]
        
        # 檢查記憶體限制
        if memory_usage[memory] + size > memory_max_size[memory]:
            continue
        memory_usage[memory] += size
        
        # 其他屬性
        input_section = random.choice(["code", "data", "bss"])
        out_section = f"{memory}_{'code' if input_section == 'code' else 'data'}"
        address = hex(np.random.randint(0x80000000, 0x8FFFFFFF))
        output_section = random.choice(output_section_types)
        realtime = random.choices(realtime_levels, weights=[2, 3, 5])[0]
        access_count = np.random.randint(0, 101)
        hw_usage = random.choice(["Yes", "No"])
        
        # 計算成本
        cost = size * memory_weights[memory]
        
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
            "symbol_cost": cost,
            "symbol_folder_name_for_file": random.choice(FOLDER_NAMES)
        })

    # 確保產生足夠的資料
    while len(records) < num_symbols:
        size = np.random.randint(16, 128)  # 產生較小的符號
        memory = random.choices(memory_types, weights=[memory_weights[m] for m in memory_types])[0]
        if memory_usage[memory] + size <= memory_max_size[memory]:
            # 加入新的小符號
            records.append(generate_small_symbol(size, memory, memory_weights, modules, filenames))
            memory_usage[memory] += size

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
        "symbol_cost": size * memory_weights[memory],
        "symbol_folder_name_for_file": random.choice(FOLDER_NAMES)
    }

if __name__ == "__main__":
    generate_symbol_data()
