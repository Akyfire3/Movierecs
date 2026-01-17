import pandas as pd
import os
import textwrap

# Absolute path to project root
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_PATH = os.path.join(BASE_DIR, "data", "movies_clean.csv")
HISTORY_PATH = os.path.join(BASE_DIR, "data", "history.txt")

import ast

def get_all_genres():
    df = pd.read_csv(DATA_PATH, usecols=["genres_list"])
    genres = set()

    for g in df["genres_list"].dropna():
        try:
            genre_list = ast.literal_eval(g)  # converts string -> list
            for genre in genre_list:
                genres.add(genre.strip())
        except Exception:
            continue

    return sorted(genres)


def load_history():
    if not os.path.exists(HISTORY_PATH):
        return set()
    with open(HISTORY_PATH, "r", encoding="utf-8") as f:
        return set(line.strip() for line in f if line.strip())


def save_to_history(imdb_id):
    with open(HISTORY_PATH, "a", encoding="utf-8") as f:
        f.write(str(imdb_id) + "\n")


def generate_reason(movie):
    rating = movie["rating"]
    votes = movie["vote_count"]
    year = movie["year"]

    if rating >= 8.5 and votes >= 50000:
        return "A critically acclaimed film with exceptional audience trust."
    
    if rating >= 8.0 and votes >= 20000:
        return "Widely praised for its storytelling and overall execution."
    
    if "Science Fiction" in str(movie["genres_list"]):
        return "A compelling science-fiction experience with strong concepts."
    
    if "Drama" in str(movie["genres_list"]):
        return "Known for its emotional depth and powerful performances."
    
    if year < 2000:
        return "A classic film that continues to influence modern cinema."
    
    return "A solid and engaging movie that fits your selected preferences."


def clean_poster(url):
    if pd.isna(url):
        return ""
    if "_V1" in url:
        return url.split("_V1")[0] + "_V1_.jpg"
    return url
def compute_weight(movie, prefer_newer, prefer_higher, preferred_genres):
    weight = 1

    if prefer_newer and movie["year"] >= 2015:
        weight += 3

    if prefer_higher and movie["rating"] >= 8.0:
        weight += 3

    if preferred_genres and pd.notna(movie["genres_list"]):
        try:
            movie_genres = set(ast.literal_eval(movie["genres_list"]))
            matches = len(movie_genres.intersection(preferred_genres))

            if matches > 0:
                weight += matches * 6   # 🔥 STRONG priority
            else:
                weight += 0.2          # still possible, very rare
        except Exception:
            pass

    return weight




def recommend_random_movie(
    min_rating,
    min_votes,
    prefer_newer=False,
    prefer_higher=False,
    preferred_genres=None
):
    if preferred_genres is None:
        preferred_genres = []



    df = pd.read_csv(DATA_PATH)

    history = load_history()

    # Base filters
    df = df[
        (df["rating"] >= min_rating) &
        (df["vote_count"] >= min_votes) &
        (df["year"] >= 1990)
    ]

    # Remove already recommended movies
    df = df[~df["imdb_id"].astype(str).isin(history)]

    # If exhausted
    if df.empty:
        open(HISTORY_PATH, "w").close()
        return {
            "error": "All matching movies have been recommended once. History reset. Click again."
        }

    # Pick random movie
    df["weight"] = df.apply(
    lambda row: compute_weight(row, prefer_newer, prefer_higher,preferred_genres),
    axis=1)

    movie = df.sample(1, weights=df["weight"]).iloc[0]

    save_to_history(movie["imdb_id"])

    reason = generate_reason(movie)


    return {
        "title": movie["title"],
        "year": int(movie["year"]),
        "rating": float(movie["rating"]),
        "votes": int(movie["vote_count"]),
        "genres": movie["genres_list"] if pd.notna(movie["genres_list"]) else "N/A",
        "overview": movie["overview"],
        "reason": reason,
        "poster": clean_poster(movie["Poster_Link"])
    }


# -------- CLI ENTRY POINT --------
if __name__ == "__main__":
    try:
        min_rating = float(input("Enter minimum IMDb rating (e.g. 7.5): "))
        min_votes = int(input("Enter minimum vote count (e.g. 3000): "))
    except ValueError:
        print("Invalid input. Please enter numeric values.")
        exit()

    print("\nFinding a movie for you...\n")
    print(recommend_random_movie(min_rating, min_votes))
