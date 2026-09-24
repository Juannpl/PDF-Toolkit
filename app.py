"""Local web interface. Run with Gunicorn in Docker."""

from io import BytesIO
from pathlib import Path
from tempfile import TemporaryDirectory

from flask import Flask, render_template, request, send_file
from werkzeug.utils import secure_filename

from compressor import CompressionError, QUALITIES, compress_pdf

app = Flask(__name__)
app.config["MAX_CONTENT_LENGTH"] = 50 * 1024 * 1024


@app.get("/")
def index():
    return render_template("index.html", qualities=QUALITIES)


@app.get("/health")
def health():
    return {"status": "ok"}


@app.post("/compress")
def compress():
    upload = request.files.get("file")
    if not upload or not upload.filename or not upload.filename.lower().endswith(".pdf"):
        return {"error": "Sélectionnez un fichier PDF."}, 400
    quality = request.form.get("quality", "ebook")
    try:
        with TemporaryDirectory(prefix="pdf-toolkit-") as directory:
            source = Path(directory) / "input.pdf"
            output = Path(directory) / "output.pdf"
            upload.save(source)
            compress_pdf(source, output, quality)
            # Read before cleanup: no uploaded documents persist after the request.
            result = BytesIO(output.read_bytes())
        filename = Path(secure_filename(upload.filename) or "document.pdf").stem
        response = send_file(result, mimetype="application/pdf", as_attachment=True,
                             download_name=f"{filename}-compresse.pdf", max_age=0)
        response.headers["Cache-Control"] = "no-store"
        return response
    except CompressionError as exc:
        return {"error": str(exc)}, 400
    except OSError:
        app.logger.exception("PDF processing failed")
        return {"error": "Erreur de traitement. Réessayez avec un autre fichier."}, 500


@app.errorhandler(413)
def too_large(error):
    return {"error": "Envoi trop volumineux : limite de 50 Mio par requête."}, 413
