import customtkinter as ctk
from tkinter import filedialog, messagebox
import os
from compressor import compress_pdf

# Création de la fenêtre principale
ctk.set_appearance_mode("dark")  # Mode sombre
ctk.set_default_color_theme("blue")  # Thème de couleur

root = ctk.CTk()
root.title("Compresseur de PDF")
root.geometry("500x400")
root.resizable(False, False)

selected_file = None  # Variable pour stocker le fichier sélectionné

my_font = ctk.CTkFont(family="Helvetica", size=12)
my_subtitle = ctk.CTkFont(family="Helvetica", size=14)
my_title = ctk.CTkFont(family="Helvetica", size=30, weight="bold")

# 📌 Fonction pour sélectionner un fichier PDF
def select_file():
    global selected_file
    file_path = filedialog.askopenfilename(filetypes=[("Fichiers PDF", "*.pdf")])
    if file_path:
        file_label.configure(text=os.path.basename(file_path), text_color="white")
        compress_button.configure(state="normal")  # Activation du bouton
        selected_file = file_path

# 📌 Fonction pour compresser le PDF
def compress():
    if not selected_file:
        messagebox.showwarning("Attention", "Veuillez sélectionner un fichier PDF.")
        return

    output_file = filedialog.asksaveasfilename(defaultextension=".pdf",
                                               filetypes=[("Fichiers PDF", "*.pdf")],
                                               title="Enregistrer sous")

    if not output_file:
        return

    quality = quality_var.get()
    compress_pdf(selected_file, output_file, quality)

# 📌 Interface utilisateur stylisée
title_label = ctk.CTkLabel(root, text="Compresseur de PDF", font=my_title)
title_label.pack(pady=(30, 10))

file_label = ctk.CTkLabel(root, text="Aucun fichier sélectionné", text_color="gray", font=my_font)
file_label.pack()

select_button = ctk.CTkButton(root, text="📂 Sélectionner un PDF", command=select_file, corner_radius=10)
select_button.pack(pady=10)

# 📌 Sélection du niveau de compression
quality_var = ctk.StringVar(value="ebook")
quality_frame = ctk.CTkFrame(root, corner_radius=10)
quality_frame.pack(pady=10, padx=20, fill="x")

ctk.CTkLabel(quality_frame, text="Niveau de compression :", font=my_subtitle).pack(pady=5)

quality_options = [
    ("Forte (screen)", "screen"),
    ("Moyenne (ebook)", "ebook"),
    ("Faible (printer)", "printer"),
    ("Haute qualité (prepress)", "prepress")
]

for text, mode in quality_options:
    ctk.CTkRadioButton(quality_frame, text=text, variable=quality_var, value=mode).pack(anchor="w", padx=20, pady=5)

# 📌 Bouton de compression désactivé par défaut
compress_button = ctk.CTkButton(root, text="⚡ Compresser PDF", command=compress, corner_radius=10, state="disabled")
compress_button.pack(pady=15)

# Lancer la boucle principale
root.mainloop()
