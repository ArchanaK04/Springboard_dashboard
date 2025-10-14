import streamlit as st
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import altair as alt
import plotly.express as px
import plotly.graph_objects as go

from src.data_collection.news_api import fetch_newsapi
from src.data_collection.gnews_api import fetch_gnews
from src.analysis.sentiment import add_vader_sentiment
from src.analysis.aggregate import prepare_daily_sentiment_grouped, run_prophet_forecast

st.set_page_config(page_title="Strategic Intelligence Dashboard", layout="wide")

# --------------------- CSS ---------------------
st.markdown("""
<style>
.main-header {font-size:2.5rem; color:#1f77b4; text-align:center; font-weight:700;}
.section-header {font-size:1.5rem; color:#2c3e50; margin:1rem 0 0.5rem 0; font-weight:600;}
.alert-success {background-color:#d4edda; padding:1rem; border-radius:10px; margin:0.5rem 0; border-left:5px solid #28a745;}
.alert-danger {background-color:#f8d7da; padding:1rem; border-radius:10px; margin:0.5rem 0; border-left:5px solid #dc3545;}
</style>
""", unsafe_allow_html=True)

st.markdown('<h1 class="main-header">🎯 Strategic Intelligence Dashboard</h1>', unsafe_allow_html=True)

# --------------------- Sidebar ---------------------
st.sidebar.header("Filters & Configuration")
default_competitors = ["Google", "Microsoft", "Amazon", "Apple", "Zoho"]

competitors = st.sidebar.multiselect("Choose Competitors:", default_competitors, default=["Google", "Microsoft"])
custom_keywords = st.sidebar.text_input("Or enter custom keywords (comma separated):", "")
sources = st.sidebar.multiselect("Select News Sources", ["NewsAPI", "GNews"], default=["NewsAPI", "GNews"])
last_month = datetime.today() - timedelta(days=30)
date_range = st.sidebar.date_input("Date Range", [last_month, datetime.today()])
article_limit = st.sidebar.slider("Number of Articles Per Source", 10, 100, 50)
alert_threshold = st.sidebar.slider("Sentiment Alert Threshold", -1.0, 1.0, -0.5)

# --------------------- Top-page CSV upload ---------------------
st.subheader("📁 Upload Your CSV for Sentiment Analysis")
uploaded_file = st.file_uploader("Drag & drop a CSV file or click to upload", type=["csv"])

user_df = None
if uploaded_file:
    user_df = pd.read_csv(uploaded_file)
    if 'description' in user_df.columns:
        user_df = add_vader_sentiment(user_df, text_col="description")
    elif 'text' in user_df.columns:
        user_df = add_vader_sentiment(user_df, text_col="text")
    st.markdown("### Sample Uploaded Data")
    st.dataframe(user_df.head(20))

# --------------------- Fetch & Analyze ---------------------
keywords = [k.strip() for k in custom_keywords.split(",") if k.strip()]
all_terms = [(c, "Competitor") for c in competitors] + [(kw, "Keyword") for kw in keywords]

combined_df = None
if st.sidebar.button("Fetch & Analyze"):
    dfs = []
    for term, term_type in all_terms:
        temp_dfs = []
        for source in sources:
            if source == "NewsAPI":
                df_newsapi = fetch_newsapi(
                    term,
                    from_date=date_range[0].strftime("%Y-%m-%d"),
                    to_date=date_range[1].strftime("%Y-%m-%d"),
                    max_articles=article_limit
                )
                if not df_newsapi.empty:
                    df_newsapi['entity'] = term
                    df_newsapi['source'] = 'NewsAPI'
                    df_newsapi['term_type'] = term_type
                    temp_dfs.append(df_newsapi)
            if source == "GNews":
                df_gnews = fetch_gnews(
                    term,
                    from_date=date_range[0].strftime("%Y-%m-%d"),
                    to_date=date_range[1].strftime("%Y-%m-%d"),
                    max_articles=article_limit
                )
                if not df_gnews.empty:
                    df_gnews['entity'] = term
                    df_gnews['source'] = 'GNews'
                    df_gnews['term_type'] = term_type
                    temp_dfs.append(df_gnews)
        if temp_dfs:
            dfs.append(pd.concat(temp_dfs, ignore_index=True))

    if dfs:
        combined_df = pd.concat(dfs, ignore_index=True).drop_duplicates(subset=["title", "url"])
        # Use description if available
        text_col = "description" if "description" in combined_df.columns else "text"
        combined_df = add_vader_sentiment(combined_df, text_col=text_col)
        st.success("✅ Data fetched and analyzed!")
    else:
        st.warning("No data fetched. Check API keys, sources, or keywords.")

