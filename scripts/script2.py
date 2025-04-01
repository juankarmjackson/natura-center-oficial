import pandas as pd
import time
import json
import os
import random
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.common.exceptions import WebDriverException
from webdriver_manager.chrome import ChromeDriverManager

UPLOAD_FOLDER = "uploads"

USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/134.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/134.0.0.0 Safari/537.36",
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/133.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:126.0) Gecko/20100101 Firefox/126.0"
]

def crear_driver(user_agent):
    options = Options()
    options.add_argument("--headless")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument(f"user-agent={user_agent}")
    return webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)

def buscar_producto(driver, row_id, codigo_barras, nombre_producto):
    url = f"https://online.feliubadalo.com/catalogsearch/result/?q={codigo_barras}#/dfclassic/query={codigo_barras}"
    print(f"🔍 Buscando: {nombre_producto} ({codigo_barras})")

    try:
        driver.get(url)
        time.sleep(4)

        if driver.find_elements(By.CLASS_NAME, "df-no-results"):
            disponibilidad = "No disponible"
        elif driver.find_elements(By.CLASS_NAME, "df-card"):
            disponibilidad = "Disponible"
        else:
            disponibilidad = "No disponible"

        print(f"✅ {disponibilidad}")
        return {
            "row_id": row_id,
            "codigo_barras": codigo_barras,
            "nombre_producto": nombre_producto,
            "enlace": url,
            "disponibilidad": disponibilidad,
            "web": "feliubadalo"
        }
    except WebDriverException as e:
        print(f"❌ Error con Selenium en {codigo_barras}: {e}")
        return None

def ejecutar_scraping_feliubadalo():
    print("🚀 Ejecutando scraping en Feliu Badaló...")

    archivos_csv = [f for f in os.listdir(UPLOAD_FOLDER) if f.endswith(".csv")]
    if not archivos_csv:
        print("❌ No hay archivos CSV en uploads/")
        return

    archivos_csv.sort(key=lambda f: os.path.getmtime(os.path.join(UPLOAD_FOLDER, f)), reverse=True)
    csv_path = os.path.join(UPLOAD_FOLDER, archivos_csv[0])
    print(f"📄 Usando archivo: {csv_path}")

    try:
        df = pd.read_csv(csv_path)
    except Exception as e:
        print(f"❌ Error leyendo CSV: {e}")
        return

    resultados = []
    user_agent = random.choice(USER_AGENTS)
    driver = crear_driver(user_agent)

    try:
        for index, row in df.iterrows():
            row_id = index + 2
            codigo = str(row.get("Código de Barras", "")).strip()
            nombre = str(row.get("Nombre del Producto", "")).strip()

            if not codigo or not nombre:
                continue

            # Reiniciar driver cada 50 productos
            if index > 0 and index % 50 == 0:
                driver.quit()
                user_agent = random.choice(USER_AGENTS)
                print(f"♻️ Reiniciando navegador con nuevo user-agent: {user_agent}")
                time.sleep(2)
                driver = crear_driver(user_agent)

            resultado = buscar_producto(driver, row_id, codigo, nombre)
            if resultado:
                resultados.append(resultado)
                print(json.dumps(resultado), flush=True)

            time.sleep(4)

    finally:
        driver.quit()

    # Guardar resultados
    resultados_path = os.path.join(UPLOAD_FOLDER, "resultados_feliubadalo.json")
    with open(resultados_path, "w", encoding="utf-8") as f:
        json.dump(resultados, f, indent=2, ensure_ascii=False)

    print(f"✅ Búsqueda completada. Resultados guardados en '{resultados_path}'")

if __name__ == "__main__":
    ejecutar_scraping_feliubadalo()
