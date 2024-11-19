import streamlit as st
import time
from helpers.instagram_api import InstagramAPI
from instagram_query_agent import InstagramQueryAgent
import json
import time
import google.generativeai as genai
from dotenv import load_dotenv
import os


def run(operation):
    
        # Load environment variables and configure Gemini
    load_dotenv()
    genai.configure(api_key=os.getenv('GEMINI_API_KEY'))


    st.markdown("""
<h1 style='
    background: linear-gradient(to right, #C13584, #F56040); 
    color: white; 
    padding: 20px; 
    border-radius: 10px; 
    text-align: center; 
    box-shadow: 0 4px 6px rgba(0,0,0,0.1);
    font-family: "Arial", sans-serif;
'>
    <span style='margin-right: 15px;'>📸</span>Instagram Post Manager 
    <span style='margin-left: 15px;'>✨</span>
</h1>
""", unsafe_allow_html=True)
    st.divider()

    # Initialize InstagramAPI instance
    try:
        api = InstagramAPI()
        query_agent = InstagramQueryAgent(api)
        st.success("Initialized Instagram API and Query Agent successfully.")
    except Exception as e:
        st.error(f"Failed to initialize APIs: {e}")

    

    # Check if Instagram API was successfully initialized before proceeding
    if api and api.access_token:
        
            # --- GET ACCOUNT INFO ---
        if operation == "Get Account Info":
            st.header("Instagram Account Information")
            
            try:
                account_info = api.get_account_info()
                
                # Create two columns for layout
                col1, col2 = st.columns([2, 1])
                
                with col1:
                    # Profile Information Table
                    st.subheader("📊 Profile Statistics")
                    metrics_data = {
                        "Metric": ["Username", "Followers", "Total Posts", "Account Type"],
                        "Value": [
                            account_info.get("username", "N/A"),
                            f"{account_info.get('followers_count', 0):,}",
                            f"{account_info.get('media_count', 0):,}",
                            "Business Account"
                        ]
                    }
                    st.table(metrics_data)
                    
                    # Engagement Metrics
                    st.subheader("📈 Account Metrics")
                    col_a, col_b, col_c = st.columns(3)
                    
                    with col_a:
                        st.metric(
                            "Followers",
                            f"{account_info.get('followers_count', 0):,}",
                            delta=None
                        )
                    
                    with col_b:
                        st.metric(
                            "Total Posts",
                            f"{account_info.get('media_count', 0):,}",
                            delta=None
                        )
                    
                    with col_c:
                        # Calculate average engagement if available
                        if account_info.get('followers_count') and account_info.get('media_count'):
                            avg_engagement = round(account_info.get('followers_count') / account_info.get('media_count'), 2)
                            st.metric(
                                "Followers/Post",
                                f"{avg_engagement:,}",
                                delta=None
                            )
                    
                    # Raw JSON data (collapsible)
                    with st.expander("View Raw Account Data"):
                        st.json(account_info)
                
                with col2:
                    # Profile Picture Display
                    st.subheader("📷 Profile Picture")
                    if "profile_picture_url" in account_info:
                        st.image(
                            account_info["profile_picture_url"],
                            caption=account_info.get("username", "Instagram Profile"),
                            use_column_width=True
                        )
                    else:
                        st.info("No profile picture available")
                    
                    # Quick Actions
                    st.subheader("⚡ Quick Actions")
                    if st.button("Refresh Data"):
                        st.rerun()
                    
                    if st.button("Download Account Info"):
                        # Convert account info to JSON string
                        json_str = json.dumps(account_info, indent=2)
                        # Create download button
                        st.download_button(
                            label="Download JSON",
                            data=json_str,
                            file_name="instagram_account_info.json",
                            mime="application/json"
                        )
            
            except Exception as e:
                st.error(f"Error fetching account information: {e}")
                st.info("Please check your API credentials and try again.")



        
        # --- PUBLISH POST ---
        elif operation == "Publish Post":
            st.header("Create and Publish an Instagram Post")
            
            # Input for the image URL and caption
            image_url = st.text_input("Image URL", "")
            caption = st.text_area("Caption", "")
            
            if st.button("Publish Post"):
                try:
                    # Step 1: Create a media container and get the creation ID
                    result = api.create_post(image_url, caption)
                    
                    if result and 'id' in result:
                        media_id = result['id']
                        st.success(f"Post created successfully! Media ID: {media_id}")
                        
                        # Step 2: Retrieve the media details to get the permalink
                        time.sleep(5)
                        media_details = api._make_request('GET', media_id, params={'fields': 'permalink'})
                        
                        if media_details and "permalink" in media_details:
                            post_url = media_details["permalink"]
                            st.markdown(f"[View New Post on Instagram]({post_url})", unsafe_allow_html=True)
                        else:
                            st.error("Failed to retrieve the permalink for the new post.")
                    else:
                        st.error("Failed to create post. Please check the image URL and your permissions.")
                except Exception as e:
                    st.error(f"Error publishing post: {e}")
        
        # --- GET MEDIA LIST ---
        elif operation == "Get Media List":
            st.header("Recent Instagram Media Posts")
            
            # Input for the number of media items to fetch
            limit = st.number_input("Number of media posts to display", min_value=1, max_value=25, value=5)
            
            if st.button("Get Media List"):
                try:
                    media_list = api.get_media_list(limit=limit)
                    if "data" in media_list:
                        for media in media_list["data"]:
                            st.subheader(f"Post ID: {media['id']}")
                            st.write(f"Caption: {media.get('caption', 'No caption')}")
                            st.write(f"Media Type: {media.get('media_type')}")
                            st.write(f"Posted on: {media.get('timestamp')}")
                            
                            # Display image if it's a photo or a thumbnail for videos
                            if media.get("media_type") in ["IMAGE", "CAROUSEL_ALBUM"]:
                                st.image(media["media_url"], use_column_width=True)
                            elif media.get("media_type") == "VIDEO":
                                if "thumbnail_url" in media:
                                    st.image(media["thumbnail_url"], caption="Video Thumbnail", use_column_width=True)
                            
                            st.markdown(f"[View on Instagram]({media['permalink']})", unsafe_allow_html=True)
                            st.write("---")
                    else:
                        st.error("No media found or an error occurred.")
                except Exception as e:
                    st.error(f"Error fetching media list: {e}")

        # --- POST ANALYSIS ---
        elif operation == "Post Analysis":
            st.header("🔍 Post Analysis with AI")
            
            # Input for analysis
            user_query = st.text_area(
                "What would you like to know about your posts?",
                placeholder="E.g., What are the main themes in my recent posts?"
            )
            
            # Number of posts to analyze
            limit = st.slider(
                "Number of Recent Posts to Analyze", 
                min_value=5, 
                max_value=25, 
                value=10
            )
            
            if st.button("Analyze Posts"):
                if not user_query:
                    st.warning("Please enter a query")
                    
                    
                try:
                    with st.spinner("Analyzing your posts..."):
                        result = query_agent.query_instagram_posts(
                            query=user_query,
                            limit=limit
                        )
                    st.subheader("Analysis Results")
                    st.markdown(result)
                except Exception as e:
                    st.error(f"Error analyzing posts: {e}")

        # --- ACCOUNT ANALYSIS ---
        elif operation == "Account Analysis":
            st.header("📊 Account Analysis with AI")
            
            user_query = st.text_area(
                "What insights would you like about your account?",
                placeholder="E.g., What is my content strategy pattern?"
            )
            
            # Number of posts to consider
            limit = st.slider(
                "Posts to Consider for Analysis", 
                min_value=5, 
                max_value=25, 
                value=10
            )
            
            if st.button("Analyze Account"):
                if not user_query:
                    st.warning("Please enter a query")
                    
                    
                try:
                    with st.spinner("Analyzing your account..."):
                        result = query_agent.analyze_account_posts(
                            query=user_query,
                            limit=limit
                        )
                    st.subheader("Analysis Results")
                    st.markdown(result)
                except Exception as e:
                    st.error(f"Error analyzing account: {e}")

    else:
        st.warning("Instagram API not initialized. Check your credentials and .env file.")

    # Sidebar account info (shown for all operations)
    if api and api.access_token:
        st.sidebar.header("Account Information")
        try:
            account_info = api.get_account_info()
            st.sidebar.metric("Username", account_info.get('username', 'N/A'))
            st.sidebar.metric("Followers", account_info.get('followers_count', 'N/A'))
            st.sidebar.metric("Total Posts", account_info.get('media_count', 'N/A'))
        except Exception as e:
            st.sidebar.error("Unable to fetch account info")