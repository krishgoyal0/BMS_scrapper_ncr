import pandas as pd
import gspread
from datetime import datetime
import os

# --- Configuration ---
excel_file_name = 'events.xlsx'
service_account_key_file = 'service_account.json'
# service_account_key_file = os.environ.get('GOOGLE_CREDENTIALS', 'service_account.json')
google_sheet_name = 'TodayReport_BMS'
worksheet_name = 'Sheet1'
timestamp_cell = 'A1'  # Cell where timestamp will be written
timestamp_format = '%Y-%m-%d %H:%M:%S'

def upload_to_sheets():
    # 1. Read the Excel file
    if not os.path.exists(excel_file_name):
        print(f"Error: Excel file '{excel_file_name}' not found")
        return False

    try:
        df = pd.read_excel(excel_file_name)
        print(f"Successfully read data from '{excel_file_name}'")
    except Exception as e:
        print(f"Error reading Excel file: {e}")
        return False

    # 2. Authenticate with Google Sheets API
    if not os.path.exists(service_account_key_file):
        print(f"Error: Service account key file not found")
        return False

    try:
        gc = gspread.service_account(filename=service_account_key_file)
    except Exception as e:
        print(f"Authentication failed: {e}")
        return False

    # 3. Get or create the spreadsheet
    try:
        sh = gc.open(google_sheet_name)
    except gspread.exceptions.SpreadsheetNotFound:
        try:
            sh = gc.create(google_sheet_name)
            print(f"Created new Google Sheet: '{google_sheet_name}'")
        except Exception as e:
            print(f"Error creating sheet: {e}")
            return False

    # 4. Get or create the worksheet
    try:
        worksheet = sh.worksheet(worksheet_name)
    except gspread.exceptions.WorksheetNotFound:
        try:
            worksheet = sh.add_worksheet(
                title=worksheet_name,
                rows=str(len(df) + 10),
                cols=str(len(df.columns) + 5)
            )
            print(f"Created new worksheet: '{worksheet_name}'")
        except Exception as e:
            print(f"Error creating worksheet: {e}")
            return False

    # 5. Update the timestamp
    try:
        current_time = datetime.now().strftime(timestamp_format)
        worksheet.update(timestamp_cell, f"Last Updated: {current_time}")
        print(f"Updated timestamp in cell {timestamp_cell}")
    except Exception as e:
        print(f"Warning: Could not update timestamp - {e}")

    # 6. Upload the data
    try:
        data_to_upload = [df.columns.tolist()] + df.values.tolist()
        worksheet.update('A2', data_to_upload)
        print(f"Successfully uploaded data to Google Sheet")
        print(f"Sheet URL: {sh.url}")
        return True
    except Exception as e:
        print(f"Error updating worksheet: {e}")
        return False

if __name__ == "__main__":
    upload_to_sheets()