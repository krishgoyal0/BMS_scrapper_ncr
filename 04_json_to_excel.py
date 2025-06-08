import json
import pandas as pd

def json_to_excel(json_file_path, excel_file_path):
    """
    Convert JSON file to Excel format with custom event IDs
    """
    # Read JSON file
    with open(json_file_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    # Convert to DataFrame
    df = pd.DataFrame(data)
    
    # Add custom event IDs starting with #0001
    df.insert(0, 'event_id', [f"#{str(i+1).zfill(4)}" for i in range(len(df))])
    
    # Clean up data (optional)
    # Check if 'event_time' column exists before cleaning
    if 'event_time' in df.columns:
        df['event_time'] = df['event_time'].fillna('Not Specified')
    else:
        print("Warning: 'event_time' column not found in JSON data. Skipping cleanup for 'event_time'.")
    
    # Save to Excel
    df.to_excel(excel_file_path, index=False, engine='openpyxl')
    print(f"Successfully converted {json_file_path} to {excel_file_path}")

if __name__ == "__main__":
    # Configuration
    JSON_FILE = 'all_event_details.json'  # Path to your JSON file
    EXCEL_FILE = 'events.xlsx'           # Path for Excel output
    
    # Convert JSON to Excel
    json_to_excel(JSON_FILE, EXCEL_FILE)