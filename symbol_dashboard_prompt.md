
# Streamlit Dashboard for Symbol Memory Cost Analysis

## Objective
Build a Streamlit + Plotly-based dashboard for analyzing ELF symbol placement in a RISC-V bare-metal image. The dashboard should help developers detect cost hotspots and suboptimal memory usage.

---

## Data Model
Each row in the dataset represents a symbol and contains:

- `symbol_name` (string)
- `input_section` (code/data/bss)
- `symbol_address` (hex string)
- `symbol_size` (int, in bytes)
- `symbol_protection` (ro/rw/always_power_on/ro_after_write)
- `symbol_out_section` (e.g., sysram data, ilm_always_power_on)
- `symbol_physical_memory`: one of [ilm, dlm, sysram, ext_memory1, ext_memory2]
- `symbol_realtime` (Yes/No)
- `symbol_filename` (string)
- `symbol_module` (string)

---

## Derived Columns
- `symbol_cost` = symbol_size × memory_weight
    - ILM / DLM: 10
    - SYSRAM: 8
    - EXT MEMORY1/2: 2
- `module_cost` = sum of all symbol_cost in that module

---

## Hierarchy
Nested relationships for visualization (from coarse to fine):

```
physical_memory
└── symbol_out_section
    └── module
        └── filename
            └── symbol_name
```

Note: modules and filenames may span multiple memory regions.

---

## Visualization Goals
1. Identify top-cost modules
2. Spot unusually costly symbols
3. See memory usage by module
4. Track memory region usage (actual vs max allowed)
5. Analyze placement for `realtime=Yes` and `always_power_on` symbols

---

## Required Visualizations
1. Treemap (memory > module > symbol), value = cost
2. Sunburst (same structure, radial)
3. Bar chart (top modules/symbols by cost)
4. Pie chart (memory zone cost share)
5. Table with sorting, conditional formatting, filtering
6. Heatmap (module × memory cost)
7. KPI Summary panel: total cost, memory usage, violations, etc.

---

## Filtering Options
- memory region
- module
- filename
- input/output section
- realtime flag
- protection type

---

## KPI Calculation
- total cost
- cost by region
- violations: realtime symbols in slow memory, power_on overflow

---

## Inline Code Comments
All major blocks must be commented using:
- WHAT: describe purpose
- WHY: explain reasoning

---

## Simulated Data Generation (for testing)

Steps to create test data:

1. Define memory zones:
   - ilm, dlm, sysram, ext_memory1, ext_memory2
   - with max_size and memory_cost

2. Randomly generate:
   - 10–20 modules
   - 50–100 files
   - 500–2000 symbols

3. Assign each symbol:
   - to a module and a filename
   - a size (e.g., 10–1000 bytes)
   - to a memory zone and out_section
   - properties like realtime, protection
   - compute cost using `symbol_size * memory_cost`

4. Calculate:
   - module-level aggregated cost
   - total memory usage per zone

5. Export as a DataFrame for Streamlit use

---

## Output
- Deliver a working `streamlit` app using the above logic
- Include sample data generator
- Support download of filtered results as CSV
