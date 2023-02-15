import datetime
import time

from bs4 import BeautifulSoup
from logs.logger import logger
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
import re
from webdriver_manager.chrome import ChromeDriverManager

from settings import destination_city_codes, origin_city_codes, price_range, pobeda_dt_format


def generate_date_range() -> list[datetime]:
    search_start_date = datetime.date(day=1, month=3, year=2023)
    search_end_date = datetime.date(day=20, month=10, year=2023)
    day_difference = (search_end_date - search_start_date).days
    date_range = [dd for dd in [search_start_date + datetime.timedelta(days=i) for i in range(day_difference)]
                  if dd.month in (3, 4, 9, 10) and dd.weekday() in (0, 1, 2, 3, 4)]
    return date_range


def get_price(tag_data) -> int:
    price = tag_data.text
    price = re.findall("\d", price)
    price = ''.join(price)
    return int(price)


def check_price(dd, origin_code, destination_code):
    if origin_code == destination_code:
        return

    prices_found = []
    formatted_date = dd.strftime(pobeda_dt_format)

    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()))
    url = f"https://ticket.pobeda.aero/websky/?origin-city-code%5B0%5D={origin_code}" \
          f"&destination-city-code%5B0%5D={destination_code}&date%5B0%5D={formatted_date}" \
          f"&segmentsCount=1&adultsCount=1&youngAdultsCount=0&childrenCount=0&" \
          f"infantsWithSeatCount=0&infantsWithoutSeatCount=0&lang=ru#/search"

    driver.get(url)
    time.sleep(2)

    html_source = driver.page_source

    soup = BeautifulSoup(html_source, features="html.parser")
    tag_data = soup.find_all('span', attrs={'class': 'price-cell__text'})

    for item in tag_data:
        price = get_price(tag_data=item)
        prices_found.append(price)

    min_price = min(prices_found) if prices_found else 0

    message = f"Вот мин цена {min_price} {origin_code} {destination_code} {formatted_date}"
    logger.info(message)

    if min_price in price_range:
        logger_message = f"{origin_code}-{destination_code} {formatted_date} {min_price}"
        logger.warning(logger_message)
        logger.warning(url)

    driver.close()


if __name__ == "__main__":
    data_range_list = generate_date_range()
    for origin in origin_city_codes:
        for destination in destination_city_codes:
            for dd in data_range_list:
                check_price(dd=dd, origin_code=origin, destination_code=destination)
