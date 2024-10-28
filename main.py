from flask import Flask, render_template, request
import google.generativeai as genai
import os

# Set your API key
os.environ["GOOGLE_API_KEY"] = "you api here"
genai.configure(api_key=os.environ["GOOGLE_API_KEY"])

app = Flask(__name__)

# Initialize the model
model = genai.GenerativeModel("models/gemini-pro")

# Function to generate recommendations
def generate_recommendation(dietary_preferences, fitness_goals, lifestyle_factors, dietary_restrictions,
                            health_conditions, user_query):
    prompt = f"""
    Can you suggest a comprehensive plan that includes diet and workout options for better fitness?
    for this user:
    dietary preferences: {dietary_preferences},
    fitness goals: {fitness_goals},
    lifestyle factors: {lifestyle_factors},
    dietary restrictions: {dietary_restrictions},
    health conditions: {health_conditions},
    user query: {user_query},

    Based on the above user’s dietary preferences, fitness goals, lifestyle factors, dietary restrictions, and health conditions provided, create a customized plan that includes:

    Diet Recommendations: RETURN LIST
    5 specific diet types suited to their preferences and goals.

    Workout Options: RETURN LIST
    5 workout recommendations that align with their fitness level and goals.

    Meal Suggestions: RETURN LIST
    5 breakfast ideas.

    5 dinner options.

    Additional Recommendations: RETURN LIST
    Any useful snacks, supplements, or hydration tips tailored to their profile.
    """

    response = model.generate_content(prompt)
    return response.text if response else "No response from the model."

@app.route('/')
def index():
    return render_template('index.html', recommendations=None)

@app.route('/recommendations', methods=['POST'])
def recommendations():
    if request.method == "POST":
        # Collect form data
        dietary_preferences = request.form['dietary_preferences']
        fitness_goals = request.form['fitness_goals']
        lifestyle_factors = request.form['lifestyle_factors']
        dietary_restrictions = request.form['dietary_restrictions']
        health_conditions = request.form['health_conditions']
        user_query = request.form['user_query']

        # Generate recommendations using the model
        recommendations_text = generate_recommendation(
            dietary_preferences, fitness_goals, lifestyle_factors, dietary_restrictions, health_conditions, user_query
        )

        # Parse the results for display
        recommendations = {
            "diet_types": [],
            "workouts": [],
            "breakfasts": [],
            "dinners": [],
            "additional_tips": []
        }

        print("text : ", recommendations_text)

        # Split and map responses based on keywords
        current_section = None
        for line in recommendations_text.splitlines():
            if "Diet Recommendations:" in line:
                current_section = "diet_types"
            elif "Workout Options:" in line:
                current_section = "workouts"
            elif "Meal Suggestions:" in line:
                current_section = "breakfasts"
            elif "Dinner Options:" in line:
                current_section = "dinners"
            elif "Additional Recommendations:" in line:
                current_section = "additional_tips"
            elif line.strip() and current_section:
                recommendations[current_section].append(line.strip())

        print("dict : ", recommendations)
        return render_template('index.html', recommendations=recommendations)

if __name__ == "__main__":
    app.run(debug=True)
