import requests
from bs4 import BeautifulSoup
from selenium import webdriver
import time
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.action_chains import ActionChains
import lxml
import datetime
import csv

url = "https://yandex.ru/maps/?azimuth=0.25496952095784897&ll=57.012519%2C53.191070&z=3"

headers = {
    "Accept": "*/*",
    "User-Agent" : "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 YaBrowser/24.1.0.0 Safari/537.36"

}

value = str(input("Введите cookies:").strip())
cookies = {
    "cookie" : value
}

cur_date = datetime.datetime.now().strftime("%d_%Y_%H_%M")
with open(f"{cur_date}.csv", "w", encoding="cp1251") as file:
    writer = csv.writer(file, delimiter=";")
    writer.writerow(
        ("Название организации",
         "Город",
         "Телефон",
         "Ссылка на сайт",
         "Соц. сети"
         )
    )









def get_source_html(url, content):
    driver = webdriver.Chrome()
    driver.maximize_window()
    try:
        driver.get(url=url)
        time.sleep(10)
        search_box = driver.find_element(By.CLASS_NAME, "input__control")
        search_box.send_keys(f"{content}")
        search_box.send_keys(Keys.ENTER)
        count = 0
        actions = ActionChains(driver)
        time.sleep(5)
        while count != 750:

            find_more_element = driver.find_elements(By.CLASS_NAME, "search-snippet-view")[-1]

            try:

                actions.move_to_element(find_more_element).perform()


                count += 1

                print(f"[INFO] Обработано страниц:{count} [INFO]")


            except:
                break
        with open("index.html", "w", encoding="utf-8") as file:
            file.write(driver.page_source)
        with open("index.html", "r", encoding="utf-8") as file:
            src = file.read()
        time.sleep(5)
        soup = BeautifulSoup(src, "lxml")
        element = soup.find_all(class_="search-snippet-view")
        count = 0
        for elem in element:




            links = "https://yandex.ru" + elem.find("a", class_="search-snippet-view__link-overlay _focusable").get("href")
            req = requests.get(links, headers=headers, cookies=cookies, allow_redirects=False)
            src = req.text
            with open("element.html", "w", encoding="utf-8") as file:
                file.write(src)
            with open("element.html", "r", encoding="utf-8") as file:
                src = file.read()
            soup = BeautifulSoup(src, "lxml")
            try:
                element_name = soup.find(class_="orgpage-header-view__header").get_text()
            except:
                element_name = soup.find(class_="orgpage-header-view__header")
            try:
                element_href = soup.find("a", class_="business-urls-view__link").get("href")
            except:
                element_href = soup.find("a", class_="business-urls-view__link")


            try:
                element_aria = soup.find(class_="business-contacts-view__address-link").get("aria-label").split(",")[-1]
            except:
                element_aria = soup.find(class_="business-contacts-view__address-link")
            try:
                element_phone = soup.find(class_="orgpage-phones-view__phone-number").get_text()
            except:
                element_phone = soup.find(class_="orgpage-phones-view__phone-number")

            element_contact = soup.find_all(class_="business-contacts-view__social-button")

            social_link = []
            for social in element_contact:
                social_link.append([social.find("a").get("aria-label").split(",")[1], social.find("a").get("href")])

            with open(f"{cur_date}.csv", "a", encoding="cp1251") as file:
                writer = csv.writer(file, delimiter=";")
                writer.writerow(
                    (
                        element_name,
                        element_aria,
                        element_phone,
                        element_href,
                        social_link
                    )
                )
            count += 1
            print(f"[INFO] Происходит сбор и запись информации: {count} [INFO]")
            time.sleep(10)

    except Exception as ex:
        print(ex)
    finally:
        driver.close()
        driver.quit()


def main():
    search_content = str(input("Введите запрос:")).strip()
    get_source_html(url = url, content = search_content)

if __name__ == "__main__":
    main()

