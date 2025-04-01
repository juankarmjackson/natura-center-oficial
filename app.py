from flask import Flask, request, render_template, Response
import os
import subprocess
import threading
import queue

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
        output_queue = queue.Queue()

        def run_script(script_name):
            try:
                process = subprocess.Popen(
                    ['python', script_name, filepath],
                    stdout=subprocess.PIPE,
                    stderr=subprocess.STDOUT,
                    universal_newlines=True,
                    bufsize=1
                )
                for line in iter(process.stdout.readline, ''):
                    if line.strip():
                        output_queue.put(f"data: {line.strip()}\n\n")
                process.stdout.close()
                process.wait()
            except Exception as e:
                output_queue.put(f"data: Error ejecutando {script_name}: {str(e)}\n\n")

        # Ejecutar ambos scripts en paralelo
        threads = []
        for script in ['scripts/script1.py', 'scripts/script2.py']:
            t = threading.Thread(target=run_script, args=(script,))
            t.start()
            threads.append(t)

        # Escuchar los mensajes que los hilos vayan generando
        while any(t.is_alive() for t in threads) or not output_queue.empty():
            try:
                yield output_queue.get(timeout=0.5)
            except queue.Empty:
                continue

    return Response(generate(), mimetype='text/event-stream')


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
