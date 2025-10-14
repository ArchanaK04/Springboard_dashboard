# Strategic Intelligence System

A comprehensive system for collecting, analyzing, and forecasting sentiment trends from social media and news sources using machine learning and time series forecasting.

## 🚀 Features

- **Data Collection**: Automated collection from GNewsAPI and NewsAPI
- **Sentiment Analysis**: Multi-model sentiment scoring with VADER
- **Trend Forecasting**: Time series forecasting using Prophet
- **Alert System**: Automated alerts for negative and positive sentiment trends
- **Interactive Dashboard**: Streamlit-based web interface
- **Real-time Monitoring**: Scheduled data collection and analysis

## 📋 Prerequisites

- Python 3.8 or higher
- Chrome browser (for web scraping Twitter data)
- NewsAPI Account (optional)
- GNewsAPI Account (optional)
- Slack Workspace (optional, for alerts)

## 🛠️ Installation

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd strategic_intelligence_system
   ```

2. **Create virtual environment**
   ```bash
   python -m venv venv
   # Windows
   venv\Scripts\activate
   # macOS/Linux
   source venv/bin/activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Set up environment variables**
   ```bash
   # Copy the template and fill in your credentials
   cp env_template.txt .env
   ```
   
   Edit `.env` with your actual API credentials:
   ```env
   # Note: Twitter/X API credentials are no longer needed
   # The system uses web scraping to collect Twitter data
   
   # Optional: Other services
   NEWSAPI_KEY=your_newsapi_key_here
   HF_TOKEN=your_hf_token_here
   SLACK_TOKEN=your_slack_token_here
   ```

## 🔧 API Setup

### GNewsAPI Setup (Optional)
1. Register at https://gnews.io/
2. Get your free API key
3. Add to `.env` file

