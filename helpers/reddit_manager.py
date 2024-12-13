import praw
import logging
from typing import Optional, List, Dict
from datetime import datetime
from dotenv import load_dotenv
import os
import google.generativeai as genai

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






    def generate_post_title(
        self, 
        topic: str, 
        tone: str = 'informative', 
        additional_context: Optional[str] = None
    ) -> str:
        """
        Generate a catchy and engaging Reddit post title using Gemini AI
        
        Args:
            topic: Main subject of the post
            tone: Writing tone to influence title style
            additional_context: Optional additional context for title generation
        
        Returns:
            Generated post title
        """
        MAX_ATTEMPTS = 3
        
        for attempt in range(MAX_ATTEMPTS):
            try:
                # Construct a prompt for title generation
                prompt = (
                    f"Create an attention-grabbing Reddit post title about {topic}. "
                    f"The tone should be {tone}. "
                    "Make it concise, intriguing, and likely to encourage clicks and comments. "
                    "Aim for 8-12 words. Use Reddit's typical engaging title styles. "
                    "Avoid clickbait, but make it compelling."
                )
                
                if additional_context:
                    prompt += f" Additional context: {additional_context}"

                # Use Gemini Pro model for title generation
                model = genai.GenerativeModel('gemini-pro')
                
                safety_settings = [
                    {"category": "HARM_CATEGORY_HARASSMENT", "threshold": "BLOCK_NONE"},
                    {"category": "HARM_CATEGORY_HATE_SPEECH", "threshold": "BLOCK_NONE"},
                    {"category": "HARM_CATEGORY_SEXUALLY_EXPLICIT", "threshold": "BLOCK_NONE"},
                    {"category": "HARM_CATEGORY_DANGEROUS_CONTENT", "threshold": "BLOCK_NONE"}
                ]
                
                response = model.generate_content(
                    prompt, 
                    safety_settings=safety_settings
                )
                
                # Check and process generated title
                if response.text:
                    generated_title = response.text.strip()
                    
                    # Additional title validation
                    words = generated_title.split()
                    if 5 <= len(words) <= 15:
                        self.logger.info(f"Generated title for topic: {topic}")
                        return generated_title
                
                self.logger.warning(f"Attempt {attempt + 1}: Invalid title generated")
            
            except Exception as e:
                self.logger.error(f"Title generation error (Attempt {attempt + 1}): {str(e)}")
        
        # Fallback title generation
        fallback_title = f"Exploring {topic}: Insights and Perspectives"
        self.logger.warning(f"Returning fallback title for topic: {topic}")
        return fallback_title





    def generate_post_content(
        self, 
        topic: str, 
        tone: str = 'informative', 
        length: int = 300, 
        additional_context: Optional[str] = None
    ) -> str:
        """
        Generate post content using Google's Gemini AI with enhanced safety and regeneration
        
        Args:
            topic: Main subject of the post
            tone: Writing tone (informative, casual, humorous, etc.)
            length: Approximate length of the content in words
            additional_context: Optional additional context for content generation
        
        Returns:
            Generated post content
        """
        MAX_ATTEMPTS = 3
        
        for attempt in range(MAX_ATTEMPTS):
            try:
                # Construct more constrained prompt
                prompt = (
                    f"Write a {tone} Reddit post about {topic}. "
                    f"The post should be approximately {length} words long. "
                    "Ensure the content is engaging, informative, and suitable for a general audience. "
                    "Avoid controversial or sensitive topics. "
                    "Use clear, straightforward language that encourages discussion."
                )
                
                if additional_context:
                    prompt += f" Additional context: {additional_context}"

                # Use Gemini Pro model for text generation
                model = genai.GenerativeModel('gemini-pro')
                
                # Generate content with safety settings
                safety_settings = [
                    {
                        "category": "HARM_CATEGORY_HARASSMENT",
                        "threshold": "BLOCK_NONE"
                    },
                    {
                        "category": "HARM_CATEGORY_HATE_SPEECH",
                        "threshold": "BLOCK_NONE"
                    },
                    {
                        "category": "HARM_CATEGORY_SEXUALLY_EXPLICIT",
                        "threshold": "BLOCK_NONE"
                    },
                    {
                        "category": "HARM_CATEGORY_DANGEROUS_CONTENT",
                        "threshold": "BLOCK_NONE"
                    }
                ]
                
                response = model.generate_content(
                    prompt, 
                    safety_settings=safety_settings
                )
                
                # Check if response contains text
                if response.text:
                    # Extract and clean generated content
                    generated_content = response.text.strip()
                    
                    # Ensure content length is appropriate
                    words = generated_content.split()
                    if len(words) > length * 1.5:
                        generated_content = ' '.join(words[:int(length * 1.5)])
                    elif len(words) < length * 0.5:
                        # If content is too short, continue to next attempt
                        continue
                    
                    self.logger.info(f"Generated content for topic: {topic}")
                    return generated_content
                
                # If no text, continue to next attempt
                self.logger.warning(f"Attempt {attempt + 1}: No content generated")
            
            except Exception as e:
                self.logger.error(f"Content generation error (Attempt {attempt + 1}): {str(e)}")
        
        # Fallback content if all attempts fail
        fallback_content = (
            f"I wanted to share some thoughts about {topic}, but encountered "
            "some technical difficulties in generating the full post. "
            "I'd love to hear your perspectives and insights on this subject!"
        )
        
        self.logger.warning(f"Returning fallback content for topic: {topic}")
        return fallback_content



class RedditPostReviewApp:
    def __init__(self, reddit_manager):
        """
        Create an object for reviewing generated Reddit posts
        
        Args:
            reddit_manager: Instance of RedditManager
        """
        self.reddit_manager = reddit_manager
        self.generated_post = None



    def review_and_publish_post(
        self, 
        topic: str, 
        tone: str = 'informative', 
        length: int = 300,
        subreddit: str = ''
    ) -> Optional[Dict[str, str]]:
        """
        Generate post content and title for review
        
        Args:
            topic: Post topic
            tone: Writing tone
            length: Approximate post length
            subreddit: Target subreddit (optional)
        
        Returns:
            Dictionary with post details for preview
        """
        # Generate title using the new LLM method
        title = self.reddit_manager.generate_post_title(topic, tone)
        
        # Generate content
        content = self.reddit_manager.generate_post_content(topic, tone, length)

        # Prepare and return post details for preview
        self.generated_post = {
            'title': title,
            'content': content,
            'subreddit': subreddit
        }
        return self.generated_post




    def publish_generated_post(
        self, 
        subreddit: Optional[str] = None
    ) -> Optional[Dict[str, str]]:
        """
        Publish a previously generated post to a specific subreddit
        
        Args:
            subreddit: Target subreddit to publish the post
        
        Returns:
            Dictionary with post details if published, None otherwise
        """
        # Use subreddit from earlier generation if not provided
        if not subreddit and self.generated_post:
            subreddit = self.generated_post.get('subreddit')

        # Ensure a post has been generated and subreddit is specified
        if not self.generated_post:
            raise ValueError("No post has been generated to publish")
        
        if not subreddit:
            raise ValueError("No subreddit specified for publication")

        try:
            post_id = self.reddit_manager.create_post(
                subreddit_name=subreddit,
                title=self.generated_post['title'],
                content=self.generated_post['content']
            )
            
            if post_id:
                # Update generated post with publication details
                self.generated_post.update({
                    'subreddit': subreddit,
                    'post_id': post_id
                })
                return self.generated_post
        except Exception as e:
            print(f"Error publishing post: {e}")
        
        return None




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