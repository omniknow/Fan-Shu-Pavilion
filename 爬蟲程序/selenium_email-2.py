# import undetected_chromedriver as uc
# from selenium.webdriver.common.by import By
# from selenium.webdriver.support.ui import WebDriverWait
# from selenium.webdriver.support import expected_conditions as EC

# import time

# # 啟用 undetected ChromeDriver
# options = uc.ChromeOptions()
# driver = uc.Chrome(options=options)

# driver.get("https://accounts.google.com/")

# # 等待 email 欄位
# email_input = WebDriverWait(driver, 10).until(
#     EC.visibility_of_element_located((By.ID, "identifierId"))
# )

# # 填入 email 並點擊
# email_input.send_keys("jeremyfan.genshin@gmail.com")
# driver.find_element(By.ID, "identifierNext").move_to_element()
# time.sleep(10)  # 等待幾秒觀察結果，依需要調整

# # driver.back()

# time.sleep(10)  # 等待幾秒觀察結果，依需要調整

# driver.quit()  # 明確關閉，不依賴 __del__



from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import undetected_chromedriver as uc
import time

# 啟動瀏覽器
options = uc.ChromeOptions()
driver = uc.Chrome(options=options)
driver.get("https://accounts.google.com/")

# 輸入 Email
email_input = WebDriverWait(driver, 10).until(
    EC.visibility_of_element_located((By.ID, "identifierId"))
)
email_input.send_keys("jeremyfan.genshin@gmail.com")

# 找到「下一步」按鈕
next_button = WebDriverWait(driver, 10).until(
    EC.element_to_be_clickable((By.ID, "identifierNext"))
)

# 模擬滑鼠移到按鈕上（不會點擊）
actions = ActionChains(driver)
actions.move_to_element(next_button).perform()

# 👉 如果要點擊，可加上 .click()
# actions.move_to_element(next_button).click().perform()


time.sleep(10)
driver.quit()

