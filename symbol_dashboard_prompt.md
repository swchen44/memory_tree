
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

## Automated Issue Analysis (optional feature)

The app should support:
- Highlighting modules with more than 50% of symbols in high-cost memories (ILM/DLM)
- Identifying symbols marked `realtime=Yes` located in ext_memory1/2
- Identifying symbols marked `realtime=No` located in ilm/dlm/sysram
- Detecting symbols with `always_power_on` in non-critical sections or low-priority modules
- Reporting memory overflow if total size exceeds defined physical memory max limit

All analysis results should be displayed:
- As a dedicated section in the UI (e.g. “Detected Issues”)
- And optionally downloadable as a CSV or Markdown summary

---

## Report Generation Features

Provide options to export analysis and summaries:
- CSV: filtered symbol table, module cost summary, issue reports
- Markdown or HTML:
  - KPI summary
  - Memory usage breakdown
  - Top modules/symbols
  - Issue diagnostics
- Optional: PDF export of dashboard snapshot (via `pdfkit` or HTML -> PDF)

Enable one-click export (Streamlit download button) for:
- Filtered data
- KPI overview
- Detected issues summary

