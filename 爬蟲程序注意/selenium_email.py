
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

# 初始化瀏覽器（請確認 chromedriver 路徑正確）
driver = webdriver.Chrome("c:\\chromedriver\\chromedriver.exe")
driver.get("https://accounts.google.com/")

# 等待 email 欄位出現
email_input = WebDriverWait(driver, 10).until(
    EC.presence_of_element_located((By.ID, "identifierId"))
)

# 填入 email
email_input.send_keys("jeremyfan.genshin@gmail.com")


time.sleep(2)
# 點擊「下一步」按鈕
next_button = driver.find_element(By.ID, "identifierNext")
next_button.click()
