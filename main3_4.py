import re

# Function to create email body by replacing placeholders with actual data
def customize_email_body(template, row_data):
    """
    Replace placeholders in the template with actual data from the row.
    For example, {Company Name} will be replaced with the actual company name.
    """
    placeholders = {
        "{Company Name}": row_data.get('Company Name', ''),
        "{Name}": row_data.get('Name', ''),
        "{Email}": row_data.get('Email Id', ''),
        "{Address}": row_data.get('Address', '')
    }

    # Replace all placeholders with actual values
    for placeholder, value in placeholders.items():
        template = template.replace(placeholder, value)
    
    return template

# Example prompt input (could be inputted by the user in your UI)
email_template = """
Hello {Name},

We are reaching out from {Company Name} located in {Address}. 

We'd love to offer you our services and discuss potential collaborations.

Best regards,
Your Company Team
"""

# Example data fetched from Google Sheet (row data)
row_data = {
    'Company Name': 'ABOVO HOSPITALITY',
    'Name': 'Lijo Thomas',
    'Email Id': '121ec0045@iiitk.ac.in',
    'Address': 'S-12, Janta Market, Rajouri Garden, New Delhi, Delhi, 110027'
}

# Customize the email body using the row data
customized_email = customize_email_body(email_template, row_data)

print(customized_email)


import pandas as pd

# Example: Reading data from a CSV file (this will work for Google Sheets too if you convert it to a DataFrame)
# Assuming you have a DataFrame `df` from CSV or Google Sheet data
df = pd.DataFrame([
    {'Company Name': 'ABOVO HOSPITALITY', 'Name': 'Lijo Thomas', 'Email Id': '121ec0045@iiitk.ac.in', 'Address': 'S-12, Janta Market, Rajouri Garden, New Delhi, Delhi, 110027'},
    {'Company Name': 'ACCENTURE', 'Name': 'Sarmishtha Sinha', 'Email Id': '121ad0036@iiitk.ac.in', 'Address': 'Prestige Technopolis, 118, Dr.MH Maregowda Road, Audugodi,Bengaluru, Karnataka, India, 560029'}
])

# Email template with placeholders
email_template = """
Hello {Name},

We are reaching out from {Company Name} located in {Address}. 

We'd love to offer you our services and discuss potential collaborations.

Best regards,
Your Company Team
"""

# Function to generate customized email body for each row dynamically
def customize_email_body_dynamic(template, row_data):
    """
    Replace placeholders dynamically with the column names as placeholders.
    """
    for column in row_data:
        placeholder = f"{{{column}}}"
        value = row_data[column]
        template = template.replace(placeholder, str(value))
    
    return template

# Example: Loop through all rows and generate a customized email for each
for index, row in df.iterrows():
    row_data = row.to_dict()  # Convert the row to a dictionary
    customized_email = customize_email_body_dynamic(email_template, row_data)
    print(f"Customized Email for {row_data['Name']}:\n{customized_email}\n")
