from flask import make_response, render_template, request, url_for
from flask_login import login_user, logout_user
from jinja2_fragments.flask import render_block
from werkzeug.security import check_password_hash

from ..extensions import htmx
from . import auth
from .models import User


@auth.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST" and htmx:
        email = request.form.get("email")
        password = request.form.get("password")
        remember = bool(request.form.get("remember"))

        user = User.query.filter_by(email=email).first()

        if user and check_password_hash(user.password, password):
            login_user(user, remember=remember)
            response = make_response("")
            response.headers["HX-Redirect"] = url_for("core.index")
            return response

        return render_block(
            "login.html",
            "content",
            email=email,
            errors={"login_modal": "Nesprávné přihlašovací údaje."},
        )

    return render_template("login.html")


@auth.route("/logout", methods=["POST"])
def logout():
    if htmx:
        logout_user()
        response = make_response("")
        response.headers["HX-Redirect"] = url_for("core.index")
        return response

    return render_template("login.html")
