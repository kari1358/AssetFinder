from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
import time
import sqlite3
from database_setup import insert_into_database, create_database
from selenium.common.exceptions import ElementNotInteractableException
import requests
from urllib.parse import urlparse, unquote


def get_model_urls(page_url):
    # Set up a headless Chrome browser
    options = Options()
    options.add_argument('--headless')
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)

def search_url_list(soup):
    # Find all links on the page
    links = soup.find_all('a')

    # Filter out any links that don't have an 'href' attribute
    links = [link for link in links if 'href' in link.attrs]

    # Extract the URLs of the 3D model pages
    return [link['href'] for link in links if '/3d-models/' in link['href']]


def get_model_urls(page_url):
    driver = webdriver.Chrome()

    driver.get(page_url)
    wait = WebDriverWait(driver, 10)  # wait for a maximum of 10 seconds

    model_urls = []

    max_pages = 2
    page_number = 1

    while page_number <= max_pages:
        try:
            print(f'starting page number {page_number}')

            html = driver.page_source
            soup = BeautifulSoup(html, 'html.parser')

            model_urls.append(search_url_list(soup))

            load_more_button = wait.until(EC.presence_of_all_elements_located((By.XPATH, "//*[contains(@class, 'button__text-container') and contains(text(), 'Load more')]")))

            if load_more_button:
                driver.execute_script("arguments[0].click();", load_more_button[0])
                time.sleep(2)  # wait for new models to load
            else:
                print(f'No more pages')
                break  # No more pages

            page_number += 1

        except (TimeoutException, ElementNotInteractableException):
            break  # no more pages
            driver.quit()
    print(f'returning model urls: {model_urls}')
    return model_urls



def main_scraping_script(url):
    # Specify the path to the chromedriver executable
    webdriver_service = Service('/Users/kariwu/Antropic AI Hackathon/chromedriver_mac_arm64/chromedriver')

    # Start the driver
    driver = webdriver.Chrome(service=webdriver_service)

    driver.get(url)

    # Add some delay to let JavaScript load.
    time.sleep(10)

    # Parse the HTML of the page with BeautifulSoup
    soup = BeautifulSoup(driver.page_source, 'html.parser')

    # Function to trim the description if it's too long
    def trim_to_char_limit(text, char_limit):
        if text and len(text) > char_limit:
            text = text[:char_limit - 3] + '...'
        return text

    # Find elements with given class tags
    review_items = []
    descriptions = soup.find_all(class_='review-item__text')  # Replace 'h1' with the correct class name for the review text

    for description in descriptions:
        review_item = {}
        review_item['description'] = trim_to_char_limit(description.text if description else '', 2048)

        # Skip this item if all fields are empty
        if all(not value for value in review_item.values()):
            continue

        insert_into_database(url, review_item['description'])


    # Print out a summary of those elements
    print(f"Found {len(review_items)} items:")
    for i, item in enumerate(review_items):
        print(f"----- ITEM {i+1} -----")
        print(f"Description: {item['description']}")
        print("----- END OF ITEM -----\n")

    # Always remember to close the driver after you're done
    driver.close()

###
def create_table_if_not_exists():
    conn = sqlite3.connect('reviews.db')
    c = conn.cursor()
    c.execute('''
        CREATE TABLE IF NOT EXISTS SketchfabModels (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            item_url TEXT,
            page_id TEXT,
            name TEXT,
            description_content TEXT,
            review TEXT
        );
    ''')
    conn.commit()
    conn.close()

####

def insert_into_database(item_url, page_id, name, description_content, review):
    # Connect to a database (or create one if it doesn't exist)
    conn = sqlite3.connect('reviews.db')
    # Create a 'cursor' for executing commands
    c = conn.cursor()
    # Checks if a record with the same item_url already exists
    def url_exists_in_db(conn, url):
        cursor = conn.cursor()
        cursor.execute("SELECT 1 FROM SketchfabModels WHERE item_url = ?", (url,))
        return cursor.fetchone() is not None
    # assuming 'conn' is your SQLite database connection
    if not url_exists_in_db(conn, item_url):
    # Insert the new record into the database
        c.execute('''
        INSERT INTO SketchfabModels (item_url, page_id, name, description_content, review)
        VALUES (?, ?, ?, ?, ?);
    ''', (item_url, page_id, name, description_content, review,))
    # Save (commit) the changes
    conn.commit()
    # Close the connection
    conn.close()


def filter_urls_for_links_to_models(candidate_urls):
    filtered_urls = []
    for url in candidate_urls:
        if '/3d-models/' in url and url.startswith("https://"):
            filtered_urls.append(url)
            print=(f'Matched with url: {url}')
    return filtered_urls


def process_url(url):
    # Parse URL
    parsed_url = urlparse(url)

    # Get ID and name
    path_parts = parsed_url.path.split('/')
    id_and_comments = path_parts[-1].split('#')
    page_id = id_and_comments[0].split('-')[-1]
    name_part = id_and_comments[0].rsplit('-', 1)[0]
    name = name_part.replace('-', ' ')


    # Send GET request
    response = requests.get(url)

    # Parse response content
    soup = BeautifulSoup(response.content, 'html.parser')

    # Find description content
    description_content_tag = soup.find(id="descriptionContent")
    description_content = description_content_tag.text.strip() if description_content_tag else None

    return page_id, name, description_content


# Let's assume your script looks something like this:
def scrape_data():
    # A placeholder function that returns data. 
    # Replace this with your actual scraping function.
    # The function should return a list of tuples, with each tuple containing an item_url, page_id, name, description_content, and a review.
    return [
        ("https://www.stechfab.com/item1", "page1", "Item 1", "This is a great item.", "5 stars"),
        ("https://www.stechfab.com/item2", "page2", "Item 2", "This item is also great.", "4 stars"),
        # Add more tuples as necessary...
    ]


#### Loop the action so that each url goes through the main scraping script #####################
create_table_if_not_exists()

model_urls_by_page = get_model_urls("https://sketchfab.com/3d-models/")

for page in model_urls_by_page:
    print("filtering...")
    page = filter_urls_for_links_to_models(page)
    print("filtered.")
    
    for url in page:
        url = str(url)
        print(f'scraping url: {url}')
        page_id, name, description_content = process_url(url)
        item_url = url
        review = "So good! 3 stars."
        insert_into_database(item_url, page_id, name, description_content, review)
        """
        # Now you can call your scraping function and use the data it returns to insert into your database:
        data = scrape_data()
        #data = main_scraping_script(url)
        for item in data:
            item_url, page_id, name, description_content, review = item
            insert_into_database(item_url, page_id, name, description_content, review)
        """

print("Done.")
