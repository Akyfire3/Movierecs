from flask import Flask, render_template, request, jsonify
import os
import sys

# ---- Fix import path ----
PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, PROJECT_ROOT)

from app.recommender import recommend_random_movie, get_all_genres


app = Flask(__name__)


@app.route("/", methods=["GET", "POST"])
def home():
    genres = get_all_genres()
    movie = None

    print("---- HOME ROUTE HIT ----")
    print("Method:", request.method)

    if request.method == "POST":
        print("Form data:", request.form)

        min_rating = request.form.get("rating")
        min_votes = request.form.get("votes")

        print("rating raw:", min_rating)
        print("votes raw:", min_votes)

        min_rating = float(min_rating)
        min_votes = int(min_votes)

        movie = recommend_random_movie(
            min_rating,
            min_votes,
            False,
            False,
            ""
        )

        print("Movie returned:", movie)

    return render_template("index.html", movie=movie, genres=genres)


@app.route("/recommend", methods=["POST"])
def recommend_api():
    try:
        data = request.get_json(force=True)

        min_rating = float(data.get("rating", 0))
        min_votes = int(data.get("votes", 0))
        prefer_newer = bool(data.get("prefer_newer", False))
        prefer_higher = bool(data.get("prefer_higher", False))

        movie = recommend_random_movie(
            min_rating,
            min_votes,
            prefer_newer,
            prefer_higher
        )

        


        if isinstance(movie, dict) and movie.get("error"):
            return jsonify(movie), 200

        return jsonify(movie), 200

    except Exception as e:
        return jsonify({
            "error": "Server error",
            "details": str(e)
        }), 500

@app.route("/reset-history", methods=["POST"])
def reset_history():
    try:
        history_path = os.path.join(PROJECT_ROOT, "data", "history.txt")
        open(history_path, "w").close()
        return jsonify({"message": "Recommendation history reset."}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# ---- THIS IS CRITICAL ----
if __name__ == "__main__":
    app.run(debug=True)
