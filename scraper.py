from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from bs4 import BeautifulSoup
import time

# Specify the path to the chromedriver executable
webdriver_service = Service('/Users/kariwu/Antropic AI Hackathon/chromedriver_mac_arm64/chromedriver')

# Start the driver
driver = webdriver.Chrome(service=webdriver_service)

url = "https://assetstore.unity.com/packages/tools/level-design/mbs-modular-building-system-208505#reviews"
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
names = soup.find_all('h1')  # Replace 'h1' with the correct class name for the reviewer's name
descriptions = soup.find_all(class_='_1_3uP')  # Replace '_1_3uP' with the correct class name for the review text

for name, description in zip(names, descriptions):
    review_item = {}
    review_item['name'] = name.text if name else ''
    review_item['description'] = trim_to_char_limit(description.text if description else '', 2048)

    # Skip this item if all fields are empty
    if all(not value for value in review_item.values()):
        continue

    review_items.append(review_item)

# Print out a summary of those elements
print(f"Found {len(review_items)} items:")
for i, item in enumerate(review_items):
    print(f"----- ITEM {i+1} -----")
    print(f"Name: {item['name']}")
    print(f"Description: {item['description']}")
    print("----- END OF ITEM -----\n")

# Always remember to close the driver after you're done
driver.close()
