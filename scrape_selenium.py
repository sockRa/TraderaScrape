from selenium import webdriver
import time
from termcolor import colored
import re
import pandas as pd

# Setup browser
options = webdriver.FirefoxOptions()
# options.add_argument('--headless')
driver = webdriver.Firefox(options=options)

search_query = str(input("Search: "))
# Open a session against server
driver.get('https://www.tradera.com/search?q=' + search_query + '&itemStatus=Ended')

# Accept "information about cookies"
driver.find_element_by_css_selector('button.btn-primary:nth-child(2)').click()

# Get the last page so we know how many iterations are possible
last_page = int(driver.find_elements_by_class_name('page-item.d-none.d-md-block')[-1].text)

user_page_choice = int(input("How many pages do you want to scrape? Min: 1, Max: " + str(last_page) + "\n:"))

products = []

page = 1

print(colored('Web scraper', 'red'), colored('has begun', 'green'))


def strip_out_currency(text):
    pattern = r" kr"
    return int(re.sub(pattern, "", text))


def strip_out_bid_text(text):
    pattern = r" bud"
    return int(re.sub(pattern, "", text))


while page <= user_page_choice:

    t0 = time.time()

    if page != 1:
        # Go to next page
        driver.find_elements_by_class_name('page-item.d-none.d-md-block')[page - 1].click()
        driver.get(driver.current_url)

        # Sleep 10x times longer than it took the server to respond
        response_delay = time.time() - t0
        print("Sleep: " + str(response_delay * 10) + " seconds")
        time.sleep(10 * response_delay)

    # Grab each product from one page and put them in a list
    containers = driver.find_elements_by_class_name("item-card-container")

    # Go through each product in containers-list and scrape essential data
    for container in containers:
        title = container.find_element_by_class_name("item-card-title.d-flex.flex-row.mb-2").text
        sell_price = strip_out_currency(
            container.find_element_by_class_name("text-nowrap.font-weight-bold.item-card-details-price").text)

        bids_container = container.find_elements_by_class_name("text-nowrap.mr-2")

        # Special case if the auction have free shipping
        if len(bids_container) == 1:
            bids = strip_out_bid_text(bids_container[0].text)
        else:
            bids = strip_out_bid_text(bids_container[1].text)

        # Scrap any auction with zero bids
        if bids > 0:
            products.append({"Title": title, "Sell price": sell_price, "Bids": bids})

    print("Page " + str(page) + " of " + str(user_page_choice) + " done")
    # Once we have gone through the whole page, switch page
    page += 1

# Create dataframe for displaying the data
data_frame = pd.DataFrame(products)

# Print out the results
# average_sales_price = int(round(data_frame['Auction price (SEK)'].mean()))
# print("Average sales price of " + search_query + " is " + str(average_sales_price) + " SEK")

# Save all products in a CSV file
data_frame.to_csv(r'Saved_scrapes\%s_scrape.csv' % search_query)

print("Saved " + search_query + r"scrape.csv at: Working_directory\Saved_scrapes")
