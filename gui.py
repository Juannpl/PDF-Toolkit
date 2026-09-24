"""Optional desktop interface; Docker uses the web interface."""

from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
from tkinter import filedialog, messagebox

import customtkinter as ctk

from compressor import QUALITIES, compress_pdf


def run():
    ctk.set_appearance_mode("dark")
    root = ctk.CTk()
    root.title("PDF Toolkit")
    root.geometry("520x460")
    executor = ThreadPoolExecutor(max_workers=1)
    selected = None
    quality = ctk.StringVar(value="ebook")

    def select_file():
        nonlocal selected
        path = filedialog.askopenfilename(filetypes=[("Fichiers PDF", "*.pdf")])
        if path:
            selected = path
            label.configure(text=Path(path).name)
            button.configure(state="normal")

    def compress():
        output = filedialog.asksaveasfilename(defaultextension=".pdf", filetypes=[("PDF", "*.pdf")])
        if not output:
            return
        button.configure(state="disabled", text="Compression en cours…")
        select.configure(state="disabled")
        future = executor.submit(compress_pdf, selected, output, quality.get())

        def poll():
            if not future.done():
                root.after(100, poll)
                return
            button.configure(state="normal", text="Compresser le PDF")
            select.configure(state="normal")
            try:
                future.result()
                messagebox.showinfo("Terminé", f"PDF enregistré :\n{output}")
            except Exception as exc:
                messagebox.showerror("Erreur", str(exc))

        root.after(100, poll)

    ctk.CTkLabel(root, text="PDF Toolkit", font=("Helvetica", 30, "bold")).pack(pady=24)
    label = ctk.CTkLabel(root, text="Aucun fichier sélectionné")
    label.pack()
    select = ctk.CTkButton(root, text="Sélectionner un PDF", command=select_file)
    select.pack(pady=16)
    for value, text in QUALITIES.items():
        ctk.CTkRadioButton(root, text=text, variable=quality, value=value).pack(anchor="w", padx=70, pady=8)
    button = ctk.CTkButton(root, text="Compresser le PDF", command=compress, state="disabled")
    button.pack(pady=24)
    try:
        root.mainloop()
    finally:
        executor.shutdown(wait=False, cancel_futures=True)
