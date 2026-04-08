"""
Authentication Routes Blueprint
"""

from flask import Blueprint, render_template, request, redirect, url_for, session, flash
from werkzeug.security import generate_password_hash, check_password_hash
import os
import requests
from urllib.parse import urlencode
import database
from utils import login_required
from config import Config

auth_bp = Blueprint('auth', __name__, url_prefix='/auth')

@auth_bp.route("/login", methods=["GET", "POST"])
def login():
    """Login page - supports both form and Google OAuth"""
    if request.method == "POST":
        username = request.form.get("username", "").strip()
        password = request.form.get("password", "").strip()

        if not username or not password:
            flash("Username and password are required.", "error")
            return render_template("auth/login.html")

        user = database.get_user_by_username(username)

        if user and check_password_hash(user["password_hash"], password):
            session["user_id"] = user["id"]
            session["auth_method"] = "password"
            flash(f"Welcome, {username}!", "success")
            return redirect(url_for("dashboard.tracker_dashboard"))
        else:
            flash("Invalid username or password.", "error")

    return render_template("auth/login.html")


@auth_bp.route("/logout", methods=["GET"])
def logout():
    """Logout user"""
    session.clear()
    flash("You have been logged out.", "success")
    return redirect(url_for("auth.login"))


@auth_bp.route("/google", methods=["GET"])
def google_auth():
    """Google OAuth initiation"""
    auth_params = {
        "client_id": Config.GOOGLE_CLIENT_ID,
        "redirect_uri": Config.GOOGLE_REDIRECT_URI,
        "response_type": "code",
        "scope": "openid profile email",
        "access_type": "offline"
    }
    auth_url = Config.GOOGLE_AUTH_URI + "?" + urlencode(auth_params)
    return redirect(auth_url)


@auth_bp.route("/google/callback", methods=["GET"])
def google_callback():
    """Google OAuth callback"""
    code = request.args.get("code")

    if not code:
        flash("Authorization failed.", "error")
        return redirect(url_for("auth.login"))

    try:
        # Exchange code for token
        token_payload = {
            "code": code,
            "client_id": Config.GOOGLE_CLIENT_ID,
            "client_secret": Config.GOOGLE_CLIENT_SECRET,
            "redirect_uri": Config.GOOGLE_REDIRECT_URI,
            "grant_type": "authorization_code"
        }

        token_response = requests.post(Config.GOOGLE_TOKEN_URI, json=token_payload)
        token_response.raise_for_status()
        token_data = token_response.json()
        access_token = token_data.get("access_token")

        if not access_token:
            flash("Failed to obtain access token.", "error")
            return redirect(url_for("auth.login"))

        # Get user info
        headers = {"Authorization": f"Bearer {access_token}"}
        userinfo_response = requests.get(Config.GOOGLE_USERINFO_URI, headers=headers)
        userinfo_response.raise_for_status()
        userinfo = userinfo_response.json()

        email = userinfo.get("email")
        name = userinfo.get("name", "User")

        if not email:
            flash("Email not provided by Google.", "error")
            return redirect(url_for("auth.login"))

        # Check if user exists
        user = database.get_user_by_email(email)

        if user:
            session["user_id"] = user["id"]
            session["auth_method"] = "google"
            flash(f"Welcome back, {user['username']}!", "success")
            return redirect(url_for("dashboard.tracker_dashboard"))

        # Create new user
        username = name.replace(" ", "_").lower()
        counter = 1
        original_username = username

        while database.get_user_by_username(username):
            username = f"{original_username}{counter}"
            counter += 1

        # Create user with Google OAuth (no password)
        password_hash = generate_password_hash(os.urandom(24).hex())
        user_id = database.create_user(username, email, password_hash)

        if user_id:
            session["user_id"] = user_id
            session["auth_method"] = "google"
            flash(f"Welcome, {username}! Your account has been created via Google Sign-In.", "success")
            return redirect(url_for("dashboard.tracker_dashboard"))
        else:
            flash("Failed to create user account.", "error")
            return redirect(url_for("auth.login"))

    except requests.exceptions.RequestException as e:
        flash("Network error during authentication.", "error")
        return redirect(url_for("auth.login"))
    except Exception as e:
        flash("An error occurred during authentication.", "error")
        return redirect(url_for("auth.login"))


@auth_bp.route("/change-password", methods=["POST"])
@login_required
def change_password():
    """Change user password"""
    user_id = session["user_id"]
    is_oauth_user = session.get("auth_method") == "google"

    current_password = request.form.get("current_password", "").strip()
    new_password = request.form.get("new_password", "").strip()
    confirm_password = request.form.get("confirm_password", "").strip()

    # Validation
    if new_password != confirm_password:
        flash("New passwords do not match.", "error")
        return redirect(url_for("dashboard.tracker_dashboard"))

    if len(new_password) < 6:
        flash("Password must be at least 6 characters long.", "error")
        return redirect(url_for("dashboard.tracker_dashboard"))

    user = database.get_user_by_id(user_id)

    # For non-OAuth users, verify current password
    if not is_oauth_user:
        if not current_password:
            flash("Current password is required.", "error")
            return redirect(url_for("dashboard.tracker_dashboard"))

        if not check_password_hash(user["password_hash"], current_password):
            flash("Current password is incorrect.", "error")
            return redirect(url_for("dashboard.tracker_dashboard"))

    # Update password
    new_password_hash = generate_password_hash(new_password)
    if database.update_user_password(user_id, new_password_hash):
        flash("Password updated successfully.", "success")
    else:
        flash("Failed to update password.", "error")

    return redirect(url_for("dashboard.tracker_dashboard"))
