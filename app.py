import streamlit as st
import google.generativeai as genai
from database import insert_data
#from database import get_chat_history
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
aimerz_employees = load_json("aimerz_employees.json")

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
- If the user asks about **AIMERZ employees**, provide details from the following data:  
  {json.dumps(aimerz_employees, indent=2)}  
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
#st.sidebar.title("📜 Chat History")
#chat_history = get_chat_history()

#if chat_history:
#    for i, chat in enumerate(chat_history):
#        if "user_input" in chat:
#            if st.sidebar.button(chat["user_input"][:40], key=f"chat_{i}"):
#                st.session_state.messages.extend([
#                    {"role": "user", "content": chat["user_input"]},
#                    {"role": "assistant", "content": chat["response"]}
#                ])
#else:
#    st.sidebar.write("No chat history yet!")

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

    # Construct chat history for context (last 5 messages)
    chat_history = "\n".join([f"{msg['role'].capitalize()}: {msg['content']}" for msg in st.session_state.messages[-5:]])

    # Generate AI response with context
    full_prompt = f"{SYSTEM_PROMPT}\n\nChat History:\n{chat_history}\n\nUser: {user_input}"
    ai_response = model.generate_content(full_prompt)

    # Extract response safely
    response = ai_response.candidates[0].content.parts[0].text if ai_response.candidates else "Sorry, I couldn't generate a response."

    # Store and display response
    st.session_state.messages.append({"role": "assistant", "content": response})
    with st.chat_message("assistant"):
        st.markdown(response)

    # Store in database
    insert_data(user_input, response)


