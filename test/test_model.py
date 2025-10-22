import pathlib
import time

from selenium import webdriver
from pathlib import Path
import undetected_chromedriver as uc
from selenium.webdriver.common.by import By
import model
from model import small_humanizer

# Define the path to your HTML file
pagina_articolo = str(pathlib.Path.cwd().joinpath("test").joinpath("pagina articolo.html"))
pagina_articolo_content = str(pathlib.Path.cwd().joinpath("test").joinpath("pagina articolo content.html"))
sidebar_articolo = str(pathlib.Path.cwd().joinpath("test").joinpath("sidebar pantaloni.html"))
articoli_utente = str(pathlib.Path.cwd().joinpath("test").joinpath("articoli utente.html"))
vendi_articolo = str(pathlib.Path.cwd().joinpath("test").joinpath("vendi un articolo.html"))
pagina_venditore_casuale = str(pathlib.Path.cwd().joinpath("test").joinpath("framboise614 - member profile _ Vinted.html"))

 #Metodo per testare se foto vengono caricate su vendi articolo
def test_carica_foto_pagina_vendita():
    options = webdriver.ChromeOptions()
    options.add_argument(r'--user-data-dir=C:\Users\Leon\AppData\Local\Google\Chrome\User Data\Default')
    driver = uc.Chrome(options=options)
    driver.get(vendi_articolo)
    path_foto = r"C:\Users\Leon\v_bot_selenium\test\DA CARICARE\12213\foto\a"
    model.carica_foto_pagina_vendita(driver, path_foto)
    elemento = driver.find_element(By.CLASS_NAME, "photo-box")
    assert elemento.is_displayed() == True

#Metodo che testa se una pagina con 205 articoli viene scrollata fino in fondo
def test_scrolla_fondo_pagina_versione_2():
    driver = uc.Chrome()
    driver.get(pagina_venditore_casuale)
    driver.maximize_window()
    model.humanizer(6)
    esito = model.scrolla_fondo_pagina_versione_2(driver)
    assert esito == True

def test_print_path():
    print(pagina_venditore_casuale)



#Metodo che controlla se l'articolo è scaduto, l'articolo salvato è vecchio di 5 mesi
def test_esito_di_cancellazione():
    driver = uc.Chrome()
    driver.get(pagina_articolo)
    driver.maximize_window()
    small_humanizer()
    esito = model.controllo_eliminazione_articolo(driver)
    assert esito == True



#Metodo che recupera codice alfanumerico, l'articolo salvato è vecchio di 5 mesi
def test_recupera_codice_alfanumerico():
    driver = uc.Chrome()
    driver.get(pagina_articolo)
    driver.maximize_window()
    small_humanizer()
    esito = model.recupera_codice_alfanumerico(driver)
    assert esito != 0
