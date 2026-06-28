import os
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
import config

def get_gdrive_credentials():
    """
    Gets valid user credentials from disk or via user login.
    Returns a Credentials object containing the Access Token.
    """
    creds = None
    
    # The file token.json stores the user's access and refresh tokens.
    # It is created automatically when the authorization flow completes for the first time.
    if os.path.exists(config.TOKEN_FILE):
        creds = Credentials.from_authorized_user_file(config.TOKEN_FILE, config.SCOPES)
        
    # If there are no valid credentials available, let the user log in.
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            print("Access token expired. Refreshing token smoothly...")
            creds.refresh(Request())
        else:
            print("No active session found. Opening browser for Google Authentication...")
            if not os.path.exists(config.CREDENTIALS_FILE):
                raise FileNotFoundError(
                    f"Missing '{config.CREDENTIALS_FILE}'. Please download your OAuth client JSON from Google Cloud Console."
                )
            
            flow = InstalledAppFlow.from_client_secrets_file(
                config.CREDENTIALS_FILE, config.SCOPES
            )
            creds = flow.run_local_server(port=0)
            
        # Save the credentials for the next run
        with open(config.TOKEN_FILE, 'w') as token:
            token.write(creds.to_json())
            print("Authentication successful! Token saved to disk.")
            
    return creds

if __name__ == "__main__":
    # Test the authentication flow directly
    try:
        credentials = get_gdrive_credentials()
        print(f"Token is valid! Token starts with: {credentials.token[:10]}...")
    except Exception as e:
        print(f"Authentication failed: {e}")