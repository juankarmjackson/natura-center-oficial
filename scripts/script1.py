import sys
import pandas as pd
import time
import json
import os
import requests
from bs4 import BeautifulSoup


def buscar_producto_dieteticavallecana(row_id, codigo_barras, nombre_producto):
    url_busqueda = f"https://www.dieteticavallecana.com/busqueda?controller=search&s={codigo_barras}"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
    }

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

    for index, row in df.iterrows():
        row_id = index + 2
        codigo_barras = row.get("Código de Barras") or row.get("Código de barras")
        nombre_producto = row.get("Nombre del Producto") or row.get("Nombre")

        if not codigo_barras or not nombre_producto:
            continue

        resultado = buscar_producto_dieteticavallecana(row_id, codigo_barras, nombre_producto)

        if resultado:
            resultados.append(resultado)
            print(json.dumps(resultado), flush=True)  # 👈 envía JSON por stdout en tiempo real

        time.sleep(2)

    resultados_path = "uploads/resultados_dieteticavallecana.json"
    with open(resultados_path, "w", encoding="utf-8") as f:
        json.dump(resultados, f, indent=2, ensure_ascii=False)

    print(f"✅ Búsqueda completada. Resultados guardados en '{resultados_path}'")


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("❌ Debes pasar el archivo CSV como argumento")
    else:
        ejecutar_scraping_dieteticavallecana(sys.argv[1])
