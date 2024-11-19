import streamlit as st
from helpers.YouTubeOperations import YouTubeOperations
from video_metadata_agent import VideoMetadataAgent
import pandas as pd
import os

def initialize_youtube_client():
    # Check if YouTube client is already authenticated in session state
    if 'youtube_ops' not in st.session_state:
        yt_ops = YouTubeOperations()
        yt_ops.authenticate()  # Authenticate automatically
        st.session_state.youtube_ops = yt_ops
    
    return st.session_state.youtube_ops

def main():
    st.title("YouTube Video Metadata Analyzer 📊")
    
    # Automatically initialize and authenticate YouTube client
    try:
        youtube_ops = initialize_youtube_client()
        st.sidebar.success("YouTube authenticated successfully!")
    except Exception as e:
        st.sidebar.error(f"Authentication failed: {e}")
        return
    
    # Create Metadata Agent with the YouTube operations
    metadata_agent = VideoMetadataAgent(youtube_ops)
    
    # Main content area
    st.header("Video Metadata Exploration")
    
    # Fetch and display video metadata
    if st.button("Fetch Video Metadata"):
        try:
            # Fetch video metadata
            videos_metadata = metadata_agent.fetch_all_video_metadata()
            
            # Convert to DataFrame for better display
            df = pd.DataFrame(videos_metadata)
            
            # Display metadata
            st.subheader("Videos Metadata")
            st.dataframe(df)
            
            # Basic statistics
            st.subheader("Quick Statistics")
            col1, col2, col3 = st.columns(3)
            
            with col1:
                st.metric("Total Videos", len(df))
            
            with col2:
                try:
                    avg_views = df['view_count'].astype(float).mean()
                    st.metric("Avg Views", f"{avg_views:,.0f}")
                except:
                    st.metric("Avg Views", "N/A")
            
            with col3:
                try:
                    max_views = df['view_count'].astype(float).max()
                    st.metric("Max Views", f"{max_views:,.0f}")
                except:
                    st.metric("Max Views", "N/A")
        
        except Exception as e:
            st.error(f"Error fetching metadata: {e}")
    
    # Natural Language Query Interface
    st.header("Metadata Query Assistant")
    
    query = st.text_input("Ask a question about your YouTube videos:", 
                           placeholder="What insights can you provide about my videos?")
    
    if st.button("Get Insights"):
        if query:
            try:
                # Generate insights using Gemini
                insights = metadata_agent.query_video_metadata(query)
                
                # Display insights
                st.subheader("AI-Generated Insights")
                st.write(insights)
            
            except Exception as e:
                st.error(f"Error generating insights: {e}")
        else:
            st.warning("Please enter a query about your video metadata.")

if __name__ == "__main__":
    main()