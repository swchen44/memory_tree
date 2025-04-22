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

# 檢查是否有篩選後的資料
if 'filtered_data' not in st.session_state:
    st.warning("請先回到首頁設定篩選條件")
    st.stop()

# 使用已篩選的資料
df_filtered = st.session_state['filtered_data']
filters = st.session_state['filter_conditions']

with st.expander("目前篩選條件"):
    st.write(filters)

# 直接顯示 Treemap
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
