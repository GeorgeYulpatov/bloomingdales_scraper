import random
import time
import re
import csv
import datetime
from selenium import webdriver
from selenium.webdriver.common.by import By
from fake_useragent import UserAgent
from bs4 import BeautifulSoup
from urllib.parse import urlparse, parse_qs
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

current_datetime = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M")  # Получение текущей даты и времени
file_name_tbl = f"PI_shop-all-rugs_{current_datetime}.csv"  # Добавление даты к имени файла


def setup_driver():
    user_agent = UserAgent()
 
    options = webdriver.ChromeOptions()
    options.add_argument(f"user-agent={user_agent.random}")
    # options.add_argument("--headless")
    # options.add_argument("--disable-gpu")
    # options.add_argument("--no-sandbox")
    # options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--disable-blink-features=AutomationControlled")
    options.add_experimental_option("excludeSwitches", ["enable-automation"])
    options.add_experimental_option("useAutomationExtension", False)

    return webdriver.Chrome(options=options)


def scraper(driver, csv_writer):
    page_source = driver.page_source
    soup = BeautifulSoup(page_source, 'lxml')

    all_container = soup.find('ul', class_="items grid-x grid-margin-x")
    products = all_container.find_all('li', class_="small-6 medium-4 large-3 cell")

    for item in products:
        url_container = item.find('a')
        base_section_url = url_container.get("href")
        base_section_url = f"https://www.bloomingdales.com{base_section_url}"
        csv_writer.writerow([base_section_url])


def get_product_links(driver, csv_writer):
    for i in range(1, 59):
        driver.get(
            f'https://www.bloomingdales.com/shop/home/shop-all-rugs/Pageindex,Productsperpage/{i},120?id=1189062')
        print(f'Page #{i}')
        scraper(driver, csv_writer)
        time.sleep(3)


def main():
    with open(file_name_tbl, 'a', newline='') as csvfile:
        csv_writer = csv.writer(csvfile)
        csv_writer.writerow(['Full URL'])

        driver = setup_driver()
        get_product_links(driver, csv_writer)
        driver.quit()


if __name__ == "__main__":
    main()
