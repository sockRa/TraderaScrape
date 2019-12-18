from requests_html import HTMLSession
from bs4 import BeautifulSoup

http://theautomatic.net/2019/01/19/scraping-data-from-javascript-webpage-python/

# Create an HTML Session object
session = HTMLSession()

# Use the object above to connect to the webpage
resp = session.get('https://www.tradera.com/search?q=lundby&itemStatus=Ended')

# Run JavaScript code on webpage
resp.html.render()












