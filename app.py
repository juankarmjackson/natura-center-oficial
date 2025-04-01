from flask import Flask, request, jsonify, render_template
import os
import subprocess
import json

app = Flask(__name__, static_folder="static", template_folder="templates")

UPLOAD_FOLDER = "uploads"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/upload', methods=['POST'])
def upload_file():
    file = request.files['file']
    if not file:
        return jsonify({"error": "No se proporcionó archivo"}), 400

    # Guardar archivo
    filename = file.filename
    filepath = os.path.join(UPLOAD_FOLDER, filename)
    file.save(filepath)

    # Ejecutar script1.py
    subprocess.call(['python', 'scripts/script1.py', filepath])

    # Ejecutar script2.py
    subprocess.call(['python', 'scripts/script2.py', filepath])

    # Leer resultados del script1
    resultados1_path = os.path.join(UPLOAD_FOLDER, "resultados_dieteticavallecana.json")
    resultados1 = []
    if os.path.exists(resultados1_path):
        with open(resultados1_path, encoding='utf-8') as f:
            resultados1 = json.load(f)

    # Leer resultados del script2
    resultados2_path = os.path.join(UPLOAD_FOLDER, "resultados_feliubadalo.csv")
    resultados2 = []
    if os.path.exists(resultados2_path):
        df = pd.read_csv(resultados2_path)
        resultados2 = df.to_dict(orient="records")

    return jsonify({
        "script1": resultados1,
        "script2": resultados2
    })

if __name__ == '__main__':
    app.run(debug=True, port=5000)
