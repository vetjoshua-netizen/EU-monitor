# -*- coding: utf-8 -*-
"""
Spyder Editor

This is a temporary script file.
"""

#%% 1. import data and combine
# ! "C:\python\python.exe" -m streamlit run "C:\Users\jjagk\Desktop\study\Data Driven Supply Chain Management\assignment c\feng.py"

import sqlite3
import pandas as pd
import streamlit as st
import plotly.express as px
import os
current_dir = os.path.dirname(os.path.abspath(__file__))
db_path = os.path.join(current_dir, 'EU monitor.db')
conn = sqlite3.connect(db_path)

query = """
SELECT *, '2023-2024' as year_label FROM (
    SELECT *,
    (CAST("Feed_use_EU_origin(I)=(F)*(G)" AS FLOAT) / NULLIF(CAST("EU_total_feed_use(H)=(E)*(G)" AS FLOAT), 0)) * 100 AS "Percentage total crude protein use of EU origin",
    (CAST("EU_imports_(B)" AS FLOAT) - CAST("EU_exports_(C)" AS FLOAT)) AS "Production surplus/shortfall"
    FROM "2023-2024"
)
UNION ALL
SELECT *, '2022-2023' as year_label FROM (
    SELECT *,
    (CAST("Feed_use_EU_origin(I)=(F)*(G)" AS FLOAT) / NULLIF(CAST("EU_total_feed_use(H)=(E)*(G)" AS FLOAT), 0)) * 100 AS "Percentage total crude protein use of EU origin",
    (CAST("EU_imports_(B)" AS FLOAT) - CAST("EU_exports_(C)" AS FLOAT)) AS "Production surplus/shortfall"
    FROM "2022-2023"
)
"""
df = pd.read_sql_query(query, conn)
conn.close()

df['Percentage total crude protein use of EU origin'] = pd.to_numeric(
    df['Percentage total crude protein use of EU origin'])
df['Production surplus/shortfall'] = pd.to_numeric(df['Production surplus/shortfall'])

#%% 1-2. clean the data and make a dictionary
exclude_cols = ['category', 'Subcategory', 'Protein_source', 'year_label', 'year']
cols_to_convert = [c for c in df.columns if c not in exclude_cols]
df[cols_to_convert] = df[cols_to_convert].apply(pd.to_numeric, errors='coerce')


#dictionary
metric_dict = {
    "Self-Sufficiency": {
        "Self-Sufficiency Rate (%)": 'Percentage total crude protein use of EU origin',
        "Production Surplus/Shortfall (T)": 'Production surplus/shortfall',
        "Total Production (Tonnes)": 'Total_EU_production_(A)',
        "Import Volume (Tonnes)": 'EU_imports_(B)',
        "Export Volume (Tonnes)": 'EU_exports_(C)',
        "Total Domestic Use (Tonnes)": 'Total_EU_domestic_use_(D)'
    },

    "Feed-Food Competition": {
        "Feed Use Share (%)": '%of_total_feed_use',
        "Total Feed Volume (Tonnes)": 'EU_total_feed_use(E)',
        "Food/Industrial Use (Tonnes)": 'Total_EU_domestic_use_(D)' 
    }
}
#%% 2. sidebar
st.sidebar.title("EU Protein Monitor")

# 1. 選擇主題
selected_theme = st.sidebar.selectbox("1. Select Theme:", list(metric_dict.keys()))

# 2. 選擇年份
available_years = sorted(df['year_label'].unique(), reverse=True)
selected_year = st.sidebar.selectbox("2. Select Marketing Year:", available_years)

# 3. 選擇視角 (Macro vs Detail)
view_mode = st.sidebar.radio("3. View Depth:", ["Macro Overview", "Detailed Breakdown"])

# 4. 選擇指標 (關鍵步驟：根據 Theme 動態載入字典裡的 Keys)
available_metrics = list(metric_dict[selected_theme].keys())
selected_metric_label = st.sidebar.selectbox("4. Select Metric to Analyze:", available_metrics)

# 取得真正的欄位名稱 (從字典反查)
selected_col = metric_dict[selected_theme][selected_metric_label]

#%% 3. rate or number
is_rate = any(x in selected_metric_label for x in ['%', 'Rate', 'Share'])
if is_rate:
    agg_func = 'mean'
    val_fmt = '.1f'
else:
    agg_func = 'sum'
    val_fmt = ',.0f'
curr_df = df[df['year_label'] == selected_year]


#%% 4. KPI Card 
st.title(f"📊 {selected_theme}")
st.markdown(f"**Focus:** {selected_metric_label} | **Year:** {selected_year}")

# 1. 計算當年度數值 (Current)
if not curr_df.empty:
    kpi_val = curr_df[selected_col].agg(agg_func)
