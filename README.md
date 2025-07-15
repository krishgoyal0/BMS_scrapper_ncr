# 🎫 BookMyShow Event Tracker (Delhi-NCR)

This project automates the process of **scraping**, **analyzing**, and **tracking** newly added or fast-filling events on BookMyShow for the Delhi-NCR region. It captures daily event data, processes screenshots, extracts key event details, and pushes everything to Google Sheets for easy monitoring.

---

## 📁 Project Workflow

### 1. `01_url_fetcher.py`  
Scrapes the BookMyShow events page and extracts event cards from the Delhi-NCR section using Playwright. It compares today's data with yesterday's and generates a daily report of newly added and removed events.

### 2. `02_url_to_ss.py`  
Parses the daily report and captures **initial screenshots** of each newly listed event. Adds retry logic and user-agent rotation for stealth.

### 3. `03_ss_to_json.py`  
Extracts event details (date, time, venue, language, price, etc.) from screenshots using **OCR (Tesseract)** and saves the structured output to a JSON file (`all_event_details.json`).

### 4. `04_json_to_excel.py`  
Converts the JSON file into an Excel sheet, assigning unique `event_id`s and filling in missing timestamps where needed.

### 5. `05_upload_to_sheets.py`  
Uploads the final Excel sheet to Google Sheets and creates **individual event logs** for tracking historical changes. Also backs up daily reports.

---

## 🔧 Tech Stack

- Python, Playwright, Tesseract (OCR)
- Pandas, OpenPyXL, Gspread
- Google Sheets API
- Regex, JSON, AsyncIO

---

## 📌 Features

- ✅ Detects **newly added** or **sold out / fast filling** events
- 📸 Captures and processes screenshots with stealth scraping
- 🔍 Extracts rich metadata using OCR + regex
- 🗃️ Pushes data to structured Excel + Google Sheets
- 🔄 Backs up daily logs with date-wise history

---

## 📂 Output Files

- `events_YYYY-MM-DD.json` — Raw scraped data
- `event_report_YYYY-MM-DD.txt` — Human-readable event diff report
- `all_event_details.json` — Final structured event dataset
- `events.xlsx` — Excel file ready for Google Sheets upload
- Google Sheet (`report` > `NCR`) — Daily data archive

---

## 🚀 How to Run

```bash
# 1. Scrape and generate daily report
python 01_url_fetcher.py

# 2. Capture screenshots
python 02_url_to_ss.py

# 3. Extract data from screenshots
python 03_ss_to_json.py

# 4. Convert JSON to Excel
python 04_json_to_excel.py

# 5. Upload and backup to Google Sheets
python 05_upload_to_sheets.py
