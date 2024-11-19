import streamlit as st
import reddit_app
import youtube_app
import facebook_app
import instagram_app
import twitter_app

# Sidebar for selecting platform and CRUD operation
st.sidebar.title("Social Media Platform Manager")
platform = st.sidebar.selectbox(
    "Select Social Media Platform", 
    ["Reddit", "YouTube", "Facebook", "Instagram", "Twitter"]
)

# Define CRUD operations based on platform
if platform == "Reddit":
    operation = st.sidebar.selectbox("Select Operation", ["Create Post", "Read Post", "Update Post", "Delete Post", "Metadata Analysis"])
    reddit_app.run(operation)
    
elif platform == "YouTube":
    operation = st.sidebar.selectbox("Select Operation", ["Create Video", "Read Video", "Update Video", "Delete Video", "Metadata Analysis"])
    youtube_app.run(operation)
    
elif platform == "Facebook":
    operation = st.sidebar.selectbox("Select Operation", ["Create Post", "Read Post", "Update Post", "Delete Post"])
    facebook_app.run(operation)

elif platform == "Instagram":
    operation = st.sidebar.selectbox("Select Operation", ["Get Account Info", "Publish Post", "Get Media List","Post Analysis", "Account Analysis"])
    instagram_app.run(operation)

elif platform == "Twitter":
    operation = st.sidebar.selectbox("Select Operation", ["Create Tweet", "Read Tweet", "Get Recent Tweets", "Delete Tweet"])
    twitter_app.run(operation)
