'''

'''
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup
import time
import csv

def setup_driver():
    chrome_options = Options()
    chrome_options.add_argument("--start-maximized")
    driver = webdriver.Chrome(options=chrome_options)
    return driver

def select_city_and_district(driver):
    wait = WebDriverWait(driver, 10)
    driver.get("https://buy.yungching.com.tw/")

    # 點選區域選單
    area_btn = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, "div.area")))
    area_btn.click()
    time.sleep(1)

    # 選擇台中市
    city_btns = wait.until(EC.presence_of_all_elements_located((By.CSS_SELECTOR, "div.menuSelect > div.menuBtn")))
    for city_btn in city_btns:
        if "台中市" in city_btn.text:
            driver.execute_script("arguments[0].click();", city_btn)
            break
    time.sleep(1)

    # 選擇太平區
    district_btns = driver.find_elements(By.CSS_SELECTOR, "span.itemBtn")
    for d_btn in district_btns:
        if "太平區" in d_btn.text:
            driver.execute_script("arguments[0].click();", d_btn)
            break
    time.sleep(1)

    # 點擊「找房子」
    search_btn = driver.find_element(By.CSS_SELECTOR, "div.search-btn")
    driver.execute_script("arguments[0].click();", search_btn)
    time.sleep(3)

def parse_house_item(item):
    card = item.find("yc-ng-buy-house-card")
    if not card:
        return None
    info = {}
    link_tag = card.find("a", class_="link")
    if link_tag:
        info['link'] = "https://buy.yungching.com.tw/" + link_tag.get('href', '').strip()
    else:
        info['link'] = None

    info['caseName'] = card.find("div", class_="caseName").text.strip() if card.find("div", class_="caseName") else None
    info['address'] = card.find("span", class_="address").text.strip() if card.find("span", class_="address") else None
    info['community'] = card.find("span", class_="community").text.strip() if card.find("span", class_="community") else None
    info['caseType'] = card.find("span", class_="caseType").text.strip() if card.find("span", class_="caseType") else None

    case_info = card.find("div", class_="case-info")
    if case_info:
        spans = case_info.find_all("span")
        # 有些資訊已經取過，以下是嘗試補充
        info['age'] = spans[1].text.strip() if len(spans) > 1 else None
        info['building_area'] = spans[2].text.strip() if len(spans) > 2 else None
        info['main_area'] = spans[3].text.strip() if len(spans) > 3 else None
        info['floor'] = spans[4].text.strip() if len(spans) > 4 else None
        info['rooms'] = spans[5].text.strip() if len(spans) > 5 else None
        info['car'] = spans[6].text.strip() if len(spans) > 6 else None
    else:
        info['age'] = info['building_area'] = info['main_area'] = info['floor'] = info['rooms'] = info['car'] = None

    info['note'] = card.find("div", class_="note").text.strip() if card.find("div", class_="note") else None

    price_wrapper = card.find("div", class_="price-wrapper")
    if price_wrapper:
        origin_price = price_wrapper.find("span", class_="origin-price")
        discount = price_wrapper.find("span", class_="discount")
        price = price_wrapper.find("div", class_="price")
        info['origin_price'] = origin_price.text.strip() if origin_price else None
        info['discount'] = discount.text.strip() if discount else None
        info['price'] = price.text.strip() if price else None
    else:
        info['origin_price'] = info['discount'] = info['price'] = None

    return info

def crawl_all_pages(driver):
    wait = WebDriverWait(driver, 10)
    all_data = []
    # max_page = 178
    max_page = 178
    current_page = 1

    while True:
        print(f"爬取第 {current_page} 頁")
        wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "li.buy-item")))
        soup = BeautifulSoup(driver.page_source, 'html.parser')
        items = soup.select("li.buy-item")
        for item in items:
            data = parse_house_item(item)
            if data:
                all_data.append(data)

        if current_page >= max_page:
            print("已達最後一頁，結束爬取。")
            break

        # 找分頁區塊
        pagination = driver.find_element(By.CSS_SELECTOR, "yc-ng-pagination div.pagination")

        # 判斷是否有 "..."，與下一頁按鈕狀態
        next_btn = pagination.find_element(By.CSS_SELECTOR, "div.paginationNext")
        disabled_next = "disabled" in next_btn.get_attribute("class")

        # 先嘗試點下一頁按鈕
        if not disabled_next:
            next_btn.click()
            current_page += 1
            time.sleep(3)
            continue
        else:
            # 下一頁按鈕 disabled 表示已到最後一頁
            break

    return all_data

def save_to_csv(data, filename="yungching_taiping.csv"):
    keys = data[0].keys() if data else []
    with open(filename, "w", newline="", encoding="utf-8-sig") as f:
        writer = csv.DictWriter(f, fieldnames=keys)
        writer.writeheader()
        writer.writerows(data)

def main():
    driver = setup_driver()
    try:
        select_city_and_district(driver)
        data = crawl_all_pages(driver)
        save_to_csv(data)
        print(f"總共爬取 {len(data)} 筆資料，已存成 CSV。")
    finally:
        driver.quit()

if __name__ == "__main__":
    main()
