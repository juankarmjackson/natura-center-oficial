from flask import Flask, request, jsonify, render_template, Response
import os
import subprocess
import threading

app = Flask(__name__, static_folder="static", template_folder="templates")

UPLOAD_FOLDER = "uploads"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

latest_csv_path = None

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/upload', methods=['POST'])
def upload_file():
    global latest_csv_path
    file = request.files['file']
    if not file:
        return jsonify({"error": "No se proporcionó archivo"}), 400

    filename = file.filename
    filepath = os.path.join(UPLOAD_FOLDER, filename)
    file.save(filepath)
    latest_csv_path = filepath

    return jsonify({"success": True})

@app.route('/stream-script1')
def stream_script1():
    def generate():
        process = subprocess.Popen(
            ["python", "scripts/script1.py", latest_csv_path],
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            bufsize=1
        )
        for line in process.stdout:
            if line.strip().startswith("{"):  # JSON del producto
                yield f"data: {line.strip()}\n\n"
        process.stdout.close()
        process.wait()

    return Response(generate(), mimetype='text/event-stream')

@app.route('/stream-script2')
def stream_script2():
    def generate():
        try:
            process = subprocess.Popen(
                ["python", "scripts/script2.py"],
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True,
                bufsize=1
            )
            for line in process.stdout:
                if line.strip().startswith("{"):
                    yield f"data: {line.strip()}\n\n"
            process.stdout.close()
            process.wait()
        except Exception as e:
            yield f"data: {{\"error\": \"{str(e)}\"}}\n\n"

    return Response(generate(), mimetype='text/event-stream')

if __name__ == '__main__':
    app.run(debug=True, port=5000)
