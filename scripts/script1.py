import sys
import pandas as pd
import time
import json
import os
import requests
import random
from bs4 import BeautifulSoup

UPLOAD_FOLDER = "uploads"

# Lista de User-Agents aleatorios
USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/134.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/134.0.0.0 Safari/537.36",
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/133.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:126.0) Gecko/20100101 Firefox/126.0",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 12.5; rv:124.0) Gecko/20100101 Firefox/124.0"
]

def buscar_producto_dieteticavallecana(row_id, codigo_barras, nombre_producto, headers):
    url_busqueda = f"https://www.dieteticavallecana.com/busqueda?controller=search&s={codigo_barras}"

    print(f"🔍 Buscando en Dietética Vallecana: {nombre_producto} ({codigo_barras}) -> {url_busqueda}")
    response = requests.get(url_busqueda, headers=headers)

    if response.status_code != 200:
        print(f"⚠️ Error al acceder a {url_busqueda}")
        return None

    soup = BeautifulSoup(response.text, 'html.parser')
    producto_disponible = soup.select_one(".card-img-top.product__card-img")
    disponibilidad = "Disponible" if producto_disponible else "No disponible"
    print(f"✅ Producto {disponibilidad}: {nombre_producto}")

    return {
        "row_id": row_id,
        "codigo_barras": codigo_barras,
        "nombre_producto": nombre_producto,
        "enlace": url_busqueda,
        "disponibilidad": disponibilidad,
        "web": "dieteticavallecana"
    }

def ejecutar_scraping_dieteticavallecana(csv_path):
    resultados = []

    try:
        df = pd.read_csv(csv_path)
    except Exception as e:
        print(f"❌ Error leyendo el CSV: {e}")
        return

    headers = {"User-Agent": random.choice(USER_AGENTS)}

    for index, row in df.iterrows():
        row_id = index + 2
        codigo_barras = row.get("Código de Barras") or row.get("Código de barras")
        nombre_producto = row.get("Nombre del Producto") or row.get("Nombre")

        if not codigo_barras or not nombre_producto:
            continue

        # Cambiar user-agent cada 50 productos
        if (index + 1) % 50 == 0:
            headers = {"User-Agent": random.choice(USER_AGENTS)}
            print(f"♻️ Cambiando User-Agent: {headers['User-Agent']}")
            time.sleep(2)

        resultado = buscar_producto_dieteticavallecana(row_id, codigo_barras, nombre_producto, headers)

        if resultado:
            resultados.append(resultado)
            print(json.dumps(resultado), flush=True)

        time.sleep(4)  # Delay para prevenir bloqueos

    resultados_path = os.path.join(UPLOAD_FOLDER, "resultados_dieteticavallecana.json")
    with open(resultados_path, "w", encoding="utf-8") as f:
        json.dump(resultados, f, indent=2, ensure_ascii=False)

    print(f"✅ Búsqueda completada. Resultados guardados en '{resultados_path}'")


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("❌ Debes pasar el archivo CSV como argumento")
    else:
        ejecutar_scraping_dieteticavallecana(sys.argv[1])
