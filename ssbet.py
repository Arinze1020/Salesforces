from flask import Flask, jsonify
import asyncio
from playwright.async_api import async_playwright
import os
import json
import requests
from concurrent.futures import ThreadPoolExecutor, as_completed



app = Flask(__name__)

phone = os.environ['phone']
password = os.environ['password']
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

# Async function to send bounties in parallel using multiple threads
async def send_bounties_in_parallel(bounties):
    loop = asyncio.get_event_loop()
    with ThreadPoolExecutor() as executor:
        futures = [
            loop.run_in_executor(executor, send_message, get_text_message_input(RECIPIENT_WAID, bounty))
            for bounty in bounties
        ]
        for future in as_completed(futures):
            await future

# Function to automate the betting process and send WhatsApp messages
async def run():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context()
        page = await context.new_page()

        # Step 1: Log in to the platform
        await page.goto("https://www.sportybet.com/ng/m/games/sportygames?game=turbo-games/aviator#login")
        await page.get_by_placeholder("Mobile Number").fill(f"{phone}")
        await page.get_by_placeholder("Mobile Number").press("Tab")
        await page.get_by_placeholder("Password").fill(f"{password}")
        await page.get_by_role("button", name="Login").click()

        # Step 2: Automate the betting process
        frame = page.frame_locator("[id=\"turbo-games\\/aviator\"]").frame_locator("iframe")
        await frame.get_by_role("button", name="Auto").first.click()
        await frame.get_by_role("button", name="100.00").first.click()
        await frame.locator(".cash-out-switcher > .ng-untouched > .input-switch").first.click()
        await frame.get_by_role("button", name="Bet 100.00 NGN").click()

        await asyncio.sleep(50)

        # Step 3: Check balance
        page1 = await context.new_page()
        await page1.goto("https://www.sportybet.com/ng/")
        balance = await page1.locator('//*[@id="j_balance"]').text_content()

        print(f"Balance: {balance}")

        # Step 4: Send balance information via WhatsApp
        await send_bounties_in_parallel([f"{balance}"])

        # Cleanup
        await context.close()
        await browser.close()

@app.route("/run-playwright")
def run_playwright():
    asyncio.run(run())
    return jsonify({"status": "Playwright task completed"})

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
