#& "C:\python\python.exe" -m streamlit run "C:\Users\jjagk\Desktop\eu monitor\mock up.py"


import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go

st.set_page_config(layout="wide", page_title="EU Protein Balance Tool")

# --- CSS Styling ---
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

# --- Sidebar Configuration ---
st.sidebar.title("🌍 Location")
countries = ["EU", "Netherlands", "Germany", "France", "Belgium", "Denmark"]
selected_country = st.sidebar.selectbox("Select Country:", countries)

st.sidebar.divider()
st.sidebar.markdown("### 🔍 Theme Guide")
with st.sidebar.expander("Learn about the Indicators", expanded=False):
    tab1, tab2, tab3, tab4, tab5 = st.tabs(["🌱", "🐄", "🚢", "🌾", "🍽️"])

    with tab1:
        st.markdown("**Production**\n\n- **Total Production:** Gross harvest volume (tons).\n- **Total Acreage:** Land area (ha) used.")
    with tab2:
        st.markdown("**Livestock**\n\n- **Population:** Total head count per category.\n- **Intake:** Quantity consumed per animal unit.")
    with tab3:
        st.markdown("**Trade Flow**\n\n- **Trade Balance:** Volume moving in/out of the EU.")
    with tab4:
        st.markdown("**Self-Sufficiency**\n\n- **National Origin %:** Use sourced from domestic production.")
    with tab5:
        st.markdown("**Competition**\n\n- **Feed-to-Food Ratio:** Analyzes crop diversion to livestock vs. human use.")

st.sidebar.divider()
st.sidebar.title("Theme select:")

current_selection = "Total production"
with st.sidebar.expander("🌱 Production"):
    choice = st.radio("Indicators:", ["Total production", "Total acreage per category/product"], key="p")
    if choice: current_selection = choice
with st.sidebar.expander("🐄 Animal Livestock"):
    choice = st.radio("Indicators:", ["Total number of livestock per production category","Composition of the feed per animal category","Feed intake per animal category per product"], key="a")
    if choice: current_selection = choice
with st.sidebar.expander("🚢 Import / Export"):
    choice = st.radio("Indicators:", ["Total imports per category/product", "Total exports per category/product"], key="ie")
    if choice: current_selection = choice
with st.sidebar.expander("🌾 Self-Sufficiency"):
    choice = st.radio("Indicators:", ["Percentage total crude protein use of national origin", "Percentage of total feed use that is of national origin","Total domestic use","Total domestic use for feed","Relative self-sufficiency per category/product","Absolute self-sufficiency per category/product"], key="ss")
    if choice: current_selection = choice
with st.sidebar.expander("🍽️ Feed/non-feed competition"):
    choice = st.radio("Indicators:", ["Total domestic use for feed", "Relative self-sufficiency", "Absolute self-sufficiency"], key="dom")
    if choice: current_selection = choice

# --- Main Header and KPIs ---
st.title("EU Protein Balance Monitoring Tool")
st.subheader(f"Theme: {current_selection}")
st.write("The total quantity of a specific commodity, such as cereals or oilseeds, consumed by the livestock sector within a given region during a marketing year.")

kpi1, kpi2, kpi3, kpi4 = st.columns(4)
kpi1.metric("Current Value", "500k Tons", "-5%")
kpi2.metric("Feed-to-Total Use Ratio", "79%", "-2%", delta_color="inverse")
kpi3.metric("10 Years Growth rate", "16.8%", "8.5%")
kpi4.metric("1 Year Growth Rate", "2.4%", "1.1%")

st.divider()

# --- Dictionary Setup ---
protein_categories = {
    "Crops (Cereals)": ["Common wheat", "Barley", "Durum", "Maize", "Rye", "Sorghum", "Oats", "Triticale", "Others (Cereals)"],
    "Crops (Oilseeds)": ["Soya beans", "Rapeseed", "Sunflowerseed"],
    "Crops (Pulses)": ["Field peas", "Broad beans", "Lupins", "Other protein crops"],
    "Co-Products (Oilseed Meals)": ["Soya bean meal", "Rapeseed meal", "Sunflower meal", "Linseed meal", "Palmkern meal", "Other oilseed meals"],
    "Co-Products (Others)": ["Starch industry products (15-30%)", "Starch industry products (60-90%)", "Distillers' dried grains", "Wheat bran", "Citrus pulp", "Beet pulp pellets", "Molasses"],
    "Non-Plant Sources": ["Fish meal", "Whey powder", "Skimmed milk powder", "Processed animal proteins", "Former foodstuff"],
    "Roughage": ["Grass", "Silage maize", "Fodder legumes", "Dried fodder"]
}

# --- Bottom Tabs Layout ---
tab_trend, tab_flow, tab_comparison = st.tabs(["📈 Annual Trends", "🔄 Sankey diagram", "📊 Detailed Breakdown"])


