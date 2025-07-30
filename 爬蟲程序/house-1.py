from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup
import time


driver = webdriver.Chrome()
driver.get("https://buy.yungching.com.tw/")
wait = WebDriverWait(driver, 15)

# 開啟地區選單
wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, "div.area"))).click()

# 點選台中市
wait.until(EC.element_to_be_clickable((By.XPATH, "//label[text()='台中市']"))).click()
time.sleep(1)

# 點選太平區
wait.until(EC.element_to_be_clickable((By.XPATH, "//span[text()='太平區']"))).click()

# 等待「找房子」按鈕啟用
search_btn_selector = (
    "body > app-root > yc-ng-layout > div > app-buy-list > div.search-result > div.search-wrapper > div > app-buy-search > div > div > div.search-condition > div.condition > div.search-btn"
)

WebDriverWait(driver, 10).until(
    lambda d: "disabled" not in d.find_element(By.CSS_SELECTOR, search_btn_selector).get_attribute("class")
)

# 點擊按鈕
driver.find_element(By.CSS_SELECTOR, search_btn_selector).click()

# 可選：等待新頁面載入
time.sleep(3)

driver = webdriver.Chrome()
driver.get("https://buy.yungching.com.tw/")
wait = WebDriverWait(driver, 15)

# 等待房屋列表載入
wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "li.buy-item")))

# 用 BeautifulSoup 擷取頁面
soup = BeautifulSoup(driver.page_source, 'html.parser')
items = soup.select("li.buy-item")

results = []
for item in items:
    title = item.select_one('.caseName')
    address = item.select_one('.address')
    community = item.select_one('.community')
    house_type = item.select_one('.caseType')
    age = item.select("span")[1].text.strip() if len(item.select("span")) > 1 else ""
    reg_area = item.select_one('.regArea')
    main_area = item.select_one('.mainArea')
    floor = item.select_one('.floor')
    room = item.select_one('.room')
    car = item.select_one('.car')
    origin_price = item.select_one('.origin-price')
    discount = item.select_one('.discount')
    price = item.select_one('.price')
    link = item.select_one('a.link')

    results.append({
        "標題": title.text.strip() if title else "",
        "地址": address.text.strip() if address else "",
        "社區": community.text.strip() if community else "",
        "類型": house_type.text.strip() if house_type else "",
        "屋齡": age,
        "建坪": reg_area.text.strip() if reg_area else "",
        "主+陽": main_area.text.strip() if main_area else "",
        "樓層": floor.text.strip() if floor else "",
        "格局": room.text.strip() if room else "",
        "車位": car.text.strip() if car else "",
        "原價": origin_price.text.strip() if origin_price else "",
        "折扣": discount.text.strip() if discount else "",
        "售價": price.text.strip() if price else "",
        "連結": f"https://buy.yungching.com.tw/{link['href']}" if link else ""
    })

# 輸出
for r in results:
    print(r)

driver.quit()
