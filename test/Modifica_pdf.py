from PyPDF2 import PdfReader, PdfWriter

# Percorso del PDF
titolo = "10. Propagazione ottica"

file_path = fr"C:\Users\Leon\OneDrive - Università Politecnica delle Marche\UNIVPM\ELETTROMAGNETISMO\SLIDE\{titolo}.pdf"


# Legge il PDF esistente
reader = PdfReader(file_path)
writer = PdfWriter()

# Copia tutte le pagine
writer.append_pages_from_reader(reader)

# Legge i metadati attuali (facoltativo)
old_metadata = reader.metadata
print("Metadati attuali:", old_metadata)

# 🔸 Sovrascrive il titolo (o lo aggiunge se manca)
writer.add_metadata({
    "/Title": f"{titolo}"
})

# Scrive di nuovo nel file originale (o in uno nuovo se preferisci)
with open(file_path, "wb") as f:
    writer.write(f)

print("Titolo aggiornato con successo!")
