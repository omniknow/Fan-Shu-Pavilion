from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import undetected_chromedriver as uc
import time

# 啟動瀏覽器
options = uc.ChromeOptions()
driver = uc.Chrome(options=options)
driver.get("https://the-internet.herokuapp.com/checkboxes")

# 等待第一個 checkbox 變得可點擊
checkbox1 = WebDriverWait(driver, 10).until(    
    EC.element_to_be_clickable((By.CSS_SELECTOR, "#checkboxes > input[type=checkbox]:nth-child(1)"))
)

# 點選 checkbox（如果沒被打勾）
if not checkbox1.is_selected():
    checkbox1.click()

print("Checkbox 1 選取狀態：", checkbox1.is_selected())

time.sleep(5)

# 關閉瀏覽器
driver.quit()









