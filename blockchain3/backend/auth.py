from flask import Blueprint, request, redirect, url_for, render_template, flash
from flask_login import login_user, logout_user
from database import db, User

auth = Blueprint("auth", __name__)

@auth.route("/signup", methods=["GET", "POST"])
def signup():
    if request.method == "POST":
        role = request.form["role"]
        email = request.form["email"]
        password = request.form["password"]

        # Check if user already exists
        existing_user = User.query.filter_by(email=email).first()
        if existing_user:
            flash("Account already exists. Please login.", "error")
            return render_template("signup.html")

        user = User(role=role, email=email, password=password)
        db.session.add(user)
        db.session.commit()

        # ✅ SUCCESS MESSAGE
        flash("Account created successfully. Please login.", "success")
        return redirect(url_for("auth.login"))

    return render_template("signup.html")

@auth.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.form["email"]
        password = request.form["password"]

        user = User.query.filter_by(email=email).first()
        if user and user.password == password:
            login_user(user)
            return redirect("/institute" if user.role == "institute" else "/student")

        flash("Invalid email or password", "error")

    return render_template("login.html")

@auth.route("/logout")
def logout():
    logout_user()
    return redirect("/")
