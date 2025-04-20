import streamlit as st
import pandas as pd
import plotly.express as px
from pathlib import Path
import sys

# 添加父目錄到路徑
parent_dir = str(Path(__file__).parent.parent)
sys.path.append(parent_dir)

from app import load_data

st.set_page_config(page_title="Cost Analysis", page_icon="💰", layout="wide")
st.title("Cost Analysis")

# 載入資料
symbol_df = load_data()
if symbol_df.empty:
    st.warning("請先回到首頁上傳或產生測試資料")
    if st.button("回到首頁"):
        st.switch_page("app.py")
    st.stop()

# 篩選器設定
filters = {
    "memory": sorted(symbol_df["symbol_physical_memory"].unique()),
    "module": sorted(symbol_df["symbol_module"].unique()),
    "folder": sorted(symbol_df["symbol_folder_name_for_file"].unique())
}

col1, col2 = st.columns([3, 1])
with col2:
    st.subheader("成本分析篩選")
    module_filter = st.multiselect("模組", options=filters["module"])
    memory_filter = st.multiselect("記憶體區域", options=filters["memory"])
    folder_filter = st.multiselect("資料夾", options=filters["folder"])

# 套用篩選
df_filtered = symbol_df.copy()
if module_filter:
    df_filtered = df_filtered[df_filtered["symbol_module"].isin(module_filter)]
if memory_filter:
    df_filtered = df_filtered[df_filtered["symbol_physical_memory"].isin(memory_filter)]
if folder_filter:
    df_filtered = df_filtered[df_filtered["symbol_folder_name_for_file"].isin(folder_filter)]

with col1:
    # 成本最高模組排行
    st.subheader("成本最高模組排行 (Top 10)")
    mod_rank = df_filtered.groupby("symbol_module")["symbol_cost"].sum().nlargest(10).reset_index()
    fig_mod = px.bar(mod_rank, x="symbol_module", y="symbol_cost", text_auto=True)
    st.plotly_chart(fig_mod, use_container_width=True)

    # 記憶體成本佔比
    st.subheader("記憶體區域成本佔比")
    mem_cost = df_filtered.groupby("symbol_physical_memory")["symbol_cost"].sum().reset_index()
    fig_pie = px.pie(mem_cost, names="symbol_physical_memory", values="symbol_cost")
    st.plotly_chart(fig_pie, use_container_width=True)

    # 資料夾成本分析
    st.subheader("資料夾成本分析")
    folder_cost = df_filtered.groupby("symbol_folder_name_for_file")["symbol_cost"].sum().sort_values(ascending=False)
    fig_folder = px.bar(
        folder_cost.reset_index(), 
        x="symbol_folder_name_for_file", 
        y="symbol_cost",
        labels={"symbol_folder_name_for_file": "資料夾", "symbol_cost": "成本"}
    )
    fig_folder.update_layout(xaxis_tickangle=-45)
    st.plotly_chart(fig_folder, use_container_width=True)

# 成本統計表
st.subheader("成本統計表")
cost_stats = df_filtered.groupby(["symbol_module", "symbol_physical_memory"]).agg({
    "symbol_cost": ["sum", "mean", "count"]
}).round(2)
cost_stats.columns = ["總成本", "平均成本", "符號數量"]
st.dataframe(cost_stats)
