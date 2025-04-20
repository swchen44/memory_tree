# app.py - 主程式 for Symbol Memory Dashboard

import streamlit as st
import pandas as pd
import plotly.express as px
import os
import logging
from data_generation import generate_symbol_data

# logging 設定
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(message)s')
logger = logging.getLogger("dashboard")

# UI 標題
st.set_page_config(page_title="Symbol Memory Dashboard", layout="wide")
st.title("Symbol Memory Dashboard")

# 測試資料按鈕
if st.button("產生測試資料 symbols.csv"):
    generate_symbol_data(num_symbols=1000)
    st.success("測試資料已產生 data/symbols.csv")

# 載入資料
@st.cache_data
def load_data():
    path = "data/symbols.csv"
    if not os.path.exists(path):
        return pd.DataFrame()
    df = pd.read_csv(path)
    df["symbol_cost"] = df["symbol_size"] * df["symbol_physical_memory"].map({
        "ilm": 10, "dlm": 10, "sysram": 8, "ext_memory1": 2, "ext_memory2": 2
    }).fillna(1)
    return df

symbol_df = load_data()
if symbol_df.empty:
    st.warning("請先上傳或產生測試資料 symbols.csv")
    st.stop()

# 新增篩選器區域
st.sidebar.header("資料篩選")

# 記憶體區域篩選
memory_filter = st.sidebar.multiselect(
    "記憶體區域",
    options=sorted(symbol_df["symbol_physical_memory"].unique()),
    default=[]
)

# 模組篩選
module_filter = st.sidebar.multiselect(
    "模組",
    options=sorted(symbol_df["symbol_module"].unique()),
    default=[]
)

# 資料夾篩選
folder_filter = st.sidebar.multiselect(
    "資料夾",
    options=sorted(symbol_df["symbol_folder_name_for_file"].unique()),
    default=[]
)

# 檔案名稱篩選
file_filter = st.sidebar.multiselect(
    "檔案名稱",
    options=sorted(symbol_df["symbol_filename"].unique()),
    default=[]
)

# Section 篩選
section_filter = st.sidebar.multiselect(
    "Section",
    options=sorted(symbol_df["input_section"].unique()),
    default=[]
)

# Realtime 優先級篩選
realtime_filter = st.sidebar.multiselect(
    "即時性需求",
    options=["High", "Medium", "Low"],
    default=[]
)

# 硬體使用篩選
hw_usage_filter = st.sidebar.multiselect(
    "硬體使用",
    options=["Yes", "No"],
    default=[]
)

# 保護類型篩選
protection_filter = st.sidebar.multiselect(
    "保護類型",
    options=sorted(symbol_df["symbol_protection"].unique()),
    default=[]
)

# 應用篩選條件
df_filtered = symbol_df.copy()

if memory_filter:
    df_filtered = df_filtered[df_filtered["symbol_physical_memory"].isin(memory_filter)]
if module_filter:
    df_filtered = df_filtered[df_filtered["symbol_module"].isin(module_filter)]
if folder_filter:
    df_filtered = df_filtered[df_filtered["symbol_folder_name_for_file"].isin(folder_filter)]
if file_filter:
    df_filtered = df_filtered[df_filtered["symbol_filename"].isin(file_filter)]
if section_filter:
    df_filtered = df_filtered[df_filtered["input_section"].isin(section_filter)]
if realtime_filter:
    df_filtered = df_filtered[df_filtered["symbol_realtime"].isin(realtime_filter)]
if hw_usage_filter:
    df_filtered = df_filtered[df_filtered["symbol_hw_usage"].isin(hw_usage_filter)]
if protection_filter:
    df_filtered = df_filtered[df_filtered["symbol_protection"].isin(protection_filter)]

# 顯示篩選後的資料筆數
st.sidebar.info(f"篩選後資料筆數: {len(df_filtered)}")

# 異常偵測區
st.subheader("自動偵測配置異常")
violations = []

# 規則 1: High realtime in ext_memory
v1 = df_filtered[(df_filtered["symbol_realtime"] == "High") & df_filtered["symbol_physical_memory"].str.contains("ext")]
if not v1.empty:
    violations.append(("High Realtime 符號放入低速記憶體", v1))

# 規則 2: Low realtime in high-cost memory
v2 = df_filtered[(df_filtered["symbol_realtime"] == "Low") & df_filtered["symbol_physical_memory"].isin(["ilm", "dlm", "sysram"])]
if not v2.empty:
    violations.append(("Low Realtime 符號放入高速記憶體", v2))

# 規則 3: hw_usage = Yes 放入 ext memory
v3 = df_filtered[(df_filtered["symbol_hw_usage"] == "Yes") & df_filtered["symbol_physical_memory"].str.contains("ext")]
if not v3.empty:
    violations.append(("HW Usage 符號放入外部記憶體", v3))

# 規則 4: symbol_realtime 與 symbol_access_count 不一致
# High realtime → access count 應偏高 (> 66)，Low realtime → 應偏低 (< 33)
v4_high_mismatch = df_filtered[(df_filtered["symbol_realtime"] == "High") & (df_filtered["symbol_access_count"] < 33)]
v4_low_mismatch = df_filtered[(df_filtered["symbol_realtime"] == "Low") & (df_filtered["symbol_access_count"] > 66)]
v4 = pd.concat([v4_high_mismatch, v4_low_mismatch])
if not v4.empty:
    violations.append(("Realtime 等級與存取次數不一致", v4))

