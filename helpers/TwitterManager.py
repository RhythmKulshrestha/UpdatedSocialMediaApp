import os
from typing import Dict, Any, List
from dotenv import load_dotenv
import tweepy

# Load environment variables from .env file
load_dotenv()

class TwitterManager:
    def __init__(self):
        """
        Initialize Twitter API credentials from environment variables
        """
        # Get credentials from environment variables
        client_id = os.getenv('TWITTER_CLIENT_ID')
        client_secret = os.getenv('TWITTER_CLIENT_SECRET')
        bearer_token = os.getenv('TWITTER_BEARER_TOKEN')
        access_token = os.getenv('TWITTER_ACCESS_TOKEN')
        access_token_secret = os.getenv('TWITTER_ACCESS_TOKEN_SECRET')

        # Verify credentials are present
        if not all([client_id, client_secret, bearer_token, access_token, access_token_secret]):
            raise ValueError("Missing required Twitter API credentials in .env file")

        # Initialize Twitter API v2 client
        self.client = tweepy.Client(
            bearer_token=bearer_token,
            consumer_key=client_id,
            consumer_secret=client_secret,
            access_token=access_token,
            access_token_secret=access_token_secret,
            wait_on_rate_limit=True
        )

        # Verify credentials
        try:
            self.client.get_me()
            print("Twitter API v2 authentication successful!")
        except tweepy.TweepyException as e:
            print(f"Error authenticating with Twitter: {str(e)}")
            raise

    # CREATE
    def create_tweet(self, text: str) -> Dict[str, Any]:
        """
        Create a new tweet
        """
        try:
            response = self.client.create_tweet(text=text)
            tweet_id = response.data['id']
            print(f"Tweet created successfully! Tweet ID: {tweet_id}")
            return response.data
        except tweepy.TweepyException as e:
            print(f"Error creating tweet: {str(e)}")
            raise

    # READ
    def get_tweet(self, tweet_id: str) -> Dict[str, Any]:
        """
        Get a specific tweet by its ID
        """
        try:
            response = self.client.get_tweet(
                id=tweet_id,
                tweet_fields=['created_at', 'public_metrics']
            )
            if response.data:
                print(f"Tweet fetched successfully! Content: {response.data['text']}")
            return response.data
        except tweepy.TweepyException as e:
            print(f"Error fetching tweet: {str(e)}")
            raise

    def get_my_tweets(self, max_results: int = 5) -> List[Dict[str, Any]]:
        """
        Get your own tweets
        """
        try:
            # First get your user ID
            me = self.client.get_me()
            user_id = me.data.id
            
            # Then get your tweets
            response = self.client.get_users_tweets(
                id=user_id,
                max_results=max_results,
                tweet_fields=['created_at']
            )
            if response.data:
                print(f"Retrieved {len(response.data)} tweets")
                for tweet in response.data:
                    print(f"Tweet ID: {tweet.id}")
                    print(f"Content: {tweet.text}")
                    print("---")
            return response.data if response.data else []
        except tweepy.TweepyException as e:
            print(f"Error fetching tweets: {str(e)}")
            raise

    # UPDATE (Note: Twitter API v2 doesn't support direct tweet updates, but you can delete and recreate)
    def update_tweet(self, tweet_id: str, new_text: str) -> Dict[str, Any]:
        """
        Update a tweet by deleting and recreating it
        """
        try:
            # Delete the old tweet
            self.delete_tweet(tweet_id)
            # Create new tweet
            return self.create_tweet(new_text)
        except tweepy.TweepyException as e:
            print(f"Error updating tweet: {str(e)}")
            raise

    # DELETE
    def delete_tweet(self, tweet_id: str) -> bool:
        """
        Delete a tweet
        """
        try:
            self.client.delete_tweet(tweet_id)
            print(f"Tweet deleted successfully!")
            return True
        except tweepy.TweepyException as e:
            print(f"Error deleting tweet: {str(e)}")
            raise

# Example usage
if __name__ == "__main__":
    try:
        # Initialize Twitter manager
        twitter = TwitterManager()

        # Create a tweet
        print("\n1. Creating a tweet...")
        new_tweet = twitter.create_tweet("Hello Twitter. this is me again on 28 october! This is a new test tweet using API v2.")
        tweet_id = new_tweet['id']
        
        # # Read the tweet
        # print("\n2. Reading the tweet...")
        # twitter.get_tweet(tweet_id)
        
        # # Get recent tweets
        # print("\n3. Getting recent tweets...")
        # twitter.get_my_tweets(max_results=3)
        
        # # Update the tweet (delete and recreate)
        # print("\n4. Updating the tweet...")
        # updated_tweet = twitter.update_tweet(tweet_id, "Updated test tweet using Twitter API v2!")
        
        # # Delete the tweet
        # print("\n5. Deleting the tweet...")
        # twitter.delete_tweet(updated_tweet['id'])

    except Exception as e:
        print(f"An error occurred: {str(e)}")