import asyncio
import random
import re
from pathlib import Path
from datetime import datetime
from playwright.async_api import async_playwright

async def take_initial_screenshot(url, output_file, attempt=1):
    """Capture just the initial view of the page with retry logic"""
    async with async_playwright() as p:
        user_agents = [
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36",
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:109.0) Gecko/20100101 Firefox/115.0"
        ]
        
        try:
            browser = await p.chromium.launch(
                headless=False,
                args=[
                    "--disable-blink-features=AutomationControlled",
                    "--start-maximized"
                ],
                timeout=30000  # Browser launch timeout
            )
            
            context = await browser.new_context(
                user_agent=random.choice(user_agents),
                viewport={"width": 1280, "height": 720},
                permissions=["geolocation"],
                locale="en-US",
                timezone_id="America/New_York"
            )

            # Stealth configurations
            await context.add_init_script("""
                delete Object.getPrototypeOf(navigator).webdriver;
                window.navigator.chrome = { runtime: {}, app: { isInstalled: false } };
            """)

            page = await context.new_page()
            
            # Set timeout for this page
            page.set_default_timeout(15000)  # 15 second timeout for page operations
            
            # Random delay before navigation
            await asyncio.sleep(random.uniform(1, 3))
            
            print(f"Attempt {attempt} for: {url}")
            try:
                await page.goto(
                    url,
                    wait_until='domcontentloaded',
                    referer="https://www.google.com/",
                    timeout=15000  # 15 seconds for page load
                )
            except Exception as e:
                print(f"Navigation warning: {str(e)}")
                # Continue even if navigation didn't fully complete

            # Wait briefly for initial content
            try:
                await page.wait_for_selector('body', state='attached', timeout=3000)
            except:
                pass  # Continue even if no content detected
            
            print(f"Capturing initial view: {output_file}")
            try:
                await page.screenshot(
                    path=output_file,
                    full_page=False,
                    type='png',
                    timeout=10000  # 10 seconds for screenshot
                )
                return True
            except Exception as e:
                print(f"Screenshot failed: {str(e)}")
                return False
            
        except Exception as e:
            print(f"Browser error: {str(e)}")
            return False
        finally:
            await browser.close()

async def process_with_retry(url, output_file, max_attempts=3):
    """Process a URL with retry logic"""
    for attempt in range(1, max_attempts + 1):
        success = await take_initial_screenshot(url, output_file, attempt)
        if success:
            return True
        if attempt < max_attempts:
            retry_delay = random.uniform(5, 10) * attempt
            print(f"Retrying in {retry_delay:.1f} seconds...")
            await asyncio.sleep(retry_delay)
    return False

async def process_event_urls_from_file(file_path, output_dir="screenshots"):
    # Clean up existing files in screenshots folder
    output_path = Path(output_dir)
    if output_path.exists():
        for f in output_path.glob("*.png"):
            f.unlink()
    else:
        output_path.mkdir()
    
    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            content = file.read()
    except FileNotFoundError:
        print(f"Error: Event report file not found: {file_path}")
        return

    pattern = r"Newly added events \(.*?\):(.*?)Removed events"
    new_events_section = re.search(pattern, content, re.DOTALL)
    
    if not new_events_section:
        print("No 'Newly added events' section found in the file.")
        return
        
    urls = re.findall(r"URL:\s+(https://[^\s]+)", new_events_section.group(1))
    event_names = re.findall(r"- (.*?)\n\s+URL:", new_events_section.group(1))
    
    if not urls:
        print("No URLs found in the 'Newly added events' section.")
        return
    
    success_count = 0
    for i, (event_name, url) in enumerate(zip(event_names, urls), start=1):
        clean_name = re.sub(r'[\\/*?:"<>|]', '', event_name.strip())
        output_file = Path(output_dir) / f"{i:02d}_{clean_name}.png"
        
        print(f"\nProcessing event {i}/{len(urls)}: {event_name}")
        success = await process_with_retry(url, str(output_file))
        
        if success:
            success_count += 1
            print("Successfully captured screenshot")
        else:
            print(f"Failed to capture screenshot after multiple attempts")
        
        delay = random.uniform(3, 8) + (i * 0.3)
        print(f"Waiting {delay:.1f} seconds before next...")
        await asyncio.sleep(delay)
    
    print(f"\nFinal result: {success_count}/{len(urls)} screenshots captured")

if __name__ == "__main__":
    event_report_file = Path("reports") / f"event_report_{datetime.now().strftime('%Y-%m-%d')}.txt"
    print(f"Using event report: {event_report_file}")
    asyncio.run(process_event_urls_from_file(event_report_file))


#THIS SCRIPT IS WORKING THE BEST AND MOST SUITABLE WAY.

#THIS SCRIPT IS WORKING THE BEST AND MOST SUITABLE WAY.