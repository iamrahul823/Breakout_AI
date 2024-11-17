import os
import base64
import pickle
import gspread
from google.auth.transport.requests import Request
from google.oauth2 import service_account
from googleapiclient.discovery import build
from dotenv import load_dotenv
from groq import Groq
import requests

# Load environment variables from .env file (for GROQ_API_KEY)
load_dotenv()

# 1. Google Sheets Authentication and Data Fetching
def authenticate_google_sheets():
    SCOPES = ['https://www.googleapis.com/auth/spreadsheets.readonly']
    
    # Correct way to load credentials from a service account
    creds = service_account.Credentials.from_service_account_file(
        r'C:\Users\iamra\OneDrive\Desktop\Brekout_ai\credent.json', scopes=SCOPES)
    
    if creds and creds.expired and creds.refresh_token:
        creds.refresh(Request())
    
    return creds

def read_google_sheet(sheet_id, range_name):
    creds = authenticate_google_sheets()
    client = gspread.authorize(creds)
    sheet = client.open_by_key(sheet_id)
    records = sheet.values_get(range_name)['values']
    return records

# 2. Groq API Authentication and Email Content Generation
def generate_email_content_with_groq(row_data):
    """
    Use Groq API to generate email content based on row data.
    """
    # The data you want to send to Groq API
    prompt = f"""
    Write a formal email to {row_data['Name']} from the company {row_data['Company Name']} located at {row_data['Address']}.
    The email should offer our services for collaboration and be polite and professional.
    """

    # Initialize the Groq client with API key from environment variable
    api_key = os.environ.get("GROQ_API_KEY")
    if not api_key:
        raise ValueError("API Key not found. Please ensure it's set in your environment variables.")
    
    client = Groq(api_key=api_key)

    # Call Groq API to generate the email content
    chat_completion = client.chat.completions.create(
        messages=[
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": prompt}
        ],
        model="llama3-8b-8192",  # Specify the model you want to use
    )

    # Return the generated content
    return chat_completion.choices[0].message.content

# 3. Gmail API Authentication and Sending Emails
def authenticate_gmail():
    creds = None
    SCOPES = ['https://www.googleapis.com/auth/gmail.send']

    # Check if we have previously stored credentials
    if os.path.exists('token.pickle'):
        with open('token.pickle', 'rb') as token:
            creds = pickle.load(token)
    
    # If no valid credentials are available, let the user log in
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                r'C:\Users\iamra\OneDrive\Desktop\Brekout_ai\credent.json', SCOPES)
            creds = flow.run_local_server(port=8080)

        # Save the credentials for the next run
        with open('token.pickle', 'wb') as token:
            pickle.dump(creds, token)

    return creds

def send_email(sender, to, subject, body):
    service = build('gmail', 'v1', credentials=authenticate_gmail())
    message = create_message(sender, to, subject, body)
    try:
        message = service.users().messages().send(userId="me", body=message).execute()
        print(f"Message sent to {to}")
        return message
    except Exception as error:
        print(f"An error occurred: {error}")
        return None

def create_message(sender, to, subject, body):
    message = f"From: {sender}\nTo: {to}\nSubject: {subject}\n\n{body}"
    raw_message = base64.urlsafe_b64encode(message.encode()).decode()
    return {'raw': raw_message}

# 4. Loop Through Rows and Send Customized Emails in Bulk
def send_bulk_emails(sheet_data):
    sender = "your_email@gmail.com"  # Replace with your Gmail address
    subject = "Potential Collaboration"

    # Loop through each row in the sheet data (skip header row)
    for row in sheet_data[1:]:  # Skip the header row
        row_data = {
            'Company Name': row[0],
            'Name': row[1],
            'Email Id': row[2],
            'Address': row[3]
        }

        # Generate the email body using Groq API
        generated_email = generate_email_content_with_groq(row_data)
        
        # Send the email to the recipient
        to = row_data['Email Id']
        body = generated_email
        send_email(sender, to, subject, body)

# Example: Sheet details
sheet_id = '1y0eIOxPDGDIl7Lwz_SHaxkSAwtOJxFLGsoEV9qlrSvI'  # Google Sheets ID
range_name = 'Sheet1!A1:D100'  # Specify the range
data = read_google_sheet(sheet_id, range_name)

# 5. Trigger Bulk Email Sending
send_bulk_emails(data)
