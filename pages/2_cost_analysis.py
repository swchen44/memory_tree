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

# 檢查是否有篩選後的資料
if 'filtered_data' not in st.session_state:
    st.warning("請先回到首頁設定篩選條件")
    st.stop()

# 使用已篩選的資料
df_filtered = st.session_state['filtered_data']
filters = st.session_state['filter_conditions']

with st.expander("目前篩選條件"):
    st.write(filters)

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
