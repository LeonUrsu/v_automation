import pathlib
import time
from idlelib.pyshell import use_subprocess

from selenium import webdriver
from pathlib import Path

from selenium.webdriver.chrome.service import Service
import undetected_chromedriver as uc
from selenium.webdriver.common.by import By
import model
from model import small_humanizer
import config
from selenium import webdriver
from selenium.webdriver.chrome.options import Options

# Define the path to your HTML file
pagina_articolo = str(pathlib.Path.cwd().joinpath("test").joinpath("pagina articolo.html"))
pagina_articolo_content = str(pathlib.Path.cwd().joinpath("test").joinpath("pagina articolo content.html"))
sidebar_articolo = str(pathlib.Path.cwd().joinpath("test").joinpath("sidebar pantaloni.html"))
articoli_utente = str(pathlib.Path.cwd().joinpath("test").joinpath("articoli utente.html"))
articoli_utente_tabs = str(pathlib.Path.cwd().joinpath("test").joinpath("articoli utente tabs.html"))
vendi_articolo = str(pathlib.Path.cwd().joinpath("test").joinpath("vendi un articolo.html"))
oggetto_categoria = str(pathlib.Path.cwd().joinpath("test").joinpath("oggetto category.html"))
pagina_venditore_casuale = str(pathlib.Path.cwd().joinpath("test").joinpath(
    "dfdanilo23 - tabs - member profile _ Vinted.html"))


# Metodo per testare se foto vengono caricate su vendi articolo
def qewrje():
    options = webdriver.ChromeOptions()
    options.add_argument(r'--user-data-dir=C:\Users\Leon\AppData\Local\Google\Chrome\User Data\Default')
    driver = uc.Chrome(options=options)
    driver.get(vendi_articolo)
    path_foto = r"/test/CARICATI/12213\foto\a"
    model.carica_foto_pagina_vendita(driver, path_foto)
    elemento = driver.find_element(By.CLASS_NAME, "photo-box")
    driver.close()
    assert elemento.is_displayed() == True


# Metodo che testa se una pagina con 205 articoli viene scrollata fino in fondo
def test_scrolla_fondo_pagina_versione_2():
    driver = uc.Chrome()
    driver.get(pagina_venditore_casuale)
    driver.maximize_window()
    model.humanizer(6)
    esito = model.scrolla_fondo_pagina_versione_2(driver)
    driver.close()
    assert esito == True


def test_print_path():
    print(pagina_venditore_casuale)


# Metodo che controlla se l'articolo è scaduto, l'articolo salvato è vecchio di 5 mesi
def test_esito_di_cancellazione():
    driver = uc.Chrome()
    driver.get(pagina_articolo)
    driver.maximize_window()
    small_humanizer()
    esito = model.controllo_eliminazione_articolo(driver)
    driver.close()
    assert esito == True


# Metodo che recupera codice alfanumerico, l'articolo salvato è vecchio di 5 mesi
def test_recupera_codice_alfanumerico():
    driver = uc.Chrome()
    driver.get(pagina_articolo)
    driver.maximize_window()
    small_humanizer()
    esito = model.recupera_codice_alfanumerico(driver)
    driver.close()
    assert esito == "b1921242"  # è l'articolo che è stato salvato nel html


#
def test_iterazione_articoli_profilo_online():
    driver = uc.Chrome()
    driver.get(articoli_utente_tabs)
    driver.maximize_window()
    small_humanizer()
    esito = model.iterazione_articoli_profilo_online(driver)
    driver.close()


def test_cambia_album():
    codice_a = "a98124"
    return_codice_b = model.cambia_album(codice_a)
    assert return_codice_b == "b98124"

    codice_b = "b1233212"
    return_codice_a = model.cambia_album(codice_b)
    assert return_codice_a == "a1233212"


# Metodo per testare lo spostamento dell'articolo dal path da CARICATI a CARICARE
def test_scadenza_articolo_database():
    codice_articolo = "b12213"
    model.scadenza_articolo_database(config, codice_articolo)
    assert True == Path(config.path_da_caricare.joinpath(codice_articolo[1:])).is_dir()