# --------------------- Tabs ---------------------
tab1, tab2 = st.tabs(["Overview & Alerts", "Visualization & Forecast"])

with tab1:
    st.subheader("📊 Overview KPIs & Alerts")
    df_to_use = combined_df if combined_df is not None else user_df

    if df_to_use is not None and not df_to_use.empty:
        # KPIs
        col1, col2, col3, col4 = st.columns(4)
        col1.metric("Total Articles", len(df_to_use))
        col2.metric("Positive Articles", len(df_to_use[df_to_use['vader_compound'] > 0.05]))
        col3.metric("Negative Articles", len(df_to_use[df_to_use['vader_compound'] < -0.05]))
        col4.metric("Avg Sentiment", round(df_to_use['vader_compound'].mean(), 2))

        # Alerts
        st.markdown('<h4 class="section-header">🚨 Alerts</h4>', unsafe_allow_html=True)
        negative_alerts = df_to_use[df_to_use['vader_compound'] <= alert_threshold]
        positive_alerts = df_to_use[df_to_use['vader_compound'] >= abs(alert_threshold)]
        if not negative_alerts.empty:
            for _, row in negative_alerts.iterrows():
                st.markdown(f'<div class="alert-danger">⚠️ Negative Alert: {row["entity"]} | {row["title"]}</div>', unsafe_allow_html=True)
        if not positive_alerts.empty:
            for _, row in positive_alerts.iterrows():
                st.markdown(f'<div class="alert-success">✅ Positive Alert: {row["entity"]} | {row["title"]}</div>', unsafe_allow_html=True)
        if negative_alerts.empty and positive_alerts.empty:
            st.info("No critical alerts at this time.")

        # Raw data preview
        st.markdown("### Sample Data")
        st.dataframe(df_to_use.head(20))
    else:
        st.info("No data available. Upload a file or fetch from API.")

with tab2:
    st.subheader("📈 Visualizations & Forecast")
    df_to_use = combined_df if combined_df is not None else user_df

    if df_to_use is not None and not df_to_use.empty:
        # Sentiment by entity stacked bar
        sentiment_by_entity = pd.crosstab(df_to_use['entity'], pd.cut(df_to_use['vader_compound'], bins=[-1,-0.05,0.05,1], labels=["Negative","Neutral","Positive"]))
        fig1 = px.bar(sentiment_by_entity, title="Sentiment by Entity", barmode='stack', color_discrete_map={"Positive":"#2ecc71","Neutral":"#f39c12","Negative":"#e74c3c"})
        st.plotly_chart(fig1, use_container_width=True)

        # Boxplot of sentiment scores
        fig2 = px.box(df_to_use, x='entity', y='vader_compound', title="Sentiment Score Distribution by Entity", color='entity')
        st.plotly_chart(fig2, use_container_width=True)

        # Daily sentiment trend
        daily_sentiment = prepare_daily_sentiment_grouped(df_to_use, group_col='entity')
        fig3 = px.line(daily_sentiment, x='ds', y='y', color='entity', title="Daily Average Sentiment by Entity", markers=True)
        st.plotly_chart(fig3, use_container_width=True)

        # Forecast for each entity
        st.markdown("### Forecast for Next 7 Days")
        forecasts = []
        for entity in daily_sentiment['entity'].unique():
            entity_df = daily_sentiment[daily_sentiment['entity']==entity]
            if len(entity_df.dropna(subset=['y'])) >= 2:
                forecast = run_prophet_forecast(entity_df)
                forecast['entity'] = entity
                forecasts.append(forecast)
        if forecasts:
            forecast_df = pd.concat(forecasts, ignore_index=True)
            fig4 = px.line(forecast_df, x='ds', y='yhat', color='entity', title="Forecasted Sentiment", markers=True)
            st.plotly_chart(fig4, use_container_width=True)
    else:
        st.info("No data available for visualizations.")
