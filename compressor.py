"""PDF compression shared by the web and desktop interfaces."""

import os
from pathlib import Path
import shutil
import subprocess
import tempfile

QUALITIES = {
    "screen": "Forte · lecture à l’écran",
    "ebook": "Équilibrée · recommandée",
    "printer": "Légère · impression",
    "prepress": "Haute qualité · prépresse",
}


class CompressionError(Exception):
    """An actionable compression failure."""


def compress_pdf(input_path, output_path, quality="ebook"):
    """Write a PDF atomically; keep the original bytes if compression grows it."""
    source, destination = Path(input_path).resolve(), Path(output_path).resolve()
    if quality not in QUALITIES:
        raise CompressionError("Niveau de compression invalide.")
    if source == destination:
        raise CompressionError("Choisissez un fichier de sortie différent de l’original.")
    if not source.is_file():
        raise CompressionError("Le fichier source est introuvable.")
    with source.open("rb") as stream:
        if not stream.read(1024).lstrip().startswith(b"%PDF-"):
            raise CompressionError("Le fichier sélectionné n’est pas un PDF valide.")
    executable = shutil.which("gs")
    if not executable:
        raise CompressionError("Ghostscript est introuvable. Installez-le ou utilisez Docker.")
    # A temporary sibling ensures failed conversions never truncate the destination.
    with tempfile.TemporaryDirectory(dir=destination.parent) as directory:
        temporary = Path(directory) / "compressed.pdf"
        command = [
            executable, "-dSAFER", "-sDEVICE=pdfwrite", "-dCompatibilityLevel=1.4",
            f"-dPDFSETTINGS=/{quality}", "-dNOPAUSE", "-dQUIET", "-dBATCH",
            f"-sOutputFile={temporary}", "-f", str(source),
        ]
        try:
            subprocess.run(command, check=True, capture_output=True, timeout=120)
        except subprocess.TimeoutExpired as exc:
            raise CompressionError("Compression trop longue (limite : 120 secondes).") from exc
        except subprocess.CalledProcessError as exc:
            raise CompressionError("Compression impossible : PDF endommagé ou protégé.") from exc
        if not temporary.is_file() or temporary.stat().st_size == 0:
            raise CompressionError("Ghostscript n’a produit aucun PDF.")
        if temporary.stat().st_size >= source.stat().st_size:
            shutil.copyfile(source, temporary)
        os.replace(temporary, destination)
    return destination
