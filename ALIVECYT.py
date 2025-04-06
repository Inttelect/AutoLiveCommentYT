import os
import pickle
import time
import random
import google_auth_oauthlib.flow
import googleapiclient.discovery
import googleapiclient.errors
from google.auth.transport.requests import Request
from datetime import datetime
import requests

# Scopes required for YouTube API
SCOPES = ["https://www.googleapis.com/auth/youtube.force-ssl"]

CLIENT_SECRET_FILE = "client_secret.json"  # Ensure you have this file
TOKEN_FILE = "token.pickle"  # File to store authentication tokens

# Authenticate and create a service object with token persistence
def authenticate():
    credentials = None

    # Check if the token file already exists
    if os.path.exists(TOKEN_FILE):
        with open(TOKEN_FILE, "rb") as token:
            credentials = pickle.load(token)

    # If credentials are invalid or expired, refresh or ask for new login
    if not credentials or not credentials.valid:
        if credentials and credentials.expired and credentials.refresh_token:
            credentials.refresh(Request())  # Refresh the token
            print("[AUTH] Token refreshed successfully!")
        else:
            print("[AUTH] No valid token found. Please log in.")
            flow = google_auth_oauthlib.flow.InstalledAppFlow.from_client_secrets_file(
                CLIENT_SECRET_FILE, SCOPES
            )
            credentials = flow.run_local_server(port=8080)  # Authenticate via Google

        # Save the new token for future use
        with open(TOKEN_FILE, "wb") as token:
            pickle.dump(credentials, token)
            print("[AUTH] Token saved for future use!")

    youtube = googleapiclient.discovery.build("youtube", "v3", credentials=credentials)
    return youtube

# Get live chat ID for all active streams on the channel
def get_live_chat_ids(youtube, channel_id):
    request = youtube.search().list(
        part="snippet",
        channelId=channel_id,
        eventType="live",
        type="video"
    )
    response = request.execute()

    live_chat_ids = []
    if response.get("items"):
        for video in response["items"]:
            video_id = video["id"]["videoId"]
            video_request = youtube.videos().list(
                part="liveStreamingDetails",
                id=video_id
            )
            video_response = video_request.execute()
            live_chat_id = video_response["items"][0]["liveStreamingDetails"].get("activeLiveChatId")
            
            if live_chat_id:
                print(f"[{datetime.now().strftime('%H:%M')}] Found live stream: {video['snippet']['title']}")
                print(f"Live Chat ID: {live_chat_id}")
                live_chat_ids.append(live_chat_id)
            else:
                print(f"[{datetime.now().strftime('%H:%M')}] No live chat found for video: {video['snippet']['title']}")
    else:
        print(f"[{datetime.now().strftime('%H:%M')}] No active live streams found.")
    
    return live_chat_ids

# Send message to live chat with retry logic
def send_message_to_chat(youtube, live_chat_id, message, retries=5, delay=5):
    attempt = 0
    while attempt < retries:
        try:
            request = youtube.liveChatMessages().insert(
                part="snippet",
                body={
                    "snippet": {
                        "liveChatId": live_chat_id,
                        "type": "textMessageEvent",
                        "textMessageDetails": {
                            "messageText": message
                        }
                    }
                }
            )
            request.execute()  # Send the message
            timestamp = datetime.now().strftime('%H:%M')
            print(f"[{timestamp}] Sent message: {message} to live chat ID: {live_chat_id}")
            return True  # Message sent successfully
        except googleapiclient.errors.HttpError as e:
            print(f"[{datetime.now().strftime('%H:%M')}] Error sending message to {live_chat_id}: {e}")
        except Exception as e:
            print(f"[{datetime.now().strftime('%H:%M')}] Unexpected error: {e}")
        
        attempt += 1
        print(f"[{datetime.now().strftime('%H:%M')}] Retrying in {delay} seconds... ({attempt}/{retries})")
        time.sleep(delay)
    
    print(f"[{datetime.now().strftime('%H:%M')}] Failed to send message after {retries} attempts.")
    return False  # Failed after all retries

# Check internet connectivity
def check_internet():
    try:
        # Attempt to reach Google (or any reliable website)
        requests.get('https://www.google.com', timeout=5)
        return True
    except requests.ConnectionError:
        return False

# Main bot function
def main():
    channel_id = "UCaoWmvBnp5n2daTTCl3LcvA"  # Replace with your channel ID
    youtube = authenticate()  # Authenticate only once, reuse token
    
    # Ensure internet is available before proceeding
    print("[INFO] Checking internet connectivity...")
    while not check_internet():
        print(f"[{datetime.now().strftime('%H:%M')}] No internet connection. Retrying...")
        time.sleep(30)  # Check every 30 seconds
    
    print("[INFO] Internet connection detected. Starting bot...")

    while True:  # Continuously check for active live streams
        live_chat_ids = get_live_chat_ids(youtube, channel_id)
        
        if live_chat_ids:
            print(f"[{datetime.now().strftime('%H:%M')}] Active live streams found. Bot is running...")

            while live_chat_ids:  # Keep checking messages
                for live_chat_id in live_chat_ids:
                    random_emoji = random.choice(["😃", " ", ".", "😎", "🐱", "🤔", "😶"])  # Neutral emojis
                    send_message_to_chat(youtube, live_chat_id, random_emoji)
                    
                time.sleep(600)  # Wait 10 minutes before sending again

            print(f"[{datetime.now().strftime('%H:%M')}] Rechecking for active live streams...")
        else:
            print(f"[{datetime.now().strftime('%H:%M')}] No active live streams found. Rechecking in 10 minutes...")
            time.sleep(600)  # Wait 10 minutes before checking again

if __name__ == "__main__":
    main()
