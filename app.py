import streamlit as st
import pandas as pd
import numpy as np
from pathlib import Path


# ============================================================
# PAGE CONFIGURATION
# ============================================================

st.set_page_config(
    page_title="Nassau Candy Factory Optimization",
    page_icon="🏭",
    layout="wide"
)


# ============================================================
# TITLE
# ============================================================

st.title("🏭 Factory Reallocation & Shipping Optimization")

st.caption(
    "Nassau Candy Distributor — Decision Intelligence Dashboard"
)


# ============================================================
# PROJECT PATH
# ============================================================

APP_DIR = Path(__file__).resolve().parent
PROJECT_DIR = APP_DIR.parent


# ============================================================
# FIND CSV FILES
# ============================================================

def find_file(filename):

    possible_paths = [

        # Main project structure
        PROJECT_DIR / "01_Data" / "Processed" / filename,

        # Results folders
        PROJECT_DIR / "05_Results" / "Recommendations" / filename,

        # Same folder as app.py
        APP_DIR / filename,

        # Project root
        PROJECT_DIR / filename,
    ]

    for path in possible_paths:

        if path.exists():
            return path

    return None


# ============================================================
# LOAD DATA
# ============================================================

@st.cache_data
def load_data():

    historical_path = find_file("nassau_candy_cleaned.csv")
    recommendations_path = find_file("factory_recommendations.csv")
    scenarios_path = find_file("scenario_results.csv")

    missing = []

    if historical_path is None:
        missing.append("nassau_candy_cleaned.csv")

    if recommendations_path is None:
        missing.append("factory_recommendations.csv")

    if scenarios_path is None:
        missing.append("scenario_results.csv")

    if missing:

        st.error("❌ Required CSV file(s) not found:")

        for file in missing:
            st.write(f"- {file}")

        st.info(
            "Put the CSV files inside your project folders and restart Streamlit."
        )

        st.stop()

    historical = pd.read_csv(historical_path)

    recommendations = pd.read_csv(recommendations_path)

    scenarios = pd.read_csv(scenarios_path)

    return historical, recommendations, scenarios


historical, recommendations, scenarios = load_data()


# ============================================================
# CLEAN COLUMN NAMES
# ============================================================

historical.columns = historical.columns.str.strip()
recommendations.columns = recommendations.columns.str.strip()
scenarios.columns = scenarios.columns.str.strip()


# ============================================================
# CLEAN TEXT COLUMNS
# ============================================================

for df in [recommendations, scenarios]:

    for column in [
        "Product Name",
        "Region",
        "Ship Mode",
        "Current Factory",
        "Scenario Factory",
        "Scenario Confidence",
        "Risk"
    ]:

        if column in df.columns:

            df[column] = (
                df[column]
                .astype(str)
                .str.strip()
            )


# ============================================================
# CONVERT NUMERIC COLUMNS
# ============================================================

numeric_columns = [

    "Current Lead Time",
    "Scenario Lead Time",
    "Lead Time Reduction",
    "Lead Time Reduction %",
    "Optimization Score",
    "Confidence_Score",
    "Profit_Margin",
    "Orders",
    "Units",
    "Sales",
    "Gross_Profit",
    "Cost"
]


for df in [recommendations, scenarios]:

    for column in numeric_columns:

        if column in df.columns:

            df[column] = pd.to_numeric(
                df[column],
                errors="coerce"
            )


# ============================================================
# SIDEBAR
# ============================================================

st.sidebar.header("🎛️ Scenario Controls")


# ============================================================
# IMPORTANT:
# CREATE ONLY VALID PRODUCT-REGION-SHIP MODE COMBINATIONS
# ============================================================

valid_combinations = (

    recommendations[
        [
            "Product Name",
            "Region",
            "Ship Mode"
        ]
    ]

    .dropna()

    .drop_duplicates()

    .sort_values(
        [
            "Product Name",
            "Region",
            "Ship Mode"
        ]
    )

    .reset_index(drop=True)
)


# ============================================================
# PRODUCT SELECTION
# ============================================================

products = sorted(
    valid_combinations["Product Name"].unique()
)

selected_product = st.sidebar.selectbox(
    "🍬 Product",
    products
)


# ============================================================
# REGION SELECTION
# ============================================================

available_regions = sorted(

    valid_combinations[
        valid_combinations["Product Name"]
        == selected_product
    ]["Region"].unique()

)


selected_region = st.sidebar.selectbox(
    "🌎 Region",
    available_regions
)


# ============================================================
# SHIP MODE SELECTION
# ============================================================

