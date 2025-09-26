# Import libraries
import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
from plotly.subplots import make_subplots

# Set page configuration
st.set_page_config(
    page_title='E-commerce Transaction Analytics Dashboard',
    page_icon='📈',
    layout = 'wide',
    initial_sidebar_state= 'expanded'
)

# Function to load dataset
@st.cache_data
def load_data() :
    df1 = pd.read_excel(r'C:\Users\dinda\Documents\Bootcamp\ecommerce_streamlit\dataset\processed_data_ecommerce.xlsx', sheet_name='processed_order')
    df2 = pd.read_excel(r'C:\Users\dinda\Documents\Bootcamp\ecommerce_streamlit\dataset\processed_data_ecommerce.xlsx', sheet_name='customer_segmentation')
    df3 = pd.read_csv(r'C:\Users\dinda\Documents\Bootcamp\ecommerce_streamlit\dataset\events.csv')
    return df1, df2, df3

# load dataset
df_order, df_customer, df_events = load_data()

# merge dataset
df_order = df_order.merge(df_customer, on = ['user_id', 'customer name', 'age_group',
                                             'gender', 'total_sales'], how='left')
# calculate average order value
df_order['aov'] = df_order['total_sales']/df_order['order_id']

# convert datatype from object to datetime
df_events['created_at'] = pd.to_datetime(df_events['created_at'], errors='coerce')

# make a new column "year"
df_events['year'] = df_events['created_at'].dt.year

# ----- SIDEBAR ------
# sidebar for filter
st.sidebar.header('⚙️ Dashboard Filter')

# Make a list of unique year
year_list = df_order['year'].unique().tolist() # take all unique years

# Sort year
year_list.sort(reverse=True)

# Add "All" as part of filter
year_list = ['All'] + year_list 

# Year filter
st.sidebar.subheader('📅 Year Filter')
selected_year = st.sidebar.selectbox('Select Year', options=year_list, index = 0 ) # set default to "All Year"

# Apply year filter
if selected_year == 'All' :
    df_filtered = df_order.copy()
    df_filtered_events = df_events.copy()
else :
    df_filtered = df_order[df_order['year'] == selected_year]
    df_filtered_events  = df_events[df_events['year'] == selected_year]


# Make a list of product department
department_list = df_order['department'].unique().tolist()

# Department filter
st.sidebar.subheader('👕 Product Department Filter')
selected_department = st.sidebar.multiselect('Select Product Department', 
                                             options=department_list, default=department_list)

# Apply segment filter
df_filtered = df_filtered[df_filtered['department'].isin(selected_department)]


# ----- MAIN PAGE ----
# Title
st.title('🛒 THELOOK DASHBOARD')
st.markdown("TheLook is a fictional e-commerce clothing site that sold diverse products of clothing and accessories for both men and women. This project aims to gain comprehensive insights into TheLook's sales performance, customer behaviour, and product analysis over the period of 2019 - 2024. Insights from in-depth analysis will deliver data-driven recommendations to boost its revenue")

# Border line
st.markdown('---')

# Create tabs 
tab_sales, tab_products, tab_customer = st.tabs(['Sales Analysis', 'Product Analysis', 'Customer Analysis'])

