import pandas as pd
import gspread
import os # Import os to check for file existence

# --- Configuration ---
excel_file_name = 'events.xlsx' # <--- IMPORTANT: Change this to your Excel file name
service_account_key_file = 'service_account.json' # <--- IMPORTANT: Ensure this file is in the same directory or provide full path
google_sheet_name = 'TodayReport_BMS' # <--- IMPORTANT: Name you want for your Google Sheet
worksheet_name = 'Sheet1' # <--- IMPORTANT: Name of the worksheet within the Google Sheet

# 1. Read the Excel file
if not os.path.exists(excel_file_name):
    print(f"Error: Excel file '{excel_file_name}' not found in the current directory.")
    print("Please make sure the Excel file is in the same directory as the script.")
    exit() # Exit if the Excel file is not found

try:
    df = pd.read_excel(excel_file_name)
    print(f"Successfully read data from '{excel_file_name}'.")
except Exception as e:
    print(f"Error reading Excel file '{excel_file_name}': {e}")
    exit()

# Convert DataFrame to a list of lists (including headers)
# gspread expects a list of lists where each inner list is a row.
data_to_upload = [df.columns.tolist()] + df.values.tolist()

# 2. Authenticate with Google Sheets API
if not os.path.exists(service_account_key_file):
    print(f"Error: Service account key file '{service_account_key_file}' not found.")
    print("Please download it from Google Cloud Console and place it in the same directory.")
    exit()

try:
    gc = gspread.service_account(filename=service_account_key_file)
    print("Successfully authenticated with Google Sheets API.")
except Exception as e:
    print(f"Authentication failed. Check your '{service_account_key_file}' file and permissions: {e}")
    exit()

# 3. Interact with Google Sheet
sh = None
try:
    # Try to open an existing spreadsheet
    sh = gc.open(google_sheet_name)
    print(f"Opened existing Google Sheet: '{google_sheet_name}'.")
except gspread.exceptions.SpreadsheetNotFound:
    # If not found, create a new one
    print(f"Google Sheet '{google_sheet_name}' not found, creating a new one...")
    try:
        sh = gc.create(google_sheet_name)
        print(f"Successfully created new Google Sheet: '{google_sheet_name}'.")
        # Share the new sheet with your own email or service account email
        # You can find your service account's email in the service_account.json file
        # under the 'client_email' key.
        # Example: sh.share('your-personal-email@example.com', perm_type='user', role='writer')
        # It's also good practice to share with the service account itself if you created it without initial sharing.
    except Exception as e:
        print(f"Error creating new Google Sheet '{google_sheet_name}': {e}")
        exit()

if sh is None: # Should not happen if previous steps are successful, but for safety
    print("Failed to get or create Google Sheet object.")
    exit()

worksheet = None
try:
    # Try to select an existing worksheet
    worksheet = sh.worksheet(worksheet_name)
    print(f"Opened existing worksheet: '{worksheet_name}'.")
except gspread.exceptions.WorksheetNotFound:
    # If the worksheet doesn't exist, create it
    print(f"Worksheet '{worksheet_name}' not found, creating a new one...")
    try:
        # Add a new worksheet with initial rows/cols if needed
        worksheet = sh.add_worksheet(title=worksheet_name, rows=str(len(data_to_upload) + 10), cols=str(len(df.columns) + 5))
        print(f"Successfully created new worksheet: '{worksheet_name}'.")
    except Exception as e:
        print(f"Error creating new worksheet '{worksheet_name}': {e}")
        exit()

if worksheet is None: # Safety check
    print("Failed to get or create worksheet object.")
    exit()

# Clear existing content of the worksheet if you want to overwrite completely
# Be careful with this! It will delete all data in the specified worksheet.
# worksheet.clear() 
# print(f"Cleared existing data in worksheet '{worksheet_name}'.")

# Write the data to the worksheet, starting from cell A1
try:
    worksheet.update('A1', data_to_upload)
    print(f"Successfully uploaded data from '{excel_file_name}' to Google Sheet '{google_sheet_name}', worksheet '{worksheet_name}'.")
    print(f"You can view your Google Sheet here: {sh.url}")
except Exception as e:
    print(f"Error updating worksheet with data: {e}")