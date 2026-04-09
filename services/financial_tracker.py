"""
Financial tracker service layer.
Provides seeded demo data, CSV ingestion, and mock analytics structures.
"""

import csv
import io
from collections import defaultdict
from datetime import date, datetime, timedelta

import database


class FinancialTrackerService:
    """Coordinates financial tracker data access and placeholder analytics."""

    CATEGORY_COLORS = {
        "Groceries": "emerald",
        "Dining": "amber",
        "Transport": "sky",
        "Bills": "violet",
        "Shopping": "rose",
        "Subscriptions": "indigo",
        "Health": "teal",
        "Other": "slate",
    }

    CATEGORY_ICONS = {
        "Groceries": "🛒",
        "Dining": "🍽️",
        "Transport": "🚕",
        "Bills": "🧾",
        "Shopping": "🛍️",
        "Subscriptions": "🔁",
        "Health": "💊",
        "Other": "💼",
    }

    PAYMENT_METHODS = ["UPI", "Card", "Cash", "Bank", "Wallet"]

    CSV_DATE_FORMATS = [
        "%Y-%m-%d",
        "%d-%m-%Y",
        "%d/%m/%Y",
        "%m/%d/%Y",
        "%d %b %Y",
        "%d %B %Y",
    ]

    @classmethod
    def ensure_seed_data(cls, user_id):
        """Populate demo entries for a new user."""
        database.seed_financial_entries(user_id)

    @classmethod
    def get_dashboard_context(cls, user_id, selected_date):
        """Build dashboard context for the financial tracker."""
        cls.ensure_seed_data(user_id)
        entries = database.get_financial_entries_by_date(user_id, selected_date)
        total_spend = database.get_financial_total(user_id, selected_date)
        category_summary = cls._decorate_summary(database.get_financial_summary(user_id, selected_date), total_spend)
        all_dates = database.get_financial_dates(user_id)

        end_date = date.fromisoformat(selected_date)
        start_date = end_date - timedelta(days=19)
        entries_20d = database.get_financial_entries_for_range(user_id, start_date.isoformat(), end_date.isoformat())

        return {
            "entries": entries,
            "total_spend": total_spend,
            "category_summary": category_summary,
            "all_dates": all_dates,
            "analytics": cls._build_mock_analytics(entries_20d, selected_date),
            "categories": sorted(cls.CATEGORY_COLORS.keys()),
            "payment_methods": cls.PAYMENT_METHODS,
        }

    @classmethod
    def parse_csv_upload(cls, file_storage):
        """Parse uploaded CSV rows into normalized financial entries."""
        if not file_storage or not file_storage.filename:
            raise ValueError("Please choose a CSV file to upload.")
        if not file_storage.filename.lower().endswith(".csv"):
            raise ValueError("Only CSV uploads are supported right now.")

        try:
            decoded = file_storage.stream.read().decode("utf-8-sig")
        except UnicodeDecodeError as exc:
            raise ValueError("The CSV file must be UTF-8 encoded.") from exc

        reader = csv.DictReader(io.StringIO(decoded))
        if not reader.fieldnames:
            raise ValueError("The uploaded CSV is missing a header row.")

        parsed_rows = []
        for raw_row in reader:
            if not any((value or "").strip() for value in raw_row.values()):
                continue
            parsed_rows.append(cls._normalize_csv_row(raw_row))

        if not parsed_rows:
            raise ValueError("No valid expense rows were found in the uploaded CSV.")

        return parsed_rows

    @classmethod
    def normalize_category(cls, category):
        """Public category normalization helper for routes and future APIs."""
        return cls._normalize_category(category)

    @classmethod
    def _normalize_csv_row(cls, row):
        normalized = {str(key).strip().lower(): (value or "").strip() for key, value in row.items() if key}

        entry_date = cls._read_first(normalized, ["date", "entry_date", "txn date", "transaction date"])
        merchant = cls._read_first(normalized, ["merchant", "description", "name", "payee", "details"])
        amount = cls._read_first(normalized, ["amount", "debit", "spent", "expense"])
        category = cls._read_first(normalized, ["category", "type", "expense category"], default="Other")
        payment_method = cls._read_first(normalized, ["payment_method", "payment method", "mode"], default="Imported")
        notes = cls._read_first(normalized, ["notes", "note", "remarks", "comment"], default="")

        if not entry_date or not merchant or not amount:
            raise ValueError("Each CSV row must include a date, merchant/description, and amount column.")

        return {
            "entry_date": cls._parse_date(entry_date),
            "merchant": merchant[:80],
            "amount": cls._parse_amount(amount),
            "category": cls._normalize_category(category),
            "payment_method": payment_method[:30] or "Imported",
            "notes": notes[:160],
        }

    @classmethod
    def _read_first(cls, row, keys, default=""):
        for key in keys:
            if row.get(key):
                return row[key]
        return default

    @classmethod
    def _parse_date(cls, value):
        cleaned = value.strip()
        for fmt in cls.CSV_DATE_FORMATS:
            try:
                return datetime.strptime(cleaned, fmt).date().isoformat()
            except ValueError:
                continue
        raise ValueError(f"Could not parse date '{value}' in the uploaded CSV.")

    @classmethod
    def _parse_amount(cls, value):
        cleaned = (
            value.replace(",", "")
            .replace("INR", "")
            .replace("Rs.", "")
            .replace("Rs", "")
            .replace("$", "")
            .strip()
        )
        amount = float(cleaned)
        return round(abs(amount), 2)

    @classmethod
    def _normalize_category(cls, category):
        cleaned = category.strip().title() if category else "Other"
        return cleaned if cleaned in cls.CATEGORY_COLORS else "Other"

    @classmethod
    def _decorate_summary(cls, summary_rows, total_spend):
        decorated = []
        for row in summary_rows:
            category = row["category"]
            total_amount = row["total_amount"] or 0
            decorated.append(
                {
                    **row,
                    "icon": cls.CATEGORY_ICONS.get(category, "💼"),
                    "color": cls.CATEGORY_COLORS.get(category, "slate"),
                    "percentage": int((total_amount / total_spend) * 100) if total_spend else 0,
                }
            )
        return decorated

    @classmethod
    def _build_mock_analytics(cls, entries, selected_date):
        total_20d = round(sum(entry["amount"] for entry in entries), 2)
        daily_totals = defaultdict(float)
        category_totals = defaultdict(float)
        merchant_totals = defaultdict(float)

        for entry in entries:
            daily_totals[entry["entry_date"]] += entry["amount"]
            category_totals[entry["category"]] += entry["amount"]
            merchant_totals[entry["merchant"]] += entry["amount"]

        average_daily_spend = round(total_20d / max(len(daily_totals), 1), 2)
        top_category = max(category_totals.items(), key=lambda item: item[1], default=("Groceries", 0))
        top_merchant = max(merchant_totals.items(), key=lambda item: item[1], default=("Fresh Basket", 0))

        last_7_days = []
        end_date = date.fromisoformat(selected_date)
        for offset in range(6, -1, -1):
            day = end_date - timedelta(days=offset)
            iso_day = day.isoformat()
            amount = round(daily_totals.get(iso_day, 0), 2)
            last_7_days.append(
                {
                    "date": iso_day,
                    "label": day.strftime("%a"),
                    "amount": amount,
                }
            )

        max_day_amount = max((item["amount"] for item in last_7_days), default=0)
        for item in last_7_days:
            item["bar_height"] = max(12, int((item["amount"] / max_day_amount) * 100)) if max_day_amount else 12

        return {
            "headline": {
                "title": "Your spending stayed concentrated around a few predictable categories.",
                "description": "This mock analysis surfaces a stable pattern: essentials are driving most of the month while discretionary spend clusters around a few merchants.",
                "icon": "📊",
            },
            "overview": {
                "total_20d": total_20d,
                "average_daily_spend": average_daily_spend,
                "active_days": len(daily_totals),
                "top_category": top_category[0],
                "top_category_amount": round(top_category[1], 2),
                "top_merchant": top_merchant[0],
                "top_merchant_amount": round(top_merchant[1], 2),
            },
            "insights": [
                {
                    "title": "Largest category footprint",
                    "text": f"{top_category[0]} accounts for the biggest share of spend in this 20-day demo window.",
                    "tone": "positive",
                },
                {
                    "title": "Recurring merchant pattern",
                    "text": f"{top_merchant[0]} appears frequently enough to be a strong candidate for future recurring-spend detection.",
                    "tone": "neutral",
                },
                {
                    "title": "Budget watch",
                    "text": "A future analytics pass could flag days where dining and shopping overlap, since those combinations create the sharpest spikes here.",
                    "tone": "warning",
                },
            ],
            "recommendations": [
                "Review grocery and dining spend together to spot meals you can consolidate.",
                "Tag recurring subscriptions so future summaries can separate fixed vs flexible spending.",
                "Upload exported app statements regularly to improve category coverage and trend accuracy.",
            ],
            "daily_series": last_7_days,
        }