# ---Page 1 : Sales Analysis ---
with tab_sales :
    st.header('Sales Performance Analysis')
    # KPI metrics
    st.subheader('Key Performance Indicators')

    # create columns
    col1, col2, col3 = st.columns(3)

    # Calculate metrics
    total_profit = df_filtered['total_profit'].sum()
    total_sales = df_filtered['total_sales'].sum()
    average_aov = df_filtered['total_sales'].sum() / df_filtered['order_id'].nunique()



    # make metrics
    with col1 :
        st.metric(label = 'Total Sales', value = f'${total_sales/1000000:.2f}M')
    with col2 :
        st.metric(label='Total Profit', value = f'${total_profit/1000:.2f}K')
    with col3 :
        st.metric(label='Average Order Value', value = f'{average_aov} $/order')


    st.markdown('---')

    # monthly sales
    st.subheader('Monthly Trend')
    # data aggregation
    df_monthly = df_filtered.groupby('month_name').agg(
        total_sales= ('total_sales', 'sum'),
        total_profit=('total_profit', 'sum'),
        month_num=('month', 'unique') #include month_num for sorting
    ).reset_index()

    df_monthly = df_monthly.sort_values('month_num')

    # code below is referenced from geeks for geeks
    # create subplots
    fig = make_subplots(specs=[[{"secondary_y": True}]])

    # main y-axis
    fig.add_trace(
        go.Scatter(x=df_monthly['month_name'], y=df_monthly['total_sales'], name='Sales'), secondary_y=False)
    
    # secondary y-axis
    fig.add_trace(
        go.Scatter(x=df_monthly['month_name'], y=df_monthly['total_profit'], name='Profit'), secondary_y=True)
    
    # add title
    fig.update_layout(title_text = 'Sales and Profit by Month')

    # add x-axis name
    fig.update_xaxes(title_text='Month')

    # add y-axes names
    fig.update_yaxes(title_text='Sales ($)', secondary_y=False)
    fig.update_yaxes(title_text='Profit ($)', secondary_y=True)

    st.plotly_chart(fig, use_container_width=True)

    st.markdown("---")

    # ----geographic analysis-----
    # create two columns
    st.subheader('Sales by Geography')
    col5, col6 = st.columns(2)
    
    with col5 :
        # sales by country
        # data aggregation by country
        df_country = df_filtered.groupby('country').agg({
            'total_sales' : 'sum',
            'total_profit' : 'sum',
            'num_of_item' : 'sum',
            'user_id' : 'nunique',
            'order_id' : 'nunique'}).reset_index()

        df_country['aov'] = df_country['total_sales'] / df_country['order_id']
        df_country['profit_per_customer'] = df_country['total_profit'] / df_country['user_id']

        fig_country = px.scatter(df_country, x='total_sales', y='aov', 
                                 size ='profit_per_customer', color='country')
        st.plotly_chart(fig_country, use_container_width=True)

    with col6 :
    # standardize country name
        country_map = {
            'Brasil' : 'Brazil',
            'Deutschland' : 'Germany',
            'España' : 'Spain'
        }

        # replace some country names
        df_country['country'] = df_country['country'].replace(country_map) 

        top_10_countries = df_country.sort_values('total_sales', ascending=False).head(10)
        bar_country = px.bar(top_10_countries, x='total_sales', y='country', orientation='h', title='Top 10 Countries by Sales')
        bar_country.update_xaxes(title_text='Total Sales ($)')
        bar_country.update_yaxes(title_text='Country')
        st.plotly_chart(bar_country, use_container_width=True)

    st.markdown("---")

    # --- conversion analysis --

    
    st.subheader('Conversion Analysis')
    
    # create columns
    col_marketing, col_conversion = st.columns(2)
    
    with col_marketing :
        # value counts
        df_marketing = df_filtered_events['traffic_source'].value_counts().reset_index()
        df_marketing.columns = ['traffic_source', 'Count']
        
        # visualization
        pie_marketing = px.pie(df_marketing, values ='Count', names='traffic_source')
        st.plotly_chart(pie_marketing, use_container_width=True)
    
    with col_conversion :
        # group by session_id and event_type
        # look for session_id with purchase
        session = df_filtered_events.groupby('session_id')['event_type'].apply(lambda x: (x == 'purchase').any()).reset_index()

        # add column "Converted" to indicate which session has converted to purchase
        session['Converted'] = session['event_type'].astype(int)

        # take only columns 'session_id' and 'traffic_source' from df_events
        df_session = df_filtered_events[['session_id', 'traffic_source']]

        # merge session and df_session
        df_session = df_session.merge(session[['session_id', 'Converted']], on ='session_id', how='left')

        # keep the first row of duplicates
        df_session.drop_duplicates(keep='first', inplace=True)

        # make a pivot table for conversion rate
        pivot_conversion = pd.pivot_table(df_session,
                                          index = 'traffic_source',
                                          columns = 'Converted',
                                          values = 'session_id',
                                          aggfunc = 'nunique').reset_index().replace({'session_id' : 'SessionCount'})

        # calculate conversion rate
        pivot_conversion['conversion_rate'] = round(pivot_conversion[1] / (pivot_conversion[0] + pivot_conversion[1]) * 100, 2)


        bar_conversion = px.bar(pivot_conversion, x='traffic_source', y = 'conversion_rate', orientation='v', title='Conversion Rate by Marketing Channel')
        bar_conversion.update_xaxes(title_text='Marketing Channel')
        bar_conversion.update_yaxes(title_text = 'Conversion Rates')
        st.plotly_chart(bar_conversion, use_container_width=True)

