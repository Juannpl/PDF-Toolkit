import subprocess
from tkinter import messagebox

def compress_pdf(input_path, output_path, quality="ebook"):
    command = [
        "gs",  
        "-sDEVICE=pdfwrite",
        "-dCompatibilityLevel=1.4",
        f"-dPDFSETTINGS=/{quality}",
        "-dNOPAUSE",
        "-dQUIET",
        "-dBATCH",
        f"-sOutputFile={output_path}",
        input_path
    ]
    
    try:
        subprocess.run(command, check=True)
        messagebox.showinfo("Succès", f"PDF compressé avec succès :\n{output_path}")
    except subprocess.CalledProcessError:
        messagebox.showerror("Erreur", "La compression a échoué.")
