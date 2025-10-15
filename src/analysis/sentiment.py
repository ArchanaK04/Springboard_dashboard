import pandas as pd
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer

class SentimentAnalyzer:
    def __init__(self):
        self.analyzer = SentimentIntensityAnalyzer()

    def vader_score(self, text):
        """Computes VADER compound score and label."""
        try:
            vs = self.analyzer.polarity_scores(str(text))
            score = vs["compound"]
            if score >= 0.05:
                label = "positive"
            elif score <= -0.05:
                label = "negative"
            else:
                label = "neutral"
            return score, label
        except Exception:
            return 0.0, "neutral"

    def add_vader_sentiment(self, df, text_col="text"):
        if text_col not in df.columns:
            raise ValueError(f"Missing column: {text_col}")
        vader_results = df[text_col].apply(self.vader_score)
        df["vader_compound"] = vader_results.apply(lambda x: x[0])
        df["vader_label"] = vader_results.apply(lambda x: x[1])
        return df

# Create one shared instance you can import and use
sentiment_analyzer = SentimentAnalyzer()

def add_vader_sentiment(df, text_col="text"):
    return sentiment_analyzer.add_vader_sentiment(df, text_col)