# --------PAGE 2 : PRODUCT ANALYSIS ---------
with tab_products :
    st.header('Product Analysis')

    # create columns
    col_quantity, col_order = st.columns(2)

    # Calculate metrics
    total_order = df_filtered['order_id'].nunique()
    total_quantity = df_filtered['num_of_item'].sum()

    # make metrics
    with col_quantity :
        st.metric(label = 'Total Quantity Sold', value =  f'${total_quantity/1000:.2f}K')
    with col_order :
        st.metric(label='Total Transactions', value = total_order)
    
    st.markdown("---")

     # monthly sales
    st.subheader('Monthly Trend')
    # data aggregation
    df_monthly_products = df_filtered.groupby('month_name').agg(
        total_orders= ('order_id', 'nunique'),
        total_quantity=('num_of_item', 'sum'),
        month_num=('month', 'unique') #include month_num for sorting
    ).reset_index()

    df_monthly_products = df_monthly_products.sort_values('month_num')

    # code below is referenced from geeks for geeks
    # create subplots
    fig_products = make_subplots(specs=[[{"secondary_y": True}]])

    # main y-axis
    fig_products.add_trace(
        go.Scatter(x=df_monthly_products['month_name'], y=df_monthly_products['total_orders'], name='Orders'), secondary_y=False)
    
    # secondary y-axis
    fig_products.add_trace(
        go.Scatter(x=df_monthly_products['month_name'], y=df_monthly_products['total_quantity'], name='Quantity'), secondary_y=True)
    
    # add title
    fig_products.update_layout(title_text = 'Total Quantity and Total Orders by Month')

    # add x-axis name
    fig_products.update_xaxes(title_text='Month')

    # add y-axes names
    fig_products.update_yaxes(title_text='Total Orders', secondary_y=False)
    fig_products.update_yaxes(title_text='Quantity Sold (Units)', secondary_y=True)

    st.plotly_chart(fig_products, use_container_width=True)

    st.markdown("---")


    # value counts
    st.subheader('Total Orders by Category')
    df_category = df_filtered['category'].value_counts().reset_index()
    df_category.columns = ['category', 'Count']
        
    # visualization
    pie_category = px.pie(df_category, values ='Count', names='category')
    st.plotly_chart(pie_category, use_container_width=True)
    
    st.markdown("---")

    st.subheader('Sales & Profit by Category')
    df_melt = df_filtered.melt(id_vars = 'category',
                                value_vars=['total_profit', 'total_sales'],
                                var_name='Metrics',
                                value_name = 'Value')
        
    # visualization
    fig_products_sp = px.bar(df_melt, y = 'category', x='Value',
                            color = 'Metrics', barmode='group', orientation='h',
                                title = 'Sales & Profit by Category')
    st.plotly_chart(fig_products_sp, use_container_width=True)
    
    st.markdown("---")

    st.subheader('Top 10 Most Sold Products')


    # Data aggregation
    df_products = df_filtered.groupby('name').agg(
        quantity_sold = ('num_of_item', 'sum'),
        total_sales = ('total_sales', 'sum'),
        total_profit = ('total_profit', 'sum'),
        category = ('category', 'first')
    ).reset_index()

    # round values
    df_products = df_products.round({'total_sales' :2, 'total_profit' :2})

    # Top 10 most sold products  
    top_10_sold = df_products.sort_values('quantity_sold', ascending=False).head(10)
    
        
    table_most_sold = go.Figure(data=[go.Table(
        header=dict(values=['Product', 'Total Quantity', 'Total Sales ($)', 'Total Profit ($)'],fill_color = 'lightskyblue'), 
        cells=dict(values=[top_10_sold['name'], top_10_sold['quantity_sold'],
                        top_10_sold['total_sales'], top_10_sold['total_profit']], 
                        fill_color = 'lightcyan'))])

    st.plotly_chart(table_most_sold, use_container_width=True)
    st.markdown('---')

    # Top 10 most profitable products
    st.subheader('Top 10 Most Profitable Products')
    top_10_profitable = df_products.sort_values('total_profit', ascending=False).head(10)
    table_most_profitable = go.Figure(data=[go.Table(
        header=dict(values=['Product', 'Total Profit ($)', 'Total Quantity', 'Total Sales ($)'],fill_color = 'lightskyblue'), 
        cells=dict(values=[top_10_profitable['name'], top_10_profitable['total_profit'],
                            top_10_profitable['quantity_sold'],top_10_profitable['total_sales']],
                              fill_color = 'lightcyan'))])

    st.plotly_chart(table_most_profitable, use_container_width=True)
    st.markdown('---')

