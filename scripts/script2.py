import pandas as pd
import time
import json
import os
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

UPLOAD_FOLDER = "uploads"

def login(driver):
    print("🔐 Iniciando sesión en Feliu Badaló...")
    driver.get("https://online.feliubadalo.com/customer/account/login/")

    # Aceptar cookies si aparece
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

def buscar_y_añadir(driver, codigo_barras):
    try:
        # Buscar el producto
        search_input = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.ID, "search"))
        )
        search_input.clear()
        search_input.send_keys(codigo_barras)
        search_input.send_keys(Keys.ENTER)

        # Esperar resultados
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "a.df-card__main"))
        )

        # Añadir al carrito
        WebDriverWait(driver, 5).until(
            EC.element_to_be_clickable((By.CSS_SELECTOR, "button.df-add-to-cart-btn"))
        ).click()

        print(f"🛒 Añadido al carrito: {codigo_barras}")
        return True

    except Exception as e:
        print(f"❌ No añadido: {codigo_barras} | {e}")
        return False

def ejecutar_carrito_feliubadalo():
    print("🛒 Iniciando scriptcarrito2.py con el archivo original del usuario...")

    # Obtener el último CSV subido
    archivos_csv = [f for f in os.listdir(UPLOAD_FOLDER) if f.endswith(".csv")]
    if not archivos_csv:
        print("⚠️ No hay archivo CSV subido")
        return

    # Usar el más reciente
    archivos_csv.sort(key=lambda f: os.path.getmtime(os.path.join(UPLOAD_FOLDER, f)), reverse=True)
    csv_path = os.path.join(UPLOAD_FOLDER, archivos_csv[0])
    print(f"📄 Usando archivo: {csv_path}")

    try:
        df = pd.read_csv(csv_path)
    except Exception as e:
        print(f"❌ Error leyendo CSV: {e}")
        return

    if "Código de Barras" not in df.columns:
        print("⚠️ El archivo no tiene columna 'Código de Barras'")
        return

    codigos = df["Código de Barras"].dropna().astype(str).tolist()
    if not codigos:
        print("⚠️ No hay códigos válidos en el CSV")
        return

    options = Options()
    options.add_argument("--headless")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")

    driver = webdriver.Chrome(options=options)
    añadidos = 0

    try:
        login(driver)

        for codigo in codigos:
            if buscar_y_añadir(driver, codigo.strip()):
                añadidos += 1
            time.sleep(2)

        print(f"✅ Añadidos al carrito: {añadidos}")

    except Exception as e:
        print(f"❌ Error general: {e}")

    finally:
        driver.quit()
        print("👋 Selenium finalizado")

        # ✅ Actualizar contador en counters.json
        try:
            counters_path = os.path.join(UPLOAD_FOLDER, "counters.json")
            if os.path.exists(counters_path):
                with open(counters_path, "r", encoding="utf-8") as f:
                    counters = json.load(f)
            else:
                counters = {}

            counters["feliubadalo"] = añadidos

            with open(counters_path, "w", encoding="utf-8") as f:
                json.dump(counters, f, indent=4)

            print("🔢 Contador actualizado correctamente")

        except Exception as e:
            print(f"⚠️ Error al guardar contador: {e}")

if __name__ == "__main__":
    ejecutar_carrito_feliubadalo()
