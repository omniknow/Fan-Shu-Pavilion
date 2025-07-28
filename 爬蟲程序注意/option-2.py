from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
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

# 使用 CSS Selector 選擇 Option 2
option2 = WebDriverWait(driver, 10).until(
    EC.element_to_be_clickable((By.CSS_SELECTOR, "#dropdown > option:nth-child(3)"))
)

# 點擊 Option 2
option2.click()

# 輸出選擇的選項
selected_option = driver.find_element(By.CSS_SELECTOR, "#dropdown option:checked")
print("選擇的選項是:", selected_option.text)

# 暫停 3 秒鐘觀察結果
import time
time.sleep(3)

# 關閉瀏覽器
driver.quit()
