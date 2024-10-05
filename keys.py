from dotenv import load_dotenv
import os
load_dotenv()

open_api_weather_key= os.getenv('open_api_weather_key')
connection_string = 'mongodb://localhost:27017'
bot_key = os.getenv("bot_key")