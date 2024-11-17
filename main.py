import gspread
from google.auth.transport.requests import Request
from google.oauth2.service_account import Credentials

# Load the credentials from your JSON file
def authenticate_google_sheets():
    creds = None
    SCOPES = ['https://www.googleapis.com/auth/spreadsheets.readonly']
    
    # The credentials JSON file you downloaded
    creds = Credentials.from_service_account_file(r'C:\Users\iamra\OneDrive\Desktop\Brekout_ai\credent.json', scopes=SCOPES)
    
    # If credentials are expired, refresh them
    if creds and creds.expired and creds.refresh_token:
        creds.refresh(Request())
    
    return creds

# Function to read data from a Google Sheet
def read_google_sheet(sheet_id, range_name):
    creds = authenticate_google_sheets()
    
    # Using gspread to connect to the Google Sheets API
    client = gspread.authorize(creds)
    
    # Open the Google Sheet using its ID
    sheet = client.open_by_key(sheet_id)
    
    # Get data from a specific range (e.g., A1:D100)
    records = sheet.values_get(range_name)['values']
    
    return records

# Example: Reading the sheet with the relevant data
sheet_id = '1y0eIOxPDGDIl7Lwz_SHaxkSAwtOJxFLGsoEV9qlrSvI'  # Sheet ID from the URL
range_name = 'Sheet1!A1:D100'  # Specify the range you want to fetch
data = read_google_sheet(sheet_id, range_name)

# Print fetched data
for row in data:
    print(row)  # This will print the rows of your sheet




