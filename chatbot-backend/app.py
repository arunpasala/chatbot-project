import os
import requests
from google.cloud import dialogflow_v2 as dialogflow
from flask import Flask, request, jsonify
from flask_cors import CORS

# Initialize Flask app and CORS
app = Flask(__name__)
CORS(app)

# Dialogflow setup
dialogflow_client = dialogflow.SessionsClient()
project_id = 'your-project-id'  # replace with your Dialogflow project ID

# OpenWeatherMap setup
WEATHER_API_KEY = 'your_openweather_api_key'  # replace with your API key
WEATHER_API_URL = 'http://api.openweathermap.org/data/2.5/weather'

# News API setup
NEWS_API_KEY = 'your_newsapi_key'  # replace with your NewsAPI key
NEWS_API_URL = 'https://newsapi.org/v2/top-headlines'

def get_dialogflow_response(user_input):
    session_id = 'unique-session-id'  # a unique session ID for each user
    session = dialogflow_client.session_path(project_id, session_id)
    text_input = dialogflow.TextInput(text=user_input, language_code='en')
    query_input = dialogflow.QueryInput(text=text_input)
    response = dialogflow_client.detect_intent(session=session, query_input=query_input)
    return response.query_result.fulfillment_text

# Fetch weather data
def get_weather(city):
    params = {
        'q': city,
        'appid': WEATHER_API_KEY,
        'units': 'metric',  # Celsius
    }
    response = requests.get(WEATHER_API_URL, params=params)
    data = response.json()
    
    if data.get('cod') != 200:
        return "Sorry, I couldn't fetch weather data at the moment."
    
    main = data.get('main', {})
    weather_description = data['weather'][0]['description']
    temperature = main.get('temp', 'N/A')
    humidity = main.get('humidity', 'N/A')

    weather_info = f"Weather: {weather_description.capitalize()}\nTemperature: {temperature}°C\nHumidity: {humidity}%"
    return weather_info

# Fetch news data
def get_news():
    params = {
        'country': 'us',
        'apiKey': NEWS_API_KEY,
    }
    response = requests.get(NEWS_API_URL, params=params)
    data = response.json()
    
    if data.get('status') != 'ok':
        return "Sorry, I couldn't fetch news at the moment."
    
    articles = data.get('articles', [])[:5]  # Get top 5 articles
    news_info = "\n".join([f"{article['title']} - {article['url']}" for article in articles])
    return f"Top news:\n{news_info}"

@app.route('/chat', methods=['POST'])
def chat():
    user_input = request.json.get('message')
    
    # Check if the user is asking for weather
    if 'weather' in user_input.lower():
        city = user_input.split("weather in")[-1].strip()  # Extract city from input
        weather_response = get_weather(city)
        return jsonify({'reply': weather_response})
    
    # Check if the user is asking for news
    if 'news' in user_input.lower():
        news_response = get_news()
        return jsonify({'reply': news_response})
    
    # For any other queries, use Dialogflow to generate a response
    if user_input:
        response = get_dialogflow_response(user_input)
        return jsonify({'reply': response})
    
    return jsonify({'reply': "Sorry, I didn't understand."}), 400

if __name__ == '__main__':
    app.run(debug=True)
