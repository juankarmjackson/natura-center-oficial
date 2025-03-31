from flask import Flask, request, render_template, Response
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
    file = request.files['file']
    if not file:
        return "No se proporcionó archivo", 400

    filename = file.filename
    filepath = os.path.join(UPLOAD_FOLDER, filename)
    file.save(filepath)

    def generate():
        process = subprocess.Popen(
            ['python', 'scripts/script1.py', filepath],
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            universal_newlines=True,
            bufsize=1
        )
        for line in iter(process.stdout.readline, ''):
            if line.strip():
                yield f"data: {line.strip()}\n\n"
        process.stdout.close()
        process.wait()

    return Response(generate(), mimetype='text/event-stream')


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
