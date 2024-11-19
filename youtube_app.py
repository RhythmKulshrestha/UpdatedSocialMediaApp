import streamlit as st
from helpers.YouTubeOperations import YouTubeOperations
import os
from video_metadata_agent import VideoMetadataAgent
import pandas as pd

def run(operation):
    yt = YouTubeOperations()
    # Authenticate only once, if not already authenticated
    if not yt.credentials or not yt.youtube:
        try:
            yt.authenticate()
            st.success("YouTube authenticated successfully!")
        except Exception as e:
            st.error(f"Failed to authenticate YouTube: {e}")
    
    # --- CREATE VIDEO ---
    if operation == "Create Video":
        st.header("Upload a New Video to YouTube")
        
        # Get user inputs for video creation
        title = st.text_input("Video Title", "")
        description = st.text_area("Video Description", "")
        privacy_status = st.selectbox("Privacy Status", ["public", "unlisted", "private"])
        
        # File uploader for video file
        video_file = st.file_uploader("Choose a video file", type=["mp4", "mov", "avi"])
        
        if st.button("Upload Video"):
            if video_file is not None:
                try:
                    # Save file temporarily and upload it
                    with open("temp_video.mp4", "wb") as f:
                        f.write(video_file.read())
                    
                    # Call the create_video method with the path to the temp file
                    response = yt.create_video(title, description, privacy_status, "temp_video.mp4")
                    
                    if response:
                        video_id = response['id']
                        st.success(f"Video uploaded successfully! Video ID: {video_id}")
                        st.markdown(f"[View Video on YouTube](https://www.youtube.com/watch?v={video_id})")
                except Exception as e:
                    st.error(f"Error uploading video: {e}")
                finally:
                    # Cleanup temporary file
                    os.remove("temp_video.mp4")
            else:
                st.warning("Please upload a video file before clicking 'Upload Video'")    

    # --- READ VIDEO ---
    elif operation == "Read Video":
        st.header("Get Video Details")
        
        # List user's recent videos to choose one to read details
        try:
            videos = yt.list_my_videos(max_results=5)
            video_options = {}
            
            if videos.get('items'):
                for item in videos['items']:
                    title = item['snippet']['title']
                    video_id = item['id']['videoId']
                    video_options[title] = video_id
                
                if video_options:
                    selected_title = st.selectbox("Choose a Video to Read", options=list(video_options.keys()))
                    video_id = video_options[selected_title]
                    
                    if st.button("Fetch Video Details"):
                        try:
                            video_info = yt.read_video(video_id)
                            
                            # Extract relevant details
                            if video_info and video_info.get('items'):
                                video_details = video_info['items'][0]
                                
                                # Prepare data for table display
                                details_data = {
                                    'Attribute': [
                                        'Title', 
                                        'Video ID', 
                                        'Published At', 
                                        'Channel Title', 
                                        'Category ID', 
                                        'Views', 
                                        'Likes', 
                                        'Comments',
                                        'Description'
                                    ],
                                    'Value': [
                                        video_details['snippet'].get('title', 'N/A'),
                                        video_details.get('id', 'N/A'),
                                        video_details['snippet'].get('publishedAt', 'N/A'),
                                        video_details['snippet'].get('channelTitle', 'N/A'),
                                        video_details['snippet'].get('categoryId', 'N/A'),
                                        video_details.get('statistics', {}).get('viewCount', 'N/A'),
                                        video_details.get('statistics', {}).get('likeCount', 'N/A'),
                                        video_details.get('statistics', {}).get('commentCount', 'N/A'),
                                        video_details['snippet'].get('description', 'N/A')
                                    ]
                                }
                                
                                # Create DataFrame
                                details_df = pd.DataFrame(details_data)
                                
                                # Display video details in a table format
                                st.subheader("Detailed Video Information")
                                st.dataframe(details_df, use_container_width=True)
                                
                                # Optional: Display full description separately if it's long
                                st.subheader("Full Description")
                                st.text_area("Video Description", 
                                            value=video_details['snippet'].get('description', 'No description'),
                                            height=200)
                            else:
                                st.warning("No detailed information found for this video.")
                        
                        except Exception as e:
                            st.error(f"Failed to fetch video details: {e}")
                else:
                    st.warning("No videos found in your channel.")
                
        except Exception as e:
            st.error(f"Failed to fetch videos: {e}")


    # --- UPDATE VIDEO ---
    elif operation == "Update Video":
        st.header("Update Video Details")
        
        # List user's recent videos to help choose one for updating
        try:
            videos = yt.list_my_videos(max_results=5)
            video_options = {}
            
            if videos.get('items'):
                for item in videos['items']:
                    title = item['snippet']['title']
                    video_id = item['id']['videoId']
                    video_options[title] = video_id
                
                if video_options:
                    selected_title = st.selectbox("Choose a Video to Update", options=list(video_options.keys()))
                    video_id = video_options[selected_title]
                    
                    # Get current video details to show in the form
                    current_video = yt.youtube.videos().list(
                        part="snippet",
                        id=video_id
                    ).execute()
                    
                    if current_video['items']:
                        current_snippet = current_video['items'][0]['snippet']
                        new_title = st.text_input("New Title", value=current_snippet['title'])
                        new_description = st.text_area("New Description", value=current_snippet['description'])
                        
                        if st.button("Update Video"):
                            try:
                                updated_video = yt.update_video(
                                    video_id=video_id,
                                    title=new_title,
                                    description=new_description
                                )
                                st.success("Video updated successfully!")
                                st.markdown(f"[View Updated Video on YouTube](https://www.youtube.com/watch?v={video_id})")
                            except Exception as e:
                                st.error(f"Failed to update video: {e}")
            else:
                st.warning("No videos found in your channel.")
                
        except Exception as e:
            st.error(f"Failed to fetch videos: {e}")

    # --- DELETE VIDEO ---
    elif operation == "Delete Video":
        st.header("Delete a Video")
        
        # List user's recent videos to help choose one for deletion
        try:
            videos = yt.list_my_videos(max_results=5)
            video_options = {}
            
            if videos.get('items'):
                for item in videos['items']:
                    title = item['snippet']['title']
                    video_id = item['id']['videoId']
                    video_options[title] = video_id
                
                if video_options:
                    selected_title = st.selectbox("Choose a Video to Delete", options=list(video_options.keys()))
                    video_id = video_options[selected_title]
                    
                    # Show video details before deletion
                    st.warning(f"You are about to delete: {selected_title}")
                    st.markdown(f"Video ID: `{video_id}`")
                    
                    confirm = st.checkbox("I understand that this action cannot be undone")
                    if st.button("Delete Video") and confirm:
                        try:
                            yt.delete_video(video_id)
                            st.success("Video deleted successfully!")
                            # Add a rerun button to refresh the video list
                            if st.button("Refresh Video List"):
                                st.experimental_rerun()
                        except Exception as e:
                            st.error(f"Failed to delete video: {e}")
                else:
                    st.warning("No videos found in your channel.")
            else:
                st.warning("No videos found in your channel.")
                
        except Exception as e:
            st.error(f"Failed to fetch videos: {e}")




    # --- METADATA ANALYSIS ---
    elif operation == "Metadata Analysis":
        st.header("YouTube Video Metadata Analysis")
        
        # Create Metadata Agent
        metadata_agent = VideoMetadataAgent(yt)
        
        # Metadata Analysis Options
        analysis_type = st.selectbox("Select Analysis Type", [
            "Fetch All Video Metadata", 
            "AI-Powered Metadata Insights"
        ])
        
        if analysis_type == "Fetch All Video Metadata":
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
        
        elif analysis_type == "AI-Powered Metadata Insights":
            # Natural Language Query Interface
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