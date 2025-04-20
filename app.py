
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
st.title("📊 Symbol Memory Dashboard")

# 測試資料按鈕
if st.button("🔄 產生測試資料 symbols.csv"):
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

# 🔎 異常偵測區
st.subheader("⚠️ 自動偵測配置異常")
violations = []

# 規則 1: High realtime in ext_memory
v1 = symbol_df[(symbol_df["symbol_realtime"] == "High") & symbol_df["symbol_physical_memory"].str.contains("ext")]
if not v1.empty:
    violations.append(("High Realtime 符號放入低速記憶體", v1))

# 規則 2: Low realtime in high-cost memory
v2 = symbol_df[(symbol_df["symbol_realtime"] == "Low") & symbol_df["symbol_physical_memory"].isin(["ilm", "dlm", "sysram"])]
if not v2.empty:
    violations.append(("Low Realtime 符號放入高速記憶體", v2))

# 規則 3: hw_usage = Yes 放入 ext memory
v3 = symbol_df[(symbol_df["symbol_hw_usage"] == "Yes") & symbol_df["symbol_physical_memory"].str.contains("ext")]
if not v3.empty:
    violations.append(("HW Usage 符號放入外部記憶體", v3))

# KPI 區 📊（含異常筆數統計）
st.subheader("📈 總覽 KPI")
total_cost = symbol_df["symbol_cost"].sum()
total_size = symbol_df["symbol_size"].sum()
realtime_high_count = len(symbol_df[symbol_df["symbol_realtime"] == "High"])
hw_usage_count = len(symbol_df[symbol_df["symbol_hw_usage"] == "Yes"])
violation_count = sum(len(df) for _, df in violations)

with st.container():
    k1, k2, k3, k4, k5 = st.columns(5)
    k1.metric("符號數", len(symbol_df))
    k2.metric("總大小 (KB)", f"{total_size // 1024} KB")
    k3.metric("總成本", f"{int(total_cost):,}")
    k4.metric("High Realtime 符號數", realtime_high_count)
    k5.metric("⚠️ 異常筆數", violation_count)

# 成本最多模組排行
st.subheader("🏷️ 成本最高模組排行 (Top 10)")
mod_rank = symbol_df.groupby("symbol_module")["symbol_cost"].sum().nlargest(10).reset_index()
fig_mod = px.bar(mod_rank, x="symbol_module", y="symbol_cost", text_auto=True)
st.plotly_chart(fig_mod, use_container_width=True)

# 圓餅圖（記憶體使用成本佔比）
st.subheader("🥧 記憶體區域成本佔比 Pie")
mem_cost = symbol_df.groupby("symbol_physical_memory")["symbol_cost"].sum().reset_index()
fig_pie = px.pie(mem_cost, names="symbol_physical_memory", values="symbol_cost", title="Memory Usage Share")
st.plotly_chart(fig_pie, use_container_width=True)

# 違規熱力圖
st.subheader("🔥 模組 × 規則違規熱力圖")
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
st.subheader("🌲 記憶體分布 Treemap")
fig_tree = px.treemap(
    symbol_df,
    path=["symbol_physical_memory", "symbol_module", "symbol_name"],
    values="symbol_cost",
    color="symbol_cost",
    color_continuous_scale="RdBu",
    hover_data=["symbol_size", "symbol_realtime", "symbol_hw_usage"]
)
st.plotly_chart(fig_tree, use_container_width=True)

# Symbol 表格
st.subheader("📋 Symbol 細節表")
st.dataframe(symbol_df, use_container_width=True)

# 顯示異常表格
if violations:
    for title, df_ in violations:
        st.markdown(f"### 🚨 {title} ({len(df_)})")
        st.dataframe(df_, use_container_width=True)
else:
    st.success("未偵測到異常配置！")

# 匯出功能（含異常報表與 Markdown 報告）
st.download_button("📥 下載資料 CSV", symbol_df.to_csv(index=False).encode("utf-8-sig"), file_name="symbols.csv")

if violations:
    all_violations_df = pd.concat([df for _, df in violations], ignore_index=True)
    st.download_button("📤 匯出異常報表 CSV", all_violations_df.to_csv(index=False).encode("utf-8-sig"), file_name="violations.csv")

    md = "# 🚨 Symbol Violation Summary\n\n"
    for title, df_ in violations:
        md += f"## {title} ({len(df_)})\n\n"
        md += df_.head(10).to_markdown(index=False) + "\n\n... (略)\n\n"
    st.download_button("📝 匯出 Markdown 報告", md.encode("utf-8"), file_name="violation_summary.md")
