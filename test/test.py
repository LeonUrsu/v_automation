from selenium import webdriver
from pathlib import Path

import body

# Define the path to your HTML file
html_file = Path.cwd() / "pagina articolo.html"

# Open the file in the browser using file:// protocol
driver = webdriver.Chrome()
driver.get(html_file.as_uri())

#Qui inserire il test--------------------------------
print(" INIZIO TEST")
num = body.recupera_codice_alfanumerico(driver)
print(num)








