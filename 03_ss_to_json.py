from PIL import Image
import pytesseract
import json
import re
import os
from pathlib import Path

def extract_event_details(image_path):
    try:
        # Open the image
        img = Image.open(image_path)
        
        # Get image dimensions
        width, height = img.size

        # Widened crop to capture price section too
        right_pane = img.crop((width * 0.5, 0, width, height))

        # Extract text from the right pane
        right_pane_text = pytesseract.image_to_string(right_pane)

        details = {
            'event_name': Path(image_path).stem.replace('_', ' '),
            'date_range': None,
            'event_end_date': None,

            'event_time': None,
            'duration': None,
            'age_limit': None,
            'language': None,
            'venue': None,
            'price': None,
            'seats_status': None,
            'source_image': Path(image_path).name
        }

        lines = [line.strip() for line in right_pane_text.split('\n') if line.strip()]

        for i, line in enumerate(lines):
            line_lower = line.lower()

            # Date
            date_matches = re.findall(
                r'(?:Mon|Tue|Wed|Thu|Fri|Sat|Sun)?\s*\d{1,2}\s+(?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)\s+\d{4}',
                line
            )
            if date_matches and not details['date_range']:
                details['date_range'] = date_matches[0]
                if len(date_matches) > 1:
                    details['event_end_date'] = date_matches[1]
                continue


            # Time
            time_match = re.search(r'\b\d{1,2}:\d{2}\s*(?:AM|PM)?\b', line, re.IGNORECASE)
            if time_match and not details['event_time']:
                details['event_time'] = time_match.group(0)
                continue

            # Duration
            if ('hour' in line_lower or 'min' in line_lower) and re.search(r'\d+', line) and not details['duration']:
                details['duration'] = line
                continue

            # Age Limit
            if ('age limit' in line_lower or 'yrs' in line_lower) and not details['age_limit']:
                details['age_limit'] = line
                continue

            # Language
            if not details['language'] and any(lang in line for lang in ['Hindi', 'English', 'Tamil', 'Telugu', 'Kannada', 'Malayalam']):
                details['language'] = line
                continue

            # Venue
            # Venue
            if details['language'] is not None and not details['venue']:
                if ':' in line or any(keyword in line_lower for keyword in ['arena', 'stadium', 'center', 'centre', 'hall', 'theatre', 'club', 'venue']):
                    # Check if line ends with ':' and next line exists
                    if line.endswith(':') and i + 1 < len(lines):
                        details['venue'] = f"{line} {lines[i+1]}".strip()
                    else:
                        details['venue'] = line
                    continue
            if details['venue']:
                details['venue'] = re.sub(r'<\d+', '', details['venue']).strip().rstrip(',;:-')

            # Skip time-misinterpreted lines
            if details['event_time'] is None and ':' in line and re.search(r'\b\d{1,2}:\d{2}\b', line):
                continue

            # Price extraction
            clean_line = re.sub(r'(?<!\d)2\s*([.,]?\d{2,6})', r'\1', line)

            price_match = re.search(
                r'(?:₹|Rs\.?|INR)?\s*[\.:]?\s*(\d{2,6})(?:\.\d{1,2})?\s*(onwards|only)?',
                clean_line
            )

            if price_match and not details['price']:
                value = price_match.group(1)
                suffix = price_match.group(2) or ''

                if value.isdigit() and (int(value) >= 50 or suffix):
                    details['price'] = f"{value} {suffix}".strip()
                continue

        # Seats Status
        for line in lines:
            line_lower = line.lower()
            if 'available' in line_lower and details['seats_status'] is None:
                details['seats_status'] = 'Available'
                break
            elif ('fast filling' in line_lower or 'filling fast' in line_lower) and details['seats_status'] is None:
                details['seats_status'] = 'Fast Filling'
                break
            elif 'sold out' in line_lower and details['seats_status'] is None:
                details['seats_status'] = 'Sold Out'
                break
            elif 'full' in line_lower and 'house' in line_lower and details['seats_status'] is None:
                details['seats_status'] = 'Sold Out'
                break

        # Clean Up Noisy Fields
        if details['age_limit']:
            match = re.search(r'(\d+\s*yrs\s*\+?)', details['age_limit'], re.IGNORECASE)
            if match:
                details['age_limit'] = match.group(1).replace(' ', '')
            else:
                details['age_limit'] = None

        if details['duration']:
            details['duration'] = re.sub(r'^[^\d]*', '', details['duration'])

        if details['language']:
            details['language'] = details['language'].replace('By', '').strip()

        if details['price'] and not details['price'].startswith(('₹', 'Rs')):
            details['price'] = f"₹ {details['price']}".strip()

        for key in details:
            if not details[key]:
                details[key] = "-"

        return details

    except Exception as e:
        print(f"Error processing {image_path}: {str(e)}")
        return {
            'event_name': Path(image_path).stem.replace('_', ' '),
            'error': str(e),
            'source_image': Path(image_path).name
        }

def process_screenshots_folder(folder_path='screenshots'):
    all_events = []
    
    # Get all PNG files in the screenshots folder
    screenshot_files = sorted(
        [f for f in os.listdir(folder_path) if f.lower().endswith('.png')],
        key=lambda x: int(x.split('_')[0]) if x.split('_')[0].isdigit() else 0
    )
    
    if not screenshot_files:
        print(f"No PNG files found in {folder_path} directory")
        return all_events
    
    print(f"Found {len(screenshot_files)} screenshots to process...")
    
    for screenshot_file in screenshot_files:
        image_path = os.path.join(folder_path, screenshot_file)
        print(f"Processing: {screenshot_file}")
        
        event_details = extract_event_details(image_path)
        all_events.append(event_details)
    
    return all_events

def save_to_json(data, output_file='all_event_details.json'):
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=4, ensure_ascii=False)

if __name__ == "__main__":
    # Process all screenshots in the folder
    all_event_data = process_screenshots_folder()
    
    if all_event_data:
        # Save all data to a single JSON file
        save_to_json(all_event_data)
        print(f"\nSuccessfully processed {len(all_event_data)} screenshots")
        print("All event details have been saved to all_event_details.json")
        
        # Print summary
        # print("\nSummary of extracted data:")
        # for event in all_event_data:
        #     print(f"\nEvent: {event.get('event_name', 'N/A')}")
        #     print(f"Date: {event.get('date_range', 'N/A')}")
        #     print(f"Time: {event.get('event_time', 'N/A')}")
        #     print(f"Price: {event.get('price', 'N/A')}")
    else:
        print("No event data was processed.")