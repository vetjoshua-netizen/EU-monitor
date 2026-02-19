#& "C:\python\python.exe" -m streamlit run "C:\Users\jjagk\Desktop\eu monitor\mock up.py"


import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px

st.set_page_config(layout="wide", page_title="EU Protein Balance Tool")

# structure
st.markdown("""
    <style>
    [data-testid="stMetric"] {
        background-color: #f8f9fa;
        border: 1px solid #d1d1d1;
        padding: 15px;
        border-radius: 5px;
    }
    </style>
    """, unsafe_allow_html=True)
st.sidebar.title("🌍 Location")

#country
countries = ["EU","Netherlands", "Germany", "France", "Belgium", "Denmark"]
selected_country = st.sidebar.selectbox("Select Country:", countries)

#Themes
st.sidebar.title("Theme select:")

current_selection = "Total production"
with st.sidebar.expander("🌱 Production"):
    choice = st.radio("Indicators:", ["Total production", "Total acreage per category/product"], key="p")
    if choice: current_selection = choice
with st.sidebar.expander("🐄 Animal Livestock"):
    choice = st.radio("Indicators:", ["Total number of livestock per production category","Composition of the feed per animal category","Feed intake per animal category per product"], key="a")
    if choice: current_selection = choice
with st.sidebar.expander("🚢 Import / Export"):
    choice = st.radio("Indicators:", ["Total imports per category/product", "Total exports per category/product"],
                      key="ie")
    if choice: current_selection = choice
with st.sidebar.expander("🌾 Self-Sufficiency"):
    choice = st.radio("Indicators:", ["Percentage total crude protein use of national origin", "Percentage of total feed use that is of national origin","Total domestic use","Total domestic use for feed","Relative self-sufficiency per category/product","Absolute self-sufficiency per category/product"], key="ss")
    if choice: current_selection = choice
with st.sidebar.expander("🍽️ Feed/non-feed competition"):
    choice = st.radio("Indicators:",
                      ["Total domestic use for feed", "Relative self-sufficiency", "Absolute self-sufficiency"],
                      key="dom")
    if choice: current_selection = choice

# Header
st.title("EU Protein Balance Monitoring Tool")
st.subheader(f"Theme: {current_selection}")
st.write(f"Showing structural visualization for **{current_selection}** across the EU.")

#KPI
kpi1, kpi2, kpi3, kpi4 = st.columns(4)
kpi1.metric("Current Value", "500k Tons", "-5%")
kpi2.metric("Self-Sufficiency", "65%", "-2%", delta_color="inverse")
kpi3.metric("10Years Growth rate", "16.8%", "8.5%")
kpi4.metric("1 Year Growth Rate", "2.4%", "1.1%")

st.divider()

# Line Chart on Left, Pie / Table on Right
left_chart, right_chart = st.columns([2, 1])

# dictionary
protein_categories = {
    "Crops (Cereals)": [
        "Common wheat", "Barley", "Durum", "Maize", "Rye",
        "Sorghum", "Oats", "Triticale", "Others (Cereals)"
    ],
    "Crops (Oilseeds)": [
        "Soya beans", "Rapeseed", "Sunflowerseed"
    ],
    "Crops (Pulses)": [
        "Field peas", "Broad beans", "Lupins", "Other protein crops"
    ],
    "Co-Products (Oilseed Meals)": [
        "Soya bean meal", "Rapeseed meal", "Sunflower meal",
        "Linseed meal", "Palmkern meal", "Other oilseed meals"
    ],
    "Co-Products (Others)": [
        "Starch industry products (15-30%)", "Starch industry products (60-90%)",
        "Distillers' dried grains", "Wheat bran", "Citrus pulp",
        "Beet pulp pellets", "Molasses"
    ],
    "Non-Plant Sources": [
        "Fish meal", "Whey powder", "Skimmed milk powder",
        "Processed animal proteins", "Former foodstuff"
    ],
    "Roughage": [
        "Grass", "Silage maize", "Fodder legumes", "Dried fodder"
    ]
}
chart_header, filter_main, filter_sub = st.columns([2, 1, 1])

#line chart
with left_chart:
    chart_head, chart_filt = st.columns([1, 1])
    with chart_head:
        st.subheader(f"Annual Trend: {current_selection}")
    with chart_filt:
        # 1. Main category selection
        main_cat = st.selectbox(
            "Filter by Category:",
            list(protein_categories.keys()),
            key="chart_main"
        )

        # 2. Define default values (Picking the first two items of the selected group)
        default_items = protein_categories[main_cat][:2]

        # 3. Multiselect with the default parameter
        sub_cats = st.multiselect(
            "Select subcategory:",
            options=protein_categories[main_cat],
            default=default_items,
            key="chart_sub"
        )

    # Render the Chart
    if sub_cats:
        chart_data = pd.DataFrame(
            np.random.randint(100, 200, size=(10, len(sub_cats))),
            columns=sub_cats,
            index=range(2016, 2026)
        )
        st.line_chart(chart_data)
    else:
        st.info("Please select subcategories from the filter above to view the trend.")

#pie chart
with right_chart:
    st.subheader("📊 Proportion Breakdown")

    if sub_cats:
        pie_df = pd.DataFrame({
            "Product": sub_cats,
            "Amount": np.random.randint(50, 150, size=len(sub_cats))
        })

        fig = px.pie(pie_df, values='Amount', names='Product',
                     hole=0.4,
                     color_discrete_sequence=px.colors.qualitative.Pastel)

        fig.update_layout(margin=dict(t=0, b=0, l=0, r=0), showlegend=True)
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.warning("Select products to see breakdown.")

    st.divider()

    # 6. Summary Table
    st.subheader("Year-on-Year Analysis")
    st.write("Detailed figures from the EU Protein Balance Sheet:")

    df_table = pd.DataFrame({
        'Sub-Category': ['Soybeans', 'Cereals', 'Rapeseed', 'Pulses'],
        '2023 (Tons)': [1200, 950, 400, 150],
        '2024 (Tons)': [1250, 930, 420, 160],
        'Change (%)': ['+4.1%', '-2.1%', '+5.0%', '+6.6%']
    })
    st.table(df_table)