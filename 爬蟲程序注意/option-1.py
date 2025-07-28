from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import Select
import undetected_chromedriver as uc

# 啟動瀏覽器
options = uc.ChromeOptions()
driver = uc.Chrome(options=options)

# 打開網站
driver.get("https://the-internet.herokuapp.com/dropdown")

# 等待下拉選單加載完畢
dropdown = WebDriverWait(driver, 10).until(
    EC.presence_of_element_located((By.ID, "dropdown"))
)


# 使用 Select 類別來操作下拉選單
select = Select(dropdown)

# 選擇下拉選單中的第一個選項（索引從 0 開始）
select.select_by_index(1)  # 選擇 "Option 1"（如果有的話）

# 輸出選擇的選項
selected_option = select.first_selected_option
print("選擇的選項是:", selected_option.text)

# 暫停 3 秒鐘觀察結果
import time
time.sleep(3)

# 關閉瀏覽器
driver.quit()
