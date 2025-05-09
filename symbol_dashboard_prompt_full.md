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
- `symbol_output_section` one of [code,data,init,always_power_on,ro_after_write]
- `symbol_out_section` (e.g., sysram_data, ilm_always_power_on, ilm_data, dlm_data)
- `symbol_physical_memory`: one of [ilm, dlm, sysram, ext_memory1, ext_memory2]
- `symbol_realtime` (High / Medium / Low) — manually labeled priority
- `symbol_access_count` (int, 0–100) — runtime access count, used for inferring potential real-time needs
- `symbol_hw_usage` (Yes / No)
- `symbol_filename` (string)
- `symbol_module` (string)
- `symbol_folder_name_for_file` one of [customer, custom/system,core/mlm, core/rlm, core/system, core/middle, open_core/mlm, open_core/rlm, open_core/system, open_core/middle, base/hal, base/prj_ram, base/exthal,open_base/hal, open_base/prj_ram, open_base/exthal]

---

## Derived Columns
- `symbol_cost` = symbol_size × memory_weight
    - ILM / DLM: 10
    - SYSRAM: 8
    - EXT MEMORY1/2: 2
- `module_cost` = sum of all symbol_cost in that module
- `symbol_cost` do not be generated in data generation and data file.

---

## Hierarchy
Nested relationships for visualization (from coarse to fine):

```
physical_memory
└── symbol_out_section
    └── module
        └── folder_name
            └── filename
                └── symbol_name
```

Note: modules , folder_name and filenames may span multiple memory regions.
Note: a file with filename existed in the one folder_name

---

## Visualization Goals
1. Identify top-cost modules
2. Spot unusually costly symbols
3. See memory usage by module
4. Track memory region usage (actual vs max allowed)
5. Analyze placement for `realtime` priority and always_power_on symbols

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
- folder_name_for_file
- filename
- input/output section
- realtime priority
- hardware usage

---

## KPI Calculation
- total cost
- cost by region
- memory usage vs max
- count of priority/hardware violations

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
   - assign `symbol_access_count` randomly from 0 to 100
   - to a module , a filename, folder_name_for_file
   - a size (e.g., 10–1000 bytes)
   - to a memory zone and out_section
   - `realtime`: High / Medium / Low
   - `hw_usage`: Yes / No
   


4. Export as a DataFrame for Streamlit use

---

## Code Maintainability and Readability Guidelines

All generated Python code must:
- Use modular structure (functions for data loading, transformation, visualization)
- Include meaningful variable names
- Use comments consistently, with:
  - WHAT: what this block does
  - WHY: why it's designed this way
- Structure UI with section headers (e.g. st.subheader) for user clarity
- Follow Streamlit best practices for performance and clarity
- Save user filtering options where appropriate (e.g. to JSON)

---

## Automated Issue Analysis

The app should automatically detect and display:

1. Modules with >50% of symbol cost placed in ILM/DLM
2. Symbols marked `realtime=High` located in slow memory (ext_memory1/2)
3. Symbols marked `realtime=Low` located in high-speed memory (ilm/dlm/sysram)
4. Symbols with `always_power_on` in low-priority modules
5. `hw_usage=Yes` symbols placed in ext_memory

All issues must be:
- Listed in a UI section (e.g., "Detected Issues")
- Optionally downloadable as CSV or Markdown summary

---

## Report Generation

Provide options to export:
- CSV: filtered symbol list, module cost summary, issue reports
- Markdown or HTML:
  - KPI summary
  - Memory usage breakdown
  - Top modules/symbols
  - Placement violations
- Optional: export visual snapshots as PDF

Enable one-click download for each report section.
