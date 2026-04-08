from openai import OpenAI, OpenAIError
import os
from dotenv import load_dotenv
load_dotenv()

def count_calorie_suggestions():
    food_item = input("Enter a food item to get calorie suggestions: ").strip()
    if food_item == "end":
        print("Exiting calorie suggestion test.")
        return False
    
    api_key = os.getenv("OPENAI_API_KEY")

    client  = OpenAI(api_key=api_key)
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {
                "role": "system",
                "content": "You are a calorie estimation assistant. Respond ONLY in this format: food_name: calories_number. Be brief and accurate."
            },
            {
                "role": "user",
                "content": f"Estimate calories for: {food_item}"
            }
        ],
        temperature=0,
        max_tokens=20
    )

    suggestion = response.choices[0].message.content.strip()
    print(f"Calorie suggestion for '{food_item}': {suggestion}")
    return True


if __name__ == "__main__":
    while True:
        try:
            rez = count_calorie_suggestions()
            if not rez:
                break

        except OpenAIError as e:
            print(f"Error communicating with OpenAI API: {str(e)}")
        except Exception as e:
            print(f"Unexpected error: {str(e)}")