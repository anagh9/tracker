"""
Financial tracker routes blueprint.
"""

import csv
import io
from datetime import date

from flask import Blueprint, Response, flash, redirect, render_template, request, session, url_for

import database
from services import FinancialTrackerService
from utils import login_required

financial_bp = Blueprint("financial", __name__)


@financial_bp.route("/", methods=["GET"])
@login_required
def index():
    """Financial tracker dashboard."""
    user_id = session["user_id"]
    user = database.get_user_by_id(user_id)
    selected_date = request.args.get("date", date.today().isoformat())
    today = date.today().isoformat()

    dashboard_context = FinancialTrackerService.get_dashboard_context(user_id, selected_date)
    all_dates = dashboard_context["all_dates"]
    if today not in all_dates:
        all_dates = [today] + list(all_dates)
    dashboard_context["all_dates"] = all_dates

    return render_template(
        "financial/dashboard.html",
        selected_date=selected_date,
        today=today,
        username=user["username"] if user else "User",
        is_oauth_user=session.get("auth_method") == "google",
        tracker_type="financial",
        **dashboard_context,
    )


@financial_bp.route("/add", methods=["POST"])
@login_required
def add():
    """Add a manual expense entry."""
    user_id = session["user_id"]
    entry_date = request.form.get("entry_date", date.today().isoformat())
    merchant = request.form.get("merchant", "").strip()
    amount = request.form.get("amount", "").strip()
    category = request.form.get("category", "").strip() or "Other"
    payment_method = request.form.get("payment_method", "").strip() or "Card"
    notes = request.form.get("notes", "").strip()

    if not merchant or not amount:
        flash("Merchant and amount are required.", "error")
        return redirect(url_for("financial.index", date=entry_date))

    try:
        parsed_amount = round(abs(float(amount)), 2)
        if parsed_amount <= 0:
            raise ValueError
    except ValueError:
        flash("Amount must be a positive number.", "error")
        return redirect(url_for("financial.index", date=entry_date))

    database.add_financial_entry(
        user_id=user_id,
        entry_date=entry_date,
        merchant=merchant,
        amount=parsed_amount,
        category=FinancialTrackerService.normalize_category(category),
        payment_method=payment_method,
        notes=notes,
        source="manual",
    )
    flash(f"Added expense for {merchant}.", "success")
    return redirect(url_for("financial.index", date=entry_date))


@financial_bp.route("/upload-csv", methods=["POST"])
@login_required
def upload_csv():
    """Upload a CSV file of expense rows."""
    user_id = session["user_id"]
    redirect_date = request.form.get("redirect_date", date.today().isoformat())

    try:
        parsed_rows = FinancialTrackerService.parse_csv_upload(request.files.get("csv_file"))
        inserted = database.add_financial_entries_bulk(user_id, parsed_rows, source="csv")
        flash(f"Imported {inserted} expense rows from CSV.", "success")
    except ValueError as exc:
        flash(str(exc), "error")

    return redirect(url_for("financial.index", date=redirect_date))


@financial_bp.route("/csv-template", methods=["GET"])
@login_required
def download_csv_template():
    """Download a starter CSV template for expense imports."""
    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(["date", "merchant", "amount", "category", "payment_method", "notes"])
    writer.writerow([date.today().isoformat(), "Fresh Basket", "24.50", "Groceries", "UPI", "Weekly essentials"])
    writer.writerow([date.today().isoformat(), "Metro Card Reload", "12.00", "Transport", "Wallet", "Commute top-up"])
    writer.writerow([date.today().isoformat(), "Cafe Meridian", "16.75", "Dining", "Card", "Lunch with team"])

    return Response(
        output.getvalue(),
        mimetype="text/csv",
        headers={"Content-Disposition": "attachment; filename=financial_tracker_template.csv"},
    )


@financial_bp.route("/delete/<int:entry_id>", methods=["POST"])
@login_required
def delete(entry_id):
    """Delete a financial entry."""
    user_id = session["user_id"]
    entry_date = request.form.get("entry_date", date.today().isoformat())
    database.delete_financial_entry(entry_id, user_id)
    flash("Expense entry deleted successfully.", "success")
    return redirect(url_for("financial.index", date=entry_date))
