#!/usr/bin/python3
"""Flask Application"""

from api.v1.api import app_views
from flask import Flask, make_response, jsonify
from flask_cors import CORS

app = Flask(__name__)
app.config["JSONIFY_PRETTYPRINT_REGULAR"] = True
app.url_map.strict_slashes = False
app.register_blueprint(app_views)
CORS(app, resources={r"/api/v1/*": {"origins": "*"}})


@app.errorhandler(404)
def not_found(error):
    """404 Error
    ---
    responses:
      404:
        description: a resource was not found
    """
    return make_response(jsonify({"error": "Not found"}), 404)


if __name__ == "__main__":
    host = "0.0.0.0"

    app.run(host=host, port=5000, threaded=True)
