from playwright.sync_api import Playwright, sync_playwright, expect
import subprocess
import time
### main.py
import os

password = os.environ['password']

subprocess.call(['sh','./install.sh'])

from random_user_agent.user_agent import UserAgent
from random_user_agent.params import SoftwareName, OperatingSystem

software_names = [SoftwareName.CHROME.value]
operating_systems = [OperatingSystem.WINDOWS.value, OperatingSystem.LINUX.value]

user_agent_rotator = UserAgent(software_names=software_names, operating_systems=operating_systems, limit=10000)
user_agent = user_agent_rotator.get_random_user_agent()


import re

import csv
with open('ott.csv', 'r') as csvfile:
    reader = csv.reader(csvfile)
    data = [row for row in reader]
    single_list = [item[0] for item in data]


def run(playwright: Playwright) -> None:
    
    browser = playwright.chromium.launch(headless=True)
    context = browser.new_context(user_agent = user_agent)
    page = context.new_page()
    page.goto("https://americantower3org.my.site.com/NOC/login")
    page.get_by_label("Username").click()
    page.get_by_label("Username").fill("arinzeugwuanyi@gmail.com")
    page.get_by_label("Password").click()
    page.get_by_label("Password").fill(password)
    page.get_by_role("button", name="Log In").click()
    page.wait_for_timeout(3_000)

    while True:
        for t in single_list:
            page.get_by_placeholder("Search...").click()
            page.get_by_placeholder("Search...").fill(f'{t}')
            page.get_by_placeholder("Search...").press("Enter")
            page.get_by_role("link", name=f'{t}').click()
            page.get_by_role("button", name="Edit: GL_NOC_AlarmClearedTime__c").click()
            page.wait_for_timeout(3_000)

            page.get_by_role("group", name="Alarm Cleared time").get_by_label("Date").click()
            page.wait_for_timeout(3_000)
            page.get_by_role("button", name="Previous Month").click()
            page.get_by_role("gridcell", name="2023-05-01").get_by_role("button", name="1").click()
            page.wait_for_timeout(3_000)


            page.get_by_role("button", name="Save").click()
            
            page.wait_for_timeout(10_000)
            page.get_by_role("button", name="Edit Sub Reason").click()
            page.locator("div").filter(has_text=re.compile(r"^Sub Reason--None--$")).get_by_role("button", name="--None--").click()
            page.get_by_role("menuitemradio", name="Affected by another site").click()
            page.locator("div").filter(has_text=re.compile(r"^Underlying Reason--None--$")).get_by_role("button", name="--None--").click()
            page.get_by_role("menuitemradio", name="Affected by another site").click()
            page.get_by_role("button", name="--None--").click()
            page.get_by_role("menuitemradio", name="No Customer Impact").click()
            page.get_by_role("article").filter(has_text="DetailsCase InformationCase OwnerSalesforce ServicesChange OwnerCreated BySalesf").get_by_role("button", name="New").click()
            page.get_by_role("menuitemradio", name="Closed").click()
            page.wait_for_timeout(3_000)

            page.get_by_label("Closing Comments").click()
            page.get_by_label("Closing Comments").fill("Alarm closed")
            page.wait_for_timeout(3_000)

            page.get_by_label("Internal Comments*").click()
            page.get_by_label("Internal Comments*").fill("Battery Alarm Closed")
            page.wait_for_timeout(3_000)
            page.get_by_role("button", name="Save").click()
            page.wait_for_timeout(300_000)
            
            print(t)


        else:

        # ---------------------
            context.close()
            browser.close()



with sync_playwright() as playwright:
    run(playwright)
