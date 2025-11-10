import streamlit as st
import pandas as pd
import plotly.express as px

# --- 1. SET UP PAGE ---
st.set_page_config(layout="wide")
st.title("Supply Chain & Logistics KPI Dashboard")

# --- 2. LOAD DATA ---
@st.cache_data
def load_data():
    df = pd.read_csv("analytics_data.csv")
    df['actual_delivery_date'] = pd.to_datetime(df['actual_delivery_date'])
    return df

df = load_data()

# --- 3. CREATE SIDEBAR FILTERS ---
st.sidebar.header("Dashboard Filters")

# Filter by Carrier
carrier_list = ['All'] + list(df['carrier_name'].unique())
selected_carrier = st.sidebar.selectbox("Select Carrier:", carrier_list)

# Filter by Route
route_list = ['All'] + list(df['route'].unique())
selected_route = st.sidebar.selectbox("Select Route:", route_list)

# --- 4. FILTER DATAFRAME ---
df_filtered = df.copy()

if selected_carrier != 'All':
    df_filtered = df_filtered[df_filtered['carrier_name'] == selected_carrier]

if selected_route != 'All':
    df_filtered = df_filtered[df_filtered['route'] == selected_route]

# --- 5. CREATE KPI CARDS ---
st.header("Overall Performance")

# Calculate KPIs
on_time_rate = df_filtered['on_time'].mean() * 100
avg_delivery_time = df_filtered['delivery_time_days'].mean()
avg_shipping_cost = df_filtered['shipping_cost'].mean()

# Display KPIs in columns
col1, col2, col3 = st.columns(3)
col1.metric("On-Time Delivery Rate", f"{on_time_rate:.2f}%")
col2.metric("Avg. Delivery Time", f"{avg_delivery_time:.1f} days")
col3.metric("Avg. Shipping Cost", f"${avg_shipping_cost:.2f}")

# --- 6. CREATE VISUALS ---
st.header("Performance Analysis")

col1, col2 = st.columns(2)

with col1:
    # Visual 1: Carrier On-Time Performance
    st.subheader("On-Time Rate by Carrier")
    if selected_carrier == 'All':
        carrier_performance = df_filtered.groupby('carrier_name')['on_time'].mean().reset_index()
        carrier_performance = carrier_performance.sort_values(by='on_time', ascending=False)
        fig_carrier = px.bar(
            carrier_performance,
            x='carrier_name',
            y='on_time',
            title="Carrier On-Time Delivery Rate (%)",
            labels={'on_time': 'On-Time Rate', 'carrier_name': 'Carrier'}
        )
        fig_carrier.update_yaxes(tickformat=".0%")
        st.plotly_chart(fig_carrier, use_container_width=True)
    else:
        st.write(f"Showing data for {selected_carrier} only.")

with col2:
    # Visual 2: Top 10 Most Expensive Routes
    st.subheader("Top 10 Most Expensive Routes")
    if selected_route == 'All':
        route_cost = df_filtered.groupby('route')['shipping_cost'].mean().reset_index()
        route_cost = route_cost.sort_values(by='shipping_cost', ascending=False).head(10)
        fig_route = px.bar(
            route_cost,
            x='route',
            y='shipping_cost',
            title="Top 10 Avg. Shipping Cost by Route",
            labels={'shipping_cost': 'Avg. Shipping Cost', 'route': 'Route'}
        )
        st.plotly_chart(fig_route, use_container_width=True)
    else:
        st.write(f"Showing data for {selected_route} only.")

# Visual 3: Delivery Time Distribution
st.subheader("Delivery Time (Lateness) Distribution")
fig_hist = px.histogram(
    df_filtered,
    x='delivery_time_days',
    title="Distribution of Delivery Times (0 = On-Time)",
    labels={'delivery_time_days': 'Days (Negative = Early, Positive = Late)'}
)
fig_hist.add_vline(x=0, line_dash="dash", line_color="red", annotation_text="On-Time")
st.plotly_chart(fig_hist, use_container_width=True)

# --- 7. SHOW RAW DATA ---
st.header("Filtered Data Explorer")
st.dataframe(df_filtered)
