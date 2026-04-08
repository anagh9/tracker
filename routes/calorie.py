"""
Calorie Tracker Routes Blueprint
"""

from flask import Blueprint, render_template, request, redirect, url_for, session, flash, send_file, jsonify
from datetime import date
from pytz import timezone
from openpyxl import Workbook
from io import BytesIO
from openai import OpenAI
import os
import database
from utils import login_required, get_timezone, get_today_iso
from config import Config

calorie_bp = Blueprint('calorie', __name__)

@calorie_bp.route("/", methods=["GET"])
@login_required
def index():
    """Calorie tracker dashboard"""
    user_id = session["user_id"]
    user = database.get_user_by_id(user_id)
    tz = get_timezone()
    selected_date = request.args.get("date", date.today().isoformat())
    entries = database.get_entries_by_date(user_id, selected_date)
    entries = [dict(entry) for entry in entries]
    total = database.get_total_calories(user_id, selected_date)
    all_dates = database.get_all_dates(user_id)
    today = date.today().isoformat()

    if today not in all_dates:
        all_dates = [today] + list(all_dates)

    return render_template(
        "calorie/dashboard.html",
        entries=entries,
        selected_date=selected_date,
        total=total,
        all_dates=all_dates,
        today=today,
        username=user["username"] if user else "User",
        is_oauth_user=session.get("auth_method") == "google",
        tracker_type="calorie"
    )


@calorie_bp.route("/add", methods=["POST"])
@login_required
def add():
    """Add a calorie entry"""
    user_id = session["user_id"]
    food_item = request.form.get("food_item", "").strip()
    calories = request.form.get("calories", "").strip()
    entry_date = request.form.get("entry_date", date.today().isoformat())

    if not food_item or not calories:
        flash("Both food item and calories are required.", "error")
        return redirect(url_for("calorie.index", date=entry_date))

    try:
        calories = int(calories)
        if calories <= 0:
            raise ValueError
    except ValueError:
        flash("Calories must be a positive number.", "error")
        return redirect(url_for("calorie.index", date=entry_date))

    database.add_entry(user_id, entry_date, food_item, calories)
    # Invalidate nutrient cache for this date so it gets recalculated
    database.delete_nutrient_data(user_id, entry_date)
    flash(f"Added {food_item} ({calories} kcal)", "success")
    return redirect(url_for("calorie.index", date=entry_date))


@calorie_bp.route("/delete/<int:entry_id>", methods=["POST"])
@login_required
def delete(entry_id):
    """Delete a calorie entry"""
    user_id = session["user_id"]
    entry_date = request.form.get("entry_date", date.today().isoformat())
    database.delete_entry(entry_id, user_id)
    # Invalidate nutrient cache for this date so it gets recalculated
    database.delete_nutrient_data(user_id, entry_date)
    flash("Entry deleted successfully.", "success")
    return redirect(url_for("calorie.index", date=entry_date))


@calorie_bp.route("/export", methods=["GET"])
@login_required
def export():
    """Export entries to Excel"""
    user_id = session["user_id"]
    user = database.get_user_by_id(user_id)
    all_dates = database.get_all_dates(user_id)

    # Create workbook
    wb = Workbook()
    ws = wb.active
    ws.title = "Calorie Entries"

    # Headers
    ws["A1"] = "Date"
    ws["B1"] = "Food Item"
    ws["C1"] = "Calories"
    ws["D1"] = "Time"

    # Style headers
    from openpyxl.styles import Font, PatternFill
    header_font = Font(bold=True)
    header_fill = PatternFill(start_color="FFA500", end_color="FFA500", fill_type="solid")

    for col in ["A1", "B1", "C1", "D1"]:
        ws[col].font = header_font
        ws[col].fill = header_fill

    # Data
    row = 2
    for entry_date in all_dates:
        entries = database.get_entries_by_date(user_id, entry_date)
        for entry in entries:
            ws[f"A{row}"] = entry_date
            ws[f"B{row}"] = entry["food_item"]
            ws[f"C{row}"] = entry["calories"]
            ws[f"D{row}"] = entry["created_at"][:16]
            row += 1

    # Auto-fit columns
    ws.column_dimensions["A"].width = 12
    ws.column_dimensions["B"].width = 25
    ws.column_dimensions["C"].width = 10
    ws.column_dimensions["D"].width = 16

    # Save to BytesIO
    output = BytesIO()
    wb.save(output)
    output.seek(0)

    return send_file(
        output,
        mimetype="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        as_attachment=True,
        download_name=f"calorie_tracker_{date.today()}.xlsx"
    )


@calorie_bp.route("/suggest-food", methods=["POST"])
@login_required
def suggest_food():
    """AI-powered food suggestion with OpenAI"""
    try:
        food_input = request.json.get("food_input", "").strip()

        if not food_input:
            return jsonify({"error": "Food input is required"}), 400

        api_key = Config.OPENAI_API_KEY
        if not api_key:
            return jsonify({"error": "OpenAI API key not configured"}), 500

        client = OpenAI(api_key=api_key)

        system_prompt = "You are a calorie estimation assistant. Respond with ONLY: 'food_name: calories_number'. Be brief and accurate."

        response = client.chat.completions.create(
            model=Config.OPENAI_MODEL,
            messages=[
                {
                    "role": "system",
                    "content": system_prompt
                },
                {
                    "role": "user",
                    "content": f"Estimate calories for: {food_input}"
                }
            ],
            temperature=Config.OPENAI_TEMPERATURE,
            max_tokens=Config.OPENAI_MAX_TOKENS
        )

        suggestion = response.choices[0].message.content.strip()

        if ":" in suggestion:
            parts = suggestion.split(":")
            food_name = parts[0].strip()
            try:
                calories = int(parts[-1].strip().split()[0])
                return jsonify({
                    "food": food_name,
                    "calories": calories,
                    "suggestion": suggestion
                })
            except (ValueError, IndexError):
                return jsonify({
                    "error": "Could not parse calorie value from response",
                    "raw_response": suggestion
                }), 400
        else:
            return jsonify({
                "error": "Invalid response format",
                "raw_response": suggestion
            }), 400

    except Exception as e:
        print(f"Error in suggest_food: {str(e)}")
        return jsonify({"error": str(e)}), 500


