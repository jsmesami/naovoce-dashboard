from flask import render_template
from flask_login import current_user

from . import core


@core.route("/")
def index():
    return render_template("index.html", user=current_user)
