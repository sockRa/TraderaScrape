from requests_html import HTMLSession
from bs4 import BeautifulSoup as soup
import pandas as pd
import re

# Create an HTML Session object
session = HTMLSession()

# Use the object above to connect to the webpage
search_query = str(input("Search: "))
resp = session.get('https://www.tradera.com/search?q=' + search_query + '&itemStatus=Ended&spage=1')

# Run JavaScript code on webpage
resp.html.render()

# Lxml parsing
page_soup = soup(resp.html.html, 'lxml')

# Grabs each product
containers = page_soup.findAll("div", {"class": "item-card-container"})

products = []


def strip_out_digit(price):
    pattern = r"\xa0kr"
    return int(re.sub(pattern, "", price))


def strip_out_bid(bids):
    pattern = r" bud"
    return int(re.sub(pattern, "", bids))


for container in containers:

    title_container = container.div.p.a["title"]

    sell_price_container = container.findAll("span", {"class": "text-nowrap font-weight-bold item-card-details-price"})

    bid_container = container.findAll("span", {"class": "text-nowrap mr-2"})

    # We don't want to save auctions with zero bids
    if bid_container[0].text[0] > '0':
        products.append({"Title": title_container, "Auction price": strip_out_digit(sell_price_container[0].text),
                         "Currency": "SEK", "Bids": strip_out_bid(bid_container[0].text)})

# Create dataframe for displaying the data
data_frame = pd.DataFrame(products)
print(data_frame)
