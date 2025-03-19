import pymongo
from pymongo import MongoClient
import datetime
import os
from dotenv import load_dotenv
import streamlit as st

#load_dotenv()

# Get MongoDB credentials from Streamlit Secrets
#MONGO_URI = os.getenv('MONGO_URI')
#DB_NAME = os.getenv('DB_NAME')
#COLLECTION_NAME = os.getenv('COLLECTION_NAME')

# Get MongoDB credentials from Streamlit Secrets
MONGO_URI = st.secrets["MONGO_URI"]
DB_NAME = st.secrets["DB_NAME"]
COLLECTION_NAME = st.secrets["COLLECTION_NAME"]

client=MongoClient(MONGO_URI)
db=client[DB_NAME]
collection = db[COLLECTION_NAME]

def insert_data(user_input,response):
    chat = {
        "user_input" : user_input,
        "response" : response,
        "timestamp": datetime.datetime.now()
    }
    collection.insert_one(chat)