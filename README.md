Fallowing requirements - 


Python library *
pip install google-auth google-auth-oauthlib google-auth-httplib2 google-api-python-client



Google side * 

Go to the Google Cloud Console:

Open Google Cloud Console.
If you don’t have a Google Cloud account, create one, and sign in.
Create a New Project:

In the top-left corner, click the project dropdown (next to "Google Cloud Platform").
Click on "New Project".
Give your project a name, choose a billing account (if necessary), and click "Create".
Enable YouTube Data API v3:

After creating your project, you will be taken to the project dashboard.
In the left sidebar, click on "APIs & Services" > "Library".
In the search bar, type "YouTube Data API v3".
Click on the YouTube Data API v3 result and then click "Enable".
Create OAuth 2.0 Credentials:

In the left sidebar, go to "APIs & Services" > "Credentials".
Click the "Create Credentials" button at the top of the page.
From the dropdown menu, select "OAuth 2.0 Client ID".
Configure the OAuth Consent Screen:

You will be prompted to configure the OAuth consent screen. Select "External" and click "Create".
Fill in the required fields:
App name (e.g., "YouTube Live Chat Bot").
User support email (your email address).
Developer contact information (your email address).
Click "Save and Continue" to move through the rest of the options and then "Back to Dashboard" once done.
Create OAuth Client ID:

After configuring the consent screen, you will be asked to select an Application type. Choose "Desktop app".
Give the client a name (e.g., "YouTube Chat Bot").
Click "Create".
Download the OAuth 2.0 Credentials:

After creating the credentials, you’ll see your Client ID and Client Secret.
Put you're credentials in proper spots in the code!

