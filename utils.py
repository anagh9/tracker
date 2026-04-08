"""
Shared utilities and decorators
"""

from functools import wraps
from flask import redirect, url_for, session
from pytz import timezone
from datetime import datetime
from config import Config

def login_required(f):
    """Decorator to require user login"""
    @wraps(f)
    def decorated(*args, **kwargs):
        if "user_id" not in session:
            return redirect(url_for("auth.login"))
        return f(*args, **kwargs)
    return decorated

def get_timezone():
    """Get application timezone"""
    return timezone(Config.TIMEZONE)

def get_today():
    """Get today's date in app timezone"""
    tz = get_timezone()
    return datetime.now(tz).date()

def get_today_iso():
    """Get today's date as ISO string"""
    return get_today().isoformat()