with tab_trend:
    left_chart, right_chart = st.columns([2, 1])

    with left_chart:
        chart_head, chart_filt = st.columns([1, 1])
        with chart_head:
            st.subheader(f"Annual Trend: {current_selection}")
        with chart_filt:
            main_cat = st.selectbox("Filter by Category:", list(protein_categories.keys()), key="chart_main")
            default_items = protein_categories[main_cat][:2]
            sub_cats = st.multiselect("Select subcategory:", options=protein_categories[main_cat], default=default_items, key="chart_sub")

        if sub_cats:
            chart_data = pd.DataFrame(
                np.random.randint(100, 200, size=(10, len(sub_cats))),
                columns=sub_cats,
                index=range(2016, 2026)
            )
            st.line_chart(chart_data)
        else:
            st.info("Please select subcategories from the filter above to view the trend.")

    with right_chart:
        st.subheader("📊 Proportion Breakdown")

        if sub_cats:
            col1, col2 = st.columns([1, 3])

            with col1:
                available_years = range(2015,2026)
                selected_year = st.selectbox("📅 Select Year", available_years)


            # 3. Place the pie chart in the second column
            with col2:
                # In a real application, you would filter your actual DataFrame here:
                # filtered_df = my_actual_df[my_actual_df['Year'] == selected_year]

                # Using your mock data setup
                pie_df = pd.DataFrame({
                    "Product": sub_cats,
                    "Amount": np.random.randint(50, 150, size=len(sub_cats))
                })

                fig = px.pie(
                    pie_df,
                    values='Amount',
                    names='Product',
                    hole=0.4,
                    color_discrete_sequence=px.colors.qualitative.Pastel
                )
                fig.update_layout(margin=dict(t=0, b=0, l=0, r=0), showlegend=True)
                st.plotly_chart(fig, use_container_width=True)

        else:
            st.warning("Select products to see breakdown.")

# TAB 2: Supply Flow (Sankey Diagram)
with tab_flow:
    st.subheader("🔄 Protein Flow Analysis (Sankey Diagram)")
    st.write("Visualizing the flow from source to end-use. This helps stakeholders identify supply chain dependencies.")

    nodes = ["Domestic Production", "Imports", "Total Supply", "Feed Use", "Food Use", "Biofuel", "Others"]
    links = {
        "source": [0, 1, 2, 2, 2, 2],
        "target": [2, 2, 3, 4, 5, 6],
        "value":  [350, 150, 420, 50, 20, 10]
    }

    fig_sankey = go.Figure(data=[go.Sankey(
        node=dict(
            pad=20, thickness=15, line=dict(color="white", width=2), label=nodes,
            color=["#81C784", "#A5D6A7", "#C8E6C9", "#4CAF50", "#66BB6A", "#9CCC65", "#AED581"]
        ),
        link=dict(
            source=links["source"], target=links["target"], value=links["value"], color="rgba(200, 230, 201, 0.5)"
        )
    )])
    fig_sankey.update_layout(
        font=dict(family="Inter, sans-serif", size=18, color="#000000"),
        paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)',
        margin=dict(t=50, b=50, l=20, r=20)
    )
    st.plotly_chart(fig_sankey, use_container_width=True)

# TAB 3: Detailed Breakdown (2015-2025 Data)
with tab_comparison:
    st.header("📊 Detailed Breakdown")
    st.subheader("Category Comparison (2015 - 2025)")
    st.write("Annual production volume comparison across key protein categories.")

    # Generate the 2015-2025 data
    years = list(range(2015, 2026))
    categories = ['Soybeans', 'Cereals', 'Rapeseed', 'Pulses']
    data = []
    for year in years:
        for cat in categories:
            base_val = {"Soybeans": 1000, "Cereals": 800, "Rapeseed": 350, "Pulses": 120}[cat]
            growth = (year - 2015) * 15
            random_flux = np.random.randint(-50, 50)
            data.append({"Year": year, "Category": cat, "Amount (Tons)": base_val + growth + random_flux})

    df_comparison = pd.DataFrame(data)

    # Bar Chart
    fig_bar = px.bar(
        df_comparison, x="Year", y="Amount (Tons)", color="Category",
        barmode="group", height=500, color_discrete_sequence=px.colors.qualitative.Pastel,
        template="plotly_white"
    )
    fig_bar.update_layout(
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
        margin=dict(t=30, b=0, l=0, r=0)
    )
    st.plotly_chart(fig_bar, use_container_width=True)

    st.divider()

    # Pivot Table
    st.subheader("Data Summary Table")
    df_pivot = df_comparison.pivot(index='Category', columns='Year', values='Amount (Tons)')
    st.dataframe(df_pivot, use_container_width=True)

# --- Sidebar Footer (Export & Contact) ---
st.sidebar.divider()
st.sidebar.subheader("📤 Export Data")

@st.cache_data
def convert_df(df):
    return df.to_csv(index=False).encode('utf-8')

# Ensure the download button uses the generated data
csv = convert_df(df_comparison)

st.sidebar.download_button(
    label="Download Report as CSV",
    data=csv,
    file_name=f'EU_Protein_Balance_{selected_country}.csv',
    mime='text/csv',
    help="Click to download the current table data for your reports."
)

st.sidebar.markdown("---")
side_col1, side_col2 = st.sidebar.columns(2)
with side_col1:
    st.link_button("Feedback", "mailto:jjagkungkungjjag@gmail.com", use_container_width=True)
with side_col2:
    st.link_button("✉ Contact", "mailto:jjagkungkungjjag@gmail.com", use_container_width=True)