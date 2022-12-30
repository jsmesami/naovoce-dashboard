from flask import redirect, render_template, request, url_for
from flask_login import login_user, logout_user
from werkzeug.security import check_password_hash

from . import auth
from .models import User


@auth.route("/login", methods=["GET", "POST"])
def login():
    error = None

    if request.method == "POST":
        email = request.form.get("email")
        password = request.form.get("password")
        remember = bool(request.form.get("remember"))

        user = User.query.filter_by(email=email).first()

        if user and check_password_hash(user.password, password):
            login_user(user, remember=remember)
            return redirect(url_for("core.index"))

        error = "Nesprávné přihlašovací údaje."

    return render_template("login.html", error=error)


@auth.route("/logout", methods=["GET"])
def logout():
    logout_user()
    return redirect(url_for("auth.login"))
