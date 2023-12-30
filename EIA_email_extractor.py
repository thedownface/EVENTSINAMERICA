import csv
import re
import boxsdk
import os
import requests 
from bs4 import BeautifulSoup
from concurrent.futures import ThreadPoolExecutor
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium import webdriver
from tldextract import extract
from selenium.webdriver.edge.service import Service as EdgeService
from webdriver_manager.microsoft import EdgeChromiumDriverManager
import logging
from urllib.parse import urlparse
from selenium.webdriver.support.ui import WebDriverWait
from Variables import Variable
from selenium.common.exceptions import TimeoutException
# Function to parse and upload emails to Box


facts= Variable.get('EventsInAmerica')


def get_exhibitor_links():
    csv_file_path=os.path.join(os.getcwd(),'eventsInAmerica.csv')
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
    
def parse(show_name, response):
    emails_directory = os.path.join(os.getcwd(), 'Emails')
    if not os.path.exists(emails_directory):
        os.mkdir(emails_directory)
    csv_file_path = os.path.join(emails_directory, f'{show_name}.csv')

    EMAIL_REGEX = r"[a-z0-9.\-+_]+@[a-z0-9.\-+_]+\.[a-z]+"
    emails = re.findall(EMAIL_REGEX, str(response.text))

    email_list = set()
    for email in emails:
        if not any(ext in email for ext in [".png", ".svg", ".webp", ".jpg", ".jpeg", ".wixpress"]) and "j" not in email and "doe" not in email:
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


def process_exhibitor(exhibitor_name, show_name):
    WINDOW_SIZE = "1920,1080"
    options = webdriver.EdgeOptions()
    options.add_argument("--headless")
    options.add_argument("--window-size=%s" % WINDOW_SIZE)
    options.add_argument('--ignore-ssl-errors=yes')
    options.add_argument('--ignore-certificate-errors')
    options.add_experimental_option('excludeSwitches', ['enable-logging'])

    url = f"https://www.bing.com/search?q=%40{exhibitor_name}+%22Email+Address%22+Contact Us"
    print(exhibitor_name)

    try:
        browser.get(url)

        # Wait for the page to load, with a timeout of 5 seconds
        WebDriverWait(browser, 5).until(EC.presence_of_element_located((By.TAG_NAME, 'cite')))
        
        links = browser.find_elements(By.TAG_NAME, 'cite')
        url_list = [link.text for link in links]

        # Process each result URL only once
        for result_url in url_list[:3]:
            try:
                parsed_url = urlparse(result_url)
                if not parsed_url.scheme:
                    result_url = 'http://' + result_url

                # Retry finding the element in case of StaleElementReferenceException
                for _ in range(3):  # Try 3 times
                    try:
                        browser.get(result_url)
                        inner_html = browser.page_source
                        soup = BeautifulSoup(inner_html, 'lxml')
                        parse(show_name, soup)
                        break  # If successful, break out of the retry loop
                    except Exception as e:
                        print(f"Stale element reference. Retrying... : {e}")

            except Exception as e:
                print(f'Cant Scrape Emails from {result_url} due to {e}')

    except TimeoutException:
        print(f"Timed out while waiting for {url} to load. Skipping.")
    except Exception as e:
        print(f"Error processing {url}: {e}")

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

def process_show(exhibitor_link, show_name):
    if show_name in facts:
        print(f"Show '{show_name}' has already been scraped.")
        return

    exhibitor_names = get_exhibitor_names(exhibitor_link)

    with ThreadPoolExecutor() as executor:
        for exhibitor_name in exhibitor_names:
            executor.submit(process_exhibitor, exhibitor_name, show_name)

    facts[show_name] = {'emails_scraped': 1}
    Variable.set('EventsInAmerica',facts)

# Set up Box SDK OAuth2 credentials
if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    logger = logging.getLogger(__name__)
    browser = webdriver.Edge(service=EdgeService(EdgeChromiumDriverManager().install()))
    print('Browser Instance Created')
    exhibitor_links = get_exhibitor_links()
    
    for show_name, exhibitor_link in exhibitor_links.items():
        print(f'Processing Exhibitor Link:{exhibitor_link}')
        process_show(exhibitor_link, show_name)