@calorie_bp.route("/nutrient-breakdown", methods=["GET"])
@login_required
def nutrient_breakdown():
    """Get nutrient breakdown - from cache or calculate with AI"""
    try:
        user_id = session["user_id"]
        selected_date = request.args.get("date", date.today().isoformat())
        entries = database.get_entries_by_date(user_id, selected_date)
        
        if not entries:
            return jsonify({
                "protein": 0,
                "carbs": 0,
                "fats": 0,
                "fiber": 0,
                "details": "No entries for this date",
                "success": True
            })
        
        # Check if nutrient data already exists in database
        cached_nutrients = database.get_nutrient_data(user_id, selected_date)
        
        if cached_nutrients:
            # Return from database
            total_cals = sum(e['calories'] for e in entries)
            protein_cals = cached_nutrients['protein_grams'] * 4
            carbs_cals = cached_nutrients['carbs_grams'] * 4
            fats_cals = cached_nutrients['fats_grams'] * 9
            
            protein_pct = round((protein_cals / total_cals * 100)) if total_cals > 0 else 0
            carbs_pct = round((carbs_cals / total_cals * 100)) if total_cals > 0 else 0
            fats_pct = round((fats_cals / total_cals * 100)) if total_cals > 0 else 0
            return jsonify({
                "protein": cached_nutrients['protein_grams'],
                "protein_pct": protein_pct,
                "carbs": cached_nutrients['carbs_grams'],
                "carbs_pct": carbs_pct,
                "fats": cached_nutrients['fats_grams'],
                "fats_pct": fats_pct,
                "fiber": cached_nutrients['fiber_grams'],
                "total_calories": total_cals,
                "analysis": cached_nutrients['analysis'],
                "success": True,
                "from_cache": True
            })
        
        # No cache found - call OpenAI to analyze nutrients
        # Prepare food list for nutrient analysis
        food_list = "\n".join([f"- {e['food_item']} ({e['calories']} kcal)" for e in entries])
        
        api_key = Config.OPENAI_API_KEY
        if not api_key:
            return jsonify({"error": "OpenAI API key not configured"}), 500
        
        client = OpenAI(api_key=api_key)
        
        system_prompt = """You are a nutritionist analyzing daily food intake. Based on the food items and calories,
        estimate the macronutrient breakdown. Respond ONLY with valid JSON (no markdown, no extra text):
        {
            "protein_grams": <number>,
            "carbs_grams": <number>,
            "fats_grams": <number>,
            "fiber_grams": <number>,
            "analysis": "<brief summary>"
        }"""
        
        response = client.chat.completions.create(
            model=Config.OPENAI_MODEL,
            messages=[
                {
                    "role": "system",
                    "content": system_prompt
                },
                {
                    "role": "user",
                    "content": f"Analyze this day's nutrition:\n{food_list}\nTotal: {sum(e['calories'] for e in entries)} kcal"
                }
            ],
            temperature=Config.OPENAI_TEMPERATURE,
            max_tokens=500
        )
        
        response_text = response.choices[0].message.content.strip()
        
        # Clean response if wrapped in markdown code blocks
        if response_text.startswith("```"):
            response_text = response_text.split("```")[1]
            if response_text.startswith("json"):
                response_text = response_text[4:]
        
        import json
        result = json.loads(response_text)
        
        # Calculate percentages
        total_cals = sum(e['calories'] for e in entries)
        protein_cals = result.get('protein_grams', 0) * 4
        carbs_cals = result.get('carbs_grams', 0) * 4
        fats_cals = result.get('fats_grams', 0) * 9
        
        protein_pct = round((protein_cals / total_cals * 100)) if total_cals > 0 else 0
        carbs_pct = round((carbs_cals / total_cals * 100)) if total_cals > 0 else 0
        fats_pct = round((fats_cals / total_cals * 100)) if total_cals > 0 else 0
        
        # Save nutrients to database for future use
        analysis = result.get('analysis', 'Daily nutrition analyzed')
        database.save_nutrient_data(
            user_id, 
            selected_date,
            result.get('protein_grams', 0),
            result.get('carbs_grams', 0),
            result.get('fats_grams', 0),
            result.get('fiber_grams', 0),
            analysis
        )
        
        return jsonify({
            "protein": result.get('protein_grams', 0),
            "protein_pct": protein_pct,
            "carbs": result.get('carbs_grams', 0),
            "carbs_pct": carbs_pct,
            "fats": result.get('fats_grams', 0),
            "fats_pct": fats_pct,
            "fiber": result.get('fiber_grams', 0),
            "total_calories": total_cals,
            "analysis": analysis,
            "success": True,
            "from_cache": False
        })
    
    except json.JSONDecodeError as e:
        print(f"JSON parse error: {str(e)}")
        return jsonify({"error": "Failed to parse nutrition data", "success": False}), 500
    except Exception as e:
        print(f"Error in nutrient_breakdown: {str(e)}")
        return jsonify({"error": str(e), "success": False}), 500
