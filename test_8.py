import os
import base64
import pickle
import gspread
import time
import threading
import schedule
import sqlite3
from google.auth.transport.requests import Request
from google.oauth2 import service_account
from googleapiclient.discovery import build
from dotenv import load_dotenv
from groq import Groq
from datetime import datetime

# Load environment variables from .env file (for GROQ_API_KEY)
load_dotenv()

# SQLite Database for Scheduling (Optional)
def create_db():
    conn = sqlite3.connect('email_scheduler.db')
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS email_schedule
                 (email_id TEXT, send_time TEXT, status TEXT, response_rate INTEGER, sent_time TEXT)''')
    conn.commit()
    conn.close()

def alter_db():
    conn = sqlite3.connect('email_scheduler.db')
    c = conn.cursor()

    # Check if the 'response_rate' and 'sent_time' columns exist
    c.execute('PRAGMA table_info(email_schedule)')
    columns = [column[1] for column in c.fetchall()]

    # Add 'response_rate' column if it doesn't exist
    if 'response_rate' not in columns:
        c.execute('''ALTER TABLE email_schedule ADD COLUMN response_rate INTEGER;''')

    # Add 'sent_time' column if it doesn't exist
    if 'sent_time' not in columns:
        c.execute('''ALTER TABLE email_schedule ADD COLUMN sent_time TEXT;''')

    conn.commit()
    conn.close()

# Call alter_db() to add the missing columns if the table already exists
alter_db()

# Store scheduling data in the database
def store_schedule(email_id, send_time):
    conn = sqlite3.connect('email_scheduler.db')
    c = conn.cursor()
    c.execute("INSERT INTO email_schedule (email_id, send_time, status) VALUES (?, ?, ?)",
              (email_id, send_time, 'scheduled'))  # Initially, the status is 'scheduled'
    conn.commit()
    conn.close()

# Update email status and store response_rate and sent_time if available
def update_email_status(email_id, status, response_rate=None):
    conn = sqlite3.connect('email_scheduler.db')
    c = conn.cursor()

    if response_rate is not None:
        c.execute("UPDATE email_schedule SET status = ?, response_rate = ?, sent_time = ? WHERE email_id = ?",
                  (status, response_rate, datetime.now(), email_id))
    else:
        c.execute("UPDATE email_schedule SET status = ?, sent_time = ? WHERE email_id = ?",
                  (status, datetime.now(), email_id))

    conn.commit()
    conn.close()

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
        update_email_status(to, 'sent', response_rate=85)  # Assuming 85% response rate (just an example)
        print(f"Message sent to {to}")
        return message
    except Exception as error:
        update_email_status(to, 'failed')
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
        
        # Store schedule data in database
        store_schedule(to, send_time)
        
        # Schedule the email
        schedule_email(sender, to, subject, body, send_time=send_time, throttle_rate=throttle_rate)


def update_analytics():
    conn = sqlite3.connect('email_scheduler.db')
    c = conn.cursor()

    # Calculate metrics
    c.execute("SELECT COUNT(*) FROM email_schedule WHERE status = 'sent'")
    total_sent = c.fetchone()[0]
    
    c.execute("SELECT COUNT(*) FROM email_schedule WHERE status = 'scheduled'")
    total_scheduled = c.fetchone()[0]
    
    c.execute("SELECT COUNT(*) FROM email_schedule WHERE status = 'failed'")
    total_failed = c.fetchone()[0]

    c.execute("SELECT COUNT(*) FROM email_schedule WHERE status IN ('scheduled', 'pending')")
    total_pending = c.fetchone()[0]

    c.execute("SELECT AVG(response_rate) FROM email_schedule WHERE response_rate IS NOT NULL")
    avg_response_rate = c.fetchone()[0]

    # Update the analytics table with the new metrics
    c.execute('''INSERT INTO email_analytics (total_sent, total_pending, total_failed, total_scheduled, avg_response_rate) 
                 VALUES (?, ?, ?, ?, ?)''', 
              (total_sent, total_pending, total_failed, total_scheduled, avg_response_rate))

    conn.commit()
    conn.close()

    # Print or log the analytics (for real-time view)
    print(f"Total Sent: {total_sent}")
    print(f"Total Pending: {total_pending}")
    print(f"Total Scheduled: {total_scheduled}")
    print(f"Total Failed: {total_failed}")
    print(f"Average Response Rate: {avg_response_rate if avg_response_rate else 'N/A'}")




# 6. Run Scheduled Tasks in a Separate Thread
def run_scheduled_tasks():
    while True:
        schedule.run_pending()
        time.sleep(1)

# Main execution: Trigger bulk email sending
sheet_id = '1y0eIOxPDGDIl7Lwz_SHaxkSAwtOJxFLGsoEV9qlrSvI'  # Your Google Sheet ID
range_name = 'Sheet1!A1:D100'  # Google Sheets range for emails
data = read_google_sheet(sheet_id, range_name)

# Initialize the database (Create table if not exists)
create_db()

# Example: Set to send emails at 3:00 PM or stagger every minute
send_bulk_emails_with_schedule(data, throttle_rate=2, send_time="22:47")

# Start the scheduling loop
thread = threading.Thread(target=run_scheduled_tasks)
thread.start()
