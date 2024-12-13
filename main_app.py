import streamlit as st
import reddit_app
import youtube_app
import facebook_app
import instagram_app
import twitter_app

# Set page configuration
st.set_page_config(
    page_title="Automated Socials", 
    page_icon="🌐", 
    layout="wide"
)

# Custom Sidebar Styling
st.markdown("""
    <style>
    .sidebar .sidebar-content {
        background-color: #f0f2f6;
    }
    </style>
""", unsafe_allow_html=True)

# Sidebar for selecting platform and CRUD operation
st.sidebar.title("🌐 Automated Socials")

# Sidebar platform selection with icons
platform = st.sidebar.radio(
    "Select Platform", 
    [   "👾 Reddit",
        "📺 YouTube", 
        "👥 Facebook",
        "📱 Instagram", 
        "🐦 Twitter"
    ],
    index=0  # Default to Instagram
)

# Strip icon from platform selection
platform = platform.split(" ", 1)[1]

if platform == "Reddit":
    operation = st.sidebar.selectbox(
        "Select Operation", 
        [
            "Create Post", 
            "Read Post", 
            "Update Post", 
            "Delete Post", 
            "Metadata Analysis",
            "Generate AI Post"
        ]
    )
    reddit_app.run(operation)

elif platform == "YouTube":
    operation = st.sidebar.selectbox(
        "Select Operation", 
        [
            "Create Video", 
            "Read Video", 
            "Update Video", 
            "Delete Video", 
            "Metadata Analysis"
        ]
    )
    youtube_app.run(operation)
    
elif platform == "Facebook":
    operation = st.sidebar.selectbox(
        "Select Operation", 
        [
            "Create Post", 
            "Read Post", 
            "Update Post", 
            "Delete Post"
        ]
    )
    facebook_app.run(operation)


elif platform == "Instagram":
    operation = st.sidebar.selectbox(
        "Select Operation", 
        [
            "Get Account Info", 
            "Publish Post", 
            "Get Media List", 
            "Post Analysis", 
            "Account Analysis"
        ]
    )
    instagram_app.run(operation)
    
elif platform == "Twitter":
    operation = st.sidebar.selectbox(
        "Select Operation", 
        [
            "Create Tweet", 
            "Read Tweet", 
            "Get Recent Tweets", 
            "Delete Tweet"
        ]
    )
    twitter_app.run(operation)


# Footer
st.sidebar.markdown("---")
st.sidebar.info("🚀 Manage your social media platforms efficiently!")