available_ship_modes = sorted(

    valid_combinations[
        (
            valid_combinations["Product Name"]
            == selected_product
        )
        &
        (
            valid_combinations["Region"]
            == selected_region
        )
    ]["Ship Mode"].unique()

)


selected_ship_mode = st.sidebar.selectbox(
    "🚚 Ship Mode",
    available_ship_modes
)


# ============================================================
# SPEED / PROFIT PRIORITY
# ============================================================

speed_priority = st.sidebar.slider(
    "⚡ Speed Priority",
    min_value=0,
    max_value=100,
    value=50
)


profit_priority = 100 - speed_priority


st.sidebar.write(
    f"⚡ Speed Priority: {speed_priority}%"
)

st.sidebar.write(
    f"💰 Profit Priority: {profit_priority}%"
)


# ============================================================
# SELECTION INFORMATION
# ============================================================

st.subheader("🔍 Selection Information")

info1, info2, info3 = st.columns(3)

info1.write("🍬 **Product**")
info1.write(selected_product)

info2.write("🌎 **Region**")
info2.write(selected_region)

info3.write("🚚 **Ship Mode**")
info3.write(selected_ship_mode)


# ============================================================
# FILTER RECOMMENDATION
# ============================================================

selected_recommendation = recommendations[

    (
        recommendations["Product Name"]
        == selected_product
    )

    &

    (
        recommendations["Region"]
        == selected_region
    )

    &

    (
        recommendations["Ship Mode"]
        == selected_ship_mode
    )

].copy()


# ============================================================
# FILTER SCENARIOS
# ============================================================

selected_scenarios = scenarios[

    (
        scenarios["Product Name"]
        == selected_product
    )

    &

    (
        scenarios["Region"]
        == selected_region
    )

    &

    (
        scenarios["Ship Mode"]
        == selected_ship_mode
    )

].copy()


# ============================================================
# KPI SECTION
# ============================================================

st.header("📊 Key Performance Indicators")


kpi1, kpi2, kpi3, kpi4 = st.columns(4)


if not selected_recommendation.empty:

    # Best recommendation row
    selected_row = (

        selected_recommendation

        .sort_values(
            "Optimization Score",
            ascending=False
        )

        .iloc[0]

    )


    current_lead = selected_row["Current Lead Time"]

    recommended_lead = selected_row["Scenario Lead Time"]

    reduction = selected_row["Lead Time Reduction %"]

    confidence = selected_row["Scenario Confidence"]


    kpi1.metric(
        "Current Lead Time",
        f"{current_lead:.1f} days"
    )


    kpi2.metric(
        "Recommended Lead Time",
        f"{recommended_lead:.1f} days"
    )


    kpi3.metric(
        "Lead Time Reduction",
        f"{reduction:.1f}%"
    )


    kpi4.metric(
        "Confidence",
        confidence
    )


else:

    kpi1.metric(
        "Current Lead Time",
        "N/A"
    )

    kpi2.metric(
        "Recommended Lead Time",
        "N/A"
    )

    kpi3.metric(
        "Lead Time Reduction",
        "N/A"
    )

    kpi4.metric(
        "Confidence",
        "N/A"
    )


# ============================================================
# SECTION 1
# FACTORY OPTIMIZATION SIMULATOR
# ============================================================

st.header("1. 🏭 Factory Optimization Simulator")


if not selected_scenarios.empty:

    st.subheader("Available Factory Scenarios")


    scenario_display_columns = [

        "Factory",
        "Scenario Factory",
        "Current Lead Time",
        "Scenario Lead Time",
        "Lead Time Reduction",
        "Lead Time Reduction %",
        "Optimization Score",
        "Scenario Confidence",
        "Risk"

    ]


    available_columns = [

        column

        for column in scenario_display_columns

        if column in selected_scenarios.columns

    ]


    scenario_table = (

        selected_scenarios[available_columns]

        .sort_values(
            "Scenario Lead Time"
        )

        .reset_index(drop=True)

    )


    st.dataframe(
        scenario_table,
        use_container_width=True,
        hide_index=True
    )


    # --------------------------------------------------------
    # FACTORY VS LEAD TIME
    # --------------------------------------------------------

    st.subheader("📈 Factory vs Predicted Lead Time")


    chart_data = (

        selected_scenarios[
            [
                "Scenario Factory",
                "Scenario Lead Time"
            ]
        ]

        .drop_duplicates()

        .set_index("Scenario Factory")

        .sort_values("Scenario Lead Time")

    )


    st.bar_chart(
        chart_data
    )


else:

    st.warning(
        "No scenario data available for the selected Product, Region and Ship Mode."
    )


