import pandas as pd
import time
import json
import os
import sys
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import NoSuchElementException
from webdriver_manager.chrome import ChromeDriverManager

UPLOAD_FOLDER = "uploads"


def buscar_producto(driver, row_id, codigo_barras, nombre_producto):
    url = f"https://online.feliubadalo.com/catalogsearch/result/?q={codigo_barras}#/dfclassic/query={codigo_barras}"
    print(f"🔍 Buscando: {nombre_producto} ({codigo_barras})")

    driver.get(url)
    time.sleep(4)

    try:
        driver.find_element(By.CLASS_NAME, "df-no-results")
        disponibilidad = "No disponible"
    except NoSuchElementException:
        try:
            driver.find_element(By.CLASS_NAME, "df-card")
            disponibilidad = "Disponible"
        except NoSuchElementException:
            disponibilidad = "No disponible"

    print(f"✅ {disponibilidad}")
    resultado = {
        "row_id": row_id,
        "codigo_barras": codigo_barras,
        "nombre_producto": nombre_producto,
        "enlace": url,
        "disponibilidad": disponibilidad,
        "web": "feliubadalo"
    }
    print(json.dumps(resultado), flush=True)
    return resultado


def ejecutar_scraping_feliubadalo(csv_path):
    print("🚀 Ejecutando búsqueda en Feliu Badaló...")

    try:
        df = pd.read_csv(csv_path)
    except Exception as e:
        print(f"❌ Error leyendo CSV: {e}")
        return

    resultados = []

    options = Options()
    options.add_argument("--headless=new")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")

    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)

    try:
        for index, row in df.iterrows():
            row_id = index + 2
            codigo = str(row.get("Código de Barras") or row.get("Código de barras") or "").strip()
            nombre = str(row.get("Nombre del Producto") or row.get("Nombre") or "").strip()

            if not codigo or not nombre:
                continue

            # Reiniciar el navegador cada 50 productos para liberar recursos
            if index != 0 and index % 50 == 0:
                driver.quit()
                time.sleep(3)
                driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)

            resultado = buscar_producto(driver, row_id, codigo, nombre)
            resultados.append(resultado)
            time.sleep(4)  # Delay más largo para evitar bloqueo

    finally:
        driver.quit()
        print("👋 Selenium finalizado")

    # Guardar resultados
    resultados_path = os.path.join(UPLOAD_FOLDER, "resultados_feliubadalo.json")
    with open(resultados_path, "w", encoding="utf-8") as f:
        json.dump(resultados, f, indent=2, ensure_ascii=False)

    print(f"📁 Resultados guardados en {resultados_path}")


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("❌ Debes pasar el archivo CSV como argumento")
    else:
        ejecutar_scraping_feliubadalo(sys.argv[1])
