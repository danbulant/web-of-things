"""Main module"""

from datetime import datetime
from time import time

from flask import Flask, g, render_template, request
from flask.typing import ResponseReturnValue
from flask_htmx import HTMX

from db import DB

app = Flask(__name__)
htmx = HTMX(app)


@app.template_filter()
def format_datetime(value):
    """Format datetime from jinja template"""
    if not value:
        return value
    return datetime.fromtimestamp(value).isoformat()


@app.route("/api/report", methods=["POST"])
def post_report() -> ResponseReturnValue:
    """Adds a measurement"""
    # timestamp = request.json["timestamp"]
    tvoc = request.json["tvoc"]
    co2 = request.json["co2"]
    try:
        # timestamp = int(timestamp)
        tvoc = float(tvoc)
        co2 = float(co2)
    except ValueError:
        return "Invalid data", 400
    db = get_db()
    timestamp = time()
    db.store(timestamp, tvoc, co2)
    return "ok", 200


@app.route("/", methods=["GET"])
def get_stats() -> ResponseReturnValue:
    """Gets overall statistics as well as few recent measurements"""
    db = get_db()
    stats = db.get_stats()
    recents = db.get_page(1, 10)
    template = "page/index.html.j2"
    if htmx:
        template = "block/index.html.j2"
    return render_template(template, stats=stats, list=recents)


@app.route("/measurements", methods=["GET"])
def get_measurements() -> ResponseReturnValue:
    """Lists measurements"""
    db = get_db()
    page_size = 20
    page = request.args["page"] if "page" in request.args else 1
    try:
        page = int(page)
        if page < 0:
            raise ValueError()
    except ValueError:
        return "Invalid page", 400
    data = db.get_page(page, page_size)
    count = db.count()
    has_next_page = count > page * page_size
    template = "page/measurements.html.j2"
    if htmx:
        template = "block/measurements.html.j2"
    return render_template(template, has_next_page=has_next_page, page=page, list=data)


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