# ----- PAGE 3 : CUSTOMER ANALYSIS -----
with tab_customer :
    st.header('Customer Analysis')
    
    st.subheader('Proportion of Customer Segmentation')
    
    # create columns
    col_rfm, col_onetime = st.columns(2)

    with col_rfm :
        pie_segment = px.pie(df_filtered,  names='segment', title='Customer Segmentation')
        st.plotly_chart(pie_segment, use_container_width=True)
    
    with col_onetime :
        df_onetime = df_filtered['is_one_time_buyer'].value_counts().reset_index()
        df_onetime.columns = ['is_one_time_buyer', 'count']

        # visualization
        pie_onetime = px.pie(df_onetime, names='is_one_time_buyer', values='count', title='One Time Buyer Distribution')
        st.plotly_chart(pie_onetime, use_container_width=True)
    
    st.markdown('---')

    # create columns 
    col_age, col_gender = st.columns(2)

    with col_age :
        df_age = df_filtered['age_group'].value_counts().reset_index()
        df_age.columns = ['age_group', 'count']

        # visualization
        pie_age = px.pie(df_age, names='age_group', values='count', title = 'Age Distribution')
        st.plotly_chart(pie_age, use_container_width=True)

    with col_gender :
        df_gender = df_filtered['gender'].value_counts().reset_index()
        df_gender.columns = ['gender', 'count']

        # visualization
        pie_gender = px.pie(df_gender, names='gender', values='count', title='Gender Distribution')
        st.plotly_chart(pie_gender, use_container_width=True)

    st.markdown('---')

    st.subheader('Average Sales & Profit by Customer Segment')
    col_sales, col_profit = st.columns(2)

    # data aggregation
    customer_segment = df_filtered.groupby('segment').agg({
        'total_sales' : 'mean',
        'total_profit' : 'mean',
        'order_id' : 'nunique'}).reset_index()
    
    with col_sales :
        bar_sales = px.bar(customer_segment, y='segment', x='total_sales', orientation='h', title = 'Average Sales')
        bar_sales.update_xaxes(title_text='Average Sales (&)')
        bar_sales.update_yaxes(title_text = 'Customer Segment')
        st.plotly_chart(bar_sales, use_container_width=True)

    with col_profit :
        bar_profit = px.bar(customer_segment, y='segment', x='total_profit', orientation='h', title = 'Average Profit')
        bar_profit.update_xaxes(title_text='Average Profit (&)')
        bar_profit.update_yaxes(title_text = 'Customer Segment')
        st.plotly_chart(bar_profit, use_container_width=True)         
    
    st.markdown('---')

    # data aggregation
    df_onetime_sales = df_filtered.groupby('is_one_time_buyer').agg({
        'total_sales' : 'mean',
        'total_profit' : 'mean',
        'order_id' : 'nunique'}).reset_index()

    st.subheader('Average Sales & Profit by One Time Buyer')

    # create columns
    col_onetime_sales, col_onetime_profit = st.columns(2)

    with col_onetime_sales :
        bar_onetime_sales = px.bar(df_onetime_sales, y='is_one_time_buyer', x='total_sales', orientation='h', title = 'Average Sales')
        bar_onetime_sales.update_xaxes(title_text='Average Sales (&)')
        bar_onetime_sales.update_yaxes(title_text = 'Customer Type')
        st.plotly_chart(bar_onetime_sales, use_container_width=True)

    with col_onetime_profit :
        bar_onetime_profit = px.bar(df_onetime_sales, y='is_one_time_buyer', x='total_profit', orientation='h', title = 'Average Profit')
        bar_onetime_profit.update_xaxes(title_text='Average Profit (&)')
        bar_onetime_profit.update_yaxes(title_text = 'Customer Type')
        st.plotly_chart(bar_onetime_profit, use_container_width=True)         









    
