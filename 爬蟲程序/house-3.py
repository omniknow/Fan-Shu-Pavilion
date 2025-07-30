'''
你這個「元素失效，跳過此筆」訊息，是因為爬取的時候 Selenium 讀取到的元素在操作過程中被網頁重新渲染了，導致元素引用失效（StaleElementReferenceException）。

你目前的做法已經用 try-except 包起來跳過失效的項目，這樣處理是合理的，因為網站資料更新或頁面動態渲染導致這種狀況常見。

如果想更穩定且少掉失效元素的方式，可以嘗試：
在抓取元素前，先取得元素清單，並用一個新的獨立方法針對每個元素重新定位。
這樣避免對原本被動態替換的元素物件直接操作。

每個元素資訊使用 xpath 或獨立定位器再次抓取，而非從舊元素繼續抓取。
'''
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
    items = driver.find_elements(By.CSS_SELECTOR, "li.buy-item")
    for item in items:
        try:
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
                "連結": link
            })
        except StaleElementReferenceException:
            print("元素失效，跳過此筆")
            continue
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
    max_page = 178  # 預估最大頁數

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
            if "disabled" in next_btn.get_attribute("class"):
                print("下一頁按鈕已禁用，結束爬取。")
                break
            next_btn.click()
            page_num += 1
            time.sleep(2)
        except (NoSuchElementException, TimeoutException):
            print("找不到下一頁按鈕或載入超時，結束爬取。")
            break

def main():
    options = webdriver.ChromeOptions()
    options.add_argument("--log-level=3")
    driver = webdriver.Chrome(options=options)

    select_city_and_district(driver)
    filename = "yungching_houses.csv"
    crawl_all_pages(driver, filename)
    print(f"資料已儲存至 {filename}")
    driver.quit()

if __name__ == "__main__":
    main()
