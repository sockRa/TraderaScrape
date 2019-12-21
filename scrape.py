from selenium import webdriver
import time
from termcolor import colored
import re
import pandas as pd
import os

# Setup browser
options = webdriver.FirefoxOptions()
# options.add_argument('--headless')
driver = webdriver.Firefox(options=options)

search_query = str(input("Search: "))
# Open a session against server
driver.get('https://www.tradera.com')

# Accept "information about cookies"
driver.find_element_by_css_selector('button.btn-primary:nth-child(2)').click()

# Search
search_element = driver.find_element_by_css_selector('.slim-header__search-field')
search_element.send_keys(search_query)
search_element.submit()

# Choose closed auctions
closed_auction_button = driver.find_element_by_css_selector('div.accordion-item:nth-child(9) > div:nth-child(1) > '
                                                            'div:nth-child(2) > div:nth-child(1) > div:nth-child(1) >'
                                                            ' div:nth-child(1) > div:nth-child(2) > label:nth-child('
                                                            '2)')
closed_auction_button.click()

# Get the last page so we know how many iterations are possible
try:
    last_page = int(driver.find_elements_by_class_name('page-item.d-none.d-md-block')[-1].text)
except IndexError:
    last_page = 1

if last_page > 1:
    user_page_choice = int(input("How many pages do you want to scrape? Min: 1, Max: " + str(last_page) + "\n:"))
else:
    # If the last page just were one page
    user_page_choice = 1

products = []

page = 1

print(colored('Web scraper', 'red'), colored('has begun', 'green'))


def remove_space(string):
    return "".join(string.split())


def strip_out_currency(sell_price_container):
    search_pattern = r"\d+\s?\d*\s*kr"
    get_digit_pattern = "kr"

    for price in sell_price_container:
        if bool(re.search(search_pattern, price.text)):
            return int((remove_space((re.sub(get_digit_pattern, "", remove_space(price.text))))))


def strip_out_bid_text(bid_container):
    pattern = r" bud"

    for bid in bid_container:
        if bool(re.search(pattern, bid.text)):
            return int(re.sub(pattern, "", bid.text))


while page <= user_page_choice:

    t0 = time.time()

    if page != 1:
        # Go to next page
        page_containers = driver.find_elements_by_class_name('page-item.d-none.d-md-block')
        for pages in page_containers:
            if pages.text == str(page):
                pages.click()
                break

        driver.get(driver.current_url)

        # Sleep 2x times longer than it took the server to respond
        response_delay = round(time.time() - t0)
        print("Sleep: " + str(response_delay * 2) + " seconds")
        time.sleep(2 * response_delay)

    # Grab each product from one page and put them in a list
    containers = (driver.find_element_by_class_name("row.mb-4")).find_elements_by_class_name("item-card-container")

    # Go through each product in containers-list and scrape essential data
    for container in containers:

        title = container.find_element_by_class_name("item-card-title.d-flex.flex-row.mb-2").text

        sell_price = strip_out_currency(container.find_elements_by_class_name('text-nowrap.font-weight-bold.item-card'
                                                                              '-details-price'))

        bids = strip_out_bid_text(container.find_elements_by_class_name("text-nowrap.mr-2"))

        link = container.find_element_by_class_name("d-block.font-weight-normal.text-truncate").get_attribute("href")

        # Scrap any auction with zero bids
        if bids > 0:
            products.append({"Title": title, "Sell price": sell_price, "Bids": bids, "Link": link})

    print("Page " + str(page) + " of " + str(user_page_choice) + " done")
    # Once we have gone through the whole page, switch page
    page += 1

print(12 * "-" + "DONE" + 12 * "-")
print(24 * "-")
# Create dataframe for displaying the data
data_frame = pd.DataFrame(products)

outname = search_query + ".csv"
outdir = './Saved scrapes'
if not os.path.exists(outdir):
    os.mkdir(outdir)

path = os.path.join(outdir, outname)
data_frame.to_csv(path)
# Save all products in a CSV file


print("Saved " + outname + " at: " + path)


def print_menu():
    print(30 * "-", "MENU", 30 * "-")
    print("1. Average sales price")
    print("2. Three highest auctions")
    print("3. Three lowest")
    print("4. Number of entries")
    print("5. Exit")
    print(67 * "-")


while True:
    print_menu()
    choice = int(input("Choice: "))

    if choice == 1:
        print(str(round(data_frame['Sell price'].mean())) + " SEK")
    elif choice == 2:
        print(data_frame.nlargest(3, ['Sell price']))
    elif choice == 3:
        print(data_frame.nsmallest(3, ['Sell price']))
    elif choice == 4:
        print("Entries: " + str(data_frame.shape[0]))
    elif choice == 5:
        break
    else:
        print("Invalid input")
