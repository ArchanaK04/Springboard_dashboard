from src.data_collection.news_api import fetch_newsapi, fetch_gnews
import pandas as pd
import pathlib

def collect_entities_combined(entities, from_days=7, out_path="data/processed/news.parquet"):
    pathlib.Path(out_path).parent.mkdir(parents=True, exist_ok=True)
    frames = []
    for entity in entities:
        df1 = fetch_newsapi(entity, from_days=from_days)
        df2 = fetch_gnews(entity, from_days=from_days)
        combined = pd.concat([df1, df2], ignore_index=True)
        frames.append(combined)
    all_df = pd.concat(frames, ignore_index=True)
    all_df.to_parquet(out_path, index=False)
    return all_df

if __name__ == "__main__":
    entities = ["Nvidia", "AMD", "Intel"]
    df = collect_entities_combined(entities)
    print("Collected news shape:", df.shape)
