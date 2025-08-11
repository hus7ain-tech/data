import streamlit as st
import pandas as pd
import plotly.express as px
import os
from datetime import datetime
import calendar

# --- Page Configuration ---
# Set the layout to wide for a more spacious dashboard
st.set_page_config(layout="wide")

# --- Data Loading and Caching ---
@st.cache_data
def load_and_prepare_data(base_path):
    """
    Loads vehicle registration data from a directory structure (year/month.csv),
    processes it, and returns a clean DataFrame.

    Args:
        base_path (str): The path to the root directory containing year folders.

    Returns:
        pandas.DataFrame: A cleaned and prepared DataFrame with all data.
    """
    all_data = []
    
    # --- REAL DATA LOADING ---
    st.info(f"Searching for data in subdirectories of: {os.path.abspath(base_path)}")
    
    found_files_log = []
    try:
        for root, _, files in os.walk(base_path):
            for file in files:
                if file.endswith('.csv') and '-' in file:
                    found_files_log.append(os.path.join(root, file))
                    try:
                        year_str, month_str = file.replace('.csv', '').split('-')
                        if os.path.basename(root) == year_str:
                            month = datetime.strptime(month_str.upper(), "%b").month
                            file_path = os.path.join(root, file)
                            df = pd.read_csv(file_path)
                            df['year'] = int(year_str)
                            df['month'] = month
                            all_data.append(df)
                    except ValueError:
                        st.warning(f"Skipping file with unexpected name format: {file}")
                    except Exception as e:
                        st.error(f"Error processing file {file}: {e}")
    except Exception as e:
        st.error(f"Could not read data directories. Error: {e}")
        return pd.DataFrame()

    with st.expander("See files found during data loading"):
        if found_files_log:
            st.write(found_files_log)
        else:
            st.write("No CSV files found. Check your folder structure.")

    if not all_data:
        st.warning("No data files were loaded. Please ensure your '2023', '2024', and '2025' folders with correctly named CSV files exist in the same directory as your script.")
        return pd.DataFrame()

    combined_df = pd.concat(all_data, ignore_index=True)

    melted_df = combined_df.melt(
        id_vars=['Maker', 'year', 'month'],
        value_vars=['2W', '3W', '4W'],
        var_name='Vehicle Category',
        value_name='Registrations'
    )

    melted_df = melted_df[melted_df['Registrations'] > 0]
    melted_df['Date'] = pd.to_datetime(melted_df[['year', 'month']].assign(day=1))
    melted_df['Quarter'] = melted_df['Date'].dt.to_period('Q')

    return melted_df

# --- Main Application ---
st.title("🚗 Vehicle Registration Analysis Dashboard")
st.markdown("An investor-focused view of vehicle registration trends, including YoY and QoQ growth.")

data = load_and_prepare_data('.')

if data.empty:
    st.warning("Dashboard cannot be displayed because no data was loaded.")
