import pathlib

from selenium import webdriver
from pathlib import Path

from selenium.webdriver.common.by import By

import model
import view

# Define the path to your HTML file
#html_file = Path.cwd() / "pagina articolo.html"
#html_file = Path.cwd() / "sidebar pantaloni.html"
#html_file = Path.cwd() / "articoli utente.html"

# Open the file in the browser using file:// protocol
#driver = webdriver.Chrome()
#driver.get(html_file.as_uri())

#Qui inserire il test--------------------------------
#print(body.conteggio_articoli_profilo(driver))

path_articolo = pathlib.Path().cwd().joinpath("DA CARICARE").joinpath("12213")


brand = path_articolo.joinpath("titolo").name
colore = path_articolo.joinpath("colore").name
condizioni = path_articolo.joinpath("condizioni").name
descrizione = path_articolo.joinpath("descrizione").name
cartelle_foto = sorted((path_articolo / "foto").iterdir())  # elenco delle sottocartelle ordinate
album_selezionato = cartelle_foto[2].name.replace("is_", "")
album_foto = path_articolo.joinpath("foto").joinpath(album_selezionato)
pacco = next(path_articolo.joinpath("pacco")).name
prezzo = path_articolo.joinpath("prezzo").name
taglia = path_articolo.joinpath("taglia").name
titolo = path_articolo.joinpath("titolo").name
print(brand)
print(colore)
print(condizioni)
print(descrizione)
print(album_foto)
print(pacco)
print(prezzo)
print(taglia)
print(titolo)



