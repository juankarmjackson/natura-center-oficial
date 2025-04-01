import os
import time
import json
import random
import pandas as pd
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import WebDriverException

UPLOAD_FOLDER = "uploads"

USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/134.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/134.0.0.0 Safari/537.36",
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/133.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:126.0) Gecko/20100101 Firefox/126.0"
]

def crear_driver(user_agent=None):
    options = Options()
    options.add_argument("--headless")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    if user_agent:
        options.add_argument(f"user-agent={user_agent}")
    return webdriver.Chrome(options=options)

def login_actibios(driver):
    print("\n🔐 Iniciando sesión en Actibios...")
    driver.get("https://actibios.com/v1/")
    time.sleep(2)

    try:
        driver.find_element(By.ID, "txtUser").send_keys("E2238")
        driver.find_element(By.ID, "txtPwd").send_keys("HERBO6")

        botones = driver.find_elements(By.TAG_NAME, "button")
        for boton in botones:
            if boton.text.strip().lower() == "aceptar":
                boton.click()
                break

        time.sleep(5)

        if "WebForms" in driver.current_url:
            print("✅ Login exitoso en Actibios")
            return True
        else:
            print("❌ Login fallido en Actibios")
            return False
    except Exception as e:
        print(f"❌ Error durante login: {e}")
        return False

def buscar_producto_actibios(driver, row_id, codigo_barras, nombre_producto):
    url_busqueda = "https://actibios.com/v1/WebForms/Clientes/GenerarPedidosVentas_new.aspx"
    print(f"🔍 Buscando en Actibios fila {row_id}: {nombre_producto} ({codigo_barras})")

    try:
        driver.get(url_busqueda)
        time.sleep(4)

        campo_select = driver.find_element(By.ID, "cbField")
        for option in campo_select.find_elements(By.TAG_NAME, "option"):
            if option.get_attribute("value") == "codBarras":
                option.click()
                break
        time.sleep(1)

        buscador_input = driver.find_element(By.ID, "txtNomArticulo")
        buscador_input.clear()
        buscador_input.send_keys(str(codigo_barras))
        time.sleep(1)

        driver.find_element(By.ID, "btnBuscar").click()
        time.sleep(4)

        tabla_resultados = driver.find_element(By.ID, "tbBuscar")
        if "No se ha encontrado ningun articulo" in tabla_resultados.text:
            disponibilidad = "No disponible"
        else:
            disponibilidad = "Disponible"

        print(f"✅ Producto {disponibilidad}: {nombre_producto}")
        return {
            "row_id": row_id,
            "codigo_barras": codigo_barras,
            "nombre_producto": nombre_producto,
            "enlace": url_busqueda,
            "disponibilidad": disponibilidad,
            "web": "actibios"
        }
    except Exception as e:
        print(f"❌ Error con Selenium en {codigo_barras}: {e}")
        return None

def ejecutar_scraping_actibios():
    print("🚀 Ejecutando scraping en Actibios...")

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

    columnas = {c.lower(): c for c in df.columns}
    col_codigo = next((v for k, v in columnas.items() if "código" in k and "barra" in k), None)
    col_nombre = next((v for k, v in columnas.items() if "nombre" in k), None)

    if not col_codigo or not col_nombre:
        print("❌ No se encontraron columnas 'código de barras' y 'nombre'")
        return

    print(f"📦 Total filas en CSV: {len(df)}")

    resultados = []
    user_agent = random.choice(USER_AGENTS)
    driver = crear_driver(user_agent)

    try:
        if not login_actibios(driver):
            return

        for index, row in df.iterrows():
            row_id = index + 2
            codigo = str(row.get(col_codigo, "")).strip()
            nombre = str(row.get(col_nombre, "")).strip()

            if not codigo or not nombre:
                print(f"⏩ Fila {row_id} omitida: código o nombre faltante")
                continue

            if index > 0 and index % 50 == 0:
                driver.quit()
                user_agent = random.choice(USER_AGENTS)
                print(f"♻️ Reiniciando navegador con nuevo user-agent: {user_agent}")
                time.sleep(2)
                driver = crear_driver(user_agent)
                if not login_actibios(driver):
                    return

            resultado = buscar_producto_actibios(driver, row_id, codigo, nombre)
            if resultado:
                resultados.append(resultado)
                print(json.dumps(resultado), flush=True)

            time.sleep(4)

    finally:
        driver.quit()

    resultados_path = os.path.join(UPLOAD_FOLDER, "resultados_actibios.json")
    with open(resultados_path, "w", encoding="utf-8") as f:
        json.dump(resultados, f, indent=2, ensure_ascii=False)

    print(f"✅ Búsqueda completada. Resultados guardados en '{resultados_path}'")

if __name__ == "__main__":
    ejecutar_scraping_actibios()
