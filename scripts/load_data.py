from datetime import datetime, timedelta
import random
import sys
import os

# Add the parent directory to the Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from database import add_entry


# Define the range of dates (from 01 March to 01 April)
start_date = datetime(2026, 3, 1)
end_date = datetime(2026, 4, 1)

# List of random food items
food_items = [
    "Apple", "Banana", "Orange", "Pizza", "Burger", "Salad", "Pasta", "Rice", "Chicken", "Fish",
    "Ice Cream", "Chocolate", "Cake", "Sandwich", "Soup", "Fries", "Steak", "Eggs", "Milk", "Juice"
]

# Function to generate random calorie values


def random_calories():
    return random.randint(50, 500)


# Iterate through each day in the range
current_date = start_date
while current_date < end_date:
    for _ in range(10):  # Add 10 items per day
        food_item = random.choice(food_items)
        calories = random_calories()
        add_entry(current_date.date().isoformat(),
                  food_item, calories)
    current_date += timedelta(days=1)

print("Random food and calorie data added successfully!")