else:
    kpi_val = 0

# 2. 計算上一年度數值 (Previous) 用於對比
# 找出目前年份在列表中的位置，下一個就是去年 (因為列表是倒序的)
current_year_idx = available_years.index(selected_year)

prev_kpi_val = 0
delta_val = None
delta_str = None

# 如果不是最後一年 (代表還有更舊的年份可以比)
if current_year_idx + 1 < len(available_years):
    prev_year = available_years[current_year_idx + 1]
    prev_df = df[df['year_label'] == prev_year]
    
    if not prev_df.empty:
        prev_kpi_val = prev_df[selected_col].agg(agg_func)
        
        # 計算差值
        raw_delta = kpi_val - prev_kpi_val
        
        # 根據是不是百分比，決定 Delta 顯示的格式
        if is_rate:
            delta_str = f"{raw_delta:.1f} pp" # pp = percentage points
        else:
            # 如果數字太大 (例如百萬噸)，縮寫顯示以免太長
            if abs(raw_delta) >= 1_000_000:
                delta_str = f"{raw_delta/1_000_000:+.1f}M"
            elif abs(raw_delta) >= 1_000:
                delta_str = f"{raw_delta/1_000:+.1f}K"
            else:
                delta_str = f"{raw_delta:+.0f}"

# 3. 顯示 KPI 卡片 (使用 st.container 增加框框感)
# 使用 columns 讓卡片不要佔滿整個寬度，看起來比較精緻
kpi_c1, kpi_c2, kpi_c3 = st.columns([1, 2, 1]) 

with kpi_c2: # 放在中間的 column
    with st.container(border=True): # 這是關鍵：加上邊框
        st.metric(
            label=f"Total/Avg {selected_metric_label}", 
            value=f"{kpi_val:{val_fmt}}",
            delta=delta_str, # 這會自動顯示綠色(正)或紅色(負)
            delta_color="normal" # normal: 漲是綠，跌是紅
        )
        
        # 如果有比較數據，顯示一行小字說明是跟哪一年比
        if delta_str:
            st.caption(f"Compared to previous year ({available_years[current_year_idx + 1]})")

st.divider()
    
#%% 5. Macro overview/detailed breakdown

if view_mode == "Macro Overview":
    st.header(f"Overview: {selected_metric_label}")
    
    # 使用 selected_col 動態畫圖
    overview_data = curr_df.groupby('category')[selected_col].agg(agg_func).reset_index()
    
    fig = px.bar(overview_data, 
                 x='category', 
                 y=selected_col,
                 color='category',
                 title=f"{selected_metric_label} by Category",
                 text_auto=val_fmt,
                 template="plotly_white")
    
    # 自給率 100% 參考線
    if is_rate and "Self" in selected_theme:
        fig.add_hline(y=100, line_dash="dash", line_color="red")
        
    st.plotly_chart(fig, use_container_width=True)

elif view_mode == "Detailed Breakdown":
    st.header(f"Detailed Analysis: {selected_metric_label}")
    
    # 1. 選 Category
    selected_cat = st.selectbox("Step 1: Select Category:", df['category'].unique())
    cat_df = curr_df[curr_df['category'] == selected_cat]
    
    # 圖表 1: Subcategory
    sub_data = cat_df.groupby('Subcategory')[selected_col].agg(agg_func).reset_index()
    
    fig1 = px.bar(sub_data,
                  x='Subcategory',
                  y=selected_col,
                  color='Subcategory',
                  title=f"Breakdown by Subcategory ({selected_cat})",
                  text_auto=val_fmt,
                  template="plotly_white")
    st.plotly_chart(fig1, use_container_width=True)
    
    st.markdown("---")
    
    # 2. 選 Subcategory
    selected_subcat = st.selectbox("Step 2: Drill down into Subcategory:", cat_df['Subcategory'].unique())
    sub_df = cat_df[cat_df['Subcategory'] == selected_subcat]
    
    # 圖表 2: Protein Source
    source_data = sub_df.groupby('Protein_source')[selected_col].agg(agg_func).reset_index()

    fig2 = px.bar(source_data,
                  x='Protein_source',
                  y=selected_col,
                  color='Protein_source',
                  title=f"Protein Sources in {selected_subcat}",
                  text_auto=val_fmt,
                  template="plotly_white")
    st.plotly_chart(fig2, use_container_width=True)
    
#%% Run streamlit
# enter code below in pycharm terminal. if you are using other python program, then i dont know.
# maybe ask gpt how to convert code into other python program.
#cd "C:\Users\jjagk\Desktop\eu monitor"
#& "C:\python\python.exe" -m streamlit run "eu monitor.py"