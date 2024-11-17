import os
import base64
import pickle
import gspread
import pandas as pd
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google.oauth2.service_account import Credentials
from googleapiclient.discovery import build
from google.auth.transport.requests import Request

# 1. Google Sheets Authentication and Data Fetching
def authenticate_google_sheets():
    SCOPES = ['https://www.googleapis.com/auth/spreadsheets.readonly']
    creds = Credentials.from_service_account_file(
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

# Example: Sheet details
sheet_id = '1y0eIOxPDGDIl7Lwz_SHaxkSAwtOJxFLGsoEV9qlrSvI'  # Google Sheets ID
range_name = 'Sheet1!A1:D100'  # Specify the range
data = read_google_sheet(sheet_id, range_name)

# 2. Email Customization Function
def customize_email_body(template, row_data):
    """
    Replace placeholders in the email template with actual row data.
    """
    placeholders = {
        "{Company Name}": row_data.get('Company Name', ''),
        "{Name}": row_data.get('Name', ''),
        "{Email}": row_data.get('Email Id', ''),
        "{Address}": row_data.get('Address', '')
    }

    # Replace placeholders in the email template
    for placeholder, value in placeholders.items():
        template = template.replace(placeholder, value)
    
    return template

# Example email template with placeholders
email_template = """
Hello {Name},

We are reaching out from {Company Name} located in {Address}. 

We'd love to offer you our services and discuss potential collaborations.

Best regards,
Your Company Team
"""

# 3. Gmail API Authentication
SCOPES = ['https://www.googleapis.com/auth/gmail.send']
def authenticate_gmail():
    creds = None
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

# 4. Loop Through Rows and Send Custom Emails in Bulk
def send_bulk_emails(sheet_data, template):
    sender = "your_email@gmail.com"  # Replace with your Gmail address
    subject = "Test Email from Python"
    
    # Loop through each row in the sheet data (skip header row)
    for row in sheet_data[1:]:  # Skip the header row
        row_data = {
            'Company Name': row[0],
            'Name': row[1],
            'Email Id': row[2],
            'Address': row[3]
        }

        # Customize the email body with actual row data
        customized_email = customize_email_body(template, row_data)
        
        # Send the customized email to the recipient
        to = row_data['Email Id']
        body = customized_email
        send_email(sender, to, subject, body)

# 5. Trigger Bulk Email Sending
send_bulk_emails(data, email_template)
