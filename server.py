from flask import Flask, request, jsonify, send_from_directory
import os
import time
from multiprocessing import Pool, cpu_count
from PIL import Image
from werkzeug.utils import secure_filename

app = Flask(__name__)
UPLOAD_FOLDER = "uploads"
CONVERTED_FOLDER = "converted"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(CONVERTED_FOLDER, exist_ok=True)

def save_uploaded_files(files):
    saved_paths = []
    for f in files:
        filename = secure_filename(f.filename)
        path = os.path.join(UPLOAD_FOLDER, filename)
        f.save(path)
        saved_paths.append(path)
    return saved_paths

def convert_to_webp(path):
    img = Image.open(path)
    if img.mode in ("RGBA", "P"):
        img = img.convert("RGBA")
    else:
        img = img.convert("RGB")
    out_name = os.path.basename(path).rsplit(".", 1)[0] + ".webp"
    out_path = os.path.join(CONVERTED_FOLDER, out_name)
    img.save(out_path, "webp")
    return out_path

@app.route("/upload", methods=["POST"])
def upload_and_convert():
    uploaded_files = request.files.getlist("images")
    file_paths = save_uploaded_files(uploaded_files)

    start_serial = time.perf_counter()
    for path in file_paths:
        convert_to_webp(path)
    end_serial = time.perf_counter()

    start_parallel = time.perf_counter()
    with Pool(cpu_count()) as pool:
        pool.map(convert_to_webp, file_paths)
    end_parallel = time.perf_counter()

    return jsonify({
        "serial_time": end_serial - start_serial,
        "parallel_time": end_parallel - start_parallel
    })

@app.route("/")
def index():
    return send_from_directory(".", "index.html")

@app.route("/<path:path>")
def static_files(path):
    return send_from_directory(".", path)

if __name__ == "__main__":
    app.run(debug=True)