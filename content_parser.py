import os
import csv
import html
import json
import time
import openpyxl
import datetime
import requests
from selenium import webdriver
from fake_useragent import UserAgent
from urllib.parse import urlparse, parse_qs
from concurrent.futures import ThreadPoolExecutor
from requests_futures.sessions import FuturesSession

current_datetime = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M")  # Получение текущей даты и времени
file_name_tbl = f"New_Product_Information_bloomingdales_{current_datetime}.xlsx"  # Добавление даты к имени файла

THREAD_COUNT = 5


def setup_driver():
    user_agent = UserAgent()

    options = webdriver.ChromeOptions()
    # Обеспечивает возможность открыть браузер в так называемом "режиме без головы"
    # options.add_argument("--headless")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument(f"user-agent={user_agent.random}")
    options.add_experimental_option("excludeSwitches", ["enable-automation"])
    options.add_experimental_option("useAutomationExtension", False)

    return webdriver.Chrome(options=options)


def download(urls):
    if not os.path.exists('photo_bloomingdales'):
        os.makedirs('photo_bloomingdales')

    with FuturesSession(executor=ThreadPoolExecutor(max_workers=THREAD_COUNT)) as session:
        for url in urls:
            max_retries = 5  # Максимальное количество попыток
            retries = 0
            while retries < max_retries:
                try:

                    response = session.get(url).result()
                    file_image_name = os.path.basename(urlparse(response.url).path).split('.')[0]
                    file_image_name = file_image_name.replace('?', '_').replace('=', '_')
                    with open(f'photo_bloomingdales/{file_image_name}.jpeg', 'wb') as f:
                        f.write(response.content)
                    time.sleep(1)
                    yield f'photo_bloomingdales/{file_image_name}.jpeg'
                    break  # Прерываем цикл повторных попыток, если загрузка прошла успешно
                except requests.exceptions.ConnectionError as e:
                    print(f"Произошла ошибка соединения: {e}. Повторная попытка...")
                    retries += 1
                    time.sleep(2)  # Пауза перед повторной попыткой
            else:
                print(f"Не удалось загрузить {url} после {max_retries} попыток.")


def scraper(data, product_id, workbook, sheet):
    global color_id, normal_name, sex, full_url, file_paths, color_name, product_info

    products = data.get('product', [])
    try:
        product_url = data['product'][0]['identifier']['productUrl']  # Ссылка на товар
    except KeyError:
        product_url = " "

    try:
        top_level_category_name = html.unescape(data['product'][0]['identifier']['topLevelCategoryName'])
    except KeyError:
        top_level_category_name = " "

    try:
        top_level_category_id = data['product'][0]['identifier']['topLevelCategoryID']
    except KeyError:
        top_level_category_id = " "

    try:
        product_name = data['product'][0]['detail']['name']  # Название продукта

        if "Men's" in product_name:
            text = product_name
            word = "Men's"
            if word in text:
                sex = word

        elif "Women's" in product_name:
            text = product_name
            word = "Women's"
            if word in text:
                sex = word

        elif "Boys" in product_name:
            text = product_name
            word = "Boys"
            if word in text:
                sex = word

        elif "Girls" in product_name:
            text = product_name
            word = "Girls"
            if word in text:
                sex = word

        else:
            sex = "Unisex"

    except KeyError:
        product_name = " "

    try:
        description = html.unescape(data['product'][0]['detail']['description'])  # Описание
    except KeyError:
        description = " "

    try:
        secondary_descrirtion = data['product'][0]['detail']['secondaryDescription']  # Вторичное Описание
    except KeyError:
        secondary_descrirtion = " "

    try:
        seo_keywords = data['product'][0]['detail']['seoKeywords']  # Типо теги для СЕО
    except KeyError:
        seo_keywords = " "

    try:
        bullet_text = data['product'][0]['detail']['bulletText']
        bullet_text = ("\n".join(map(str, bullet_text)))  # Пуля текст
    except KeyError:
        bullet_text = " "

    try:
        dimensions_bullet_text = data['product'][0]['detail']['dimensionsBulletText']
        dimensions_bullet_text = ("\n".join(map(str, dimensions_bullet_text)))  # Пуля текст 2
    except KeyError:
        dimensions_bullet_text = " "

    try:
        materials_and_care = data['product'][0]['detail']['materialsAndCare']
        materials_and_care = ("\n".join(map(str, materials_and_care)))  # Характер материал
    except KeyError:
        materials_and_care = " "

    try:
        type_name = html.unescape(data['product'][0]['detail']['typeName'])  # Тип товара
    except KeyError:
        type_name = " "

    try:
        brand_name = html.unescape(data['product'][0]['detail']['brand']['name'])  # Бренд
    except KeyError:
        brand_name = " "

    try:
        brand_sub_brand = data['product'][0]['detail']['brand']['subBrand']  # Суб бренд
    except KeyError:
        brand_sub_brand = " "

    # Доступ к карте цветов
    for product in products:
        color_map = product.get('traits', {}).get('colors', {}).get('colorMap', {})

        for color_id, color_info in color_map.items():
            color_id = color_info['id']
            color_name = color_info['name'].replace(' ', '_')
            try:
                normal_name = color_info['normalName']
            except KeyError:
                normal_name = "Unknown"
            imagery_files = color_info['imagery']['images']

            file_paths = []
            for image_info in imagery_files:
                file_path = image_info['filePath']
                file_path = (f'https://images.bloomingdalesassets.com/is/image/BLM/products/{file_path}?op_sharpen=1&'
                             f'wid=500&fit=fit,1&$filtersm$&fmt=webp')
                file_paths.append(file_path)

            full_url = (f'https://www.bloomingdales.com{product_url}&CategoryID={top_level_category_id}'
                        f'#color={color_name}')
            color_name = color_name.replace('_', ' ')

            dir_pic_name = list(download(file_paths))
            image_file_paths = ", ".join(file_paths)

            product_info = {
                "Product ID": product_id,
                "Product Name": product_name,
                "Product Link": full_url,
                "Top Level Category Name": top_level_category_name,
                "Type Name": type_name,
                # "Rootcategory": rootcategory,
                # "Homecategory": homecategory,
                "Color Name": color_name,
                "Color ID": color_id,
                "Normal Name": normal_name,
                "Image File Paths": image_file_paths,
                # "Department Name": department_name,
                "Sex": sex,
                "Description": description,
                "Secondary Description": secondary_descrirtion,
                "SEO Keywords": seo_keywords,
                "Bullet Text": bullet_text,
                "Dimensions Bullet Text": dimensions_bullet_text,
                "Materials And Care": materials_and_care,
                "Brand Name": brand_name,
                "Brand Sub Brand": brand_sub_brand,
                "Image Names": ", ".join(dir_pic_name),

            }
            print(product_info)
            sheet.append(tuple(product_info.values()))
            workbook.save(file_name_tbl)

    return product_info


