""""""

from flask import Blueprint, jsonify, abort
from datetime import date
from models.selection import DaySelection

app_views = Blueprint("app_views", __name__, url_prefix="/api/v1")

tday = DaySelection(date.today())
if not tday.words:
    tday.make_selection()


@app_views.route("/status", methods=["GET"])
def status():
    """Status of API"""
    return jsonify({"status": "OK"})


@app_views.route("/words", methods=["GET"])
def get_today_words():
    """"""
    return jsonify(tday.definitions)


@app_views.route("/word/<int:idx>", methods=["GET"])
def get_today_word(idx):
    """"""
    if 0 <= idx < 20:
        return jsonify(tday.get_word(idx))

    abort(404)


@app_views.route("/<date>/words", methods=["GET"])
def get_date_words(date):
    """"""
    day = DaySelection(date)
    if not day.words:
        abort(404)

    return jsonify(day.definitions)


@app_views.route("/<date>/word/<int:idx>", methods=["GET"])
def get_date_word(date, idx):
    """"""
    day = DaySelection(date)
    if not day.words:
        abort(404)

    return jsonify(day.get_word(idx))
