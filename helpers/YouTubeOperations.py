from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from googleapiclient.errors import HttpError, ResumableUploadError
from googleapiclient.http import MediaFileUpload
import os
import pickle
import socket
from dotenv import load_dotenv

class YouTubeOperations:
    def __init__(self):
        load_dotenv()
        self.api_key = os.getenv('YOUTUBE_API_KEY')
        self.client_id = os.getenv('CLIENT_ID')
        self.client_secret = os.getenv('CLIENT_SECRET')
        self.redirect_uri = os.getenv('REDIRECT_URI')
        self.credentials = None
        self.youtube = None
        self.channel_id = None
        self.SCOPES = [
            'https://www.googleapis.com/auth/youtube.force-ssl',
            'https://www.googleapis.com/auth/youtube'
        ]

    def find_available_port(self, start_port=8080, max_attempts=100):
        for port in range(start_port, start_port + max_attempts):
            try:
                with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                    s.bind(('localhost', port))
                    return port
            except OSError:
                continue
        raise RuntimeError("Could not find an available port")

    def verify_youtube_channel(self):
        try:
            channels_response = self.youtube.channels().list(
                part='id,snippet',
                mine=True
            ).execute()

            if not channels_response.get('items'):
                print("\nERROR: No YouTube channel found for this Google account!")
                return False

            self.channel_id = channels_response['items'][0]['id']
            channel_title = channels_response['items'][0]['snippet']['title']
            print(f"\nConnected to YouTube channel: {channel_title}")
            return True

        except HttpError as e:
            print(f"\nError verifying YouTube channel: {e}")
            return False

    def authenticate(self):
        try:
            if os.path.exists('token.pickle'):
                with open('token.pickle', 'rb') as token:
                    self.credentials = pickle.load(token)

            if not self.credentials or not self.credentials.valid:
                if self.credentials and self.credentials.expired and self.credentials.refresh_token:
                    print("Refreshing expired credentials...")
                    self.credentials.refresh(Request())
                else:
                    print("Starting new authentication flow...")
                    port = self.find_available_port()
                    flow = InstalledAppFlow.from_client_secrets_file(
                        'client_secrets.json',
                        self.SCOPES
                    )
                    self.credentials = flow.run_local_server(port=port)

                with open('token.pickle', 'wb') as token:
                    pickle.dump(self.credentials, token)
                print("Credentials saved successfully!")

            self.youtube = build('youtube', 'v3', credentials=self.credentials)
            print("YouTube API client created successfully!")
            
            if not self.verify_youtube_channel():
                raise Exception("YouTube channel verification failed")
                
            return self.youtube

        except Exception as e:
            print(f"Authentication error: {e}")
            raise

    def create_video(self, title, description, privacy_status, file_path):
        try:
            if not os.path.exists(file_path):
                raise FileNotFoundError(f"Video file not found: {file_path}")

            body = {
                'snippet': {
                    'title': title,
                    'description': description,
                    'tags': ['API Test'],
                    'categoryId': '22'
                },
                'status': {
                    'privacyStatus': privacy_status,
                    'selfDeclaredMadeForKids': False,
                }
            }

            media = MediaFileUpload(
                file_path,
                chunksize=1024*1024,
                resumable=True
            )

            print("\nStarting video upload...")
            request = self.youtube.videos().insert(
                part=','.join(body.keys()),
                body=body,
                media_body=media
            )

            response = None
            while response is None:
                status, response = request.next_chunk()
                if status:
                    print(f"Uploaded {int(status.progress() * 100)}%")

            print(f"\nVideo upload completed successfully! Video ID: {response['id']}")
            return response

        except ResumableUploadError as e:
            print(f"\nUpload error: {e}")
            raise
        except Exception as e:
            print(f"\nUnexpected error during video upload: {e}")
            raise

    def read_video(self, video_id):
        try:
            request = self.youtube.videos().list(
                part="snippet,contentDetails,statistics",
                id=video_id
            )
            response = request.execute()
            return response
        except Exception as e:
            print(f"Error reading video details: {e}")
            raise



    def update_video(self, video_id, title=None, description=None):
        try:
            video = self.youtube.videos().list(part="snippet", id=video_id).execute()
            if not video['items']:
                raise ValueError('Video not found')

            snippet = video['items'][0]['snippet']
            if title:
                snippet['title'] = title
            if description:
                snippet['description'] = description

            request = self.youtube.videos().update(
                part="snippet", body={"id": video_id, "snippet": snippet}
            )
            response = request.execute()
            return response

        except HttpError as e:
            print(f"Error updating video: {e}")
            raise
        except Exception as e:
            print(f"Unexpected error while updating video: {e}")
            raise

    def delete_video(self, video_id):
        try:
            request = self.youtube.videos().delete(id=video_id)
            request.execute()
            print("Video deleted successfully!")
            return True
        except Exception as e:
            print(f"Error deleting video: {e}")
            raise

    def list_my_videos(self, max_results=10):
        try:
            request = self.youtube.search().list(
                part="snippet", forMine=True, type="video", maxResults=max_results
            )
            response = request.execute()
            return response
        except Exception as e:
            print(f"Error listing videos: {e}")
            raise