import asyncio
import csv
import os
import re
from bs4 import BeautifulSoup
import logging
from urllib.parse import urlparse
import requests
from Variables import Variable
from pyppeteer import launch
from concurrent.futures import ThreadPoolExecutor

facts = Variable.get('EventsInAmerica')
async def parse_show(exhibitor_name, show_name):
    emails_directory = os.path.join(os.getcwd(), 'Emails')
    if not os.path.exists(emails_directory):
        os.mkdir(emails_directory)
    csv_file_path = os.path.join(emails_directory, f'{show_name}.csv')

    EMAIL_REGEX = r"[a-z0-9.\-+_]+@[a-z0-9.\-+_]+\.[a-z]+"

    browser = await launch(headless=True)
    page = await browser.newPage()

    try:
        url = f"https://www.bing.com/search?q=%40{exhibitor_name}+%22Email+Address%22+Contact Us"
        await page.goto(url)

        # Wait for the required elements or content to be visible before parsing
        await page.waitForSelector('cite')

        # Extract emails from the page content
        inner_html = await page.content()
        soup = BeautifulSoup(inner_html, 'html.parser')
        emails = re.findall(EMAIL_REGEX, str(soup))

        email_list = set()
        for email in emails:
            # Validate and filter emails as needed
            if not any(ext in email for ext in [".png", ".svg", ".webp", ".jpg", ".jpeg", ".wixpress"]) \
                    and "j" not in email and "doe" not in email:
                email_list.add(email)

        # Load existing emails from the CSV file
        existing_emails = set()
        if os.path.exists(csv_file_path):
            with open(csv_file_path, 'r', newline='', encoding='utf-8') as file:
                csv_reader = csv.reader(file)
                existing_emails.update(row[0] for row in csv_reader)

        # Insert only new emails into the CSV file
        new_emails = email_list - existing_emails
        print(f'Emails on the current page: {email_list}')
        print(f'Existing emails in CSV: {existing_emails}')
        print(f'New emails to be inserted: {new_emails}')

        if new_emails:
            with open(csv_file_path, 'a', newline='', encoding='utf-8') as file:
                csv_writer = csv.writer(file)
                for email in new_emails:
                    csv_writer.writerow([email, 'EVENTS IN AMERICA'])
                    print(f'Successfully Inserted {email} in csv')
        else:
            print(f'No new emails found for {show_name}')

    except Exception as e:
        print(f"Error processing {url}: {e}")

    finally:
        await browser.close()

def get_exhibitor_links():
    csv_file_path=r"C:\Users\iamfa\OneDrive\Desktop\TRADESHOWS_DB\eventsInAmerica.csv"
    show_links_dict = {}
    with open(csv_file_path, 'r', newline='', encoding='utf-8') as file:
    # Use csv.DictReader and skip the first row
        csv_reader = csv.DictReader(file)

        for row in csv_reader:
            # Assuming the exhibitor link is in the 'exhibitor_link' column and show name is in the 'show_name' column
            show_name = row['SHOW_NAME'].strip()
            exhibitor_link = row['EXHIBITOR_LINK'].strip()

            # Check if the exhibitor link is not empty
            if exhibitor_link:
                show_links_dict[show_name] = exhibitor_link
        return show_links_dict
    
def get_exhibitor_names(base_url):
    exhibitor_names = []
    page_number = 1
    
    while True:
        exhibitor_link = f"{base_url}?page={page_number}"
        html = requests.get(exhibitor_link).text
        soup = BeautifulSoup(html, 'lxml')
        
        table = soup.find('table', class_='rwd-table booklistWrap booktourlistTable')
        exhibitor_names.extend(exhibitor.text.strip() for exhibitor in table.find_all('td', {'align': 'left'}))
        
        current_page = soup.find('a', class_='current_page')
        if current_page and current_page.text.strip().lower() == 'next':
            page_number += 1
        else:
            break
    
    return exhibitor_names
exhibitor_links = get_exhibitor_links()
    
def process_show(exhibitor_link, show_name):
    if show_name in facts:
        print(f"Show '{show_name}' has already been scraped.")
        return

    exhibitor_names = get_exhibitor_names(exhibitor_link)

    with ThreadPoolExecutor() as executor:
        for exhibitor_name in exhibitor_names:
            asyncio.get_event_loop().run_until_complete(parse_show(exhibitor_name, show_name))
    facts[show_name] = {'emails_scraped': 1}
    Variable.set('EventsInAmerica',facts)

if __name__ == "__main__":
    for show_name, exhibitor_link in exhibitor_links.items():
        print(f'Processing Exhibitor Link:{exhibitor_link}')
        process_show(exhibitor_link,show_name)

    
