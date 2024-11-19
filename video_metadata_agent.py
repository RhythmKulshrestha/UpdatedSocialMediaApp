import google.generativeai as genai
import json
from helpers.YouTubeOperations import YouTubeOperations
import os

class VideoMetadataAgent:

    def __init__(self, youtube_ops):
        """
        Initialize the VideoMetadataAgent with YouTube operations and Gemini API.
        
        :param youtube_ops: An instance of YouTubeOperations
        """
        self.youtube_ops = youtube_ops
        
        # Configure Gemini API 
        # Assuming you want to use a separate API key for Gemini
        
        gemini_api_key = os.getenv('GEMINI_API_KEY')  # Get Gemini API key from environment
        genai.configure(api_key=gemini_api_key)
        
        self.model = genai.GenerativeModel('gemini-pro')  # Or whatever model name you're using

    def fetch_all_video_metadata(self):
        """
        Fetch metadata for all videos in the user's channel.
        
        :return: List of dictionaries containing video metadata
        """
        try:
            # Fetch initial list of videos
            all_videos_metadata = []
            next_page_token = None
            
            while True:
                request = self.youtube_ops.youtube.search().list(
                    part="snippet",
                    forMine=True,
                    type="video",
                    maxResults=50,
                    pageToken=next_page_token
                )
                response = request.execute()
                
                # For each video, fetch detailed metadata
                for item in response.get('items', []):
                    video_id = item['id']['videoId']
                    # Fetch detailed video information
                    detailed_info = self.youtube_ops.read_video(video_id)
                    
                    if detailed_info and detailed_info.get('items'):
                        video_details = detailed_info['items'][0]
                        metadata = {
                            'video_id': video_id,
                            'title': item['snippet']['title'],
                            'description': item['snippet']['description'],
                            'published_at': item['snippet']['publishedAt'],
                            'view_count': video_details.get('statistics', {}).get('viewCount', 'N/A'),
                            'likes_count': video_details.get('statistics', {}).get('likeCount', 'N/A'),
                            'comment_count': video_details.get('statistics', {}).get('commentCount', 'N/A')
                        }
                        all_videos_metadata.append(metadata)
                
                # Check for next page
                next_page_token = response.get('nextPageToken')
                if not next_page_token:
                    break
            
            return all_videos_metadata
        
        except Exception as e:
            print(f"Error fetching video metadata: {e}")
            return []

    def query_video_metadata(self, query):
        """
        Use Gemini to query and analyze video metadata.
        
        :param query: Natural language query about video metadata
        :return: AI-generated response based on video metadata
        """
        try:
            # Fetch all video metadata
            videos_metadata = self.fetch_all_video_metadata()
            
            # Convert metadata to a JSON string for LLM processing
            metadata_json = json.dumps(videos_metadata, indent=2)
            
            # Create a comprehensive prompt
            prompt = f"""
            You are a YouTube video metadata analyst. 
            Here is the metadata for all videos in the channel:
            {metadata_json}

            User Query: {query}

            Please provide a detailed, insightful analysis based on the query. 
            If the query requires specific calculations or comparisons, perform them.
            If no relevant information is found, explain why.
            """
            
            # Generate response using Gemini
            response = self.model.generate_content(prompt)
            
            return response.text
        
        except Exception as e:
            return f"Error processing query: {e}"

def main():
    """
    Example usage of VideoMetadataAgent
    """
    # Initialize YouTube Operations
    yt_ops = YouTubeOperations()
    yt_ops.authenticate()
    
    # Create Metadata Agent
    metadata_agent = VideoMetadataAgent(yt_ops)
    
    # Example queries
    queries = [
        "What is the average number of views across all videos?",
        "Which video has the most likes?",
        "Provide insights on the publishing pattern of videos"
    ]
    
    for query in queries:
        print(f"\nQuery: {query}")
        result = metadata_agent.query_video_metadata(query)
        print(result)

if __name__ == "__main__":
    main()