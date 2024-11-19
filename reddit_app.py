import streamlit as st
from helpers.reddit_manager import RedditManager
from reddit_query_agent import RedditQueryAgent
import pandas as pd

def run(operation):

        
    st.markdown("""
    <h1 style='
        background: linear-gradient(to right, #FF4500, #FF6347); 
        color: white; 
        padding: 20px; 
        border-radius: 10px; 
        text-align: center; 
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
        font-family: "Arial", sans-serif;
    '>
        <span style='margin-right: 15px;'>📝</span>Reddit Post Manager 
        <span style='margin-left: 15px;'>🚀</span>
    </h1>
    """, unsafe_allow_html=True)
    st.divider()

    # Custom CSS for enhanced styling
    st.markdown("""
    <style>
    .stApp {
        background-color: #f4f4f8;
    }
    .stButton>button {
        color: white;
        background-color: #FF4500;  /* Reddit Orange-Red */
        border-radius: 10px;
    }
    .stMetric {
        background-color: white;
        padding: 10px;
        border-radius: 10px;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
    }
    </style>
    """, unsafe_allow_html=True)

    reddit_manager = RedditManager()

    # Initialize Reddit client if not already initialized
    if 'reddit_manager' not in st.session_state:
        try:
            st.session_state.reddit_manager = reddit_manager
            st.session_state.query_agent = RedditQueryAgent(reddit_manager)
            st.success("🎉 Reddit authenticated successfully!")
        except Exception as e:
            st.error(f"🚫 Failed to authenticate Reddit: {e}")

    # Function to fetch and display recent posts in a dropdown
    def get_recent_posts_dropdown():
        # Fetch recent posts (limit can be adjusted as needed)
        recent_posts = reddit_manager.get_recent_posts(limit=10)  # Ensure get_recent_posts is defined in RedditManager
        if recent_posts:
            post_titles = {post['title']: post['id'] for post in recent_posts}
            selected_title = st.selectbox("🔍 Select a Post", list(post_titles.keys()))
            selected_post_id = post_titles[selected_title]
            return selected_post_id
        else:
            st.warning("🚨 No recent posts found.")
            return None

    if operation == "Create Post":
        st.header("📝 Create a New Reddit Post")

        # Get user inputs for post creation
        subreddit_name = st.text_input("🌐 Subreddit Name (without 'r/')", "")
        title = st.text_input("📋 Post Title", "")
        content = st.text_area("📄 Post Content", "")
        post_type = st.selectbox("🔖 Post Type", ["text", "link", "image"])

        if st.button("🚀 Create Post"):
            post_id = reddit_manager.create_post(subreddit_name, title, content, post_type)
            if post_id:
                st.success(f"✅ Post created successfully! Post ID: {post_id}")
                post_url = f"https://www.reddit.com/r/{subreddit_name}/comments/{post_id}/"
                st.markdown(f"[🌐 View Post on Reddit]({post_url})", unsafe_allow_html=True)
            else:
                st.error("❌ Failed to create the post.")


    elif operation == "Read Post":
        st.header("📖 Read a Reddit Post")
        
        # Display dropdown for recent posts
        post_id = get_recent_posts_dropdown()
        
        if post_id and st.button("🔎 Fetch Post"):
            post_data = reddit_manager.read_post(post_id)
            
            if post_data:
                st.write("📄 Post Details:")
                
                # Check if post_data is a dictionary
                if isinstance(post_data, dict):
                    # Convert dictionary to DataFrame for better display
                    df = pd.DataFrame.from_dict(post_data, orient='index', columns=['Value'])
                    df.index.name = 'Attribute'
                    
                    # Display the DataFrame as a table
                    st.table(df)
                
                # If it's already a DataFrame, display directly
                elif isinstance(post_data, pd.DataFrame):
                    st.dataframe(post_data)
                
                # For other types, fall back to write
                else:
                    st.write(post_data)
            
            else:
                st.error("❌ Failed to fetch the post.")

    elif operation == "Update Post":
        st.header("♻️ Update an Existing Reddit Post")

        # Display dropdown for recent posts
        post_id = get_recent_posts_dropdown()
        new_content = st.text_area("📝 New Content", "")
        
        if post_id and st.button("🔄 Update Post"):
            update_success = reddit_manager.update_post(post_id, new_content)
            if update_success:
                st.success("✅ Post updated successfully!")
                # Display the link to view the updated post
                post_data = reddit_manager.read_post(post_id)
                subreddit_name = post_data.get('subreddit', 'unknown')  # Ensure subreddit name is retrieved correctly
                post_url = f"https://www.reddit.com/r/{subreddit_name}/comments/{post_id}/"
                st.markdown(f"[🌐 View Updated Post on Reddit]({post_url})", unsafe_allow_html=True)
            else:
                st.error("❌ Failed to update the post.")

    elif operation == "Delete Post":
        st.header("🗑️ Delete a Reddit Post")

        # Display dropdown for recent posts
        post_id = get_recent_posts_dropdown()
        
        if post_id and st.button("❌ Delete Post"):
            delete_success = reddit_manager.delete_post(post_id)
            if delete_success:
                st.success("✅ Post deleted successfully!")
                # Inform the user that the post is deleted and cannot be viewed
                st.info("🚫 Note: The post has been deleted, so it is no longer available on Reddit.")
            else:
                st.error("❌ Failed to delete the post.")

    # --- METADATA ANALYSIS ---
    elif operation == "Metadata Analysis":
        st.header("📊 Reddit Post Metadata Analysis")
        
        # Metadata Analysis Options
        analysis_type = st.selectbox("🔍 Select Analysis Type", [
            "Fetch Subreddit Posts",
            "AI-Powered Metadata Insights"
        ])
        
        if analysis_type == "Fetch Subreddit Posts":
            subreddit_name = st.text_input("🌐 Enter Subreddit Name", placeholder="technology")
            fetch_limit = st.slider("🔢 Number of Posts to Fetch", 10, 200, 50)
            
            if st.button("🔎 Fetch Posts"):
                try:
                    posts_metadata = st.session_state.reddit_manager.get_all_posts(
                        subreddit_name, limit=fetch_limit
                    )
                    
                    # Convert to DataFrame
                    df = pd.DataFrame(posts_metadata)
                    
                    # Display metadata
                    st.subheader("📋 Posts Metadata")
                    st.dataframe(df)
                    
                    # Basic statistics
                    st.subheader("📈 Quick Statistics")
                    col1, col2, col3 = st.columns(3)
                    
                    with col1:
                        st.metric("📊 Total Posts", len(df))
                    with col2:
                        avg_score = df['score'].mean()
                        st.metric("⭐ Avg Score", f"{avg_score:.1f}")
                    with col3:
                        total_comments = df['num_comments'].sum()
                        st.metric("💬 Total Comments", f"{total_comments:,}")
                
                except Exception as e:
                    st.error(f"❌ Error fetching posts: {e}")
        
        elif analysis_type == "AI-Powered Metadata Insights":
            subreddit_name = st.text_input("🌐 Enter Subreddit Name", placeholder="technology")
            query = st.text_input(
                "❓ Ask a question about the posts:",
                placeholder="What insights can you provide?"
            )
            
            if st.button("🤖 Get Insights"):
                if query and subreddit_name:
                    try:
                        insights = st.session_state.query_agent.query_subreddit_posts(
                            subreddit_name=subreddit_name,
                            query=query,
                            limit=50
                        )
                        st.subheader("🧠 AI-Generated Insights")
                        st.write(insights)
                    except Exception as e:
                        st.error(f"❌ Error generating insights: {e}")
                else:
                    st.warning("⚠️ Please enter both a subreddit name and a query.")

# Add main function to run the Streamlit app
def main():
    st.sidebar.title("🤖 Reddit Analytics")
    
    # Sidebar navigation
    operation = st.sidebar.radio(
        "Choose an Operation", 
        [
            "Create Post", 
            "Read Post", 
            "Update Post", 
            "Delete Post", 
            "Metadata Analysis"
        ],
        icons=[
            "📝", 
            "📖", 
            "♻️", 
            "🗑️", 
            "📊"
        ]
    )

    # Add a brief description or welcome message
    st.sidebar.markdown("""
    ### 🌐 Welcome to Reddit Analytics
    Manage and analyze your Reddit posts 
    with powerful tools and AI insights.
    """)

    # Run the selected operation
    run(operation)

    # Footer
    st.sidebar.markdown("---")
    st.sidebar.markdown("💡 Powered by Reddit & AI")

# Ensure the script can be run directly
if __name__ == "__main__":
    main()