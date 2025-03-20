import pymongo
from pymongo import MongoClient
import datetime
import os
from dotenv import load_dotenv
import streamlit as st

load_dotenv()

MONGO_URI = os.getenv('MONGO_URI')
DB_NAME = os.getenv('DB_NAME')
COLLECTION_NAME = os.getenv('COLLECTION_NAME')

# Get MongoDB credentials from Streamlit Secrets
#MONGO_URI = st.secrets["MONGO_URI"]
#DB_NAME = st.secrets["DB_NAME"]
#COLLECTION_NAME = st.secrets["COLLECTION_NAME"]

client=MongoClient(MONGO_URI)
db=client[DB_NAME]
collection = db[COLLECTION_NAME]

def insert_data(user_input, response):
    """Insert a new chat message into the MongoDB collection."""
    chat = {
        "user_input": user_input,
        "response": response,
        "timestamp": datetime.datetime.now()
    }
    collection.insert_one(chat)

def get_chat_history(limit=10):
    """Retrieve the latest chat history from MongoDB."""
    return list(collection.find().sort("timestamp", -1).limit(limit))