# data_generation.py
# Generate synthetic symbol data for Streamlit Symbol Memory Dashboard

import pandas as pd
import numpy as np
import random
import os
import csv
import logging

def setup_logging():
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
    protection_modes = ["ro", "rw", "always_power_on", "ro_after_write"]
    
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
        protection = random.choice(protection_modes)
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
            "symbol_protection": protection,
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
    # 產生較小的符號的輔助函數
    return {
        "symbol_name": f"small_symbol_{random.randint(1000, 9999)}",
        "symbol_module": random.choice(modules),
        "symbol_filename": random.choice(filenames),
        "input_section": random.choice(["code", "data", "bss"]),
        "symbol_size": size,
        "symbol_address": hex(np.random.randint(0x80000000, 0x8FFFFFFF)),
        "symbol_physical_memory": memory,
        "symbol_out_section": f"{memory}_data",
        "symbol_protection": random.choice(["ro", "rw"]),
        "symbol_realtime": "Low",
        "symbol_access_count": np.random.randint(0, 33),
        "symbol_hw_usage": "No",
        "symbol_cost": size * memory_weights[memory],
        "symbol_folder_name_for_file": random.choice(FOLDER_NAMES)
    }

if __name__ == "__main__":
    generate_symbol_data()
