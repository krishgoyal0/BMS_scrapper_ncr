import pandas as pd
import gspread
import os

# --- Configuration ---
excel_file_name = 'events.xlsx'
# service_account_key_file = 'service_account.json'
service_account_key_file = os.getenv("GOOGLE_SERVICE_ACCOUNT", "service_account.json")
google_sheet_name = 'TodayReport_BMS'
worksheet_name = 'Sheet1'

def upload_to_sheets():
    """
    Uploads data from a specified Excel file to a Google Sheet.

    This function performs the following steps:
    1. Reads data from an Excel file.
    2. Authenticates with the Google Sheets API using a service account.
    3. Opens an existing Google Sheet or creates a new one if it doesn't exist.
    4. Opens an existing worksheet within the spreadsheet or creates a new one.
    5. Uploads the DataFrame's data, including headers, to the worksheet.

    Returns:
        bool: True if the upload is successful, False otherwise.
    """

    # 1. Read the Excel file
    if not os.path.exists(excel_file_name):
        print(f"Error: Excel file '{excel_file_name}' not found. Please ensure it's in the same directory as the script.")
        return False

    try:
        df = pd.read_excel(excel_file_name)
        print(f"Successfully read data from '{excel_file_name}'. Rows: {len(df)}, Columns: {len(df.columns)}")
        if df.empty:
            print("Warning: The Excel file is empty. No data will be uploaded.")
            return False
    except Exception as e:
        print(f"Error reading Excel file: {e}")
        return False

    # 2. Authenticate with Google Sheets API
    if not os.path.exists(service_account_key_file):
        print(f"Error: Service account key file '{service_account_key_file}' not found. Please ensure it's in the same directory.")
        return False

    try:
        gc = gspread.service_account(filename=service_account_key_file)
        print("Successfully authenticated with Google Sheets API.")
    except Exception as e:
        print(f"Authentication failed: {e}. Please check your service account key file and permissions.")
        return False

    # 3. Get or create the spreadsheet
    try:
        sh = gc.open(google_sheet_name)
        print(f"Successfully opened Google Sheet: '{google_sheet_name}'")
    except gspread.exceptions.SpreadsheetNotFound:
        try:
            sh = gc.create(google_sheet_name)
            # Share the newly created spreadsheet with the service account email
            # (Important for collaborative access, if needed, though the service account itself can write)
            # You might need to get the service account email from your key file or Google Cloud Console
            # service_account_email = gc.auth.service_account_email # This is not directly available like this
            # sh.share(service_account_email, perm_type='user', role='writer')
            print(f"Created new Google Sheet: '{google_sheet_name}'")
        except Exception as e:
            print(f"Error creating Google Sheet '{google_sheet_name}': {e}")
            return False

    # 4. Get or create the worksheet
    try:
        worksheet = sh.worksheet(worksheet_name)
        print(f"Successfully opened worksheet: '{worksheet_name}'")
    except gspread.exceptions.WorksheetNotFound:
        try:
            # Added missing parenthesis here!
            worksheet = sh.add_worksheet(
                title=worksheet_name,
                rows=str(len(df) + 10),  # Add some buffer rows
                cols=str(len(df.columns) + 5) # Add some buffer columns
            )
            print(f"Created new worksheet: '{worksheet_name}'")
        except Exception as e:
            print(f"Error creating worksheet '{worksheet_name}': {e}")
            return False

    # 5. Upload the data
    try:
        # Prepare data: header row + data rows
        data_to_upload = [df.columns.tolist()] + df.values.tolist()
        worksheet.update('A1', data_to_upload)
        print(f"Successfully uploaded data to Google Sheet '{google_sheet_name}', worksheet '{worksheet_name}'.")
        print(f"You can view the sheet here: {sh.url}")
        return True
    except Exception as e:
        print(f"Error updating worksheet: {e}. Ensure the service account has write permissions.")
        return False

if __name__ == "__main__":
    print("Starting data upload to Google Sheets...")
    success = upload_to_sheets()
    if success:
        print("Upload process completed successfully!")
    else:
        print("Upload process failed.")