from flask import Flask, request, jsonify
import sqlite3

app = Flask(__name__)

@app.route('/webhook', methods=['POST'])

def get_email_stats():
    conn = sqlite3.connect('email_scheduler.db')
    c = conn.cursor()

    # Count emails based on their status
    c.execute("SELECT COUNT(*) FROM email_schedule WHERE status = 'delivered'")
    total_delivered = c.fetchone()[0]

    c.execute("SELECT COUNT(*) FROM email_schedule WHERE status = 'bounced'")
    total_bounced = c.fetchone()[0]

    c.execute("SELECT COUNT(*) FROM email_schedule WHERE status = 'opened'")
    total_opened = c.fetchone()[0]

    c.execute("SELECT COUNT(*) FROM email_schedule WHERE status = 'failed'")
    total_failed = c.fetchone()[0]

    # Calculate average response rate if available
    c.execute("SELECT AVG(response_rate) FROM email_schedule WHERE response_rate IS NOT NULL")
    avg_response_rate = c.fetchone()[0]
    avg_response_rate = avg_response_rate if avg_response_rate else 'N/A'

    conn.close()

    # Return the stats as a dictionary
    return {
        'total_delivered': total_delivered,
        'total_bounced': total_bounced,
        'total_opened': total_opened,
        'total_failed': total_failed,
        'avg_response_rate': avg_response_rate
    }


def webhook():
    event_data = request.json
    print(f"Received event: {event_data}")

    # Extract relevant data from SendGrid webhook payload
    email_id = event_data.get('email')  # The email address
    event = event_data.get('event')  # The event type (e.g., delivered, bounced)

    # Update email status in the database
    update_email_status(event, email_id)
    
    return jsonify({"status": "success"}), 200

# Function to update email delivery status in the database
def update_email_status(event, email_id):
    conn = sqlite3.connect('email_scheduler.db')
    c = conn.cursor()

    # Update email status based on the event
    if event == "delivered":
        c.execute("UPDATE email_schedule SET status = 'delivered' WHERE email_id = ?", (email_id,))
    elif event == "bounce":
        c.execute("UPDATE email_schedule SET status = 'bounced' WHERE email_id = ?", (email_id,))
    elif event == "open":
        c.execute("UPDATE email_schedule SET status = 'opened' WHERE email_id = ?", (email_id,))
    elif event == "spamreport":
        c.execute("UPDATE email_schedule SET status = 'spam' WHERE email_id = ?", (email_id,))

    conn.commit()
    conn.close()

if __name__ == "__main__":
    app.run(debug=True)
