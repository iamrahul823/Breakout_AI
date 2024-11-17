import os
import base64
import pickle
import gspread
import time
import threading
import schedule
from google.auth.transport.requests import Request
from google.oauth2 import service_account
from googleapiclient.discovery import build
from dotenv import load_dotenv
from groq import Groq
from datetime import datetime

# Load environment variables from .env file (for GROQ_API_KEY)
load_dotenv()

# 1. Google Sheets Authentication and Data Fetching
def authenticate_google_sheets():
    SCOPES = ['https://www.googleapis.com/auth/spreadsheets.readonly']
    
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
    prompt = f"""
    Write a formal email to {row_data['Name']} from the company {row_data['Company Name']} located at {row_data['Address']}.
    The email should offer our services for collaboration and be polite and professional.
    """
    
    api_key = os.environ.get("GROQ_API_KEY")
    if not api_key:
        raise ValueError("API Key not found. Please ensure it's set in your environment variables.")
    
    client = Groq(api_key=api_key)

    chat_completion = client.chat.completions.create(
        messages=[
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": prompt}
        ],
        model="llama3-8b-8192"
    )

    return chat_completion.choices[0].message.content

# 3. Gmail API Authentication and Sending Emails
def authenticate_gmail():
    creds = None
    SCOPES = ['https://www.googleapis.com/auth/gmail.send']

    if os.path.exists('token.pickle'):
        with open('token.pickle', 'rb') as token:
            creds = pickle.load(token)
    
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                r'C:\Users\iamra\OneDrive\Desktop\Brekout_ai\credent.json', SCOPES)
            creds = flow.run_local_server(port=8080)

        with open('token.pickle', 'wb') as token:
            pickle.dump(creds, token)

    return creds

def send_email(sender, to, subject, body):
    service = build('gmail', 'v1', credentials=authenticate_gmail())
    message = create_message(sender, to, subject, body)
    try:
        service.users().messages().send(userId="me", body=message).execute()
        print(f"Message sent to {to}")
        return message
    except Exception as error:
        print(f"An error occurred: {error}")
        return None

def create_message(sender, to, subject, body):
    message = f"From: {sender}\nTo: {to}\nSubject: {subject}\n\n{body}"
    raw_message = base64.urlsafe_b64encode(message.encode()).decode()
    return {'raw': raw_message}

# 4. Scheduling and Throttling
def schedule_email(sender, to, subject, body, send_time=None, throttle_rate=1):
    if send_time:
        # Schedule to send email at a specific time
        schedule.every().day.at(send_time).do(send_email_throttled, sender, to, subject, body, delay=throttle_rate)
        print(f"Scheduled email to {to} at {send_time}")
    else:
        # Schedule to send emails at fixed intervals
        schedule.every(1).minute.do(send_email_throttled, sender, to, subject, body, delay=throttle_rate)
        print(f"Scheduled email to {to} every minute")

def send_email_throttled(sender, to, subject, body, delay=1):
    send_email(sender, to, subject, body)
    time.sleep(delay)  # Delay to throttle email sending rate

# 5. Loop Through Data and Schedule Emails
def send_bulk_emails_with_schedule(sheet_data, throttle_rate=2, send_time=None):
    sender = "your_email@gmail.com"  # Replace with your Gmail address
    subject = "Potential Collaboration"
    
    for row in sheet_data[1:]:
        row_data = {
            'Company Name': row[0],
            'Name': row[1],
            'Email Id': row[2],
            'Address': row[3]
        }

        body = generate_email_content_with_groq(row_data)
        to = row_data['Email Id']
        
        # Schedule the email
        schedule_email(sender, to, subject, body, send_time=send_time, throttle_rate=throttle_rate)

# 6. Run Scheduled Tasks in a Separate Thread
def run_scheduled_tasks():
    while True:
        schedule.run_pending()
        time.sleep(1)

# Main execution: Trigger bulk email sending
sheet_id = '1y0eIOxPDGDIl7Lwz_SHaxkSAwtOJxFLGsoEV9qlrSvI'  # Your Google Sheet ID
range_name = 'Sheet1!A1:D100'  # Google Sheets range for emails
data = read_google_sheet(sheet_id, range_name)

# Example: Set to send emails at 3:00 PM or stagger every minute
send_bulk_emails_with_schedule(data, throttle_rate=2, send_time="10:19")

# Start the scheduling loop
thread = threading.Thread(target=run_scheduled_tasks)
thread.start()
