import sqlite3

def create_db():
    conn = sqlite3.connect('email_scheduler.db')
    c = conn.cursor()
    # Create table for tracking emails
    c.execute('''CREATE TABLE IF NOT EXISTS email_schedule
                 (email_id TEXT, send_time TEXT, status TEXT, response_rate REAL, sent_time TIMESTAMP)''')
    conn.commit()
    conn.close()

create_db()


# Function to store scheduled email
def store_schedule(email_id, send_time):
    conn = sqlite3.connect('email_scheduler.db')
    c = conn.cursor()
    c.execute("INSERT INTO email_schedule (email_id, send_time, status) VALUES (?, ?, ?)",
              (email_id, send_time, 'scheduled'))  # Initially, the status is 'scheduled'
    conn.commit()
    conn.close()

# Function to update email status
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

# Function to send email and update status
def send_email(sender, to, subject, body):
    try:
        # Send the email using Gmail API
        service = build('gmail', 'v1', credentials=authenticate_gmail())
        message = create_message(sender, to, subject, body)
        message = service.users().messages().send(userId="me", body=message).execute()

        # Update the status as sent after successful sending
        update_email_status(to, 'sent', response_rate=85)  # Example response rate
        print(f"Message sent to {to}")
    except Exception as error:
        # Update the status as failed if an error occurs
        update_email_status(to, 'failed')
        print(f"An error occurred: {error}")

# Example of scheduling and storing emails
def send_bulk_emails_with_schedule(sheet_data, throttle_rate=2, send_time=None):
    sender = "your_email@gmail.com"  # Replace with your Gmail address
    subject = "Potential Collaboration"
    
    for row in sheet_data[1:]:  # Skip the header row
        row_data = {
            'Company Name': row[0],
            'Name': row[1],
            'Email Id': row[2],
            'Address': row[3]
        }

        body = generate_email_content_with_groq(row_data)
        to = row_data['Email Id']

        # Store the scheduled email in the database
        store_schedule(to, send_time)

        # Schedule the email
        schedule_email(sender, to, subject, body, send_time=send_time, throttle_rate=throttle_rate)