### NewsAPI Setup (Optional)
1. Register at [NewsAPI](https://newsapi.org)
2. Get your free API key
3. Add to `.env` file

### Slack Setup (Optional)
1. Create a Slack app at [api.slack.com/apps](https://api.slack.com/apps)
2. Add `chat:write` scope
3. Install to your workspace
4. Add bot token to `.env` file

## 🧪 Testing

Run the comprehensive test suite to verify your setup:

```bash
python test_system.py
```

This will test:
- Environment configuration
- Package imports
- Data collection
- Sentiment analysis
- Trend forecasting
- Alert system
- Dashboard components

## 🚀 Usage

### 1. Interactive Dashboard
Start the Streamlit dashboard:
```bash
streamlit run src/dashboard.py
```

The dashboard provides:
- Topic input and data filtering
- Sentiment trend visualization
- Forecast charts with confidence intervals
- Alert management
- Data export capabilities

### 2. Automated Pipeline
Run the main pipeline:
```bash
python app.py
```

This will:
- Collect data for the entered number of articles
- Analyze sentiment trends
- Generate forecasts
- Check for alerts
- Store results in CSV files
- Show results in Dashboard

### 3. Individual Components

**Data Collection**
```python
from src.data_collection.news_api import fetch_newsapi
from src.data_collection.gnews_api import fetch_gnews
df_newsapi = fetch_newsapi("ai", from_date="2023-12-01", to_date="2023-12-31", max_articles=50)
df_gnews = fetch_gnews("ai", from_date="2023-12-01", to_date="2023-12-31", max_articles=50)

```

**Sentiment Analysis**
```python
from src.analysis.sentiment import add_vader_sentiment
df_with_sentiment = add_vader_sentiment(df_newsapi, text_col="description")

```

**Trend Forecasting**
```python
from src.analysis.aggregate import prepare_daily_sentiment_grouped, run_prophet_forecast
daily_sentiment = prepare_daily_sentiment_grouped(df_with_sentiment, group_col="entity")
forecast_df = run_prophet_forecast(daily_sentiment)

```

**Alert Management**
```python
alert_threshold = -0.5
negative_alerts = df_with_sentiment[df_with_sentiment['vader_compound'] <= alert_threshold]
positive_alerts = df_with_sentiment[df_with_sentiment['vader_compound'] >= abs(alert_threshold)]
```

## 📁 Project Structure

```
Springboard_dashboard/
│
├── .venv/ # Virtual environment files
├── data/
│ ├── processed/
│ │ ├── daily_sentiment.csv
│ │ ├── forecast_sentiment.csv
│ │ ├── news_with_sentiment.parquet
│ │ └── news.parquet
│ └── raw/
│
├── src/
│ ├── alerting/
│ │ └── alerts.py
│ ├── analysis/
│ │ ├── aggregate.py
│ │ └── sentiment.py
│ ├── data_collection/
│ │ ├── gnews_api.py
│ │ └── news_api.py
│ └── utils/
│
├── .env
├── .gitattributes
├── app.py
└── requirements.txt
```

## ⚙️ Configuration

Edit `src/config.py` to customize:

- **POLL_INTERVAL_MINUTES**: How often to collect data (default: 30)
- **SENTIMENT_THRESHOLD**: Alert threshold for low sentiment (default: -0.5)
- **NEWSAPI_ENDPOINT**: NewsAPI base URL (default: https://newsapi.org/v2/everything)
- **GNEWS_ENDPOINT**: GNews API base URL (default: https://gnews.io/api/v4/search)
- **NEWSAPI_KEY**: Your NewsAPI key
- **GNEWS_KEY**: Your GNews API key
- **RAW_DATA_PATH**: File path template for raw data (default: `data/raw/news_raw_<topic>.parquet`)
- **PROCESSED_SENTIMENT_PATH**: File path for processed daily sentiment CSV (default: `data/processed/daily_sentiment_<topic>.csv`)
- **FORECAST_PATH**: File path for forecast CSV (default: `data/processed/forecast_sentiment_<topic>.csv`)
- **ALERTS_PATH**: File path for alert logs (default: `data/alerts/alerts_<topic>.csv`)


## 📊 Data Output

The system generates several CSV files:

- `raw_data_<topic>.csv`: Raw collected data with timestamps, source, text, and sentiment scores
- `processed_sentiment_<topic>.csv`: Daily aggregated sentiment for forecasting
- `forecasts_<topic>.csv`: Prophet forecast results with confidence intervals
- `alerts_<topic>.csv`: Alert logs with timestamps and messages


## 🚨 Troubleshooting

### Common Issues

**401 Unauthorized Error**
- Check your API credentials in `.env`
- Verify your access tokens are not expired

**No Data Collected**
- Check your internet connection
- Verify API keys are correct
- Check rate limits (if using Twitter,It has strict limits)

**Sentiment Analysis Fails**
- Limited Handling of Negations and Context
- Accuracy is Limited by Rule-Based Approach

**Dashboard Won't Start**
- Ensure Streamlit is installed: `pip install streamlit`
- Check for port conflicts (default: 8501)

### Getting Help

1. Run `python test_system.py` for diagnostics
2. Check the logs in your terminal
3. Verify all environment variables are set
4. Test individual components separately

## 🔄 Updates and Maintenance

- **Data Cleanup**: Old CSV files can be safely deleted
- **API Limits**: Monitor your API usage to avoid rate limits
- **Dependencies**: Regularly update packages with `pip install -r requirements.txt --upgrade`

## 📝 License

This project is for educational and research purposes. Please ensure compliance with:
- GNewsAPI Terms of Service
- NewsAPI Terms of Service
- Hugging Face Terms of Service

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests for new functionality
5. Submit a pull request

## 📞 Support

For issues and questions:
1. Check the troubleshooting section above
2. Run the test suite for diagnostics
3. Review the logs for specific error messages
4. Ensure all dependencies are properly installed

---

**Happy analyzing! 🎉**
