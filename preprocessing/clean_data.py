import pandas as pd
import os

# Absolute paths
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
INPUT_PATH = os.path.join(BASE_DIR, "data", "movies.csv")
OUTPUT_PATH = os.path.join(BASE_DIR, "data", "movies_clean.csv")

print("Reading from:", INPUT_PATH)

df = pd.read_csv(INPUT_PATH, low_memory=False)

# ✅ KEEP ALL REQUIRED COLUMNS + release_year
columns_needed = [
    "title",
    "IMDB_Rating",
    "vote_count",
    "original_language",
    "overview",
    "Director",
    "Poster_Link",
    "imdb_id",
    "popularity",
    "genres_list",
    "release_year"
]

df = df[columns_needed]

# Rename columns for consistency
df = df.rename(columns={
    "IMDB_Rating": "rating",
    "original_language": "language",
    "release_year": "year"
})

# Convert numeric columns
df["rating"] = pd.to_numeric(df["rating"], errors="coerce")
df["vote_count"] = pd.to_numeric(df["vote_count"], errors="coerce")
df["year"] = pd.to_numeric(df["year"], errors="coerce")

# Drop only truly critical missing values
df = df.dropna(subset=["title", "rating", "vote_count", "overview", "year"])

df["year"] = df["year"].astype(int)

df = df.reset_index(drop=True)

print("Cleaned dataset shape:", df.shape)

# Save cleaned dataset
df.to_csv(OUTPUT_PATH, index=False)
print("Saved cleaned data to:", OUTPUT_PATH)
