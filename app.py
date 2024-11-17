import os
import sqlite3
import sendgrid
from sendgrid.helpers.mail import Mail, Email, To, Content
from flask import Flask, render_template, request, redirect
from datetime import datetime
import threading
import time
from dotenv import load_dotenv

# Load environment variables from .env file (for SendGrid API Key)
load_dotenv()

app = Flask(__name__)

# SendGrid Email Sending Function
def send_email_with_sendgrid(sender, to, subject, body):
    api_key = os.getenv('SENDGRID_API_KEY')  # Make sure the SendGrid API key is stored securely
    sg = sendgrid.SendGridAPIClient(api_key)

    from_email = Email(sender)
    to_email = To(to)
    content = Content("text/plain", body)
    
    mail = Mail(from_email, to_email, subject, content)
    
    response = sg.send(mail)
    print(f"SendGrid response status code: {response.status_code}")
    return response.status_code

# SQLite Database Setup (Create Table if Not Exist)
def create_db():
    conn = sqlite3.connect('email_scheduler.db')
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS email_schedule
                 (email_id TEXT, subject TEXT, body TEXT, status TEXT, scheduled_time TEXT, response_rate INTEGER)''')
    conn.commit()
    conn.close()

# Function to Store Scheduled Emails in Database
def store_schedule(email_id, subject, body, status, scheduled_time):
    conn = sqlite3.connect('email_scheduler.db')
    c = conn.cursor()
    c.execute("INSERT INTO email_schedule (email_id, subject, body, status, scheduled_time) VALUES (?, ?, ?, ?, ?)",
              (email_id, subject, body, status, scheduled_time))
    conn.commit()
    conn.close()

# Function to Update Email Status
def update_email_status(email_id, status, response_rate=None):
    conn = sqlite3.connect('email_scheduler.db')
    c = conn.cursor()

    if response_rate is not None:
        c.execute("UPDATE email_schedule SET status = ?, response_rate = ?, scheduled_time = ? WHERE email_id = ?",
                  (status, response_rate, datetime.now(), email_id))
    else:
        c.execute("UPDATE email_schedule SET status = ?, scheduled_time = ? WHERE email_id = ?",
                  (status, datetime.now(), email_id))

    conn.commit()
    conn.close()

# Main Route to Display Dashboard
@app.route('/')
def index():
    conn = sqlite3.connect('email_scheduler.db')
    c = conn.cursor()

    # Fetch statistics from the database
    c.execute("SELECT COUNT(*) FROM email_schedule WHERE status = 'sent'")
    total_sent = c.fetchone()[0]

    c.execute("SELECT COUNT(*) FROM email_schedule WHERE status = 'pending'")
    total_pending = c.fetchone()[0]

    c.execute("SELECT COUNT(*) FROM email_schedule WHERE status = 'failed'")
    total_failed = c.fetchone()[0]

    c.execute("SELECT COUNT(*) FROM email_schedule WHERE status = 'scheduled'")
    total_scheduled = c.fetchone()[0]

    c.execute("SELECT AVG(response_rate) FROM email_schedule WHERE response_rate IS NOT NULL")
    avg_response_rate = c.fetchone()[0] or "N/A"

    conn.close()

    return render_template('index.html', total_sent=total_sent, total_pending=total_pending,
                           total_failed=total_failed, total_scheduled=total_scheduled, avg_response_rate=avg_response_rate)

# Route to Send Scheduled Email via SendGrid
@app.route('/schedule_email', methods=['POST'])
def schedule_email():
    email = request.form['email']
    subject = request.form['subject']
    body = request.form['body']
    sender = 'your_email@example.com'  # replace with your SendGrid verified sender email

    # Send the email via SendGrid
    send_status = send_email_with_sendgrid(sender, email, subject, body)

    # If the email was successfully sent, log the email in the database
    if send_status == 202:  # 202 is the SendGrid success status code
        store_schedule(email, subject, body, 'sent', datetime.now())
        return redirect('/')  # Redirect to dashboard after scheduling
    else:
        return 'Error sending email', 500

# Route to Webhook Handler for Delivery Events (from SendGrid)
@app.route('/webhook', methods=['POST'])
def webhook():
    data = request.json  # Assuming SendGrid sends JSON data
    print(f"Webhook received: {data}")  # For debugging
    for event in data:
        email = event.get('email')
        event_type = event.get('event')  # e.g., delivered, bounced, open, etc.

        if event_type == 'delivered':
            update_email_status(email, 'delivered')
        elif event_type == 'bounced':
            update_email_status(email, 'bounced')
        elif event_type == 'open':
            update_email_status(email, 'opened')
        elif event_type == 'spamreport':
            update_email_status(email, 'spam_reported')

    return '', 200  # Respond with 200 OK after processing the webhook data

# Background Job to Update Email Stats (Optional, if you want to update stats in real-time)
def update_stats():
    while True:
        time.sleep(60)  # Update every minute

        # Here, you can do any stats updating you want, for example:
        # Re-fetch data from the database and update the dashboard as necessary
        print("Updating email stats...")

# Run the background job in a separate thread
def start_background_jobs():
    thread = threading.Thread(target=update_stats)
    thread.daemon = True  # Daemonize the thread to exit with the main process
    thread.start()

# Initialize the database
create_db()

# Start background jobs
start_background_jobs()

if __name__ == '__main__':
    app.run(debug=True)
