from flask import Blueprint, render_template, request, redirect, url_for
from app.models.user import User
from app import db
from flask_login import login_user
import bcrypt

auth = Blueprint("auth", __name__)

# ----------------------
# LOGIN ROUTE
# ----------------------
@auth.route("/login", methods=["GET", "POST"])
def login():

    if request.method == "POST":

        username = request.form.get("username")
        password = request.form.get("password")

        user = User.query.filter_by(username=username).first()

        if user and bcrypt.checkpw(password.encode("utf-8"), user.password_hash.encode("utf-8")):
            login_user(user)

            return redirect(url_for("dashboard.dashboard_home"))

    return render_template("auth/login.html")


# ----------------------
# REGISTER ROUTE
# ----------------------
@auth.route("/register", methods=["GET", "POST"])
def register():

    if request.method == "POST":

        username = request.form.get("username")
        email = request.form.get("email")
        password = request.form.get("password")

        hashed = bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt())

        user = User(
            username=username,
            email=email,
            password_hash=hashed.decode("utf-8")
        )

        db.session.add(user)
        db.session.commit()

        return redirect(url_for("auth.login"))

    return render_template("auth/register.html")