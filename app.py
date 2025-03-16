import streamlit as st
import google.generativeai as genai
from text_interaction import handle_text_interaction
from db import insert_data
import os
import json
from dotenv import load_dotenv

# Load API key
load_dotenv()
API_KEY = os.getenv('GENAI_API_KEY')
genai.configure(api_key=API_KEY)

# Function to load JSON files dynamically
def load_json(file_name):
    """Load JSON data from the 'data/' folder."""
    file_path = os.path.join("data", file_name)
    try:
        with open(file_path, "r", encoding="utf-8") as file:
            return json.load(file)
    except FileNotFoundError:
        st.error(f"Error: {file_name} not found in 'data/' folder. Please check the file path.")
        return {}

# Load structured data from JSON files
creator_info = load_json("creator_info.json")
aimerz_data = load_json("aimerz_data.json")

# Convert JSON to a readable system prompt
SYSTEM_PROMPT = f"""
You are a chatbot created by {creator_info.get("name", "N/A")}.  
Here is some information about your creator:

{json.dumps(creator_info, indent=2)}

Additionally, here is information about your project:

{json.dumps(aimerz_data, indent=2)}

If anyone asks about the creator, always mention {creator_info.get("name", "N/A")}.  
For more details, refer them to their LinkedIn profile:  
[LinkedIn Profile](https://www.linkedin.com/in/vishwa-mohan/).  

For more information about AIMERZ, visit:  
[AIMERZ Official Website](https://aimerz.ai/)
"""

# Load the model
model = genai.GenerativeModel("gemini-1.5-flash")

# Streamlit UI
st.title('Realtime Chatbot App')

def handle_text_interaction(model):
    """Handles text-to-text chatbot interaction"""
    user_input = st.text_input('Enter your query:')
    button = st.button('Get Response')

    if button and user_input:
        full_prompt = SYSTEM_PROMPT + "\nUser Query: " + user_input
        response = model.generate_content(full_prompt)
        chatbot_response = response.text.strip()  # Clean output

        st.write(chatbot_response)

        return {"user_input": user_input, "response": chatbot_response}

    return None

# Call text interaction function
response = handle_text_interaction(model)

if response:
    insert_data(response['user_input'], response['response'])  # Store in DB if needed
