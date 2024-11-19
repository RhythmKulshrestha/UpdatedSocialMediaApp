# instagram_api.py
import os
import requests
from datetime import datetime
from dotenv import load_dotenv
import json

class InstagramAPI:
    def __init__(self):
        # Load environment variables
        load_dotenv()
        
        # Initialize credentials from .env file
        self.page_id = os.getenv('FACEBOOK_PAGE_ID')
        self.access_token = os.getenv('FACEBOOK_ACCESS_TOKEN')
        self.instagram_account_id = os.getenv('INSTAGRAM_BUSINESS_ACCOUNT_ID')
        
        # Base URL for Graph API
        self.base_url = 'https://graph.facebook.com/v18.0'
        
    def _make_request(self, method, endpoint, params=None, data=None):
        """Helper method to make API requests"""
        url = f"{self.base_url}/{endpoint}"
        
        if params is None:
            params = {}
        
        # Add access token to all requests
        params['access_token'] = self.access_token
        
        try:
            response = requests.request(method, url, params=params, json=data)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            print(f"Error making request: {e}")
            if hasattr(e.response, 'text'):
                print(f"Response: {e.response.text}")
            raise

    def get_account_info(self):
        """Get Instagram Business Account Information"""
        return self._make_request('GET', self.instagram_account_id, {
            'fields': 'username,profile_picture_url,followers_count,media_count'
        })

    def create_media_container(self, image_url, caption):
        """Create a media container for posting"""
        return self._make_request('POST', f'{self.instagram_account_id}/media', data={
            'image_url': image_url,
            'caption': caption
        })

    def publish_media(self, creation_id):
        """Publish media using a creation ID"""
        return self._make_request('POST', f'{self.instagram_account_id}/media_publish', data={
            'creation_id': creation_id
        })

    def create_post(self, image_url, caption):
        """Create and publish an Instagram post"""
        try:
            # First, create a media container
            container = self.create_media_container(image_url, caption)
            creation_id = container.get('id')
            
            if not creation_id:
                raise ValueError("Failed to get creation ID")
            
            # Wait for media to be ready (in production, you should implement proper polling)
            import time
            time.sleep(5)
            
            # Then publish it
            return self.publish_media(creation_id)
            
        except Exception as e:
            print(f"Error creating post: {e}")
            raise

    def get_media_list(self, limit=25):
        """Get list of media posts"""
        return self._make_request('GET', f'{self.instagram_account_id}/media', {
            'fields': 'id,caption,media_type,media_url,permalink,thumbnail_url,timestamp,username',
            'limit': limit
        })

    def delete_media(self, media_id):
        """Delete a media post"""
        return self._make_request('DELETE', f'{media_id}')

# Main execution example
if __name__ == "__main__":
    try:
        # Initialize the API client
        api = InstagramAPI()
        
        # Example usage
        account_info = api.get_account_info()
        print("Account Info:", json.dumps(account_info, indent=2))
        

        #Example: Create a post
        image_url = "https://codevibrant.com/wp-content/uploads/2017/11/unsplash-600x450.jpg"
        caption = "Hello Instagram! #python #api"
        result = api.create_post(image_url, caption)
        print("Post Created:", json.dumps(result, indent=2))
        
        # Get recent posts
        media_list = api.get_media_list(limit=5)
        print("Recent Posts:", json.dumps(media_list, indent=2))
        
    except Exception as e:
        print(f"Error: {e}")