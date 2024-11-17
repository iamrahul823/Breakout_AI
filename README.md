Custom Email Sender - Internship Project
Overview
This project aims to build a custom email-sending application with a front-end dashboard that performs a variety of tasks. The application reads data from a Google Sheet or CSV file, customizes email content using an LLM (Groq API), allows scheduling and throttling of emails, and provides real-time analytics for sent emails. The project integrates with Email Service Providers (ESP) like SendGrid or Mailgun to track email delivery status.

Internship Details
Stipend: €200-400 per month, based on experience and performance
Duration: 3 months
Location: Remote
Project Deadline
Deadline: November 18th, 2024
Submission: Please send your completed project, including the GitHub repository link, to kapil@breakoutinvesting.in
Features
Google Sheets or CSV Integration:

Reads email data (e.g., Company Name, Location, Email, Products) from a Google Sheet or CSV file.
Email Integration:

Allows users to connect their email account (Gmail, Outlook, etc.) using OAuth2 or SMTP/ESP for secure email sending.
Customizable Email Content:

Allows users to provide a customizable prompt with placeholders (e.g., {Company Name}) which get replaced with actual data from the Google Sheet or CSV.
Email Scheduling and Throttling:

Users can schedule emails for specific times or stagger the delivery of emails over time.
Throttling options to ensure emails are sent within provider limits (e.g., emails per minute/hour).
Real-Time Email Status and Analytics:

Displays real-time metrics, including:
Total Emails Sent
Emails Pending
Emails Scheduled
Emails Failed
Response Rate (if available)
ESP Integration for Delivery Tracking:

Integrates with ESPs such as SendGrid, Amazon SES, or Mailgun to track delivery statuses like Delivered, Opened, Bounced, and Failed.
Real-Time Dashboard:

Displays email send status and delivery status in a user-friendly dashboard.
Real-time updates using WebSockets or polling.
Requirements
Python 3.x
Libraries:
gspread (for Google Sheets API)
google-auth, google-auth-oauthlib, google-auth-httplib2 (for authentication)
schedule (for scheduling emails)
requests (for HTTP requests)
sqlite3 (for database management)
Groq (for content generation)
sendgrid or mailgun (for ESP integration)
Setup Instructions
1. Install Dependencies
To set up the project, first, clone the repository and install the required libraries:

bash
Copy code
git clone https://github.com/iamrahul823/CustomEmailSender.git
cd CustomEmailSender
pip install -r requirements.txt
2. Configure Google Sheets API
Follow the steps to create a Google Sheets API project in the Google Cloud Console.
Download the credentials.json file and place it in the root of the project.
3. Configure ESP Integration
Choose an ESP provider (e.g., SendGrid, Mailgun) and create an account.
Obtain the API key and set it in the .env file for SendGrid or Mailgun API.
Example .env file:

env
Copy code
SENDGRID_API_KEY=your_sendgrid_api_key_here
GROQ_API_KEY=your_groq_api_key_here
4. Configure Email Sending
Use OAuth2 to authenticate your Gmail account or configure SMTP settings for other email services.
Ensure the email service you use supports the required API integrations (OAuth2 or SMTP).
5. Run the Application
To start the application, simply run:

bash
Copy code
python app.py
This will start the backend, and you can interact with the dashboard via your web browser.

Usage
Upload Data:

Provide a Google Sheet or CSV file with the necessary columns (e.g., Company Name, Location, Email, Products).
Connect Email Account:

Follow the authentication steps to connect your email account (e.g., Gmail via OAuth2 or use SMTP).
Create Custom Email Content:

Input a prompt with placeholders for the email content (e.g., "Hello {Company Name}, we are excited to collaborate with you").
Schedule Emails:

Choose a time to schedule emails or set a throttling rate to avoid sending too many emails at once.
Track Analytics:

View real-time metrics on email send status, delivery, and performance in the dashboard.
Example Output
Company Name	Email Status	Delivery Status	Opened
ABC Corp	Sent	Delivered	Yes
XYZ Ltd	Scheduled	N/A	N/A
DEF Inc	Failed	Bounced	No
Evaluation Criteria
Functionality: The application should meet all the specified requirements including email scheduling, analytics, and ESP integration.
Code Quality: The code should be well-structured, documented, and maintainable.
User Experience: The front-end dashboard should be intuitive and easy to use.
Reliability: The solution should gracefully handle errors, rate limits, and ESP limits.
Documentation: The README should provide clear and detailed setup and usage instructions.
