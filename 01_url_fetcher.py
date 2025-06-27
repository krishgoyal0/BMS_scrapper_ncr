import json
import os
import time
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Any, Optional
from playwright.sync_api import sync_playwright, TimeoutError as PlaywrightTimeoutError
import random

# ----------------------------
# Configuration
# ----------------------------
BASE_URL = "https://in.bookmyshow.com/explore/events-national-capital-region-ncr"
DATA_DIR = Path("data/bookmyshow")
REPORTS_DIR = Path("reports")
DATA_DIR.mkdir(parents=True, exist_ok=True)
REPORTS_DIR.mkdir(parents=True, exist_ok=True)
TIME_THRESHOLD = datetime.now() - timedelta(hours=24)
MAX_RETRIES = 3
WAIT_TIMEOUT = 120000  # Increased timeout to 120 seconds
USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
    "Mozilla/5.0 (iPhone; CPU iPhone OS 14_6 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.0 Mobile/15E148 Safari/604.1"
]
IGNORE_FIELDS = {'timestamp', 'scraped_at'}
STATUS_INDICATORS = {
    'fast_filling': ['fast filling', 'filling fast', 'almost full', 'limited seats'],
    'sold_out': ['sold out', 'housefull', 'no seats']
}

# ----------------------------
# Helper Functions
# ----------------------------
def get_random_user_agent():
    return random.choice(USER_AGENTS)

def get_current_date() -> str:
    return datetime.now().strftime("%Y-%m-%d")

def get_yesterday_date() -> str:
    return (datetime.now() - timedelta(days=1)).strftime("%Y-%m-%d")

def get_filename(date: str) -> Path:
    return DATA_DIR / f"events_{date}.json"

def get_report_filename(date: str) -> Path:
    return REPORTS_DIR / f"event_report_{date}.txt"

def is_recent_event(event_date_str: str) -> bool:
    try:
        event_date = datetime.strptime(event_date_str, "%Y-%m-%d %H:%M:%S")
        return event_date >= TIME_THRESHOLD
    except (ValueError, TypeError):
        return False

def check_event_status(text: str) -> Dict[str, bool]:
    text = text.lower()
    return {
        'is_fast_filling': any(indicator in text for indicator in STATUS_INDICATORS['fast_filling']),
        'is_sold_out': any(indicator in text for indicator in STATUS_INDICATORS['sold_out'])
    }

# ----------------------------
# Scraping Functions
# ----------------------------
def scrape_events() -> Optional[List[Dict[str, Any]]]:
    for attempt in range(MAX_RETRIES):
        try:
            with sync_playwright() as p:
                browser = p.chromium.launch(
                    headless=True,
                    args=[
                        '--no-sandbox',
                        '--disable-setuid-sandbox',
                        '--disable-dev-shm-usage',
                        '--disable-blink-features=AutomationControlled',
                        '--user-agent=' + get_random_user_agent()
                    ],
                    slow_mo=100
                )

                context = browser.new_context(
                    user_agent=get_random_user_agent(),
                    viewport={"width": 1280, "height": 720},
                    locale="en-IN",
                    timezone_id="Asia/Kolkata",
                    java_script_enabled=True,
                    has_touch=False,
                    is_mobile=False
                )

                # Stealth measures
                context.add_init_script("""
                    Object.defineProperty(navigator, 'webdriver', { get: () => undefined });
                    window.navigator.chrome = { runtime: {}, app: { isInstalled: false } };
                """)

                page = context.new_page()
                page.set_default_timeout(WAIT_TIMEOUT)

                print("Loading BookMyShow with enhanced detection...")
                page.goto(BASE_URL, wait_until="domcontentloaded")

                # Human-like interactions
                for _ in range(3):
                    page.mouse.move(random.randint(0, 500), random.randint(0, 500))
                    time.sleep(random.uniform(0.3, 1.5))

                # Dismiss popups
                for selector in ["button:has-text('Accept')", "button:has-text('Close')"]:
                    try:
                        page.click(selector, timeout=3000)
                    except:
                        pass

                # Scrolling logic
                print("Scrolling to load all events...")
                last_height = page.evaluate("document.body.scrollHeight")
                scroll_attempts = 0
                max_scroll_attempts = 15
                last_event_count = 0
                retry_count = 0
                max_retries = 2

                while scroll_attempts < max_scroll_attempts:
                    page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
                    time.sleep(random.uniform(1.5, 3.0))

                    try:
                        page.wait_for_function(
                            "(prevHeight) => { return document.body.scrollHeight > prevHeight; }",
                            arg=last_height,
                            timeout=5000
                        )
                    except:
                        pass

                    new_height = page.evaluate("document.body.scrollHeight")
                    if new_height == last_height:
                        current_events = page.query_selector_all("div[class*='event-card']")
                        if len(current_events) > last_event_count:
                            last_event_count = len(current_events)
                            retry_count = 0
                        else:
                            retry_count += 1
                            if retry_count >= max_retries:
                                break
                    else:
                        last_height = new_height
                        retry_count = 0

                    scroll_attempts += 1

                # Event extraction
                event_selectors = [
                    "div[class*='event-card']",
                    "a[href*='/events/']",
                    "div[data-testid*='event']",
                    "div[class*='card']:has(h3, h4)",
                    "div[class*='event']",
                ]

                events = []
                seen_urls = set()

                for selector in event_selectors:
                    try:
                        cards = page.query_selector_all(selector)
                        print(f"Found {len(cards)} events with selector: {selector}")
                        
                        for card in cards:
                            try:
                                name = card.query_selector("h2, h3, h4, [class*='title']")
                                url = card.get_attribute("href") or "N/A"
                                
                                if not name or url == "N/A" or url in seen_urls:
                                    continue
                                seen_urls.add(url)

                                event_data = {
                                    "name": name.text_content().strip(),
                                    "url": url,
                                    "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                                    "scraped_at": datetime.now().isoformat()
                                }

                                details = {
                                    "venue": "[class*='venue'], [class*='location']",
                                    "date": "[class*='date'], [class*='time']",
                                    "price": "[class*='price'], [class*='amount']",
                                    "status": "[class*='status'], [class*='tag']"
                                }
                                
                                for key, sel in details.items():
                                    element = card.query_selector(sel)
                                    if element:
                                        event_data[key] = element.text_content().strip()
                                        if key == "status":
                                            event_data.update(check_event_status(event_data[key]))

                                events.append(event_data)
                            except Exception as e:
                                print(f"Error processing card: {e}")
                                continue

                    except Exception as e:
                        print(f"Selector failed: {selector} - {e}")

                print(f"Total events captured: {len(events)}")
                browser.close()
                return events

        except Exception as e:
            print(f"Attempt {attempt + 1} failed: {str(e)}")
            if attempt == MAX_RETRIES - 1:
                print("Max retries reached. Aborting.")
                return None
            time.sleep(5 * (attempt + 1))
    
    return None

