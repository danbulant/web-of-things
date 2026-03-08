from flask import Flask, g, redirect, render_template, request, url_for
from werkzeug.wrappers.response import Response

from db import DB

app = Flask(__name__)


@app.route("/api/report", methods=["POST"])
def report() -> str | Response:
    """Adds a measurement"""
    timestamp = request.form["timestamp"]
    tvoc = request.form["tvoc"]
    co2 = request.form["co2"]
    try:
        timestamp = int(timestamp)
        tvoc = float(tvoc)
        co2 = float(co2)
    except ValueError:
        return "Invalid data", 400
    db = get_db()
    db.store(timestamp, tvoc, co2)
    return "ok", 200


@app.route("/api/stats", methods=["GET"])
def stats() -> Response:
    db = get_db()
    return db.get_stats()


@app.route("/api/measurements", methods=["GET"])
def measurements() -> Response:
    db = get_db()
    page = request.get["page"]
    page_size = 20
    try:
        page = int(page)
        if page < 0:
            raise ValueError()
    except ValueError:
        return "Invalid page", 400
    return db.get_page(page, page_size)


def get_db() -> DB:
    """gets database connection"""
    db_instance = getattr(g, "_database", None)
    if db_instance is None:
        db_instance = g._database = DB()
    return db_instance


@app.teardown_appcontext
def close_connection(_exception):
    """disconnects database on connection close (if opened)"""
    db_instance = getattr(g, "_database", None)
    if db_instance is not None:
        db_instance.close()


if __name__ == "__main__":
    app.run(debug=True)
