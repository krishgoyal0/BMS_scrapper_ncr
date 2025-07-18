import pandas as pd
import gspread
from datetime import datetime, timedelta
import os
import time
import json
from typing import Dict, List

# ========================
# SHARED CONFIGURATION (UNCHANGED)
# ========================
CONFIG = {
    'excel_file': 'events.xlsx',
    'service_account_file': 'service_account.json',
    'spreadsheet_name': 'report',
    'worksheet_name': 'NCR',
    'daily_reports_folder_id': '1pixEQ9Vu9Sq8SqN5PdFlqhuyKjkAjPqx',
    'event_history_folder_id': '1ACEskNlX6VLo1YSGl1N7RMlhnnWV2pxx',
    'backup_delay_seconds': 5,
    'historical_folder': 'historical'
}

# ========================
# SHARED UTILITIES (UNCHANGED)
# ========================
def log_message(message: str) -> None:
    print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] {message}")

def get_gspread_client():
    try:
        return gspread.service_account(CONFIG['service_account_file'])
    except Exception as e:
        log_message(f"Authentication failed: {str(e)}")
        raise

# ========================
# ORIGINAL UPLOAD SYSTEM (UNCHANGED)
# ========================
def upload_and_backup() -> bool:
    try:
        log_message("(Original System) Loading Excel data...")
        df = pd.read_excel(CONFIG['excel_file'])
        if df.empty:
            log_message("Warning: No data found in Excel file")
            return False

        gc = get_gspread_client()

        try:
            sh = gc.open(CONFIG['spreadsheet_name'])
            log_message(f"Opened existing spreadsheet: {CONFIG['spreadsheet_name']}")
        except gspread.SpreadsheetNotFound:
            sh = gc.create(CONFIG['spreadsheet_name'])
            log_message(f"Created new spreadsheet: {CONFIG['spreadsheet_name']}")

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
# EVENT TRACKING SYSTEM (MODIFIED TO FIX DUPLICATES)
# ========================
def sanitize_sheet_name(name: str) -> str:
    clean = (name[:95] + '..') if len(name) > 100 else name
    return ''.join(c for c in clean if c.isprintable())

def create_event_sheet(gc, sheet_name: str, event_data: Dict) -> None:
    try:
        spreadsheet = gc.create(sheet_name, folder_id=CONFIG['event_history_folder_id'])
        worksheet = spreadsheet.get_worksheet(0)
        worksheet.update([list(event_data.keys()), list(event_data.values())], 'A1')
        log_message(f"(Event System) Created new sheet: {sheet_name}")
    except Exception as e:
        log_message(f"(Event System) Error creating sheet {sheet_name}: {str(e)}")
        raise

def update_event_sheet(gc, sheet_name: str, event_data: Dict) -> None:
    try:
        spreadsheet = gc.open(sheet_name)
        worksheet = spreadsheet.get_worksheet(0)
        worksheet.append_row(list(event_data.values()))
        log_message(f"(Event System) Updated sheet: {sheet_name}")
    except Exception as e:
        log_message(f"(Event System) Error updating sheet {sheet_name}: {str(e)}")
        raise

def track_events() -> bool:
    try:
        today_date = datetime.now().strftime('%d-%m-%y')
        yesterday_date = (datetime.now() - timedelta(days=1)).strftime('%d-%m-%y')
        
        today_file = os.path.join(CONFIG['historical_folder'], f"{today_date}_aed.json")
        yesterday_file = os.path.join(CONFIG['historical_folder'], f"{yesterday_date}_aed.json")
        
        log_message(f"(Event System) Looking for files: {today_file} (today) and {yesterday_file} (yesterday)")
        
        if not os.path.exists(today_file):
            log_message(f"Error: Today's file '{today_file}' not found!")
            return False
            
        with open(today_file) as f:
            today_events = {e['event_name']: e for e in json.load(f)}
        
        yesterday_events = {}
        if os.path.exists(yesterday_file):
            with open(yesterday_file) as f:
                yesterday_events = {e['event_name']: e for e in json.load(f)}
        else:
            log_message("(Event System) No yesterday's file found - treating all events as new")
        
        gc = get_gspread_client()
        
        # Get all existing sheets in the folder once
        existing_sheets = {}
        try:
            for sheet in gc.list_spreadsheet_files(folder_id=CONFIG['event_history_folder_id']):
                existing_sheets[sheet['name']] = sheet['id']
        except Exception as e:
            log_message(f"(Event System) Warning: Could not list existing sheets - {str(e)}")
        
        for event_name, event_data in today_events.items():
            sheet_name = sanitize_sheet_name(event_name)
            is_new = event_name not in yesterday_events
            
            try:
                if sheet_name in existing_sheets:
                    # Sheet exists - update it
                    update_event_sheet(gc, sheet_name, event_data)
                else:
                    # Sheet doesn't exist - create new
                    create_event_sheet(gc, sheet_name, event_data)
            except Exception as e:
                log_message(f"(Event System) Error processing {sheet_name}: {str(e)}")
                continue
        
        return True

    except Exception as e:
        log_message(f"(Event System) Critical error: {str(e)}")
        return False

# ========================
# MAIN EXECUTION CONTROL (UNCHANGED)
# ========================
def main():
    log_message("=== Starting both systems ===")
    
    required_files = [
        CONFIG['service_account_file'],
        CONFIG['excel_file']
    ]
    
    for file in required_files:
        if not os.path.exists(file):
            log_message(f"Error: Required file '{file}' not found")
            exit(1)
    
    log_message("--- Running Upload System ---")
    upload_success = upload_and_backup()
    
    log_message("--- Running Event Tracking System ---")
    events_success = track_events()
    
    if upload_success and events_success:
        log_message("=== Both systems completed successfully ===")
        exit(0)
    else:
        log_message("=== One or both systems completed with errors ===")
        exit(1)

if __name__ == "__main__":
    main()