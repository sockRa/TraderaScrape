from requests_html import HTMLSession
from bs4 import BeautifulSoup as soup
import pyppdf.patch_pyppeteer

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

# Save to csv file
filename = "products.csv"
f = open(filename, "w")

headers = "title, auction_price, bids\n"

f.write(headers)

for container in containers:
    title = container.div.p.a["title"]

    sell_price_container = container.findAll("span", {"class": "text-nowrap font-weight-bold item-card-details-price"})
    auction_price = sell_price_container[0].text

    bid_container = container.findAll("span", {"class": "text-nowrap mr-2"})
    bids = bid_container[0].text

    print("Title: " + title)
    print("Auction_price " + auction_price)
    print("Bids: " + bids)

    f.write(title + "," + auction_price + "," + bids + "\n")

f.close()
