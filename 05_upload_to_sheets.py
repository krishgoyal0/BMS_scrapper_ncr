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