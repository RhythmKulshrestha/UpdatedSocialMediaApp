import os
import google.generativeai as genai
from typing import List, Dict
from helpers.reddit_manager import RedditManager
from dotenv import load_dotenv

class RedditQueryAgent:
    def __init__(self, reddit_manager: RedditManager):
        """
        Initialize the query agent with Reddit manager and Gemini API
        
        Args:
            reddit_manager: Initialized RedditManager instance
        """
        # Load environment variables
        load_dotenv()
        
        # Configure Gemini API
        genai.configure(api_key=os.getenv('GEMINI_API_KEY'))
        
        # Initialize models and managers
        self.reddit_manager = reddit_manager
        self.llm_model = genai.GenerativeModel('gemini-pro')
        
        # Logging setup
        import logging
        logging.basicConfig(level=logging.INFO)
        self.logger = logging.getLogger(__name__)

    def query_subreddit_posts(self, subreddit_name: str, query: str, limit: int = 100) -> str:
        """
        Fetch posts from a subreddit and use Gemini to answer specific queries
        
        Args:
            subreddit_name: Name of the subreddit to query
            query: User's specific query about the posts
            limit: Number of posts to fetch
        
        Returns:
            AI-generated response based on post data
        """
        try:
            # Fetch posts from the subreddit
            posts = self.reddit_manager.get_all_posts(subreddit_name, limit)
            
            if not posts:
                return "No posts found in the specified subreddit."
            
            # Prepare post data for AI query
            posts_text = "\n\n".join([
                f"Title: {post['title']}\n"
                f"Content: {post['content']}\n"
                f"Author: {post['author']}\n"
                f"Score: {post['score']}\n"
                f"Comments: {post['num_comments']}\n"
                f"Created: {post['created_utc']}"
                for post in posts
            ])
            
            # Construct prompt for Gemini
            full_prompt = (
                f"You are an AI assistant analyzing Reddit posts from r/{subreddit_name}. "
                f"Here are the recent posts:\n\n{posts_text}\n\n"
                f"User Query: {query}\n\n"
                "Provide a comprehensive and insightful response based on the post data."
            )
            
            # Generate response using Gemini
            response = self.llm_model.generate_content(full_prompt)
            
            return response.text
        
        except Exception as e:
            self.logger.error(f"Error in subreddit query: {str(e)}")
            return f"An error occurred: {str(e)}"

    def analyze_user_feed(self, query: str, limit: int = 10) -> str:
        """
        Analyze the authenticated user's recent posts using Gemini
        
        Args:
            query: Specific analysis request
            limit: Number of recent posts to analyze
        
        Returns:
            AI-generated analysis of user's posts
        """
        try:
            # Fetch user's recent posts
            recent_posts = self.reddit_manager.get_recent_posts(limit)
            
            if not recent_posts:
                return "No recent posts found for the user."
            
            # Prepare post data for AI analysis
            posts_text = "\n\n".join([
                f"Post Title: {post['title']}"
                for post in recent_posts
            ])
            
            # Construct prompt for Gemini
            full_prompt = (
                "You are an AI assistant analyzing a user's recent Reddit posts. "
                f"Recent post titles:\n{posts_text}\n\n"
                f"User Query: {query}\n\n"
                "Provide a detailed and insightful analysis."
            )
            
            # Generate response using Gemini
            response = self.llm_model.generate_content(full_prompt)
            
            return response.text
        
        except Exception as e:
            self.logger.error(f"Error in user feed analysis: {str(e)}")
            return f"An error occurred: {str(e)}"

# Example usage
if __name__ == "__main__":
    # Initialize Reddit Manager
    reddit_manager = RedditManager()
    
    # Create Query Agent
    query_agent = RedditQueryAgent(reddit_manager)
    
    # Example Queries
    subreddit_analysis = query_agent.query_subreddit_posts(
        subreddit_name="technology", 
        query="What are the most discussed tech trends this week?"
    )
    print("Subreddit Analysis:", subreddit_analysis)
    
    user_feed_analysis = query_agent.analyze_user_feed(
        query="Summarize the themes of my recent posts"
    )
    print("User Feed Analysis:", user_feed_analysis)