# ============================================================
# SECTION 2
# WHAT-IF ANALYSIS
# ============================================================

st.header("2. 🔄 What-If Scenario Analysis")


if not selected_recommendation.empty:

    selected_row = (

        selected_recommendation

        .sort_values(
            "Optimization Score",
            ascending=False
        )

        .iloc[0]

    )


    current_factory = selected_row["Current Factory"]

    recommended_factory = selected_row["Scenario Factory"]

    current_lead = selected_row["Current Lead Time"]

    recommended_lead = selected_row["Scenario Lead Time"]

    time_saved = current_lead - recommended_lead


    # --------------------------------------------------------
    # FACTORY COMPARISON
    # --------------------------------------------------------

    st.subheader(
        "Current vs Recommended Factory"
    )


    comparison = pd.DataFrame({

        "Configuration": [
            "Current Factory",
            "Recommended Factory"
        ],

        "Factory": [
            current_factory,
            recommended_factory
        ],

        "Lead Time": [
            current_lead,
            recommended_lead
        ]

    })


    st.dataframe(
        comparison,
        use_container_width=True,
        hide_index=True
    )


    # --------------------------------------------------------
    # LEAD TIME CHART
    # --------------------------------------------------------

    chart_comparison = pd.DataFrame({

        "Lead Time": [
            current_lead,
            recommended_lead
        ]

    }, index=[

        "Current Factory",
        "Recommended Factory"

    ])


    st.bar_chart(
        chart_comparison
    )


    # --------------------------------------------------------
    # IMPACT
    # --------------------------------------------------------

    st.subheader("🎯 Optimization Impact")


    impact1, impact2, impact3 = st.columns(3)


    impact1.metric(
        "Current Factory",
        current_factory
    )


    impact2.metric(
        "Recommended Factory",
        recommended_factory
    )


    impact3.metric(
        "Time Saved",
        f"{time_saved:.1f} days"
    )


else:

    st.warning(
        "No recommendation available for the selected Product, Region and Ship Mode."
    )


# ============================================================
# SECTION 3
# RECOMMENDATION DASHBOARD
# ============================================================

st.header("3. 🎯 Recommendation Dashboard")

st.write(
    "Top factory recommendations ranked by optimization score."
)


# ============================================================
# TOP RECOMMENDATIONS
# ============================================================

top_recommendations = (

    recommendations

    .sort_values(
        "Optimization Score",
        ascending=False
    )

    .head(10)

    .copy()

)


recommendation_columns = [

    "Product Name",
    "Region",
    "Ship Mode",
    "Current Factory",
    "Scenario Factory",
    "Current Lead Time",
    "Scenario Lead Time",
    "Lead Time Reduction %",
    "Optimization Score",
    "Scenario Confidence",
    "Risk"

]


available_recommendation_columns = [

    column

    for column in recommendation_columns

    if column in top_recommendations.columns

]


st.dataframe(

    top_recommendations[
        available_recommendation_columns
    ],

    use_container_width=True,

    hide_index=True

)


# ============================================================
# BEST OVERALL RECOMMENDATION
# ============================================================

st.subheader("🏆 Best Overall Recommendation")


if not recommendations.empty:

    best = (

        recommendations

        .sort_values(
            "Optimization Score",
            ascending=False
        )

        .iloc[0]

    )


    best1, best2, best3, best4 = st.columns(4)


    best1.metric(
        "Product",
        best["Product Name"]
    )


    best2.metric(
        "Region",
        best["Region"]
    )


    best3.metric(
        "Recommended Factory",
        best["Scenario Factory"]
    )


    best4.metric(
        "Optimization Score",
        f"{best['Optimization Score']:.3f}"
    )


# ============================================================
# OPTIMIZATION SCORE DISTRIBUTION
# ============================================================

st.subheader("Optimization Score Distribution")


score_chart = (

    recommendations

    .groupby("Product Name")["Optimization Score"]

    .max()

    .sort_values(
        ascending=False
    )

)


st.bar_chart(
    score_chart
)


# ============================================================
# SECTION 4
# RISK & IMPACT
# ============================================================

st.header("4. ⚠️ Risk & Impact Panel")


# ============================================================
# CONFIDENCE COUNTS
# ============================================================

confidence_counts = (

    recommendations[
        "Scenario Confidence"
    ]

    .value_counts()

)


high_confidence = confidence_counts.get(
    "High",
    0
)


medium_confidence = confidence_counts.get(
    "Medium",
    0
)


low_confidence = confidence_counts.get(
    "Low",
    0
)


risk1, risk2, risk3, risk4 = st.columns(4)


