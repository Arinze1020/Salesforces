import re
from playwright.sync_api import Playwright, sync_playwright
import time
import os
import json
import requests
from concurrent.futures import ThreadPoolExecutor, as_completed
import schedule

subprocess.call(['sh','./install.sh'])

password = os.environ['password']
phone = os.environ['phone']
ACCESS_TOKEN = os.environ['ACCESS_TOKEN']
RECIPIENT_WAID = os.environ['RECIPIENT_WAID']
PHONE_NUMBER_ID = os.environ['PHONE_NUMBER_ID']



VERSION = 'v18.0'

# Function to get the input for the WhatsApp message
def get_text_message_input(recipient, text):
    return json.dumps(
        {
            "messaging_product": "whatsapp",
            "recipient_type": "individual",
            "to": recipient,
            "type": "text",
            "text": {"preview_url": False, "body": text},
        }
    )

# Function to send the message via WhatsApp API
def send_message(data):
    headers = {
        "Content-type": "application/json",
        "Authorization": f"Bearer {ACCESS_TOKEN}",
    }

    url = f"https://graph.facebook.com/{VERSION}/{PHONE_NUMBER_ID}/messages"

    response = requests.post(url, data=data, headers=headers)
    if response.status_code == 200:
        print("Status:", response.status_code)
        print("Content-type:", response.headers["content-type"])
        print("Body:", response.text)
    else:
        print("Error:", response.status_code)
        print(response.text)
    return response

# Function to send bounties in parallel using multiple threads
def send_bounties_in_parallel(bounties):
    with ThreadPoolExecutor() as executor:
        futures = [executor.submit(send_message, get_text_message_input(RECIPIENT_WAID, bounty)) for bounty in bounties]

        for future in as_completed(futures):
            try:
                future.result()
            except Exception as e:
                print(f"Error in sending bounty: {e}")

# Function to automate the betting process and send WhatsApp messages
def run(playwright: Playwright) -> None:
    browser = playwright.chromium.launch(headless=True)
    context = browser.new_context()
    page = context.new_page()

    # Step 1: Log in to the platform
    page.goto("https://www.sportybet.com/ng/m/games/sportygames?game=turbo-games/aviator#login")
    page.get_by_placeholder("Mobile Number").fill(f"{phone}")  # Replace with your mobile number
    page.get_by_placeholder("Mobile Number").press("Tab")
    page.get_by_placeholder("Password").fill(f"{password}")  # Replace with your password
    page.get_by_role("button", name="Login").click()

    # Step 2: Automate the betting process
    page.frame_locator("[id=\"turbo-games\\/aviator\"]").frame_locator("iframe").get_by_role("button", name="Auto").first.click()
    page.frame_locator("[id=\"turbo-games\\/aviator\"]").frame_locator("iframe").get_by_role("button", name="100.00").first.click()
    page.frame_locator("[id=\"turbo-games\\/aviator\"]").frame_locator("iframe").locator(".cash-out-switcher > .ng-untouched > .input-switch").first.click()
    page.frame_locator("[id=\"turbo-games\\/aviator\"]").frame_locator("iframe").get_by_role("button", name="Bet 100.00 NGN").click()

    time.sleep(50)  # Adjust this based on the required wait time

    # Step 3: Check balance
    page1 = context.new_page()
    page1.goto("https://www.sportybet.com/ng/")
    balance = page1.locator('//*[@id="j_balance"]').text_content()
    
    print(f"Balance: {balance}")

    # Step 4: Send balance information via WhatsApp
    send_bounties_in_parallel([f"{balance}"])

    # Cleanup
    context.close()
    browser.close()

def run_task():
    with sync_playwright() as playwright:
        run(playwright)

# Scheduler function
def schedule_tasks():
    # First run the task 15 times, each run 1 minute apart (for demonstration, adjust as needed)
    for _ in range(15):
        run_task()
        time.sleep(60)  # Wait for 1 minute between each run

    # Alternate between 20-minute and 15-minute intervals
    while True:
        time.sleep(20 * 60)  # Wait for 20 minutes
        run_task()
        time.sleep(15 * 60)  # Wait for 15 minutes
        run_task()

if __name__ == "__main__":
    schedule_tasks()
