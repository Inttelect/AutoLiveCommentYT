import time
import random
import google_auth_oauthlib.flow
import googleapiclient.discovery
import googleapiclient.errors
from google.auth.transport.requests import Request
import os
import pickle


# Replace the contents of `client_secret.json` with your actual credentials here
CLIENT_SECRET = {
    "installed": {
        "client_id": "",
        "project_id": "",
        "auth_uri": "",
        "token_uri": "",
        "auth_provider_x509_cert_url": "",
        "client_secret": "",
        "redirect_uris": [
            "http://localhost"
        ]
    }
}

# Authenticate and create a service object
def authenticate():
    api_service_name = "youtube"
    api_version = "v3"
    
    flow = google_auth_oauthlib.flow.InstalledAppFlow.from_client_config(
        CLIENT_SECRET, SCOPES
    )
    
    credentials = flow.run_local_server(port=8080)
    youtube = googleapiclient.discovery.build(api_service_name, api_version, credentials=credentials)
    
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
    if response["items"]:
        for video in response["items"]:
            video_id = video["id"]["videoId"]
            
            video_request = youtube.videos().list(
                part="liveStreamingDetails",
                id=video_id
            )
            video_response = video_request.execute()
            live_chat_id = video_response["items"][0]["liveStreamingDetails"].get("activeLiveChatId")
            
            if live_chat_id:
                print(f"Found live stream: {video['snippet']['title']}")
                print(f"Live Chat ID: {live_chat_id}")
                live_chat_ids.append(live_chat_id)
            else:
                print(f"No live chat found for video: {video['snippet']['title']}")
    else:
        print("No active live streams found.")
    
    return live_chat_ids

# Send message to live chat
def send_message_to_chat(youtube, live_chat_id, message):
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
        request.execute()
        print(f"Sent message: {message} to live chat ID: {live_chat_id}")
    except googleapiclient.errors.HttpError as e:
        print(f"Error sending message to {live_chat_id}: {e}")

# Main bot function
def main():
    channel_id = "??????????????????"  # Replace with your channel ID
    youtube = authenticate()

    while True:  # Continuously check for active live streams
        live_chat_ids = get_live_chat_ids(youtube, channel_id)
        
        if live_chat_ids:
            print("Active live streams found. Bot is running...")
            while live_chat_ids:  # Keep sending messages as long as streams are active
                for live_chat_id in live_chat_ids:
                    random_emoji = random.choice(["😃", ".", "😎", "🐱", "🤔","😶"])  #In thsi case, i'm using random, for different messages being sent every 10min
                    send_message_to_chat(youtube, live_chat_id, random_emoji)
                time.sleep(600)  # Wait for 10 minutes before sending again

            # Recheck for active streams after finishing the current list
            print("Rechecking for active live streams...")
        else:
            print("No active live streams found. Rechecking in 1 minute...")
            time.sleep(600)  # Wait 10 minute before checking again

if __name__ == "__main__":
    main()
