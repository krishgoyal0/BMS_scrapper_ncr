# import pandas as pd
# import gspread
# import os

# # --- Configuration ---
# excel_file_name = 'events.xlsx'
# # service_account_key_file = 'service_account.json'
# service_account_key_file = os.getenv("GOOGLE_SERVICE_ACCOUNT", "service_account.json")
# google_sheet_name = 'TodayReport_BMS'
# worksheet_name = 'Sheet1'

# def upload_to_sheets():
#     """
#     Uploads data from a specified Excel file to a Google Sheet.

#     This function performs the following steps:
#     1. Reads data from an Excel file.
#     2. Authenticates with the Google Sheets API using a service account.
#     3. Opens an existing Google Sheet or creates a new one if it doesn't exist.
#     4. Opens an existing worksheet within the spreadsheet or creates a new one.
#     5. Uploads the DataFrame's data, including headers, to the worksheet.

#     Returns:
#         bool: True if the upload is successful, False otherwise.
#     """

#     # 1. Read the Excel file
#     if not os.path.exists(excel_file_name):
#         print(f"Error: Excel file '{excel_file_name}' not found. Please ensure it's in the same directory as the script.")
#         return False

#     try:
#         df = pd.read_excel(excel_file_name)
#         print(f"Successfully read data from '{excel_file_name}'. Rows: {len(df)}, Columns: {len(df.columns)}")
#         if df.empty:
#             print("Warning: The Excel file is empty. No data will be uploaded.")
#             return False
#     except Exception as e:
#         print(f"Error reading Excel file: {e}")
#         return False

#     # 2. Authenticate with Google Sheets API
#     if not os.path.exists(service_account_key_file):
#         print(f"Error: Service account key file '{service_account_key_file}' not found. Please ensure it's in the same directory.")
#         return False

#     try:
#         gc = gspread.service_account(filename=service_account_key_file)
#         print("Successfully authenticated with Google Sheets API.")
#     except Exception as e:
#         print(f"Authentication failed: {e}. Please check your service account key file and permissions.")
#         return False

#     # 3. Get or create the spreadsheet
#     try:
#         sh = gc.open(google_sheet_name)
#         print(f"Successfully opened Google Sheet: '{google_sheet_name}'")
#     except gspread.exceptions.SpreadsheetNotFound:
#         try:
#             sh = gc.create(google_sheet_name)
#             # Share the newly created spreadsheet with the service account email
#             # (Important for collaborative access, if needed, though the service account itself can write)
#             # You might need to get the service account email from your key file or Google Cloud Console
#             # service_account_email = gc.auth.service_account_email # This is not directly available like this
#             # sh.share(service_account_email, perm_type='user', role='writer')
#             print(f"Created new Google Sheet: '{google_sheet_name}'")
#         except Exception as e:
#             print(f"Error creating Google Sheet '{google_sheet_name}': {e}")
#             return False

#     # 4. Get or create the worksheet
#     try:
#         worksheet = sh.worksheet(worksheet_name)
#         print(f"Successfully opened worksheet: '{worksheet_name}'")
#     except gspread.exceptions.WorksheetNotFound:
#         try:
#             # Added missing parenthesis here!
#             worksheet = sh.add_worksheet(
#                 title=worksheet_name,
#                 rows=str(len(df) + 10),  # Add some buffer rows
#                 cols=str(len(df.columns) + 5) # Add some buffer columns
#             )
#             print(f"Created new worksheet: '{worksheet_name}'")
#         except Exception as e:
#             print(f"Error creating worksheet '{worksheet_name}': {e}")
#             return False

#     # 5. Upload the data
#     try:
#         # Prepare data: header row + data rows
#         data_to_upload = [df.columns.tolist()] + df.values.tolist()
#         worksheet.update('A1', data_to_upload)
#         print(f"Successfully uploaded data to Google Sheet '{google_sheet_name}', worksheet '{worksheet_name}'.")
#         print(f"You can view the sheet here: {sh.url}")
#         return True
#     except Exception as e:
#         print(f"Error updating worksheet: {e}. Ensure the service account has write permissions.")
#         return False

# if __name__ == "__main__":
#     print("Starting data upload to Google Sheets...")
#     success = upload_to_sheets()
#     if success:
#         print("Upload process completed successfully!")
#     else:
#         print("Upload process failed.")

# import pandas as pd
# import gspread
# import os
# from pathlib import Path
# import json

# # --- Configuration ---
# excel_file_name = 'events.xlsx'
# service_account_key_file = os.path.join(os.getcwd(), 'service_account.json')
# google_sheet_name = 'TodayReport_BMS'
# worksheet_name = 'Sheet1'

# def upload_to_sheets():
#     """
#     Uploads data from a specified Excel file to a Google Sheet.
    
#     Returns:
#         bool: True if upload is successful, False otherwise.
#     """
#     print("\n=== Starting Google Sheets Upload Process ===")
#     print(f"Current working directory: {os.getcwd()}")
#     print(f"Service account file path: {service_account_key_file}")
#     print(f"Directory contents: {os.listdir()}")
    
#     # 1. Verify and read Excel file
#     try:
#         if not os.path.exists(excel_file_name):
#             raise FileNotFoundError(f"Excel file '{excel_file_name}' not found")
            
#         df = pd.read_excel(excel_file_name)
#         print(f"\nSuccessfully read data from '{excel_file_name}'")
#         print(f"Data shape: {len(df)} rows, {len(df.columns)} columns")
        
#         if df.empty:
#             print("Warning: The Excel file is empty")
#             return False
            
#     except Exception as e:
#         print(f"\nError reading Excel file: {str(e)}")
#         return False

