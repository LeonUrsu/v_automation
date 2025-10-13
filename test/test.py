import pathlib
import time

from selenium import webdriver
from pathlib import Path

from selenium.webdriver.common.by import By

import model
import view

# Define the path to your HTML file
html_file = Path.cwd() / "pagina articolo.html"
#html_file = Path.cwd() / "sidebar pantaloni.html"
#html_file = Path.cwd() / "articoli utente.html"

# Open the file in the browser using file:// protocol

#Qui inserire il test--------------------------------
#print(body.conteggio_articoli_profilo(driver))
i =0
while i<50:
    time.sleep(2)
    driver = webdriver.Chrome()
    driver.get(html_file.as_uri())
    model.apertura_pagina_vendita(driver)
    time.sleep(2)
    i+=1
    driver.quit()



