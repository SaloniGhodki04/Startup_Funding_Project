import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px

# LOAD DATASET
df = pd.read_csv('startup_funding.csv')

# DROP COLUMNS
df.drop(columns=['SNo', 'Remarks'], inplace=True)

# RENAME COLUMNS
df.rename(columns={
    'Date': 'date',
    'StartupName': 'startup',
    'IndustryVertical': 'vertical',
    'SubVertical': 'subvertical',
    'CityLocation': 'city',
    'InvestorsName': 'investor',
    'InvestmentType': 'round',
    'AmountInUSD': 'amount'
}, inplace=True)

# DATE CLEANING
df['date'] = pd.to_datetime(
    df['date'],
    errors='coerce'
)

df['year'] = df['date'].dt.year
df['month'] = df['date'].dt.month

# AMOUNT CLEANING
df['amount'] = (
    df['amount']
    .astype(str)
    .str.replace(',', '', regex=False)
    .str.replace('$', '', regex=False)
)

df['amount'] = pd.to_numeric(
    df['amount'],
    errors='coerce'
)

# INVESTOR CLEANING
df['investor'] = (
    df['investor']
    .astype(str)
    .str.lower()
    .str.replace(r'\(.*?\)', '', regex=True)
    .str.replace(r'[^a-z0-9\s]', '', regex=True)
    .str.replace(r'\s+', ' ', regex=True)
    .str.strip()
)

# STARTUP CLEANING
df['startup'] = (
    df['startup']
    .astype(str)
    .str.lower()
    .str.replace(r'xe2x80x99', '', regex=True)
    .str.replace(r'[^a-z0-9\s]', '', regex=True)
    .str.replace(r'\s+', ' ', regex=True)
    .str.strip()
)

# UNIQUE LISTS
startup_list = sorted(
    df['startup'].dropna().unique().tolist()
)

investor_list = sorted(
    df['investor'].dropna().unique().tolist()
)

# SIDEBAR
st.sidebar.title('Indian Startup Funding Analysis')

option = st.sidebar.selectbox(
    'Select One',
    ['Overall Analysis', 'Startup', 'Investor']
)

# OVERALL ANALYSIS
if option == 'Overall Analysis':

    st.title('Overall Startup Funding Analysis')

    # CARDS
    total = round(df['amount'].sum())

    max_funding = round(
        df.groupby('startup')['amount']
        .sum()
        .sort_values(ascending=False)
        .values[0]
    )

    avg_funding = round(
        df.groupby('startup')['amount']
        .sum()
        .mean()
    )

    total_startup = df['startup'].nunique()

    col1, col2, col3, col4 = st.columns(4)

    col1.metric('Total Funding', f"${total:,}")
    col2.metric('Max Funding', f"${max_funding:,}")
    col3.metric('Average Funding', f"${avg_funding:,}")
    col4.metric('Total Startups', total_startup)

    # MOM CHART
    st.subheader('Month on Month Funding Count')

    temp = (
        df.groupby(['year', 'month'])['startup']
        .count()
        .reset_index()
    )

    temp['x'] = (
        temp['month'].astype(str)
        + "-"
        + temp['year'].astype(str)
    )

    fig = px.line(
        temp,
        x='x',
        y='startup'
    )

    st.plotly_chart(fig, use_container_width=True)

    # TOP SECTORS
    st.subheader('Top Sectors')

    sector = (
        df.groupby('vertical')['amount']
        .sum()
        .sort_values(ascending=False)
        .head(10)
    )

    fig = px.pie(
        values=sector.values,
        names=sector.index
    )

    st.plotly_chart(fig, use_container_width=True)

    # FUNDING TYPE
    st.subheader('Funding Type')

    funding_type = df['round'].value_counts()

    fig = px.bar(
        x=funding_type.index,
        y=funding_type.values
    )

    st.plotly_chart(fig, use_container_width=True)

    # CITY WISE FUNDING
    st.subheader('City Wise Funding')

    city = (
        df.groupby('city')['amount']
        .sum()
        .sort_values(ascending=False)
        .head(10)
    )

    fig = px.bar(
        x=city.index,
        y=city.values
    )

    st.plotly_chart(fig, use_container_width=True)

    # TOP STARTUPS
    st.subheader('Top Startups')

    top_startups = (
        df.groupby('startup')['amount']
        .sum()
        .sort_values(ascending=False)
        .head(10)
    )

    st.dataframe(top_startups)

    # TOP INVESTORS
    st.subheader('Top Investors')

    top_investors = (
        df['investor']
        .value_counts()
        .head(10)
    )

    st.dataframe(top_investors)

    # HEATMAP
    st.subheader('Funding Heatmap')

    heatmap = df.pivot_table(
        index='city',
        columns='year',
        values='amount',
        aggfunc='sum'
    )

    st.dataframe(heatmap)

