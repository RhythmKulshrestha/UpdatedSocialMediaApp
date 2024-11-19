import os
import json
import google.generativeai as genai
from typing import List, Dict
from helpers.instagram_api import InstagramAPI
from dotenv import load_dotenv

class InstagramQueryAgent:
    def __init__(self, instagram_api: InstagramAPI):
        """
        Initialize the query agent with Instagram API and Gemini API
        
        Args:
            instagram_api: Initialized InstagramAPI instance
        """
        # Load environment variables
        load_dotenv()
        
        # Configure Gemini API
        genai.configure(api_key=os.getenv('GEMINI_API_KEY'))
        
        # Initialize models and managers
        self.instagram_api = instagram_api
        self.llm_model = genai.GenerativeModel('gemini-pro')
        
        # Logging setup
        import logging
        logging.basicConfig(level=logging.INFO)
        self.logger = logging.getLogger(__name__)

    def query_instagram_posts(self, query: str, limit: int = 25) -> str:
        """
        Fetch recent posts and use Gemini to answer specific queries
        
        Args:
            query: User's specific query about the posts
            limit: Number of posts to fetch
        
        Returns:
            AI-generated response based on post data
        """
        try:
            # Fetch posts from Instagram
            media_list = self.instagram_api.get_media_list(limit=limit)
            
            if not media_list or 'data' not in media_list:
                return "No posts found."
            
            # Prepare post data for AI query
            posts_text = "\n\n".join([
                f"Post ID: {post.get('id', 'N/A')}\n"
                f"Media Type: {post.get('media_type', 'N/A')}\n"
                f"Caption: {post.get('caption', 'No caption')}\n"
                f"Permalink: {post.get('permalink', 'N/A')}\n"
                f"Timestamp: {post.get('timestamp', 'N/A')}"
                for post in media_list.get('data', [])
            ])
            
            # Construct prompt for Gemini
            full_prompt = (
                "You are an AI assistant analyzing Instagram posts. "
                f"Here are the recent posts:\n\n{posts_text}\n\n"
                f"User Query: {query}\n\n"
                "Provide a comprehensive and insightful response based on the post data."
            )
            
            # Generate response using Gemini
            response = self.llm_model.generate_content(full_prompt)
            
            return response.text
        
        except Exception as e:
            self.logger.error(f"Error in Instagram post query: {str(e)}")
            return f"An error occurred: {str(e)}"

    def analyze_account_posts(self, query: str, limit: int = 25) -> str:
        """
        Analyze the Instagram account's posts using Gemini
        
        Args:
            query: Specific analysis request
            limit: Number of recent posts to analyze
        
        Returns:
            AI-generated analysis of account's posts
        """
        try:
            # Fetch account info
            account_info = self.instagram_api.get_account_info()
            
            # Fetch recent posts
            media_list = self.instagram_api.get_media_list(limit=limit)
            
            if not media_list or 'data' not in media_list:
                return "No posts found."
            
            # Prepare account and posts data for AI analysis
            account_text = (
                f"Account Username: {account_info.get('username', 'N/A')}\n"
                f"Followers Count: {account_info.get('followers_count', 'N/A')}\n"
                f"Total Media Count: {account_info.get('media_count', 'N/A')}"
            )
            
            posts_text = "\n\n".join([
                f"Media Type: {post.get('media_type', 'N/A')}\n"
                f"Caption: {post.get('caption', 'No caption')}"
                for post in media_list.get('data', [])
            ])
            
            # Construct prompt for Gemini
            full_prompt = (
                "You are an AI assistant analyzing an Instagram account's posts. "
                f"Account Details:\n{account_text}\n\n"
                f"Recent Posts:\n{posts_text}\n\n"
                f"User Query: {query}\n\n"
                "Provide a detailed and insightful analysis."
            )
            
            # Generate response using Gemini
            response = self.llm_model.generate_content(full_prompt)
            
            return response.text
        
        except Exception as e:
            self.logger.error(f"Error in account posts analysis: {str(e)}")
            return f"An error occurred: {str(e)}"

# Example usage
if __name__ == "__main__":
    # Initialize Instagram API
    instagram_api = InstagramAPI()
    
    # Create Query Agent
    query_agent = InstagramQueryAgent(instagram_api)
    
    # Example Queries
    posts_analysis = query_agent.query_instagram_posts(
        query="What are the main themes of my recent posts?"
    )
    print("Posts Analysis:", posts_analysis)
    
    account_analysis = query_agent.analyze_account_posts(
        query="Provide insights into my account's content strategy"
    )
    print("Account Analysis:", account_analysis)