#     # 2. Verify and authenticate with service account
#     try:
#         if not os.path.exists(service_account_key_file):
#             raise FileNotFoundError("Service account JSON file not found")
            
#         # Validate JSON file
#         with open(service_account_key_file) as f:
#             json.load(f)  # Test if valid JSON
            
#         gc = gspread.service_account(filename=service_account_key_file)
#         print("\nSuccessfully authenticated with Google Sheets API")
        
#     except Exception as e:
#         print(f"\nAuthentication failed: {str(e)}")
#         return False

#     # 3. Access or create spreadsheet
#     try:
#         try:
#             sh = gc.open(google_sheet_name)
#             print(f"\nOpened existing Google Sheet: '{google_sheet_name}'")
#         except gspread.exceptions.SpreadsheetNotFound:
#             sh = gc.create(google_sheet_name)
#             print(f"\nCreated new Google Sheet: '{google_sheet_name}'")
            
#         print(f"Spreadsheet URL: {sh.url}")
        
#     except Exception as e:
#         print(f"\nError accessing spreadsheet: {str(e)}")
#         return False

#     # 4. Access or create worksheet
#     try:
#         try:
#             worksheet = sh.worksheet(worksheet_name)
#             print(f"\nOpened existing worksheet: '{worksheet_name}'")
#         except gspread.exceptions.WorksheetNotFound:
#             worksheet = sh.add_worksheet(
#                 title=worksheet_name,
#                 rows=str(len(df) + 10),
#                 cols=str(len(df.columns) + 5)
#             )
#             print(f"\nCreated new worksheet: '{worksheet_name}'")
            
#     except Exception as e:
#         print(f"\nError accessing worksheet: {str(e)}")
#         return False

#     # 5. Upload data
#     try:
#         # Clear existing data if any
#         worksheet.clear()
        
#         # Prepare and upload data
#         data_to_upload = [df.columns.tolist()] + df.values.tolist()
#         worksheet.update('A1', data_to_upload)
        
#         print("\nSuccessfully uploaded data to Google Sheets")
#         print(f"Updated range: A1:{chr(64 + len(df.columns))}{len(df) + 1}")
#         return True
        
#     except Exception as e:
#         print(f"\nError uploading data: {str(e)}")
#         return False

# if __name__ == "__main__":
#     print("Starting data upload to Google Sheets...")
#     success = upload_to_sheets()
    
#     if success:
#         print("\n=== Upload completed successfully! ===")
#     else:
#         print("\n=== Upload failed ===")
#         exit(1)


import pandas as pd
import gspread
import os
import json
from datetime import datetime

# Configuration
CONFIG = {
    'excel_file': 'events.xlsx',
    'service_account_file': 'service_account.json',
    'spreadsheet_name': 'TodayReport_BMS',
    'worksheet_name': 'Sheet1'
}

def log_message(message):
    """Helper function for consistent logging"""
    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    print(f"[{timestamp}] {message}")

def verify_files():
    """Verify required files exist"""
    log_message("Verifying required files...")
    
    if not os.path.exists(CONFIG['excel_file']):
        log_message(f"ERROR: Excel file '{CONFIG['excel_file']}' not found")
        log_message(f"Current directory contents: {os.listdir()}")
        return False
    
    if not os.path.exists(CONFIG['service_account_file']):
        log_message(f"ERROR: Service account file '{CONFIG['service_account_file']}' not found")
        return False
        
    try:
        with open(CONFIG['service_account_file']) as f:
            json.load(f)  # Validate JSON
    except Exception as e:
        log_message(f"ERROR: Invalid service account JSON: {str(e)}")
        return False
    
    return True

def upload_data():
    """Main upload function"""
    try:
        # 1. Load Excel data
        log_message("Loading Excel data...")
        df = pd.read_excel(CONFIG['excel_file'])
        log_message(f"Loaded {len(df)} records with {len(df.columns)} columns")
        
        if df.empty:
            log_message("WARNING: Empty dataframe - no data to upload")
            return False

        # 2. Authenticate with Google
        log_message("Authenticating with Google Sheets...")
        gc = gspread.service_account(filename=CONFIG['service_account_file'])
        
        # 3. Access Spreadsheet
        try:
            sh = gc.open(CONFIG['spreadsheet_name'])
            log_message(f"Opened existing spreadsheet: {CONFIG['spreadsheet_name']}")
        except gspread.SpreadsheetNotFound:
            sh = gc.create(CONFIG['spreadsheet_name'])
            log_message(f"Created new spreadsheet: {CONFIG['spreadsheet_name']}")
        
        # 4. Access Worksheet
        try:
            worksheet = sh.worksheet(CONFIG['worksheet_name'])
            log_message(f"Opened existing worksheet: {CONFIG['worksheet_name']}")
        except gspread.WorksheetNotFound:
            worksheet = sh.add_worksheet(
                title=CONFIG['worksheet_name'],
                rows=str(len(df) + 10),
                cols=str(len(df.columns) + 5)
            )
            log_message(f"Created new worksheet: {CONFIG['worksheet_name']}")
        
        # 5. Upload data
        log_message("Uploading data...")
        worksheet.clear()
        data = [df.columns.tolist()] + df.values.tolist()
        worksheet.update('A1', data)
        
        log_message(f"Success! Data uploaded to: {sh.url}")
        return True
        
    except Exception as e:
        log_message(f"ERROR: {str(e)}")
        return False

if __name__ == "__main__":
    log_message("Starting Google Sheets upload process")
    
    if not verify_files():
        log_message("File verification failed")
        exit(1)
        
    success = upload_data()
    
    if success:
        log_message("Process completed successfully")
        exit(0)
    else:
        log_message("Process failed")
        exit(1)