# Metodo per testare lo spostamento dell'articolo dal path da CARICARE a CARICATI
def test_rinnovo_articolo_database():
    codice_articolo = "b12213"
    model.rinnovo_articolo_database(config, codice_articolo)
    assert True == Path(config.path_caricati.joinpath(codice_articolo[1:])).is_dir()


def test_cambia_album_nel_database():
    articolo = config.articolo552132
    album_nuovo = ""
    path_articoli_database = config.path_da_caricare

    if path_articoli_database.joinpath(config.articolo552132[1:]).joinpath("foto").joinpath(f"is_a").is_dir():
        articolo = config.articolo552132.replace("b", "a")
        album_nuovo = "b"
    elif path_articoli_database.joinpath(config.articolo552132[1:]).joinpath("foto").joinpath(f"is_b").is_dir():
        album_nuovo = "a"
    model.cambia_album_nel_database(path_articoli_database, articolo)
    esito = pathlib.Path(
        path_articoli_database.joinpath(articolo[1:]).joinpath("foto").joinpath(f"is_{album_nuovo}")).is_dir()
    assert esito == True


# Meteodo per verificare se back funziona e fa andare indietro alla pagina web precedente
def test_driver_back():
    driver = uc.Chrome()
    current = driver.current_url
    driver.get(articoli_utente_tabs)
    time.sleep(2)
    driver.back()
    assert current == "chrome://new-tab-page/"
    driver.close()


# Metodo per verificare se refresh funziona
def test_driver_refresh():
    driver = uc.Chrome()
    driver.get(config.sito_google)
    current_before = driver.current_url
    time.sleep(1)
    driver.refresh()
    time.sleep(1)
    current_now = driver.current_url
    assert current_before == current_now


def test_creazione_dizionario_dati_articolo():
    path_articolo = config.path_da_caricare.joinpath(config.articolo552132[1:])
    dati_articolo = model.creazione_dizionario_dati_articolo(path_articolo, config.articolo552132[1:])
    assert dati_articolo["titolo"] == "titolo_articolo"
    assert dati_articolo["taglia"] == "taglia_articolo"
    assert dati_articolo["prezzo"] == "0"
    assert dati_articolo["pacco"] == "2"
    assert dati_articolo["descrizione"] == "test di descrizione"


def test_carica_foto_pagina_vendita():
    driver = uc.Chrome()
    driver.get(vendi_articolo)
    elemento_photos = driver.find_element(By.ID, "photos")
    path_photo = config.path_da_caricare.joinpath(config.articolo552132[1:]).joinpath("foto").joinpath("a")
    model.carica_foto_pagina_vendita(elemento_photos, path_photo)
    # input_file = elemento_photos.find_element(By.CSS_SELECTOR, 'input[data-testid="add-photos-input"]')
    time.sleep(1)
    driver.close()


def test_merge_two_dicts():
    x = {'a': 1, 'b': 2}
    y = {'b': 3, 'c': 4}
    z = model.merge_two_dicts(x, y)
    print("-x- " + str(z))


# codice da runnare in cmd
# "C:\Program Files\Google\Chrome\Application\chrome.exe" --remote-debugging-port=9222 --user-data-dir="C:\ChromeDebug"
def test_hook_to_chrome():
    options = Options()
    options.debugger_address = "127.0.0.1:9222"  # stessa porta scelta sopra
    service = Service(executable_path="chromedriver.exe")
    driver = webdriver.Chrome(options=options, service=service)
    codice_articolo = "12345"
    path_articolo = pathlib.Path(
        r"C:\Users\Leon\OneDrive - Università Politecnica delle Marche\_Vinted\DA CARICARE").joinpath(codice_articolo)
    dati_articolo = model.creazione_dizionario_dati_articolo(path_articolo, codice_articolo)
    esito = model.inserimento_dati_articolo_pagina_vendita(driver, dati_articolo)
    time.sleep(10)
    assert True == esito


























