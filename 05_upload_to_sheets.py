import pandas as pd
import gspread
from datetime import datetime, timedelta
import os
import time
import json
from typing import Dict, List

# ========================
# SHARED CONFIGURATION
# ========================
CONFIG = {
    # Original upload configuration
    'excel_file': 'events.xlsx',
    'service_account_file': 'service_account.json',
    'spreadsheet_name': 'report',
    'worksheet_name': 'NCR',
    'daily_reports_folder_id': '1pixEQ9Vu9Sq8SqN5PdFlqhuyKjkAjPqx',
    
    # Event tracking configuration
    # 'event_history_folder_id': '1Gnrt7hTh1kVdt_jk1nhHWXawNOFHQKpq',
    'event_history_folder_id': '1ACEskNlX6VLo1YSGl1N7RMlhnnWV2pxx',
    'backup_delay_seconds': 5,
    'historical_folder': 'historical'  # Folder for dated JSON files
}

# ========================
# SHARED UTILITIES
# ========================
def log_message(message: str) -> None:
    """Standard logging function"""
    print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] {message}")

def get_gspread_client():
    """Shared authentication for Google Sheets"""
    try:
        return gspread.service_account(CONFIG['service_account_file'])
    except Exception as e:
        log_message(f"Authentication failed: {str(e)}")
        raise

# ========================
# ORIGINAL UPLOAD SYSTEM
# ========================
def upload_and_backup() -> bool:
    """Uploads Excel data to main spreadsheet and creates backup"""
    try:
        log_message("(Original System) Loading Excel data...")
        df = pd.read_excel(CONFIG['excel_file'])
        if df.empty:
            log_message("Warning: No data found in Excel file")
            return False

        gc = get_gspread_client()

        # Main spreadsheet operations
        try:
            sh = gc.open(CONFIG['spreadsheet_name'])
            log_message(f"Opened existing spreadsheet: {CONFIG['spreadsheet_name']}")
        except gspread.SpreadsheetNotFound:
            sh = gc.create(CONFIG['spreadsheet_name'])
            log_message(f"Created new spreadsheet: {CONFIG['spreadsheet_name']}")

        # Worksheet operations
        try:
            worksheet = sh.worksheet(CONFIG['worksheet_name'])
        except gspread.WorksheetNotFound:
            worksheet = sh.add_worksheet(
                title=CONFIG['worksheet_name'],
                rows=len(df)+10,
                cols=len(df.columns)+5
            )
        
        worksheet.clear()
        worksheet.update([df.columns.tolist()] + df.values.tolist())
        log_message(f"Data updated in worksheet: {CONFIG['worksheet_name']}")

        # Backup with rate limiting
        time.sleep(CONFIG['backup_delay_seconds'])
        backup_name = f"{datetime.now().strftime('%d-%m-%Y')}_{CONFIG['spreadsheet_name']}"
        new_file = gc.copy(
            file_id=sh.id,
            title=backup_name,
            copy_permissions=False,
            folder_id=CONFIG['daily_reports_folder_id']
        )
        log_message(f"Backup created: {backup_name}")
        return True

    except Exception as e:
        log_message(f"(Original System) Error: {str(e)}")
        return False

# ========================
# EVENT TRACKING SYSTEM
# ========================
def sanitize_sheet_name(name: str) -> str:
    """Make event names safe for Google Sheets"""
    clean = (name[:95] + '..') if len(name) > 100 else name
    return ''.join(c for c in clean if c.isprintable())

def create_event_sheet(gc, sheet_name: str, event_data: Dict) -> None:
    """Create new event sheet"""
    spreadsheet = gc.create(sheet_name, folder_id=CONFIG['event_history_folder_id'])
    worksheet = spreadsheet.get_worksheet(0)
    worksheet.update([list(event_data.keys()), list(event_data.values())], 'A1')
    log_message(f"(Event System) Created new sheet: {sheet_name}")

def update_event_sheet(gc, sheet_name: str, event_data: Dict) -> None:
    """Update existing event sheet"""
    spreadsheet = gc.open(sheet_name)
    worksheet = spreadsheet.get_worksheet(0)
    worksheet.append_row(list(event_data.values()))
    log_message(f"(Event System) Updated sheet: {sheet_name}")

def track_events() -> bool:
    """Tracks events using dated JSON files from historical folder"""
    try:
        # Get today's and yesterday's dates in DD-MM-YY format
        today_date = datetime.now().strftime('%d-%m-%y')
        yesterday_date = (datetime.now() - timedelta(days=1)).strftime('%d-%m-%y')
        
        # Build file paths
        today_file = os.path.join(CONFIG['historical_folder'], f"{today_date}_aed.json")
        yesterday_file = os.path.join(CONFIG['historical_folder'], f"{yesterday_date}_aed.json")
        
        log_message(f"(Event System) Looking for files: {today_file} (today) and {yesterday_file} (yesterday)")
        
        # Verify today's file exists (required)
        if not os.path.exists(today_file):
            log_message(f"Error: Today's file '{today_file}' not found!")
            return False
            
        # Load today's data
        with open(today_file) as f:
            today_events = {e['event_name']: e for e in json.load(f)}
        
        # Load yesterday's data if available
        yesterday_events = {}
        if os.path.exists(yesterday_file):
            with open(yesterday_file) as f:
                yesterday_events = {e['event_name']: e for e in json.load(f)}
        else:
            log_message("(Event System) No yesterday's file found - treating all events as new")
        
        # Process events
        gc = get_gspread_client()
        for event_name, event_data in today_events.items():
            is_new = event_name not in yesterday_events
            sheet_name = sanitize_sheet_name(event_name)
            
            try:
                if is_new:
                    create_event_sheet(gc, sheet_name, event_data)
                else:
                    update_event_sheet(gc, sheet_name, event_data)
            except Exception as e:
                log_message(f"(Event System) Error processing {sheet_name}: {str(e)}")
        
        return True

    except Exception as e:
        log_message(f"(Event System) Critical error: {str(e)}")
        return False

# ========================
# MAIN EXECUTION CONTROL
# ========================
def main():
    """Run both systems sequentially"""
    log_message("=== Starting both systems ===")
    
    # Verify required files exist
    required_files = [
        CONFIG['service_account_file'],
        CONFIG['excel_file']
    ]
    
    for file in required_files:
        if not os.path.exists(file):
            log_message(f"Error: Required file '{file}' not found")
            exit(1)
    
    # Run upload system
    log_message("--- Running Upload System ---")
    upload_success = upload_and_backup()
    
    # Run event tracking system
    log_message("--- Running Event Tracking System ---")
    events_success = track_events()
    
    # Final status
    if upload_success and events_success:
        log_message("=== Both systems completed successfully ===")
        exit(0)
    else:
        log_message("=== One or both systems completed with errors ===")
        exit(1)

if __name__ == "__main__":
    main()