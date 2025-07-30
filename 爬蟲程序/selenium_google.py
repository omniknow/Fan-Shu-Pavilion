from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time

# 初始化瀏覽器
driver=webdriver.Chrome("c:\\chromedriver\\chromedriver.exe")
driver.get("https://accounts.google.com")  # 替換為實際登入頁

# # 登入
driver.find_element(By.CLASS_NAME, "whsOnd zHQkBf").send_keys("your_username")
# driver.find_element(By.ID, "password").send_keys("your_password")
# driver.find_element(By.ID, "login-button").click()    

# # 等待登入完成（例如等待某個 dashboard 出現）
# WebDriverWait(driver, 10).until(
#     EC.presence_of_element_located((By.ID, "checkbox-section"))
# )

# # 勾選 checkbox 並送出
# checkbox = driver.find_element(By.ID, "agree-check")
# checkbox.click()
# driver.find_element(By.ID, "submit-button").click()

# # 開始爬取 10 頁資料
# for page in range(1, 11):
#     print(f"📄 正在爬第 {page} 頁資料...")

#     # 等待資料區載入
#     WebDriverWait(driver, 10).until(
#         EC.presence_of_element_located((By.CLASS_NAME, "data-row"))
#     )

#     # 擷取資料（假設每行資料是 .data-row class）
#     rows = driver.find_elements(By.CLASS_NAME, "data-row")
#     for row in rows:
#         print(row.text)  # 或自訂的資料擷取規則

#     # 點擊下一頁按鈕（如果不是最後一頁）
#     if page < 10:
#         next_button = WebDriverWait(driver, 10).until(
#             EC.element_to_be_clickable((By.ID, "next-page"))
#         )
#         next_button.click()

#         # 可加 sleep，給網頁載入一點緩衝時間（或更好地用 WebDriverWait）
#         time.sleep(2)

# # 關閉瀏覽器
# driver.quit()
