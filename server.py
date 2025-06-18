from flask import Flask, request, jsonify, send_from_directory
import os
import time
from multiprocessing import Pool, cpu_count
from PIL import Image
from werkzeug.utils import secure_filename

# Inicijalizacija Flask aplikacije
app = Flask(__name__)

# Definisanje foldera za uploadovane i konvertovane slike
UPLOAD_FOLDER = "uploads"
CONVERTED_FOLDER = "converted"

# Kreira folder ako ne postoji
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(CONVERTED_FOLDER, exist_ok=True)

# Funkcija za čuvanje uploadovanih fajlova u lokalni folder
def save_uploaded_files(files):
    saved_paths = []
    for f in files:
        # Osigurava da ime fajla ne sadrži maliciozne karaktere
        filename = secure_filename(f.filename)
        path = os.path.join(UPLOAD_FOLDER, filename)
        f.save(path)
        saved_paths.append(path)  # Pamti putanju do fajla
    return saved_paths

# Funkcija za konverziju slike u WebP format
def convert_to_webp(path):
    img = Image.open(path)
    # Konvertuje format slike ako je potrebno
    if img.mode in ("RGBA", "P"):
        img = img.convert("RGBA")
    else:
        img = img.convert("RGB")
    # Pravi izlazno ime fajla
    out_name = os.path.basename(path).rsplit(".", 1)[0] + ".webp"
    out_path = os.path.join(CONVERTED_FOLDER, out_name)
    img.save(out_path, "webp")  # Snima sliku u WebP formatu
    return out_path

# Ruta za upload slika i njihovu konverziju u WebP format
@app.route("/upload", methods=["POST"])
def upload_and_convert():
    # Dobijanje liste fajlova iz forme (key: "images")
    uploaded_files = request.files.getlist("images")

    # Snimanje fajlova i čuvanje njihovih putanja
    file_paths = save_uploaded_files(uploaded_files)

    # Mjerenje vremena za serijsku obradu
    start_serial = time.perf_counter()
    for path in file_paths:
        convert_to_webp(path)
    end_serial = time.perf_counter()

    # Mjerenje vremena za paralelnu obradu koristeći multiprocessing
    start_parallel = time.perf_counter()
    with Pool(cpu_count()) as pool: #cpu_count() vrati broj dostupnih CPU jezgara
    pool.map(convert_to_webp, file_paths) #Pool(...) kreira više procesa (jedan po jezgru)
    end_parallel = time.perf_counter() #dodeljuje svakom procesu po jedan fajl da obradi (radi istu funkciju convert_to_webp)

    # Vraća JSON odgovor sa vremenima obrade
    return jsonify({
        "serial_time": end_serial - start_serial,
        "parallel_time": end_parallel - start_parallel
    })

# Renders index.html kada se pristupi glavnoj stranici
@app.route("/")
def index():
    return send_from_directory(".", "index.html")

# Servira statičke fajlove (npr. .js, .css, slike) sa lokalnog direktorijuma
@app.route("/<path:path>")
def static_files(path):
    return send_from_directory(".", path)

# Pokretanje Flask aplikacije
if __name__ == "__main__":
    app.run(debug=True)
