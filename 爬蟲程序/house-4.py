import csv
import os
import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException, StaleElementReferenceException


def select_city_and_district(driver):
    wait = WebDriverWait(driver, 10)
    driver.get("https://buy.yungching.com.tw/")

    area_btn = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, "div.area")))
    area_btn.click()
    time.sleep(1)

    city_btns = wait.until(EC.presence_of_all_elements_located((By.CSS_SELECTOR, "div.menuSelect > div.menuBtn")))
    for city_btn in city_btns:
        if "台中市" in city_btn.text:
            driver.execute_script("arguments[0].click();", city_btn)
            break
    time.sleep(1)

    district_btns = driver.find_elements(By.CSS_SELECTOR, "span.itemBtn")
    for d_btn in district_btns:
        if "太平區" in d_btn.text:
            driver.execute_script("arguments[0].click();", d_btn)
            break
    time.sleep(1)

    search_btn = driver.find_element(By.CSS_SELECTOR, "div.search-btn")
    driver.execute_script("arguments[0].click();", search_btn)
    time.sleep(3)


def parse_items(driver):
    results = []
    wait = WebDriverWait(driver, 10)
    try:
        items = wait.until(EC.presence_of_all_elements_located((By.CSS_SELECTOR, "li.buy-item")))
    except TimeoutException:
        return results

    for idx in range(len(items)):
        try:
            item = driver.find_element(By.XPATH, f"(//li[contains(@class, 'buy-item')])[{idx + 1}]")
            title = item.find_element(By.CSS_SELECTOR, '.caseName').text.strip() if item.find_elements(By.CSS_SELECTOR, '.caseName') else ""
            address = item.find_element(By.CSS_SELECTOR, '.address').text.strip() if item.find_elements(By.CSS_SELECTOR, '.address') else ""
            community = item.find_element(By.CSS_SELECTOR, '.community').text.strip() if item.find_elements(By.CSS_SELECTOR, '.community') else ""
            house_type = item.find_element(By.CSS_SELECTOR, '.caseType').text.strip() if item.find_elements(By.CSS_SELECTOR, '.caseType') else ""
            spans = item.find_elements(By.CSS_SELECTOR, 'span')
            age = spans[1].text.strip() if len(spans) > 1 else ""
            reg_area = item.find_element(By.CSS_SELECTOR, '.regArea').text.strip() if item.find_elements(By.CSS_SELECTOR, '.regArea') else ""
            main_area = item.find_element(By.CSS_SELECTOR, '.mainArea').text.strip() if item.find_elements(By.CSS_SELECTOR, '.mainArea') else ""
            floor = item.find_element(By.CSS_SELECTOR, '.floor').text.strip() if item.find_elements(By.CSS_SELECTOR, '.floor') else ""
            room = item.find_element(By.CSS_SELECTOR, '.room').text.strip() if item.find_elements(By.CSS_SELECTOR, '.room') else ""
            car = item.find_element(By.CSS_SELECTOR, '.car').text.strip() if item.find_elements(By.CSS_SELECTOR, '.car') else ""
            origin_price = item.find_element(By.CSS_SELECTOR, '.origin-price').text.strip() if item.find_elements(By.CSS_SELECTOR, '.origin-price') else ""
            discount = item.find_element(By.CSS_SELECTOR, '.discount').text.strip() if item.find_elements(By.CSS_SELECTOR, '.discount') else ""
            price = item.find_element(By.CSS_SELECTOR, '.price').text.strip() if item.find_elements(By.CSS_SELECTOR, '.price') else ""
            link_el = item.find_element(By.CSS_SELECTOR, 'a.link') if item.find_elements(By.CSS_SELECTOR, 'a.link') else None
            link = f"https://buy.yungching.com.tw/{link_el.get_attribute('href')}" if link_el else ""

            results.append({
                "標題": title,
                "地址": address,
                "社區": community,
                "類型": house_type,
                "屋齡": age,
                "建坪": reg_area,
                "主+陽": main_area,
                "樓層": floor,
                "格局": room,
                "車位": car,
                "原價": origin_price,
                "折扣": discount,
                "售價": price,
                "連結": link,
                "資料來源": "永慶房仲網"  # 新增欄位
            })
        except StaleElementReferenceException:
            print("元素失效，跳過此筆")
        except Exception as e:
            print(f"其他錯誤：{e}")
    return results


def write_to_csv(filename, data, is_first_page):
    file_exists = os.path.isfile(filename)
    with open(filename, mode='a', newline='', encoding='utf-8-sig') as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=data[0].keys())
        if is_first_page and not file_exists:
            writer.writeheader()
        writer.writerows(data)


def crawl_all_pages(driver, filename):
    wait = WebDriverWait(driver, 15)
    page_num = 1
    max_page = 200

    while page_num <= max_page:
        print(f"爬取第 {page_num} 頁")

        try:
            wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "li.buy-item")))
        except TimeoutException:
            print("等待列表元素超時，跳出")
            break

        data = parse_items(driver)

        if data:
            write_to_csv(filename, data, is_first_page=(page_num == 1))

        try:
            pagination = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "yc-ng-pagination div.pagination")))
            next_btn = pagination.find_element(By.CSS_SELECTOR, "div.paginationNext")
            classes = next_btn.get_attribute("class")
            if "disabled" in classes:
                print("下一頁按鈕已禁用，結束爬取。")
                break
            else:
                next_btn.click()
                page_num += 1
                time.sleep(2)
        except (NoSuchElementException, TimeoutException):
            print("找不到下一頁按鈕或載入超時，結束爬取。")
            break


def main():
    options = webdriver.ChromeOptions()
    # options.add_argument("--headless")
    options.add_argument("--log-level=3")
    driver = webdriver.Chrome(options=options)

    select_city_and_district(driver)

    filename = "yungching_houses.csv"
    crawl_all_pages(driver, filename)

    print(f"資料已儲存至 {filename}")
    driver.quit()


if __name__ == "__main__":
    main()