else:
    # --- Sidebar Filters ---
    st.sidebar.header("Dashboard Filters")

    month_list = ["All Months"] + list(calendar.month_name)[1:]
    selected_month_name = st.sidebar.selectbox("Select Month", month_list)

    selected_month_number = 0
    if selected_month_name != "All Months":
        selected_month_number = month_list.index(selected_month_name)

    all_years = sorted(data['year'].unique(), reverse=True)
    if selected_month_name != "All Months":
        selected_year = st.sidebar.selectbox("Select Year", all_years)
        selected_years = (selected_year, selected_year)
    else:
        min_year, max_year = int(data['year'].min()), int(data['year'].max())
        if min_year == max_year:
            st.sidebar.write(f"Data available for year: **{min_year}**")
            selected_years = (min_year, max_year)
        else:
            selected_years = st.sidebar.slider(
                "Select Year Range",
                min_value=min_year,
                max_value=max_year,
                value=(min_year, max_year)
            )

    vehicle_categories = sorted(data['Vehicle Category'].unique())
    selected_categories = st.sidebar.multiselect(
        "Select Vehicle Category",
        options=vehicle_categories,
        default=vehicle_categories
    )

    manufacturers = sorted(data['Maker'].unique())
    # --- UPDATE: Set default manufacturers to the top 10 ---
    top_manufacturers = data.groupby('Maker')['Registrations'].sum().nlargest(10).index.tolist()
    
    selected_manufacturers = st.sidebar.multiselect(
        "Select Manufacturer",
        options=manufacturers,
        default=top_manufacturers
    )

    # --- Filter Data based on selections ---
    filtered_data = data[
        (data['year'] >= selected_years[0]) &
        (data['year'] <= selected_years[1]) &
        (data['Vehicle Category'].isin(selected_categories)) &
        (data['Maker'].isin(selected_manufacturers))
    ]
    if selected_month_number > 0:
        filtered_data = filtered_data[filtered_data['month'] == selected_month_number]


    if filtered_data.empty:
        st.warning("No data available for the selected filters.")
    else:
        # --- Metrics Calculation ---
        if selected_month_name != "All Months":
            st.subheader(f"Key Metrics for {selected_month_name} {selected_years[0]}")
            
            current_month_data = filtered_data
            current_registrations = current_month_data['Registrations'].sum()

            prev_month_date = pd.to_datetime(f"{selected_years[0]}-{selected_month_number}-01") - pd.DateOffset(months=1)
            prev_month_data = data[
                (data['year'] == prev_month_date.year) & 
                (data['month'] == prev_month_date.month) &
                (data['Vehicle Category'].isin(selected_categories)) &
                (data['Maker'].isin(selected_manufacturers))
            ]
            prev_month_registrations = prev_month_data['Registrations'].sum()

            prev_year_data = data[
                (data['year'] == selected_years[0] - 1) & 
                (data['month'] == selected_month_number) &
                (data['Vehicle Category'].isin(selected_categories)) &
                (data['Maker'].isin(selected_manufacturers))
            ]
            prev_year_registrations = prev_year_data['Registrations'].sum()

            mom_growth = ((current_registrations - prev_month_registrations) / prev_month_registrations) * 100 if prev_month_registrations else 0
            yoy_growth = ((current_registrations - prev_year_registrations) / prev_year_registrations) * 100 if prev_year_registrations else 0

            col1, col2, col3 = st.columns(3)
            col1.metric("Total Registrations", f"{current_registrations:,.0f}")
            col2.metric("MoM Growth", f"{mom_growth:.2f}%", delta=f"{mom_growth:.2f}%")
            col3.metric("YoY Growth", f"{yoy_growth:.2f}%", delta=f"{yoy_growth:.2f}%")

        else:
            latest_quarter_period = filtered_data['Quarter'].max()
            st.subheader(f"Key Metrics for {str(latest_quarter_period)}")

            latest_quarter_df = filtered_data[filtered_data['Quarter'] == latest_quarter_period]
            current_registrations = latest_quarter_df['Registrations'].sum()

            prev_quarter_period = latest_quarter_period - 1
            prev_quarter_df = filtered_data[filtered_data['Quarter'] == prev_quarter_period]
            prev_quarter_registrations = prev_quarter_df['Registrations'].sum()

            prev_year_quarter_period = latest_quarter_period - 4
            prev_year_quarter_df = filtered_data[filtered_data['Quarter'] == prev_year_quarter_period]
            prev_year_quarter_registrations = prev_year_quarter_df['Registrations'].sum()

            qoq_growth = ((current_registrations - prev_quarter_registrations) / prev_quarter_registrations) * 100 if prev_quarter_registrations else 0
            yoy_growth = ((current_registrations - prev_year_quarter_registrations) / prev_year_quarter_registrations) * 100 if prev_year_quarter_registrations else 0

            col1, col2, col3 = st.columns(3)
            col1.metric("Total Registrations", f"{current_registrations:,.0f}")
            col2.metric("QoQ Growth", f"{qoq_growth:.2f}%", delta=f"{qoq_growth:.2f}%")
            col3.metric("YoY Growth", f"{yoy_growth:.2f}%", delta=f"{yoy_growth:.2f}%")

        st.markdown("---")

        # --- Visualizations ---
        st.subheader("Monthly Registration Trends")
        monthly_trends = filtered_data.groupby('Date')['Registrations'].sum().reset_index()
        fig_trends = px.bar(
            monthly_trends,
            x='Date',
            y='Registrations',
            title='Total Vehicle Registrations Over Time',
            labels={'Registrations': 'Number of Registrations'}
        )
        fig_trends.update_layout(title_x=0.5)
        st.plotly_chart(fig_trends, use_container_width=True)

        st.subheader("Manufacturer Performance")
        col1, col2 = st.columns(2)

        with col1:
            st.markdown("#### Market Share (by Registrations)")
            manufacturer_share = filtered_data.groupby('Maker')['Registrations'].sum().reset_index()
            fig_share = px.pie(
                manufacturer_share.nlargest(10, 'Registrations'),
                names='Maker',
                values='Registrations',
                title=f'Top 10 Manufacturers by Registrations'
            )
            fig_share.update_layout(title_x=0.5)
            st.plotly_chart(fig_share, use_container_width=True)

        with col2:
            st.markdown("#### Category-wise Registrations")
            category_share = filtered_data.groupby('Vehicle Category')['Registrations'].sum().reset_index()
            fig_cat_share = px.bar(
                category_share,
                x='Vehicle Category',
                y='Registrations',
                title=f'Registrations by Vehicle Category',
                color='Vehicle Category'
            )
            fig_cat_share.update_layout(title_x=0.5)
            st.plotly_chart(fig_cat_share, use_container_width=True)
