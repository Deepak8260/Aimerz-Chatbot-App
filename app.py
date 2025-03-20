import streamlit as st
import google.generativeai as genai
from database import insert_data, get_chat_history
import os
import json
from dotenv import load_dotenv

# Load API key
#load_dotenv()
#API_KEY = os.getenv('GENAI_API_KEY')

# Load API Key from Streamlit Secrets
API_KEY = st.secrets["GENAI_API_KEY"]

# Configure Generative AI
genai.configure(api_key=API_KEY)
model = genai.GenerativeModel("gemini-1.5-flash")

# --------------------------------------------
# 🔹 Function to Load JSON Files
# --------------------------------------------

def load_json(file_name):
    """Load JSON data from the 'data' folder."""
    file_path = os.path.join("data", file_name)
    try:
        with open(file_path, "r", encoding="utf-8") as file:
            return json.load(file)
    except FileNotFoundError:
        st.error(f"Error: {file_name} not found in 'data/' folder.")
        return {}

# Load structured data from JSON files
creator_info = load_json("creator_info.json")
aimerz_data = load_json("aimerz_data.json")

# Extract creator details
creator_name = creator_info.get("name", "Unknown")
creator_bio = creator_info.get("bio", "No bio available.")
aimerz_description = aimerz_data.get("description", "AIMERZ is an AI-powered platform for learning.")

# --------------------------------------------
# 🔹 System Prompt (Professional & Structured)
# --------------------------------------------

SYSTEM_PROMPT = f"""
You are **AIMERZ Bot 🤖**, an AI chatbot designed to provide intelligent and professional responses to both general and AIMERZ-related queries.

🔹 **How to Introduce Yourself**  
- If the user asks **"Who are you?"**, **"Who r u?"**, **"What is your name?"**, or similar questions, respond with:  
  **"I am AIMERZ Bot 🤖, your AI assistant here to help with AIMERZ-related and general queries."**  

🔹 **General Queries (Default Mode)**  
- For general topics (e.g., programming, history, politics), respond normally **without mentioning AIMERZ**, unless explicitly asked.  
- **Do NOT include AIMERZ or its creator** in responses unless the query is specifically related to them.  

🔹 **AIMERZ-Specific Queries**  
- If the user asks **"What is AIMERZ?"**, respond with:  
  **"AIMERZ is India's first job-focused learning platform, founded by Vishwa Mohan, Former CIO of PhysicsWallah. It provides career-aligned courses in Full Stack Development, Data Science, and DSA, along with hands-on projects and industry internships. You can learn more at [AIMERZ Official Website](https://aimerz.ai/)."**  
- If the user asks about **AIMERZ courses or instructors**, provide details from the following data:  
  {json.dumps(aimerz_data, indent=2)}  
- If the user asks about **Vishwa Mohan**, mention that he is the creator of AIMERZ and provide his LinkedIn profile:  
  [LinkedIn Profile](https://www.linkedin.com/in/vishwa-mohan/).  
- If the user asks how to learn more about AIMERZ, refer them to:  
  [AIMERZ Official Website](https://aimerz.ai/).  

🔹 **Creator Information**  
Here is some information about your creator:  
{json.dumps(creator_info, indent=2)}

🔹 **Behavior Rules**  
- **Always introduce yourself as AIMERZ Bot 🤖 ONLY when asked about your identity.**  
- **Do NOT include self-introduction when answering 'What is AIMERZ?'.**  
- **Mention AIMERZ ONLY when relevant.**  
- If the query does not explicitly ask about AIMERZ, act as a normal chatbot.  
"""


# Streamlit UI Configuration
st.set_page_config(page_title="AIMERZ Chatbot", layout="wide")
st.title("💬 AIMERZ Chatbot")

# Initialize session state for messages
if "messages" not in st.session_state:
    st.session_state.messages = []

# Sidebar for Chat History
st.sidebar.title("📜 Chat History")

chat_history = get_chat_history()  # Now returns grouped data

if chat_history:
    for date, chats in chat_history.items():
        with st.sidebar.expander(f"📅 {date}"):  # Grouped by date
            for i, chat in enumerate(chats):
                if "user_input" in chat:
                    if st.sidebar.button(f"🔹 {chat['user_input'][:40]}", key=f"chat_{date}_{i}"):
                        st.session_state.messages.extend([
                            {"role": "user", "content": chat["user_input"]},
                            {"role": "assistant", "content": chat["response"]}
                        ])
else:
    st.sidebar.write("No chat history yet!")

# Display Chat Messages
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# Chat Input & AI Response Handling
user_input = st.chat_input("Type your message...")
if user_input:
    st.session_state.messages.append({"role": "user", "content": user_input})
    with st.chat_message("user"):
        st.markdown(user_input)

    # Determine response
    response = ""
    if user_input.lower() in ["what is aimerz?", "tell me about aimerz", "explain aimerz"]:
        response = aimerz_description
    elif user_input.lower() in ["who is the creator?", "who founded aimerz?", "who is the founder?"]:
        response = f"The founder of AIMERZ is **{creator_name}**. {creator_bio}"
    else:
        full_prompt = SYSTEM_PROMPT + "\nUser Query: " + user_input
        ai_response = model.generate_content(full_prompt)
        response = getattr(ai_response, "text", "Sorry, I couldn't generate a response.").strip()

    # Display bot response
    st.session_state.messages.append({"role": "assistant", "content": response})
    with st.chat_message("assistant"):
        st.markdown(response)

    # Store in database
    insert_data(user_input, response)

