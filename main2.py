import os
import base64
import pickle
import smtplib
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build

# If modifying the following SCOPES, delete the file token.pickle.
SCOPES = ['https://www.googleapis.com/auth/gmail.send']

# Function to authenticate with Gmail API
def authenticate_gmail():
    creds = None
    # The token.pickle file stores the user's access and refresh tokens, and is created automatically when the authorization flow completes for the first time.
    if os.path.exists('token.pickle'):
        with open('token.pickle', 'rb') as token:
            creds = pickle.load(token)
    
    # If there are no (valid) credentials available, let the user log in.
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(r'C:\Users\iamra\OneDrive\Desktop\Brekout_ai\client_secret_519387517875-4p09ue0018h2c3hka5anigjo0b059ie5.apps.googleusercontent.com.json', SCOPES)  # Replace with your credentials.json file path
            creds = flow.run_local_server(port=8081)

        # Save the credentials for the next run
        with open('token.pickle', 'wb') as token:
            pickle.dump(creds, token)

    return creds

# Function to create a message in raw format (base64 encoding)
def create_message(sender, to, subject, body):
    message = f"From: {sender}\nTo: {to}\nSubject: {subject}\n\n{body}"
    # Encode the message to base64 format
    raw_message = base64.urlsafe_b64encode(message.encode()).decode()
    return {'raw': raw_message}

# Function to send an email via Gmail
def send_email(sender, to, subject, body):
    try:
        service = build('gmail', 'v1', credentials=authenticate_gmail())
        
        # Create the email message
        message = create_message(sender, to, subject, body)
        
        # Send the email
        message = service.users().messages().send(userId="me", body=message).execute()
        print(f"Message sent to {to}")
        return message
    except Exception as error:
        print(f"An error occurred: {error}")
        return None

# Example of sending an email
if __name__ == '__main__':
    sender = "your_email@gmail.com"  # Replace with your Gmail address
    to = "recipient_email@example.com"  # Replace with recipient's email address
    subject = "Test Email from Python"
    body = "Hello, this is a test email sent from a Python script using Gmail API."

    send_email(sender, to, subject, body)
