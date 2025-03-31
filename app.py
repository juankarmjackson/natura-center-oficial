from flask import Flask, request, jsonify, send_file
import os
import subprocess
import json

app = Flask(__name__)
UPLOAD_FOLDER = 'uploads'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/upload', methods=['POST'])
def upload_file():
    file = request.files['file']
    if not file:
        return jsonify({"error": "No se proporcionó archivo"}), 400

    filename = file.filename
    filepath = os.path.join(UPLOAD_FOLDER, filename)
    file.save(filepath)

    # Ejecutar script1.py con el archivo
    subprocess.call(['python', 'script1.py', filepath])

    # Cargar el JSON de resultados y devolverlo al frontend
    resultados_path = os.path.join(UPLOAD_FOLDER, "resultados_dieteticavallecana.json")
    if os.path.exists(resultados_path):
        with open(resultados_path, encoding='utf-8') as f:
            resultados = json.load(f)
        return jsonify(resultados)
    else:
        return jsonify({"error": "No se generó el archivo de resultados"}), 500


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)