# KPI 區
st.subheader("總覽 KPI")
total_cost = df_filtered["symbol_cost"].sum()
total_size = df_filtered["symbol_size"].sum()
realtime_high_count = len(df_filtered[df_filtered["symbol_realtime"] == "High"])
hw_usage_count = len(df_filtered[df_filtered["symbol_hw_usage"] == "Yes"])
violation_count = sum(len(df) for _, df in violations)

with st.container():
    k1, k2, k3, k4, k5, k6 = st.columns(6)
    k1.metric("符號數", len(df_filtered))
    k2.metric("總大小 (KB)", f"{total_size // 1024} KB")
    k3.metric("總成本", f"{int(total_cost):,}")
    k4.metric("High Realtime 符號數", realtime_high_count)
    k5.metric("異常筆數", violation_count)
    k6.metric("Realtime 標記與存取不一致", len(v4), delta_color="inverse" if len(v4) > 0 else "off")

# 記憶體使用量監控
memory_limits = {
    "ilm": 64 * 1024,
    "dlm": 64 * 1024,
    "sysram": 256 * 1024,
    "ext_memory1": 1024 * 1024,
    "ext_memory2": 1024 * 1024
}

mem_usage = df_filtered.groupby("symbol_physical_memory")["symbol_size"].sum()
mem_usage_pct = {mem: (usage/memory_limits[mem])*100 
                 for mem, usage in mem_usage.items()}

# 在 KPI 區域後顯示記憶體使用量
st.subheader("記憶體使用量")
cols = st.columns(len(memory_limits))
for i, (mem, usage_pct) in enumerate(mem_usage_pct.items()):
    cols[i].metric(
        f"{mem} 使用率",
        f"{usage_pct:.1f}%",
        delta_color="inverse" if usage_pct > 90 else "off"
    )

# 成本最多模組排行
st.subheader("成本最高模組排行 (Top 10)")
mod_rank = df_filtered.groupby("symbol_module")["symbol_cost"].sum().nlargest(10).reset_index()
fig_mod = px.bar(mod_rank, x="symbol_module", y="symbol_cost", text_auto=True)
st.plotly_chart(fig_mod, use_container_width=True)

# 圓餅圖（記憶體使用成本佔比）
st.subheader("記憶體區域成本佔比 Pie")
mem_cost = df_filtered.groupby("symbol_physical_memory")["symbol_cost"].sum().reset_index()
fig_pie = px.pie(mem_cost, names="symbol_physical_memory", values="symbol_cost", title="Memory Usage Share")
st.plotly_chart(fig_pie, use_container_width=True)

# 違規熱力圖
st.subheader("模組 × 規則違規熱力圖")
violation_heat = pd.DataFrame()
if violations:
    for title, df_ in violations:
        heat_part = df_.groupby("symbol_module")["symbol_name"].count().reset_index()
        heat_part.columns = ["symbol_module", title]
        violation_heat = pd.merge(violation_heat, heat_part, on="symbol_module", how="outer") if not violation_heat.empty else heat_part
    violation_heat = violation_heat.fillna(0).set_index("symbol_module")
    fig_heat = px.imshow(violation_heat, text_auto=True, aspect="auto", color_continuous_scale="Reds")
    st.plotly_chart(fig_heat, use_container_width=True)

# Treemap
st.subheader("記憶體分布 Treemap")
fig_tree = px.treemap(
    df_filtered,
    path=["symbol_physical_memory", "symbol_folder_name_for_file", "symbol_module", "symbol_name"],
    values="symbol_cost",
    color="symbol_cost",
    color_continuous_scale="RdBu",
    hover_data=["symbol_size", "symbol_realtime", "symbol_hw_usage"]
)
st.plotly_chart(fig_tree, use_container_width=True)

# 新增 folder_name 分析圖表
st.subheader("資料夾成本分析")
folder_cost = df_filtered.groupby("symbol_folder_name_for_file")["symbol_cost"].sum().sort_values(ascending=False)
fig_folder = px.bar(folder_cost.reset_index(), 
                   x="symbol_folder_name_for_file", 
                   y="symbol_cost",
                   title="各資料夾成本分布",
                   labels={"symbol_folder_name_for_file": "資料夾", "symbol_cost": "成本"})
fig_folder.update_layout(xaxis_tickangle=-45)
st.plotly_chart(fig_folder, use_container_width=True)

# Symbol 表格
st.subheader("Symbol 細節表")
st.dataframe(df_filtered, use_container_width=True)

# 顯示異常表格
if violations:
    for title, df_ in violations:
        st.markdown(f"### {title} ({len(df_)})")
        st.dataframe(df_, use_container_width=True)
else:
    st.success("未偵測到異常配置！")

# 匯出功能（含異常報表與 Markdown 報告）
st.download_button("下載資料 CSV", df_filtered.to_csv(index=False).encode("utf-8-sig"), file_name="symbols.csv")

if violations:
    all_violations_df = pd.concat([df for _, df in violations], ignore_index=True)
    st.download_button("匯出異常報表 CSV", all_violations_df.to_csv(index=False).encode("utf-8-sig"), file_name="violations.csv")

    md = "# Symbol Violation Summary\n\n"
    for title, df_ in violations:
        md += f"## {title} ({len(df_)})\n\n"
        md += df_.head(10).to_markdown(index=False) + "\n\n... (略)\n\n"
    st.download_button("匯出 Markdown 報告", md.encode("utf-8"), file_name="violation_summary.md")
