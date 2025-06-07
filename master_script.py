import os
import subprocess
import sys
import time

def run_script(script_name):
    """Run a Python script and handle any errors."""
    print(f"\n{'='*50}")
    print(f"Running {script_name}...")
    print(f"{'='*50}\n")
    
    try:
        # Run the script and wait for it to complete
        result = subprocess.run([sys.executable, script_name], check=True)
        print(f"\n{script_name} completed successfully.")
        return True
    except subprocess.CalledProcessError as e:
        print(f"\nError running {script_name}: {e}")
        return False
    except Exception as e:
        print(f"\nUnexpected error running {script_name}: {e}")
        return False

def main():
    # List of scripts to run in order
    scripts = [
        "01_url_fetcher.py",
        "02_url_to_ss.py",
        "03_ss_to_json.py",
        "04_json_to_excel.py",  # Note: There's a typo in your filename (excel vs excel)
        "05_upload_to_sheets.py"
    ]
    
    # Verify all scripts exist before running
    for script in scripts:
        if not os.path.exists(script):
            print(f"Error: Required script {script} not found!")
            return
    
    # Run each script in sequence
    for script in scripts:
        success = run_script(script)
        if not success:
            print(f"Processing halted due to failure in {script}")
            return
        
        # Small delay between scripts (optional)
        time.sleep(1)
    
    print("\nAll processing steps completed successfully!")
    print(f"Final outputs created: all_event_details.json and events.xlsx")

if __name__ == "__main__":
    main()