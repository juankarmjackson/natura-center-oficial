import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC


def login():
    print("🔐 Iniciando sesión en Feliu Badaló...")

    options = Options()
    options.add_argument("--headless")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")

    driver = webdriver.Chrome(options=options)

    try:
        driver.get("https://online.feliubadalo.com/customer/account/login/")

        try:
            WebDriverWait(driver, 5).until(
                EC.element_to_be_clickable((By.ID, "CybotCookiebotDialogBodyLevelButtonLevelOptinAllowAll"))
            ).click()
            print("🍪 Cookies aceptadas")
        except:
            print("👌 No apareció el banner de cookies")

        WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.ID, "email")))
        driver.find_element(By.ID, "email").send_keys("majadahonda@naturacenter.es")
        driver.find_element(By.ID, "pass").send_keys("NaturaH6")
        WebDriverWait(driver, 5).until(EC.element_to_be_clickable((By.ID, "send2"))).click()

        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, ".customer-welcome, .action.logout"))
        )
        print("✅ Login correcto")

    except Exception as e:
        print(f"❌ Error durante login: {e}")

    finally:
        driver.quit()
        print("👋 Sesión cerrada")


if __name__ == "__main__":
    login()
