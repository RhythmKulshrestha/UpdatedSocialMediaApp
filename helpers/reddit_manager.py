import praw
import logging
from typing import Optional, List
from datetime import datetime
from dotenv import load_dotenv
import os

# Load environment variables
load_dotenv()

class RedditManager:
    def __init__(self):
        """
        Initialize Reddit API client using environment variables
        """
        # Load credentials from .env file
        self.client_id = os.getenv('REDDIT_CLIENT_ID')
        self.client_secret = os.getenv('REDDIT_CLIENT_SECRET')
        self.username = os.getenv('REDDIT_USERNAME')
        self.password = os.getenv('REDDIT_PASSWORD')
        self.user_agent = os.getenv('REDDIT_USER_AGENT')

        # Validate that all required environment variables are present
        required_vars = ['REDDIT_CLIENT_ID', 'REDDIT_CLIENT_SECRET', 'REDDIT_USERNAME', 'REDDIT_PASSWORD', 'REDDIT_USER_AGENT']
        missing_vars = [var for var in required_vars if not os.getenv(var)]
        
        if missing_vars:
            raise ValueError(f"Missing required environment variables: {', '.join(missing_vars)}")

        # Initialize Reddit instance
        self.reddit = praw.Reddit(
            client_id=self.client_id,
            client_secret=self.client_secret,
            user_agent=self.user_agent,
            username=self.username,
            password=self.password
        )
        
        # Set up logging
        logging.basicConfig(level=logging.INFO)
        self.logger = logging.getLogger(__name__)
        self.logger.info("Reddit Manager initialized successfully")

    def create_post(self, subreddit_name: str, title: str, content: str, post_type: str = 'text') -> Optional[str]:
        """
        Create a new Reddit post
        
        Args:
            subreddit_name: Name of the subreddit without 'r/'
            title: Title of the post
            content: Content of the post
            post_type: Type of post ('text', 'link', 'image')
            
        Returns:
            Post ID if successful, None if failed
        """
        try:
            subreddit = self.reddit.subreddit(subreddit_name)
            
            if post_type == 'text':
                post = subreddit.submit(title=title, selftext=content)
            elif post_type == 'link':
                post = subreddit.submit(title=title, url=content)
            elif post_type == 'image':
                post = subreddit.submit_image(title=title, image_path=content)
            else:
                raise ValueError("Invalid post type. Must be 'text', 'link', or 'image'")
                
            self.logger.info(f"Created post: {post.id}")
            return post.id
            
        except Exception as e:
            self.logger.error(f"Error creating post: {str(e)}")
            return None

    def read_post(self, post_id: str) -> Optional[dict]:
        """
        Read a Reddit post by ID
        
        Args:
            post_id: Reddit post ID
            
        Returns:
            Dictionary containing post information
        """
        try:
            post = self.reddit.submission(id=post_id)
            post_data = {
                'id': post.id,
                'title': post.title,
                'content': post.selftext,
                'score': post.score,
                'url': post.url,
                'created_utc': datetime.fromtimestamp(post.created_utc),
                'author': str(post.author),
                'num_comments': post.num_comments
            }
            return post_data
            
        except Exception as e:
            self.logger.error(f"Error reading post: {str(e)}")
            return None

    def update_post(self, post_id: str, new_content: str) -> bool:
        """
        Update a Reddit post's content
        
        Args:
            post_id: Reddit post ID
            new_content: New content for the post
            
        Returns:
            True if successful, False otherwise
        """
        try:
            post = self.reddit.submission(id=post_id)
            post.edit(new_content)
            self.logger.info(f"Updated post: {post_id}")
            return True
            
        except Exception as e:
            self.logger.error(f"Error updating post: {str(e)}")
            return False

    def delete_post(self, post_id: str) -> bool:
        """
        Delete a Reddit post
        
        Args:
            post_id: Reddit post ID
            
        Returns:
            True if successful, False otherwise
        """
        try:
            post = self.reddit.submission(id=post_id)
            post.delete()
            self.logger.info(f"Deleted post: {post_id}")
            return True
            
        except Exception as e:
            self.logger.error(f"Error deleting post: {str(e)}")
            return False
        


    def get_recent_posts(self, limit=10):
        """
        Fetches recent posts from the authenticated user's account.
        
        Args:
            limit (int): The number of recent posts to fetch.

        Returns:
            List[Dict[str, str]]: A list of dictionaries, each containing 'title' and 'id' of a post created by the user.
        """
        try:
            # Fetch posts from the authenticated user's profile
            user = self.reddit.user.me()
            recent_posts = user.submissions.new(limit=limit)

            # Create a list of dictionaries with 'title' and 'id' for each post created by the user
            posts_data = [{'title': post.title, 'id': post.id} for post in recent_posts]
            
            return posts_data

        except Exception as e:
            self.logger.error(f"Error fetching user's recent posts: {str(e)}")
            return []


    
    def get_all_posts(self, subreddit_name: str, limit: int = 100):
        """
        Fetch all posts from a subreddit up to a given limit.

        Args:
            subreddit_name (str): Name of the subreddit.
            limit (int): Number of posts to fetch.

        Returns:
            List[dict]: List of dictionaries containing post details.
        """
        try:
            subreddit = self.reddit.subreddit(subreddit_name)
            posts = []
            for submission in subreddit.new(limit=limit):
                posts.append({
                    'id': submission.id,
                    'title': submission.title,
                    'content': submission.selftext,
                    'score': submission.score,
                    'url': submission.url,
                    'created_utc': datetime.fromtimestamp(submission.created_utc),
                    'author': str(submission.author),
                    'num_comments': submission.num_comments,
                })
            return posts
        except Exception as e:
            self.logger.error(f"Error fetching posts: {str(e)}")
            return []




# Example usage
if __name__ == "__main__":
    try:
        # Initialize RedditManager (will automatically load from .env)
        reddit_manager = RedditManager()
        
        # Create a test post
        post_id = reddit_manager.create_post(
            subreddit_name="test",
            title="Test Post using Environment Variables",
            content="This is a test post created using PRAW with environment variables",
            post_type="text"
        )
        
        if post_id:
            # Read the post
            post_data = reddit_manager.read_post(post_id)
            print(f"Post created successfully: {post_data}")
            
            # Update the post
            update_success = reddit_manager.update_post(
                post_id,
                "This content has been updated using environment variables"
            )
            print(f"Post update status: {update_success}")
            
            # Delete the post
            delete_success = reddit_manager.delete_post(post_id)
            print(f"Post deletion status: {delete_success}")
            
    except Exception as e:
        print(f"Error: {str(e)}")