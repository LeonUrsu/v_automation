from selenium import webdriver
from pathlib import Path
import undetected_chromedriver as uc
from selenium.webdriver.common.by import By

import model

# Define the path to your HTML file
html_file1 = Path.cwd() / "pagina articolo.html"
html_file2 = Path.cwd() / "sidebar pantaloni.html"
html_file3 = Path.cwd() / "articoli utente.html"
html_file4 = Path.cwd() / "vendi un articolo.html"


def test_carica_foto_pagina_vendita():
    options = webdriver.ChromeOptions()
    options.add_argument(r'--user-data-dir=C:\Users\Leon\AppData\Local\Google\Chrome\User Data\Default')
    driver = uc.Chrome(options=options)
    driver.get(html_file4)

    path_foto = r"C:\Users\Leon\v_bot_selenium\test\DA CARICARE\12213\foto\a"
    model.carica_foto_pagina_vendita(driver, path_foto)
    elemento = driver.find_element(By.CLASS_NAME, "photo-box")
    assert elemento.is_displayed() == True

