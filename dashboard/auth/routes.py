from flask import abort, render_template, request
from flask_login import login_user, logout_user
from werkzeug.security import check_password_hash

from ..extensions import htmx
from . import auth
from .models import User


@auth.route("/login", methods=["POST"])
def login():
    if not htmx:
        abort(403)

    email = request.form.get("email")
    password = request.form.get("password")
    remember = bool(request.form.get("remember"))

    user = User.query.filter_by(email=email).first()

    if user and check_password_hash(user.password, password):
        login_user(user, remember=remember)
        return render_template("inc/index-content.html", current_user=user)

    return render_template(
        "inc/index-content.html",
        errors={"login_modal": "Nesprávné přihlašovací údaje."},
    )


@auth.route("/logout", methods=["POST"])
def logout():
    if not htmx:
        abort(403)

    logout_user()
    return render_template("inc/index-content.html", login_modal=False)
