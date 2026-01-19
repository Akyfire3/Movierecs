from flask import Flask, render_template, request, jsonify
import os
import sys

from flask import send_from_directory




# ---- Fix import path ----
PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, PROJECT_ROOT)

from app.recommender import recommend_random_movie, get_all_genres


app = Flask(
    __name__,
    static_folder="static",
    static_url_path=""
)


@app.route("/", methods=["GET", "POST"])
def home():
    genres = get_all_genres()
    movie = None

    print("---- HOME ROUTE HIT ----")
    print("Method:", request.method)

    if request.method == "POST":
        print("Form data:", request.form)

        rating_raw = request.form.get("rating")
        votes_raw = request.form.get("votes")

        try:
            min_rating = float(rating_raw)
            min_votes = int(votes_raw)
        except (TypeError, ValueError):
            return render_template(
                "index.html",
                movie=None,
                genres=get_all_genres(),
                error="Please enter valid numeric values for rating and votes."
            )

        if not (0 <= min_rating <= 10):
            return render_template(
                "index.html",
                movie=None,
                genres=get_all_genres(),
                error="IMDb rating must be between 0 and 10."
            )

        if min_votes < 0:
            return render_template(
                "index.html",
                movie=None,
                genres=get_all_genres(),
                error="Vote count cannot be negative."
            )
        # IMDb realistic sanity checks (soft warnings)
        if min_rating > 9.3:
            return render_template(
                "index.html",
                movie=None,
                genres=get_all_genres(),
                error="IMDb ratings rarely exceed 9.3. Try a value between 6.0 and 9.0."
            )

        if min_votes > 34495:
            return render_template(
                "index.html",
                movie=None,
                genres=get_all_genres(),
                error="Very few movies have over 1,000,000 votes. Try a lower vote count."
            )


        

        print("rating raw:", min_rating)
        print("votes raw:", min_votes)

        

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
