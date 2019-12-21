from selenium import webdriver
import time
from termcolor import colored
import re
import pandas as pd

# Setup browser
options = webdriver.FirefoxOptions()
options.add_argument('--headless')
driver = webdriver.Firefox(options=options)

search_query = str(input("Search: "))
# Open a session against server
driver.get('https://www.tradera.com/search?q=' + search_query + '&itemStatus=Ended')

# Accept "information about cookies"
driver.find_element_by_css_selector('button.btn-primary:nth-child(2)').click()

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

        # Sleep 10x times longer than it took the server to respond
        response_delay = round(time.time() - t0)
        print("Sleep: " + str(response_delay * 10) + " seconds")
        time.sleep(10 * response_delay)

    # Grab each product from one page and put them in a list
    containers = driver.find_elements_by_class_name("item-card-container")

    # Go through each product in containers-list and scrape essential data
    for container in containers:
        title = container.find_element_by_class_name("item-card-title.d-flex.flex-row.mb-2").text
        sell_price = strip_out_currency(container.find_elements_by_class_name('text-nowrap.font-weight-bold.item-card'
                                                                              '-details-price'))

        bids = strip_out_bid_text(container.find_elements_by_class_name("text-nowrap.mr-2"))

        # Scrap any auction with zero bids
        if bids > 0:
            products.append({"Title": title, "Sell price": sell_price, "Bids": bids})

    print("Page " + str(page) + " of " + str(user_page_choice) + " done")
    # Once we have gone through the whole page, switch page
    page += 1

# Create dataframe for displaying the data
data_frame = pd.DataFrame(products)

# Print out the results
average_sales_price = int(round(data_frame['Sell price'].mean()))
print("Average sales price of " + search_query + " is " + str(average_sales_price) + " SEK")

# Save all products in a CSV file
data_frame.to_csv(r'Saved_scrapes\%s_scrape.csv' % search_query)

print("Saved " + search_query + r"scrape.csv at: Working_directory\Saved_scrapes")
