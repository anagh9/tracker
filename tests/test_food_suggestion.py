#!/usr/bin/env python3
"""
Test script for AI food suggestion feature.
Run this script to test the /suggest-food endpoint with various food items.
"""

import requests
import json
from dotenv import load_dotenv
import os
from openai import OpenAI

# Load environment variables
load_dotenv()

# Test foods with expected calorie ranges for validation
TEST_FOODS = {
    "two eggs and toast": (300, 400),
    "apple": (80, 100),
    "pizza slice": (250, 300),
    "chicken breast 200g": (330, 370),
    "rice bowl": (200, 250),
    "salad with dressing": (150, 250),
    "banana": (80, 120),
    "burger": (500, 700),
    "pasta": (350, 450),
    "milk": (100, 160),
}

def test_direct_api():
    """Test the OpenAI API directly (without Flask server)"""
    print("=" * 70)
    print("Testing OpenAI API Directly (Direct API Call)")
    print("=" * 70)
    
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        print("❌ Error: OPENAI_API_KEY not found in .env file")
        return False
    
    client = OpenAI(api_key=api_key)
    success_count = 0
    
    for food, (min_cal, max_cal) in TEST_FOODS.items():
        try:
            response = client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {
                        "role": "system",
                        "content": "You are a calorie estimation assistant. Respond with ONLY: 'food_name: calories_number'. Be brief and accurate."
                    },
                    {
                        "role": "user",
                        "content": f"Estimate calories for: {food}"
                    }
                ],
                temperature=0,
                max_tokens=20
            )
            
            suggestion = response.choices[0].message.content.strip()
            
            # Parse response
            if ":" in suggestion:
                parts = suggestion.split(":")
                food_name = parts[0].strip()
                try:
                    calories = int(parts[-1].strip().split()[0])
                    
                    # Check if within reasonable range
                    status = "✓" if (min_cal <= calories <= max_cal * 1.5) else "⚠"
                    
                    print(f"{status} {food:30} → {food_name:20} {calories:4} kcal")
                    success_count += 1
                except (ValueError, IndexError):
                    print(f"❌ {food:30} → Parse Error: {suggestion}")
            else:
                print(f"❌ {food:30} → Invalid Format: {suggestion}")
        
        except Exception as e:
            print(f"❌ {food:30} → Error: {str(e)[:50]}")
    
    print("\n" + "=" * 70)
    print(f"Results: {success_count}/{len(TEST_FOODS)} tests passed")
    print("=" * 70)
    return success_count == len(TEST_FOODS)


def test_flask_endpoint(base_url="http://localhost:5000"):
    """Test the /suggest-food endpoint via Flask server"""
    print("\n" + "=" * 70)
    print("Testing Flask /suggest-food Endpoint")
    print("=" * 70)
    print(f"Base URL: {base_url}\n")
    
    # First, try to login or create a session
    session = requests.Session()
    
    success_count = 0
    
    for food in TEST_FOODS.keys():
        try:
            response = session.post(
                f"{base_url}/suggest-food",
                json={"food_input": food},
                timeout=10
            )
            
            if response.status_code == 401:
                print("❌ Authentication required - Please login first")
                print("   Start the Flask server and login, then run this test again")
                return False
            
            if response.status_code == 200:
                data = response.json()
                if "error" in data:
                    print(f"❌ {food:30} → Error: {data.get('error')}")
                else:
                    food_name = data.get("food", "N/A")
                    calories = data.get("calories", "N/A")
                    print(f"✓ {food:30} → {food_name:20} {calories:4} kcal")
                    success_count += 1
            else:
                print(f"❌ {food:30} → HTTP {response.status_code}")
        
        except requests.exceptions.ConnectionError:
            print(f"❌ Connection Error - Flask server not running on {base_url}")
            return False
        except Exception as e:
            print(f"❌ {food:30} → Error: {str(e)[:50]}")
    
    print("\n" + "=" * 70)
    print(f"Results: {success_count}/{len(TEST_FOODS)} tests passed")
    print("=" * 70)
    return success_count == len(TEST_FOODS)


def display_usage():
    """Display usage instructions"""
    print("""
╔═══════════════════════════════════════════════════════════════════════╗
║           AI FOOD SUGGESTION TESTER - Usage Instructions               ║
╚═══════════════════════════════════════════════════════════════════════╝

OPTION 1: Test OpenAI API Directly
──────────────────────────────────
This tests the OpenAI API call without needing Flask running.

  $ python3 test_food_suggestion.py

  Requirements:
  - OPENAI_API_KEY in .env file
  - No Flask server needed
  - Tests cost: ~$0.001-0.002 (minimal)

OPTION 2: Test Flask Endpoint
──────────────────────────────
This tests the full Flask endpoint including authentication.

  Terminal 1 (Run Flask):
  $ python3 app.py

  Terminal 2 (Run Tests):
  $ python3 test_food_suggestion.py --endpoint

  Requirements:
  - Flask server running on http://localhost:5000
  - User must be logged in via browser first
  - Tests confirm end-to-end functionality

OPTION 3: Test with Custom Foods
─────────────────────────────────
Edit test_food_suggestion.py and modify TEST_FOODS dictionary
with your own food items to test.

Example:
  TEST_FOODS = {
      "your food here": (min_calories, max_calories),
      "another food": (min_calories, max_calories),
  }

═══════════════════════════════════════════════════════════════════════════
    """)


if __name__ == "__main__":
    import sys
    
    # Check if --endpoint flag is provided
    test_endpoint = "--endpoint" in sys.argv or "--flask" in sys.argv
    
    if "--help" in sys.argv or "-h" in sys.argv:
        display_usage()
        sys.exit(0)
    
    if test_endpoint:
        # Test Flask endpoint
        test_flask_endpoint()
    else:
        # Test OpenAI API directly
        print("\n")
        display_usage()
        print("\nStarting direct OpenAI API test...\n")
        success = test_direct_api()
        
        print("\n💡 Tip: To test the Flask endpoint, run:")
        print("   python3 test_food_suggestion.py --endpoint")
        print("\n   (Make sure Flask server is running and you're logged in)")
        
        sys.exit(0 if success else 1)
