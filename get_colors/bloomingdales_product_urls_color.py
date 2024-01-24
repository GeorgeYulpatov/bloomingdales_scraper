import random
import time
import re
from selenium import webdriver
from selenium.webdriver.common.by import By
from fake_useragent import UserAgent
from bs4 import BeautifulSoup
from urllib.parse import urlparse, parse_qs
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC


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


def scraper(driver):
    page_source = driver.page_source
    soup = BeautifulSoup(page_source, 'lxml')

    all_container = soup.find('ul', class_="items grid-x grid-margin-x")
    products = all_container.find_all('li', class_="small-6 medium-4 large-3 cell")

    for item in products:
        url_container = item.find('a')
        base_section_url = url_container.get("href")

        colors_container = item.find("ul", class_="colorSwatches swatch-count-2")
        if colors_container:
            colors_names = colors_container.find_all('li')

            colors = []
            for item_colors in colors_names:
                color = item_colors.get("aria-label")
                colors.append(color)

            for element_colors in colors:
                element_colors = element_colors.replace(" ", "_")
                full_url_color = f"https://www.bloomingdales.com{base_section_url}#color={element_colors}"
                print(full_url_color)
        else:
            base_section_url = f"https://www.bloomingdales.com{base_section_url}"
            print(base_section_url)


def get_product_links(driver):

    for i in range(1, 158):
        driver.get(f'https://www.bloomingdales.com/shop/womens-apparel/all-women/Pageindex,Productsperpage/{i},120?id=1003340')
        print(f'Page #{i}')
        scraper(driver)
        time.sleep(3)


def main():
    driver = setup_driver()
    get_product_links(driver)
    driver.quit()


if __name__ == "__main__":
    main()