risk1.metric(
    "🟢 High Confidence",
    int(high_confidence)
)


risk2.metric(
    "🟠 Medium Confidence",
    int(medium_confidence)
)


risk3.metric(
    "🔴 Low Confidence",
    int(low_confidence)
)


risk4.metric(
    "📋 Total Recommendations",
    len(recommendations)
)


# ============================================================
# CONFIDENCE DISTRIBUTION
# ============================================================

st.subheader("Confidence Distribution")


confidence_chart = (

    recommendations[
        "Scenario Confidence"
    ]

    .value_counts()

)


st.bar_chart(
    confidence_chart
)


# ============================================================
# RISK DISTRIBUTION
# ============================================================

if "Risk" in recommendations.columns:

    st.subheader("Risk Distribution")


    risk_chart = (

        recommendations[
            "Risk"
        ]

        .value_counts()

    )


    st.bar_chart(
        risk_chart
    )


# ============================================================
# SECTION 5
# BUSINESS IMPACT
# ============================================================

st.header("5. 💼 Business Impact")


business1, business2, business3, business4 = st.columns(4)


# ============================================================
# AVERAGE LEAD TIME REDUCTION
# ============================================================

avg_reduction = (

    recommendations[
        "Lead Time Reduction %"
    ]

    .mean()

)


business1.metric(
    "Average Lead Time Reduction",
    f"{avg_reduction:.1f}%"
)


# ============================================================
# AVERAGE PROFIT MARGIN
# ============================================================

avg_profit_margin = (

    recommendations[
        "Profit_Margin"
    ]

    .mean()

)


# Handle both decimal and percentage formats

if avg_profit_margin <= 1:

    avg_profit_margin_display = avg_profit_margin * 100

else:

    avg_profit_margin_display = avg_profit_margin


business2.metric(
    "Average Profit Margin",
    f"{avg_profit_margin_display:.2f}%"
)


# ============================================================
# TOTAL ORDERS
# ============================================================

total_orders = (

    recommendations[
        "Orders"
    ]

    .sum()

)


business3.metric(
    "Total Orders Analyzed",
    f"{int(total_orders):,}"
)


# ============================================================
# TOTAL UNITS
# ============================================================

total_units = (

    recommendations[
        "Units"
    ]

    .sum()

)


business4.metric(
    "Total Units Analyzed",
    f"{int(total_units):,}"
)


# ============================================================
# SECTION 6
# ABOUT PROJECT
# ============================================================

st.header("6. ℹ️ About This Project")


with st.expander(
    "View Project Methodology"
):

    st.write(
        """
        ### Project Objective

        This dashboard evaluates factory reallocation scenarios
        for Nassau Candy Distributor.

        The objective is to identify factory assignments that may
        reduce shipping lead time while considering profitability
        and scenario confidence.

        ### Methodology

        1. Historical order data was cleaned and analyzed.
        2. Product, region and shipping-mode performance was evaluated.
        3. Factory scenarios were simulated.
        4. Predicted lead times were calculated.
        5. Lead-time reduction was measured.
        6. Optimization scores were calculated.
        7. Confidence levels were assigned.
        8. Recommendations were presented through this dashboard.

        ### Important

        The factory recommendations are analytical simulations
        rather than observed real-world shipments from multiple
        factories for the same product.

        Therefore, recommendations should be validated operationally
        before implementation.
        """
    )


# ============================================================
# DATASET INFORMATION
# ============================================================

st.subheader("Dataset Information")


dataset1, dataset2, dataset3 = st.columns(3)


dataset1.metric(
    "Historical Records",
    f"{len(historical):,}"
)


dataset2.metric(
    "Factory Recommendations",
    f"{len(recommendations):,}"
)


dataset3.metric(
    "Scenario Records",
    f"{len(scenarios):,}"
)


# ============================================================
# DATA PREVIEW
# ============================================================

with st.expander(
    "View Historical Dataset"
):

    st.dataframe(
        historical.head(100),
        use_container_width=True
    )


with st.expander(
    "View Factory Recommendations"
):

    st.dataframe(
        recommendations,
        use_container_width=True
    )


with st.expander(
    "View Scenario Results"
):

    st.dataframe(
        scenarios,
        use_container_width=True
    )


# ============================================================
# DISCLAIMER
# ============================================================

st.divider()


st.caption(
    """
    Disclaimer: Factory recommendations are analytical simulations
    based on historical product-region-shipping performance and
    assumed factory scenario factors.

    The source dataset does not contain observed shipments of the
    same product from multiple factories.

    Therefore, scenario results should be validated operationally
    before implementation.
    """
)