def get_product_links(sheet, driver, workbook):

    with open('all_urls_main_comp.csv', newline='', encoding='utf-8') as csvfile:
        csvreader = csv.reader(csvfile, delimiter=',')

        for row in csvreader:
            try:
                parsed_url = urlparse(row[0])
                query_params = parse_qs(parsed_url.query)
                id_value = query_params.get('ID', None)
                if id_value:
                    product_id = id_value[0]
                    api_url_product = (f'https://www.bloomingdales.com/xapi/digital/v1/product/{product_id}'
                                       f'?clientId=PROS&_regionCode=US&currencyCode=USD&_shoppingMode=SITE&size=small'
                                       f'&_customerState=GUEST')
                    driver.get(api_url_product)
                    page_source = driver.page_source

                    start = page_source.find('{')
                    end = page_source.rfind('}')
                    json_str = page_source[start:end + 1]  # <class 'str'>

                    data = json.loads(json_str)  # <class 'dict'>
                    # print(type(data))

                    scraper(data, product_id, workbook, sheet)
                    # product_info = scraper(data, product_id, workbook, sheet)
                    #
                    # sheet.append(tuple(product_info.values()))
                    # workbook.save('Product Information MACYS.xlsx')

                else:
                    print("Отличие элементов ожидаемого JSON : ID не найден")
                    continue  # Пропускаем текущую итерацию и переходим к следующей

            except json.decoder.JSONDecodeError as e:
                print(f"Ошибка при декодировании JSON: {e}")
                continue  # Пропускаем текущую итерацию и переходим к следующей

    driver.quit()


def create_workbook():
    workbook = openpyxl.Workbook()
    sheet = workbook.active

    headers = [
        "Product ID",
        "Product Name",
        "Product Link",
        "Top Level Category Name",
        "Type Name",
        # "Rootcategory",
        # "Homecategory",
        "Color Name",
        "Color ID",
        "Normal Name",
        "Image File Path",
        # "Department Name",
        "Sex",
        "Description",
        "Secondary Description",
        "SEO Keywords",
        "Bullet Text",
        "Dimensions Bullet Text",
        "Materials And Care",
        "Brand Name",
        "Brand Sub Brand",
        "Image Names",

    ]

    for col_num, header in enumerate(headers, 1):
        sheet.cell(row=1, column=col_num).value = header

    return workbook, sheet


def main():
    with setup_driver() as driver:
        workbook, sheet = create_workbook()
        get_product_links(sheet, driver, workbook)
        workbook.save(file_name_tbl)

    return True


if __name__ == "__main__":
    main()
