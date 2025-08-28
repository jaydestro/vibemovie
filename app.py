import os
from dotenv import load_dotenv
from flask import Flask, render_template, request, redirect, url_for, flash
from cosmos_client import get_cosmos, CosmosUnavailable


def create_app():
    # Load environment from .env if present (local dev convenience)
    load_dotenv(override=False)
    app = Flask(__name__)
    app.secret_key = os.environ.get("FLASK_SECRET_KEY", "dev-secret-key")

    @app.route("/")
    def index():
        try:
            db = get_cosmos()
            movies = db.list_movies()
            return render_template(
                "index.html", movies=movies, cosmos_error=None
            )
        except CosmosUnavailable as e:
            flash(str(e), "warning")
            return render_template(
                "index.html", movies=[], cosmos_error=str(e)
            )

    @app.post("/movies")
    def create_movie():
        title = request.form.get("title", "").strip()
        if not title:
            flash("Movie title is required", "error")
            return redirect(url_for("index"))
        try:
            db = get_cosmos()
            movie = db.create_movie(title)
            flash(f"Added '{movie['title']}'", "success")
        except CosmosUnavailable as e:
            flash(str(e), "error")
        return redirect(url_for("index"))

    @app.get("/movies/<movie_id>")
    def movie_detail(movie_id: str):
        try:
            db = get_cosmos()
            movie = db.get_movie(movie_id)
            if not movie:
                flash("Movie not found", "error")
                return redirect(url_for("index"))
            ratings = db.list_ratings(movie_id)
            comments = db.list_comments(movie_id)
            avg = db.average_rating(movie_id)
            return render_template(
                "movie.html",
                movie=movie,
                ratings=ratings,
                comments=comments,
                avg=avg,
                cosmos_error=None,
            )
        except CosmosUnavailable as e:
            flash(str(e), "warning")
            return render_template(
                "movie.html",
                movie=None,
                ratings=[],
                comments=[],
                avg=None,
                cosmos_error=str(e),
            )

    @app.post("/movies/<movie_id>/rate")
    def add_rating(movie_id: str):
        try:
            stars = int(request.form.get("stars", "0"))
        except ValueError:
            stars = -1
        if stars < 0 or stars > 5:
            flash("Rating must be an integer between 0 and 5", "error")
            return redirect(url_for("movie_detail", movie_id=movie_id))
        try:
            db = get_cosmos()
            db.add_rating(movie_id, stars)
            flash("Rating added", "success")
        except CosmosUnavailable as e:
            flash(str(e), "error")
        return redirect(url_for("movie_detail", movie_id=movie_id))

    @app.post("/movies/<movie_id>/comment")
    def add_comment(movie_id: str):
        text = request.form.get("text", "").strip()
        if not text:
            flash("Comment cannot be empty", "error")
            return redirect(url_for("movie_detail", movie_id=movie_id))
        try:
            db = get_cosmos()
            db.add_comment(movie_id, text)
            flash("Comment added", "success")
        except CosmosUnavailable as e:
            flash(str(e), "error")
        return redirect(url_for("movie_detail", movie_id=movie_id))

    return app


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 3000))
    app = create_app()
    app.run(host="0.0.0.0", port=port, debug=True)