# ----------------------------
# Rest of the file remains unchanged
# ----------------------------
def save_events(events: List[Dict], date: str) -> None:
    if not events:
        return
        
    filename = get_filename(date)
    try:
        with open(filename, "w", encoding="utf-8") as f:
            json.dump(events, f, indent=2, ensure_ascii=False)
        print(f"Saved {len(events)} events to {filename}")
    except Exception as e:
        print(f"Error saving events: {e}")

def load_events(filename: str) -> Dict[str, Dict[str, Any]]:
    try:
        with open(filename, 'r', encoding='utf-8') as f:
            events = json.load(f)
        return {event['url']: event for event in events}
    except FileNotFoundError:
        return {}
    except json.JSONDecodeError:
        print(f"Error: Could not decode {filename}")
        return {}

def compare_events(old_file: str, new_file: str) -> Dict[str, Any]:
    old_events = load_events(old_file)
    new_events = load_events(new_file)
    
    old_urls = set(old_events.keys())
    new_urls = set(new_events.keys())
    
    return {
        'added': list(new_events.values()),
        'removed': [old_events[url] for url in old_urls - new_urls],
        'stats': {
            'added': len(new_events),
            'removed': len(old_urls - new_urls),
            'total_old': len(old_events),
            'total_new': len(new_events)
        }
    }

def generate_report_content(results: Dict[str, Any]) -> str:
    stats = results['stats']
    report_lines = []
    
    report_lines.append("\n=== Event Comparison Results ===")
    report_lines.append(f"Old file: {stats['total_old']} events")
    report_lines.append(f"New file: {stats['total_new']} events")
    report_lines.append(f"Comparison time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
    
    report_lines.append(f"Newly added events ({stats['added']}):")
    for event in results['added']:
        report_lines.append(f"- {event.get('name', 'Untitled Event')}")
        report_lines.append(f"  URL: {event.get('url', 'N/A')}")
        if event.get('is_fast_filling', False):
            report_lines.append("  (Fast Filling!)")
        if event.get('is_sold_out', False):
            report_lines.append("  (SOLD OUT!)")
    
    report_lines.append(f"\nRemoved events ({stats['removed']}):")
    for event in results['removed']:
        report_lines.append(f"- {event.get('name', 'Untitled Event')}")
        report_lines.append(f"  URL: {event.get('url', 'N/A')}")
    
    if results['added']:
        report_lines.append("\n=== New Events Summary ===")
        for i, event in enumerate(results['added'][:10], 1):
            report_lines.append(f"\n{i}. {event.get('name', 'Untitled Event')}")
            report_lines.append(f"   Venue: {event.get('venue', 'N/A')}")
            report_lines.append(f"   Date: {event.get('date', 'N/A')}")
            report_lines.append(f"   URL: {event.get('url', 'N/A')}")
            if event.get('price'):
                report_lines.append(f"   Price: {event.get('price')}")
            if event.get('is_fast_filling', False):
                report_lines.append("   Status: FAST FILLING!")
            if event.get('is_sold_out', False):
                report_lines.append("   Status: SOLD OUT!")
    
    return "\n".join(report_lines)

def save_report(report_content: str, date: str) -> None:
    filename = get_report_filename(date)
    try:
        with open(filename, "w", encoding="utf-8") as f:
            f.write(report_content)
        print(f"\nReport saved to {filename}")
    except Exception as e:
        print(f"Error saving report: {e}")

def print_and_save_report(results: Dict[str, Any], date: str) -> None:
    report_content = generate_report_content(results)
    print(report_content)
    save_report(report_content, date)

def main():
    current_date = get_current_date()
    yesterday_date = get_yesterday_date()
    
    print(f"Scraping BookMyShow NCR events (recent since {TIME_THRESHOLD})...")
    recent_events = scrape_events()
    
    if not recent_events:
        print("No recent events found or scraping failed.")
        return
    
    save_events(recent_events, current_date)
    
    today_file = get_filename(current_date)
    yesterday_file = get_filename(yesterday_date)
    
    if not yesterday_file.exists():
        print("\nNo previous day's file found for comparison.")
        return
    
    print("\nComparing with previous day's events...")
    comparison_results = compare_events(yesterday_file, today_file)
    print_and_save_report(comparison_results, current_date)

if __name__ == "__main__":
    main()