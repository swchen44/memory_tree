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

def generate_symbol_data(num_symbols=1500, outfile="data/symbols.csv"):
    logger = setup_logging()
    logger.info(f"Generating {num_symbols} synthetic symbols...")

    memory_types = ["ilm", "dlm", "sysram", "ext_memory1", "ext_memory2"]
    out_sections = [
        "ilm", "dlm", "ilm_always_power_on", "dlm_always_power_on",
        "sysram_code", "sysram_data",
        "ext_memory1_code", "ext_memory1_data",
        "ext_memory2_code", "ext_memory2_data"
    ]
    realtime_levels = ["High", "Medium", "Low"]
    protection_modes = ["ro", "rw", "always_power_on", "ro_after_write"]

    modules = [f"module_{i}" for i in range(1, 16)]
    filenames = [f"file_{i}.c" for i in range(1, 61)]

    random.seed(42)
    np.random.seed(42)

    records = []
    for i in range(num_symbols):
        symbol_name = f"symbol_{i}"
        module = random.choice(modules)
        filename = random.choice(filenames)
        input_section = random.choice(["code", "data", "bss"])
        size = np.random.randint(16, 2048)
        memory = random.choices(memory_types, weights=[5, 5, 8, 10, 10])[0]
        out_section = random.choice(out_sections)
        address = hex(np.random.randint(0x80000000, 0x8FFFFFFF))
        protection = random.choice(protection_modes)
        access_count = np.random.randint(0, 101)
        realtime = random.choices(realtime_levels, weights=[2, 4, 4])[0]
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
            "symbol_protection": protection,
            "symbol_realtime": realtime,
            "symbol_access_count": access_count,
            "symbol_hw_usage": hw_usage
        })

    os.makedirs(os.path.dirname(outfile), exist_ok=True)
    df = pd.DataFrame(records)
    df.to_csv(outfile, index=False, quoting=csv.QUOTE_NONNUMERIC)
    logger.info(f"✅ Generated {len(df)} symbols → {outfile}")

if __name__ == "__main__":
    generate_symbol_data()
