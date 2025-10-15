import pandas as pd
from prophet import Prophet


def prepare_daily_sentiment_grouped(df, group_col='entity', date_col='date', sentiment_col='vader_compound'):
    """
    Aggregates sentiment scores per day grouped by an entity (e.g., competitor or source).
    Returns daily aggregated DataFrame with columns: ds (datetime), entity/group_col, y (mean sentiment), count (article count).
    """
    df[date_col] = pd.to_datetime(df[date_col])
    grouped_df = df.groupby([group_col, date_col]).agg(
        y=(sentiment_col, "mean"),
        count=(sentiment_col, "count")
    ).reset_index().rename(columns={date_col: "ds"}).sort_values([group_col, "ds"])
    return grouped_df


def run_prophet_forecast(daily_df, periods=7):
    """
    Fits Prophet model and forecasts sentiment for given future days.
    Expects daily_df with columns including ds (date) and y (value).
    Returns forecast DataFrame with columns including ds (date), yhat (forecast), yhat_lower, yhat_upper.
    """
    model = Prophet()
    model.fit(daily_df)
    future = model.make_future_dataframe(periods=periods)
    forecast = model.predict(future)
    return forecast

