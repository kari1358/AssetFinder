import requests
from bs4 import BeautifulSoup

url = "https://assetstore.unity.com/"
response = requests.get(url)
soup = BeautifulSoup(response.text, 'html.parser')

# now you can use the 'soup' object to find elements, e.g., soup.find_all('a')
