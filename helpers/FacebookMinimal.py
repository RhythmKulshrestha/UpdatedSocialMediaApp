import os
from dotenv import load_dotenv
import requests
import json

# Load .env file
load_dotenv()

class FacebookMinimal:
    def __init__(self):
        self.user_token = os.getenv('FB_ACCESS_TOKEN')
        self.page_id = os.getenv('FB_PAGE_ID')
        self.base_url = 'https://graph.facebook.com/v18.0'
        
        # Verify credentials are loaded
        if not self.user_token or not self.page_id:
            raise ValueError("Missing credentials. Please check your .env file.")
        
        # Get page access token
        self.token = self.get_page_access_token()
        if not self.token:
            raise ValueError("Failed to get page access token")
            
        print(f"Initialized with Page ID: {self.page_id}")

    def get_page_access_token(self):
        """Convert user access token to page access token"""
        try:
            response = requests.get(
                f'{self.base_url}/{self.page_id}',
                params={
                    'fields': 'access_token',
                    'access_token': self.user_token
                }
            )
            response.raise_for_status()
            data = response.json()
            return data.get('access_token')
        except requests.exceptions.RequestException as e:
            print(f"Failed to get page access token: {str(e)}")
            if response.text:
                print(f"API Response: {response.text}")
            return None
        

        

    def verify_permissions(self):
        """Verify required permissions are granted"""
        try:
            response = requests.get(
                f'{self.base_url}/me/permissions',
                params={'access_token': self.user_token}
            )
            response.raise_for_status()
            permissions = response.json().get('data', [])
            
            required_permissions = {
                'pages_read_engagement',
                'pages_manage_posts'
            }
            
            granted_permissions = {
                perm['permission'] 
                for perm in permissions 
                if perm['status'] == 'granted'
            }
            
            missing_permissions = required_permissions - granted_permissions
            
            if missing_permissions:
                print(f"Missing permissions: {missing_permissions}")
                return False
            return True
            
        except requests.exceptions.RequestException as e:
            print(f"Failed to verify permissions: {str(e)}")
            return False

    def create_post(self, message):
        """Create a simple post"""
        try:
            response = requests.post(
                f'{self.base_url}/{self.page_id}/feed',
                params={
                    'message': message,
                    'access_token': self.token  # Using page access token
                }
            )
            
            # Print full response for debugging
            print(f"API Response: {response.text}")
            
            # Check if request was successful
            response.raise_for_status()
            
            data = response.json()
            if 'error' in data:
                print(f"API Error: {data['error']['message']}")
                return None
            return data
            
        except requests.exceptions.RequestException as e:
            print(f"Request failed: {str(e)}")
            return None

    def read_post(self, post_id):
        """Read a post"""
        try:
            response = requests.get(
                f'{self.base_url}/{post_id}',
                params={'access_token': self.token}  # Using page access token
            )
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            print(f"Failed to read post: {str(e)}")
            return None

    def update_post(self, post_id, new_message):
        """Update a post"""
        try:
            response = requests.post(
                f'{self.base_url}/{post_id}',
                params={
                    'message': new_message,
                    'access_token': self.token  # Using page access token
                }
            )
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            print(f"Failed to update post: {str(e)}")
            return None

    def delete_post(self, post_id):
        """Delete a post"""
        try:
            response = requests.delete(
                f'{self.base_url}/{post_id}',
                params={'access_token': self.token}  # Using page access token
            )
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            print(f"Failed to delete post: {str(e)}")
            return None



# Usage example
if __name__ == "__main__":
    try:
        fb = FacebookMinimal()
        
        # Create post
        print("Creating post...")
        post = fb.create_post("Hello Facebook!")
        if post and 'id' in post:
            post_id = post['id']
            print(f"Created post with ID: {post_id}")
            
            # Read post
            print("\nReading post...")
            content = fb.read_post(post_id)
            if content:
                print(f"Post content: {json.dumps(content, indent=2)}")
            
            # Update post
            print("\nUpdating post...")
            update_result = fb.update_post(post_id, "Updated post!")
            if update_result:
                print("Post updated successfully")
            
            # Delete post
            print("\nDeleting post...")
            delete_result = fb.delete_post(post_id)
            if delete_result:
                print("Post deleted successfully")
        else:
            print("Failed to create post. Please check your credentials and permissions.")
            
    except Exception as e:
        print(f"An error occurred: {str(e)}")