# STARTUP ANALYSIS
elif option == 'Startup':

    selected_startup = st.sidebar.selectbox(
        'Select Startup',
        startup_list
    )

    st.title(selected_startup.upper())

    st.button('Show Startup Analysis')

    startup_df = df[
        df['startup'] == selected_startup
    ]

    # BASIC DETAILS
    st.subheader('Basic Details')

    st.write(
        'Industry :',
        startup_df['vertical'].iloc[0]
    )

    st.write(
        'SubIndustry :',
        startup_df['subvertical'].iloc[0]
    )

    st.write(
        'Location :',
        startup_df['city'].iloc[0]
    )

    # FUNDING ROUNDS
    st.subheader('Funding Rounds')

    st.dataframe(
        startup_df[
            ['date', 'round', 'investor', 'amount']
        ]
    )

    # TOTAL FUNDING
    st.subheader('Total Funding')

    st.metric(
        'Funding Raised',
        f"${round(startup_df['amount'].sum()):,}"
    )

    # SIMILAR STARTUPS
    st.subheader('Similar Startups')

    similar = df[
        df['vertical']
        == startup_df['vertical'].iloc[0]
    ]['startup'].unique()

    st.write(similar)

# INVESTOR ANALYSIS
elif option == 'Investor':

    selected_investor = st.sidebar.selectbox(
        'Select Investor',
        investor_list
    )

    st.title(selected_investor.upper())


    st.button('Show Investor Analysis')

    investor_df = df[
        df['investor'] == selected_investor
    ]

    # RECENT INVESTMENTS
    st.subheader('Recent Investments')

    recent = investor_df.sort_values(
        'date',
        ascending=False
    )[
        ['date', 'startup', 'vertical', 'city', 'amount']
    ]

    st.dataframe(recent)

    # BIGGEST INVESTMENTS
    st.subheader('Biggest Investments')

    biggest = investor_df.sort_values(
        'amount',
        ascending=False
    )[
        ['startup', 'amount']
    ].head(10)

    st.dataframe(biggest)

    # GENERALLY INVESTS IN
    st.subheader('Generally Invests In')

    st.write(
        investor_df['vertical'].mode()[0]
    )

    # SECTOR PIE
    st.subheader('Sector Distribution')

    sector = (
        investor_df['vertical']
        .value_counts()
        .head(10)
    )

    fig = px.pie(
        values=sector.values,
        names=sector.index
    )

    st.plotly_chart(fig, use_container_width=True)

    # STAGE PIE
    st.subheader('Funding Stage')

    stage = investor_df['round'].value_counts()

    fig = px.pie(
        values=stage.values,
        names=stage.index
    )

    st.plotly_chart(fig, use_container_width=True)

    # CITY PIE
    st.subheader('City Distribution')

    city = investor_df['city'].value_counts()

    fig = px.pie(
        values=city.values,
        names=city.index
    )

    st.plotly_chart(fig, use_container_width=True)

    # YOY GRAPH
    st.subheader('Year on Year Investments')

    yoy = (
        investor_df.groupby('year')['amount']
        .sum()
        .reset_index()
    )

    fig = px.line(
        yoy,
        x='year',
        y='amount'
    )

    st.plotly_chart(fig, use_container_width=True)

    # SIMILAR INVESTORS
    st.subheader('Similar Investors')

    similar = df[
        df['vertical'].isin(
            investor_df['vertical'].unique()
        )
    ]['investor'].value_counts().head(10)

    st.write(similar)