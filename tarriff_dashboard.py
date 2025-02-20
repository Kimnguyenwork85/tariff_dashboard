import streamlit as st
import pandas as pd
import plotly.express as px

st.set_page_config(page_title='Steel Tariff Dashboard', layout='wide')

# Custom CSS for styling
st.markdown("""
    <style>
    .main {
        background-color: #333333;  /* Light black background */
        color: white;  /* White text */
    }
    .stButton>button {
        color: white;
        background-color: #4CAF50;
    }
    .stSidebar {
        background-color: #333333;  /* Light black background */
        color: white;  /* White text */
    }
    .stExpander {
        background-color: #f0f2f6;  /* Light grey to match DataFrame columns */
    }
    .css-1d391kg p, .css-1d391kg h1, .css-1d391kg h2, .css-1d391kg h3, .css-1d391kg h4, .css-1d391kg h5, .css-1d391kg h6 {
        color: white;  /* White text for headers and paragraphs */
    }
    .css-1d391kg h1 {
        border: 2px solid white;  /* Border around title */
        padding: 10px;
    }
    .css-1d391kg h2 {
        border: 2px solid white;  /* Border around subheader */
        padding: 10px;
    }
    </style>
    """, unsafe_allow_html=True)

# Load data directly from the local file
csv_file_path = '/Users/kimnguyen/Documents/steel_dashboard/dashboard_source_data.csv'
data = pd.read_csv(csv_file_path)

# Streamlit app title
st.title("Tariff Performance Dashboard")
# Metrics
col1, col2, col3, col4 = st.columns(4)
col1.metric(label="Average 1-Day Return (%)", value=f"{data['1-Day Return (%)'].mean():.2f}%")
col2.metric(label="Average 7-Day Return (%)", value=f"{data['7-Day Return (%)'].mean():.2f}%")
col3.metric(label="Average 30-Day Return (%)", value=f"{data['30-Day Return (%)'].mean():.2f}%")
col4.metric(label="Average 6-Month Return (%)", value=f"{data['6-Month Return (%)'].mean():.2f}%")
# Top company by return
col6, col7, col8, col9 = st.columns(4)
top_company_1d = data.loc[data['1-Day Return (%)'].idxmax()]
top_company_7d = data.loc[data['7-Day Return (%)'].idxmax()]
top_company_30d = data.loc[data['30-Day Return (%)'].idxmax()]
top_company_6m = data.loc[data['6-Month Return (%)'].idxmax()]
col6.metric(label="Top Company by 1-Day Return", value=top_company_1d['Company'], delta=f"{top_company_1d['1-Day Return (%)']:.2f}%")
col7.metric(label="Top Company by 7-Day Return", value=top_company_7d['Company'], delta=f"{top_company_7d['7-Day Return (%)']:.2f}%")
col8.metric(label="Top Company by 30-Day Return", value=top_company_30d['Company'], delta=f"{top_company_30d['30-Day Return (%)']:.2f}%")
col9.metric(label="Top Company by 6-Month Return", value=top_company_6m['Company'], delta=f"{top_company_6m['6-Month Return (%)']:.2f}%")


# Lowest company by return (losers)
col10, col11, col12, col13 = st.columns(4)
low_company_1d = data.loc[data['1-Day Return (%)'].idxmin()]
low_company_7d = data.loc[data['7-Day Return (%)'].idxmin()]
low_company_30d = data.loc[data['30-Day Return (%)'].idxmin()]
low_company_6m = data.loc[data['6-Month Return (%)'].idxmin()]
col10.metric(label="Lowest Company by 1-Day Return", value=low_company_1d['Company'], delta=f"{low_company_1d['1-Day Return (%)']:.2f}%")
col11.metric(label="Lowest Company by 7-Day Return", value=low_company_7d['Company'], delta=f"{low_company_7d['7-Day Return (%)']:.2f}%")
col12.metric(label="Lowest Company by 30-Day Return", value=low_company_30d['Company'], delta=f"{low_company_30d['30-Day Return (%)']:.2f}%")
col13.metric(label="Lowest Company by 6-Month Return", value=low_company_6m['Company'], delta=f"{low_company_6m['6-Month Return (%)']:.2f}%")


# Show the full dataset
st.subheader("Companies Data")
st.write(data)

# Dropdown for selecting return period
return_period = st.selectbox(
    'Select Return Period',
    ['1-Day Return (%)', '7-Day Return (%)', '30-Day Return (%)', '6-Month Return (%)']
)

# 1. Stock Heatmap
with st.expander(f"Stock Heatmap {return_period}"):
    fig = px.treemap(data, path=['Industry', 'Company'], values='Market Cap',
                     color=return_period, hover_data={return_period: ':.2f%'},
                     color_continuous_scale=['#d73027', '#fee08b', '#1a9850'], color_continuous_midpoint=0,
                     custom_data=[return_period])
    fig.update_traces(texttemplate='%{label}<br>%{customdata[0]:.2f%}', textposition='middle center')
    fig.update_layout(margin=dict(t=50, l=25, r=25, b=25))
    st.plotly_chart(fig)

# 2. Return Comparison (Bar plot)
with st.expander(f"{return_period} Comparison"):
    fig = px.bar(data, x='Company', y=return_period, title=f"{return_period} Comparison by Company",
                 labels={'Company': 'Company', return_period: return_period}, color=return_period,
                 color_continuous_scale='viridis')
    fig.update_layout(xaxis_title="Company", yaxis_title=return_period, title_x=0.5)
    fig.update_xaxes(tickangle=90)
    st.plotly_chart(fig)

# 3. Average Return by Industry (Bar plot)
with st.expander(f"Average {return_period} by Industry"):
    industry_avg_return = data.groupby('Industry')[return_period].mean().reset_index()
    fig = px.bar(industry_avg_return, x='Industry', y=return_period, title=f"Average {return_period} by Industry",
                 labels={'Industry': 'Industry', return_period: f"Average {return_period}"},
                 color=return_period, color_continuous_scale='Blues')
    fig.update_layout(xaxis_title="Industry", yaxis_title=f"Average {return_period}", title_x=0.5)
    fig.update_xaxes(tickangle=45)
    st.plotly_chart(fig)

# 4. Correlation Heatmap
with st.expander("Correlation Heatmap"):
    corr_matrix = data[['Current Price (USD)', '1-Day Return (%)', '7-Day Return (%)', '30-Day Return (%)', '6-Month Return (%)', 'P/E Ratio', 'Market Cap', 'Short Ratio', 'Forward P/E']].corr()
    fig = px.imshow(corr_matrix, text_auto=True, color_continuous_scale='RdYlGn', title="Correlation Heatmap")
    fig.update_layout(
        width=1000,  # Adjust the width as needed
        height=800,  # Adjust the height as needed
        margin=dict(t=50, l=25, r=25, b=25)
    )
    st.plotly_chart(fig)