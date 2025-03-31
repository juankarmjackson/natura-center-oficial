from flask import Flask, request, render_template
import os
import subprocess

app = Flask(__name__, static_folder="static", template_folder="templates")

UPLOAD_FOLDER = 'uploads'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/upload', methods=['POST'])
def upload_file():
    try:
        file = request.files['file']
        if not file:
            return "No se proporcionó archivo", 400

        filename = file.filename
        filepath = os.path.join(UPLOAD_FOLDER, filename)
        file.save(filepath)

        print(f"📁 Archivo guardado en: {filepath}")

        # Ejecutar script1.py
        subprocess.call(['python', 'script1.py', filepath])

        return 'OK', 200

    except Exception as e:
        print(f"❌ Error al subir archivo: {e}")
        return str(e), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
