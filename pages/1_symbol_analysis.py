import streamlit as st
import pandas as pd
import plotly.express as px
from pathlib import Path
import sys

# 添加父目錄到路徑
parent_dir = str(Path(__file__).parent.parent)
sys.path.append(parent_dir)

from app import load_data

st.set_page_config(page_title="Symbol Analysis", page_icon="🔍", layout="wide")
st.title("Symbol Analysis")

# 側邊欄導航
#selected_page = st.sidebar.radio(
#    "選擇頁面",
#    options=["首頁", "符號分析"],
#    index=1  # 預設選擇符號分析
#)

#if selected_page == "首頁":
#    st.switch_page("app.py")

# 載入資料
symbol_df = load_data()
if symbol_df.empty:
    st.warning("請先回到首頁上傳或產生測試資料")
#if st.button("回到首頁"):
#   st.switch_page("app.py")
    st.stop()

# 篩選器設定
filters = {
    "memory": sorted(symbol_df["symbol_physical_memory"].unique()),
    "module": sorted(symbol_df["symbol_module"].unique()),
    "folder": sorted(symbol_df["symbol_folder_name_for_file"].unique()),
    "section": sorted(symbol_df["input_section"].unique()),
    "realtime": ["High", "Medium", "Low"]
}

# 篩選功能
col1, col2 = st.columns([3, 1])
with col2:
    st.subheader("記憶體分布篩選")
    memory_filter = st.multiselect("記憶體區域", options=filters["memory"])
    module_filter = st.multiselect("模組", options=filters["module"])
    section_filter = st.multiselect("Section", options=filters["section"])

# 套用篩選
df_filtered = symbol_df.copy()
if memory_filter:
    df_filtered = df_filtered[df_filtered["symbol_physical_memory"].isin(memory_filter)]
if module_filter:
    df_filtered = df_filtered[df_filtered["symbol_module"].isin(module_filter)]
if section_filter:
    df_filtered = df_filtered[df_filtered["input_section"].isin(section_filter)]

with col1:
    st.subheader("記憶體分布 Treemap")
    module_sizes = (df_filtered.groupby("symbol_module")["symbol_size"].sum() / 1024).to_dict()
    df_filtered["module_total_size"] = df_filtered["symbol_module"].map(module_sizes)

    fig_tree = px.treemap(
        df_filtered,
        path=["symbol_physical_memory", "symbol_module", "symbol_name"],
        values="symbol_size",
        color="symbol_cost",
        color_continuous_scale="RdBu",
        hover_data={
            "symbol_size": ":,.0f",
            "symbol_realtime": True,
            "symbol_hw_usage": True,
            "module_total_size": ":.2f KB"
        },
        custom_data=["module_total_size", "symbol_size"]
    )

    fig_tree.update_traces(
        hovertemplate="""
        <b>%{label}</b><br>
        Size: %{customdata[1]:,.0f} bytes<br>
        Module Total: %{customdata[0]:.2f} KB<br>
        Cost: %{color}<br>
        <extra></extra>
        """
    )
    st.plotly_chart(fig_tree, use_container_width=True)

    # 記憶體使用統計
    st.subheader("記憶體使用統計")
    mem_stats = df_filtered.groupby("symbol_physical_memory").agg({
        "symbol_size": ["sum", "count", "mean"]
    }).round(2)
    mem_stats.columns = ["總大小(bytes)", "符號數量", "平均大小(bytes)"]
    st.dataframe(mem_stats)
