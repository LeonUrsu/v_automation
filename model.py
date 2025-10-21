import os
import pathlib
import re
import undetected_chromedriver as uc
import pickle
import random
from selenium import webdriver
from selenium.common import NoSuchElementException, TimeoutException
from selenium.webdriver import ActionChains, Keys
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time

import Database_locale
import controller

# -----------------------------------------------------------------------------------------------------------------------

# TODO check versioni chromedriver e chrome

# TODO aggiungere tempi di attesa per rendere il programma random

# TODO implementareaction chains

# TODO offset dei click

# TODO evitare sempre la stessa sequenza di azioni

# TODO SI potrebbero utilizzare le librerie (PyAutoGUI, pynput) per simulare lo spostamento del mouse, purtroppo
# queste librerie interagiscono con il sistema operativo e non con il web browser quindi bisognerebbe calcolare gli offset manualmente
# Queste sono le coordinate della finestra del browser angolo sx-up-(x=0 ,y=139) e dx-down-(x=1904, y=1031) quindi y invertita oppure
# si potrebbe implementare semplicemente il movimento del mouse per simulare un movimento semplice

# TODO aggiungere repository remote

# TODO ricorda che CLASS_NAME non possono avere spazi nei nomi perciò non si lavora cosi, So if you have spaces in your class attribute, switch to CSS_SELECTOR or XPATH

# TODO il caricamento di un nuovo articolo va fatto con due album di foto diverse in modo che vinted non si accorge che sono le stesse foto???

# TODO Fare un metodo per verificare se gli href cambiano nel tempo su vinted se no, si potrebbe salvare a priori il link del
#  articolo e andare direttamente al link per eliminarlo senza fare la verifica online ma in locale dellla data di caricamento vistop che la si può salvare durante il caricamento

# TODO IDEA fare che la data dell'oggetto non viene letta dal sito ma viene salvata in locale durante il caricamento dell'oggetto



# QUESTO é IL METODO PRINCIPALE DELLO SCRIPT
def processo_rinnovo_articoli():
    try:
        driver = avvio_browser()
        apertura_pagina_profilo(driver, "https://www.vinted.it/member/168504727")
        clicca_articoli_attivi(driver)
        numero_articoli = conteggio_articoli_profilo(driver)  # TODO da controllare/testare
        individuazione_articoli(driver, numero_articoli)
        processo_carica_articoli_online()
        print("Resoconto: SUCCESSO")
        time.sleep(20)
    except Exception:
        print("Resoconto: ERRORE")
    print("- - - Software Terminato - - -")


# Metodo per caricare articoli sun profilo del sito web, dalla cartella DA CARICARE
def processo_carica_articoli_online():
    driver = avvio_browser()
    codici_articoli_da_caricare = [item.name for item in controller.path_da_caricare.iterdir() if item.is_dir()]
    for codice in codici_articoli_da_caricare:
        try:
            dati_articolo = creazione_dizionario_dati_articolo(controller.path_da_caricare, codice)
            apertura_pagina_vendita(driver)
            esito = inserimento_dati_articolo_pagina_vendita(driver, dati_articolo)
            if esito:
                scadenza_articolo_database(codice)
            else:
                raise Exception
        except Exception:
            print(f"{codice} - Articolo Non Inserito")


# Metodo per creare un dizionario con i dati dell'articolo dai dati disponibili nei path
# questo metodo deve essere rivisto se cambiamo il modo di archiviazione dell'articolo offline
def creazione_dizionario_dati_articolo(da_caricare_path, codice):
    path_articolo = da_caricare_path.joinpath(codice)
    dati_articolo = {}
    dati_articolo["titolo"] = next(path_articolo.joinpath("titolo")).name
    dati_articolo["colore"] = next(path_articolo.joinpath("colore")).name
    dati_articolo["condizioni"] = next(path_articolo.joinpath("condizioni")).name
    dati_articolo["descrizione"] = next(path_articolo.joinpath("descrizione")).name
    cartelle_foto = sorted((path_articolo / "foto").iterdir())  # elenco delle sottocartelle ordinate
    lettera_album_selezionato = cartelle_foto[2].name.replace("is_", "")
    dati_articolo["album_foto_path"] = path_articolo.joinpath("foto").joinpath(lettera_album_selezionato)
    dati_articolo["codice_alfanumerico"] = lettera_album_selezionato + codice
    dati_articolo["pacco"] = next(path_articolo.joinpath("pacco")).name
    dati_articolo["prezzo"] = next(path_articolo.joinpath("prezzo")).name
    dati_articolo["taglia"] = next(path_articolo.joinpath("taglia")).name
    dati_articolo["titolo"] = next(path_articolo.joinpath("titolo")).name
    return dati_articolo


# Metodo per avviare il browser, login e cookie
def avvio_browser():
    driver = start_browser(controller.sito_vinted)
    accetta_consensi_cookie(driver)
    apertura_pagina_login(driver)
    load_cookies(driver)
    login(driver)
    return driver


# Metodo per inserire i dati dell'articolo nella pagina di vendita
def inserimento_dati_articolo_pagina_vendita(driver, dati_articolo):
    carica_foto_pagina_vendita(driver, dati_articolo["album_foto_path"])
    carica_titolo_pagina_vendita(driver, dati_articolo["titolo"])
    carica_descrizione_pagina_vendita(driver, dati_articolo)
    seleziona_opzione_drop_menu_consigliata_articolo_pagina_vendita(driver, "category", "[id*='catalog-suggestion-']")
    seleziona_opzione_drop_menu_consigliata_articolo_pagina_vendita(driver, "brand", "[id*='suggested-brand-radio-']")
    seleziona_opzione_drop_menu_articolo_pagina_vendita(driver, "size", dati_articolo["taglia"])
    seleziona_opzione_drop_menu_articolo_pagina_vendita(driver, "condition", dati_articolo["condizioni"])
    seleziona_opzione_drop_menu_consigliata_articolo_pagina_vendita(driver, "color", ".web_ui__Checkbox__button.web_ui__Checkbox__button-left text-top")
    #seleziona_opzione_drop_menu_articolo_pagina_vendita(driver, "material", dati_articolo["material"]) #TODO or no
    seleziona_dimensione_pacco_articolo_pagina_vendita(driver, dati_articolo["pacco"])
    seleziona_prezzo_di_vendita_nuovo_articolo(driver, dati_articolo["prezzo"])
    click_carica_articolo_pagina_vendita(driver)
    esito = verifica_click_carica_articolo_pagina_vendita(driver)
    return esito


#Metodo che verifica se il click o l'articolo è stato caricato o è successo qualche errore torna al caricamento nuovo
# articolo
def verifica_click_carica_articolo_pagina_vendita(driver):
    humanizer(2) #TODO - Qui si potrebbe diminuire il tempo per la performance
    current_url = driver.current_url
    if current_url == controller.sito_vinted + "/items/new":
        return False
    else:
        return True



#Metodo per caricare premere il pulsante di carica articolo sulla pagina vendita e che verifica se è stato caricato se
def click_carica_articolo_pagina_vendita(driver):
    humanizer(0)
    elemento = driver.find_element(By.CSS_SELECTOR, "button[data-test-id='upload-form-save-button']")
    offset_move_and_click_like_human(driver,elemento)
    humanizer(0)


#Metodo per selezionare la dimensione del pacco di destinazione
#dimensione = {1, 2, 3} una delle precedenti, 3 è il più grande
def seleziona_dimensione_pacco_articolo_pagina_vendita(driver, dimensione):
    id_dimensione = "package-size-" + str(dimensione)
    elemento = driver.find_element(By.ID, id_dimensione)
    offset_move_and_click_like_human(driver, elemento)


# Metodo per selezionare il materiale dell'articolo di vendita
def seleziona_materiale_articolo_pagina_vendita(driver, materiale):
    elementi_materiali = selettore_elementi_multipli_pagina_di_vendita(driver, "material")
    materiale = materiale.lower()
    for elemento_materiale in elementi_materiali:
        materiale_trovato = elemento_materiale.text.lower()
        if materiale_trovato == materiale.lower():
            azione = ActionChains(driver)
            azione.move_to_element(elemento_materiale)
            azione.pause(small_humanizer())
            azione.click(elemento_materiale)
            azione.pause(small_humanizer())
            azione.perform()
            humanizer(0)
            return True
    return False


# Metodo per selezionare l'oggetto dalla drop-menu serve per DRY (Don't Repeat Yourself)
#cosa_cercare = esempio "size", "category"...
#text_oggetto = Xl, L sono le taglie che abbiamo inserito
def seleziona_opzione_drop_menu_articolo_pagina_vendita(driver, cosa_cercare , text_oggetto):
    try:
        elementi_menu = selettore_elementi_multipli_pagina_di_vendita(driver, cosa_cercare)
        text_oggetto = text_oggetto.lower()
        for elemento_menu in elementi_menu:
            text_trovato = elemento_menu.text.lower()
            if text_trovato == text_oggetto:
                azione = ActionChains(driver)
                azione.move_to_element(elemento_menu)
                azione.pause(small_humanizer())
                azione.click(elemento_menu)
                azione.pause(small_humanizer())
                azione.perform()
                humanizer(0)
                return True
    except Exception as e: print(e)

#Metodo DRY (Don't Repeat Yourself) per spostarso come un umano su un elemento web passato e cliccarci sopra con un delay
#tra le azioni
#TODO def move_and_click_like_human(driver, elemento):


#Metodo per spostarsi su un elemento con un piccolo offset e cliccarlo
def offset_move_and_click_like_human(driver, elemento):
    small_humanizer()
    azione = ActionChains(driver)
    azione.pause(small_humanizer())
    azione.move_to_element_with_offset(elemento, random.randint(0, 60), random.randint(0, 10))
    azione.pause(small_humanizer())
    azione.click(elemento)
    azione.pause(small_humanizer())
    azione.perform()
    small_humanizer()


#Questo metodo serve per DRY (Don't Repeat Yourself)
#cosa_cercare = "category", "size", "material"
def selettore_elementi_multipli_pagina_di_vendita(driver, cosa_cercare):
    elemento = driver.find_element(By.ID, cosa_cercare)
    elementi_trovati = elemento.find_elements(By.CSS_SELECTOR,
                                              "li.web_ui__Item__item.web_ui__Item__with-divider")
    return elementi_trovati


# Metodo per selezionare la condizione dell'articolo di vendita
# condizione = 1-5 (intero) in ordine di qualità maggiore
def seleziona_condizioni_articolo_pagina_vendita(driver, condizione):
    condizione = int(condizione)
    elementi_condizioni = selettore_elementi_multipli_pagina_di_vendita(driver, "condition")
    indice = 5 - condizione
    if indice < 0 or indice >= len(elementi_condizioni):
        raise IndexError()
    elemento_condizione = elementi_condizioni[indice]
    azione = ActionChains(driver)
    azione.move_to_element(elemento_condizione)
    azione.pause(small_humanizer())
    azione.click(elemento_condizione)
    azione.pause(small_humanizer())
    azione.perform()


# TODO verificare se è case-sensitive
def seleziona_taglia_articolo_pagina_vendita(driver, taglia):
    taglia = taglia.lower()
    elemento = driver.find_element(By.ID, "size")
    elementi_taglie = elemento.find_elements(By.CSS_SELECTOR, "li.web_ui__Item__item.web_ui__Item__with-divider")
    for elemento_taglia in elementi_taglie:
        taglia_trovata = elemento_taglia.text
        if taglia_trovata == taglia:
            azione = ActionChains(driver)
            azione.move_to_element(elemento_taglia)
            azione.pause(small_humanizer())
            azione.click(elemento_taglia)
            azione.pause(small_humanizer())
            azione.perform()
            humanizer(0)
            return True
    return False


# Metodo per risolvere la ridondanza delle stesse operazioni
# opzioni_input = esempio:"category" indica l'id della tendina ancora chiusa delle opzioni che compaiono dopo il click
# css_opzioni_suggerite = "[id*='catalog-suggestion-']" indica il pallino di selezione consigliata da cliccare
def seleziona_opzione_drop_menu_consigliata_articolo_pagina_vendita(driver, opzione_input, css_opzioni_suggerite):
    elemento = driver.find_element(By.ID, opzione_input)
    genitore_elemento = elemento.find_element_by_xpath('..')
    azione = ActionChains(driver)
    azione.move_to_element(elemento)
    azione.pause(medium_random())
    azione.click(elemento)
    azione.pause(medium_random())
    azione.perform()
    azione.pause(medium_random())
    # qui troviamo le cose suggerite quando apriamo il menu delle opzioni
    opzioni_suggerite = genitore_elemento.find_element(By.CSS_SELECTOR, css_opzioni_suggerite)
    button_opzione = opzioni_suggerite.find_element(By.CLASS_NAME, "web_ui__Radio__button")
    azione = ActionChains(driver)
    azione.move_to_element(button_opzione)
    azione.pause(medium_random())
    azione.click(button_opzione)
    azione.pause(medium_random())
    azione.perform()


# TODO da testare, importantissimo per il rinnnovo che il codice sia presente in modo e formato corretto
# Metodo per caricare la descrizione e il codice del articolo
def carica_descrizione_pagina_vendita(driver, dati_articolo):
    elemento = driver.find_element(By.ID, "description")
    azione = ActionChains(driver)
    azione.move_to_element(elemento)
    azione.pause(humanizer(0))
    azione.click(elemento)
    azione.pause(humanizer(0))
    azione.perform()
    humanizer(0)
    send_delayed_keys(elemento, dati_articolo["descrizione"] + " " + dati_articolo["codice_alfanumerico"])
    humanizer(1)


# Metodo per selezionare il prezzo di vendita dell'articolo nella pagina di vendita nuovo articolo del sito
def seleziona_prezzo_di_vendita_nuovo_articolo(driver, prezzo):
    elemento = driver.find_element(By.ID, "price")  # todo da controllare
    azione = ActionChains(driver)
    azione.move_to_element(elemento)
    azione.pause(humanizer(0))
    azione.click(elemento)
    azione.pause(humanizer(0))
    azione.perform()
    humanizer(0)
    elemento.send_keys(prezzo)
    humanizer(1)


# Metodo per caricare il titolo del articolo passato nella pagina di vendita
def carica_titolo_pagina_vendita(driver, titolo):
    elemento = driver.find_element(By.ID, "title")
    send_delayed_keys(elemento, titolo)
    humanizer(1)


# Metodo per selezionare la categoria consigliata da vinted per il nostro articolo
def seleziona_categoria_standard_pagina_vendita(driver):
    elemento = driver.find_element(By.ID, "category")
    genitore_elemento = elemento.find_element_by_xpath('..')
    azione = ActionChains(driver)
    azione.move_to_element(elemento)
    azione.pause(medium_random())
    azione.click(elemento)
    azione.pause(medium_random())
    azione.perform()
    azione.pause(medium_random())
    categoria = genitore_elemento.find_element(By.CSS_SELECTOR, "[id*='catalog-suggestion-']")
    button_categoria = categoria.find_element(By.CLASS_NAME, "web_ui__Radio__button")
    azione = ActionChains(driver)
    azione.move_to_element(button_categoria)
    azione.pause(medium_random())
    azione.click(button_categoria)
    azione.pause(medium_random())
    azione.perform()


# Metodo per caricare le foto nella finestra della pagina vendi articolo, si passa il driver e il path delle foto da caricare
def carica_foto_pagina_vendita(driver, path_foto):
    # Crea la lista completa dei file (solo immagini, opzionale)
    file_list = [
        os.path.join(path_foto, f)
        for f in os.listdir(path_foto)
        if os.path.isfile(os.path.join(path_foto, f))
    ]
    upload = driver.find_element(By.XPATH, '//span[text()="Carica le foto"]')
    upload.send_keys(r"\n".join(file_list))
    attesa_caricamento_elemento(driver, 10, By.CLASS_NAME, "photo-box")
    # TODO qui ci dovrebbe essere un fallback ^^^^^^^^^^^^^


# TODO da testare in qualche modo intelligente, l'offset impostato sembra che clicca sempre sul pulsante vendi, da mettere un fallback di recupero
# Metodo per aprire la pagina per caricare l'articolo di vendita, perchè funzioni correttamente questo metodo deve
# essere chiamato da un luogo in cui è presente la foto del profilo e il tasto di vendi subito
def apertura_pagina_vendita(driver):
    humanizer(0)
    immagine_profilo = driver.find_element(By.ID, "user-menu-button")
    azione = ActionChains(driver)
    azione.move_to_element_with_offset(immagine_profilo, 50 + random.randint(0, 60), random.randint(0, 10))
    humanizer(0)
    azione.click()
    humanizer(0)
    azione.perform()
    humanizer(5)
    # routine di fallback
    try:
        attesa_caricamento_elemento(driver, 5, By.ID, "photos")
    except NoSuchElementException:
        humanizer(0)
        driver.get("https://www.vinted.it/items/new")
        humanizer(0)


# serve per accendere il browser, metterlo a schermo intero e andare ad un sito web passato per parametro
def start_browser(sito_web):
    options = webdriver.ChromeOptions()
    options.add_argument(r'--user-data-dir=C:\Users\Leon\AppData\Local\Google\Chrome\User Data\Default')
    driver = uc.Chrome(options=options)
    driver.get(sito_web)
    humanizer(3)
    driver.maximize_window()
    return driver


# Metodo per gestire le scelte dei cookie
def accetta_consensi_cookie(driver):
    gestisci_cookie_button_id = "onetrust-pc-btn-handler"
    finestra_conferma_cookie = "onetrust-pc-sdk"
    conferma_scelte_button_class = ".save-preference-btn-handler.onetrust-close-btn-handler"
    try:
        humanizer(0)
        attesa_caricamento_elemento(driver, 5, By.ID, gestisci_cookie_button_id)  # click su gestisci cookie
        elemento_cookie = driver.find_element(By.ID, gestisci_cookie_button_id)
        elemento_cookie.click()
        humanizer(0)
        attesa_caricamento_elemento(driver, 5, By.ID, finestra_conferma_cookie)  # click su conferma le mie scelte
        elemento_cookie = driver.find_element(By.CSS_SELECTOR, conferma_scelte_button_class)
        elemento_cookie.click()
        humanizer(-0.5)
    except Exception:
        pass


# Metodo per attendere il caricamento della pagina in caso un elemento ancora non è stato caricato
# integer tempo = secondi dopo di cui lanciare un eccezione NoSuchElementException
# string elemento = elemento da attendere nella pagina di caricamento
def attesa_caricamento_elemento(driver, tempo, tipo_elemento, nome_elemento, ):
    WebDriverWait(driver, tempo).until(EC.presence_of_element_located((tipo_elemento, nome_elemento)))


# metodo che non fa nulla per un determinato numero di secondi e ritorna il valore
def humanizer(offset):
    ran = medium_random()
    ran += offset
    time.sleep(ran)
    return ran


def medium_random():
    ran = random.uniform(0.9, 1.8)
    return ran


def small_humanizer():
    ran = random.uniform(0.3, 0.6)
    return ran


# Metodo per attendere il tempo tra la premuta di un tasto e l'altro
def typing_humanizer():
    humanizer(0)
    ran = random.uniform(0.166, 0.254)
    time.sleep(ran)
    humanizer(0)
    return ran


# Questo metodo serve per accedere alla pagina del login e se non riesce lancia un eccezione
def apertura_pagina_login(driver):
    nome_classe = ".web_ui__Button__button.web_ui__Button__outlined.web_ui__Button__small.web_ui__Button__primary.web_ui__Button__truncated"
    try:
        attesa_caricamento_elemento(driver, 5, By.CSS_SELECTOR, nome_classe)
        elemento_accedi = driver.find_element(By.CSS_SELECTOR, nome_classe)
        azione = ActionChains(driver).move_to_element(elemento_accedi)
        azione.pause(humanizer(0))
        azione.click()
        azione.pause(humanizer(0))
        azione.perform()
        nome_classe = "auth-select-type--register-switch"
        attesa_caricamento_elemento(driver, 5, By.CSS_SELECTOR, f"[data-testid={nome_classe}]")
        elemento_accedi = driver.find_element(By.CSS_SELECTOR, f"[data-testid={nome_classe}]")
        azione = ActionChains(driver).move_to_element(elemento_accedi)
        azione.pause(humanizer(0))
        azione.click()
        azione.pause(humanizer(0))
        azione.perform()
        humanizer(0)
        nome_classe = " auth-select-type--login-email"
        attesa_caricamento_elemento(driver, 5, By.CSS_SELECTOR, f"[data-testid={nome_classe}]")
        elemento_accedi = driver.find_element(By.CSS_SELECTOR, f"[data-testid={nome_classe}]")
        azione = ActionChains(driver).move_to_element(elemento_accedi)
        azione.pause(humanizer(0))
        azione.click()
        azione.pause(humanizer(0))
        azione.perform()
        humanizer(0)
    except (NoSuchElementException, TimeoutException) as e:
        print(e)


# serve per accedere al account specificato dalla finestra che appare dopo aver cliccato di accedere tramite email
def login(driver):
    try:
        attesa_caricamento_elemento(driver, 2, By.ID, "username")
        email_element = driver.find_element(By.ID, "username")
        email_element.clear()
        send_delayed_keys(email_element, controller.my_email)
        humanizer(0)
        password_element = driver.find_element(By.ID, "password")
        password_element.clear()
        send_delayed_keys(password_element, controller.my_password)
        humanizer(0)
        button = driver.find_element(By.XPATH, "//button[.//span[text()='Continua']]")
        azione = ActionChains(driver)
        azione.move_to_element(button)
        humanizer(0)
        humanizer(0)
        azione.click(button)
        azione.perform()
        time.sleep(5)
        save_cookies(driver)
    except Exception:
        humanizer(5)  # TODO cambiare con attesa_caricamento_elemento


# Metodo per salvare i cookies del utente, è stato utiulizzato solo una volta perchè abbiamo già i cookie,
# TODO sarebbe da implementare un controllo per vedere se abbiamo il file cookies.pkl e se non lo abbiamo lo creiamo con questo metodo
def save_cookies(driver):
    cookies = driver.get_cookies()
    pickle.dump(cookies, open("cookies.pkl", "wb"))
    driver.get(controller.sito_vinted)


# Metodo per cariacare i cookie nel browser
def load_cookies(driver):
    cookies = pickle.load(open("cookies.pkl", "rb"))
    for cookie in cookies:
        cookie["domain"] = ".vinted.it"
        try:
            driver.add_cookie(cookie)
            driver.refresh()
        except Exception:
            pass


# Metodo per fare ingresso di caratteri con un delay umano
def send_delayed_keys(input_element, text_to_input):
    for character in text_to_input:
        input_element.send_keys(character)
        typing_humanizer()


# metodo per recarsi profilo del sito
def apertura_pagina_profilo(driver, link):
    # nome = "user-menu-button"
    # oggetto = driver.find_element(By.ID, nome)
    # performa_click(driver,oggetto)
    humanizer(0)
    carica_link(driver, link)  # TODO da modificare e mettere un action chains invece di carica_link
    humanizer(0)


# Metodo per cliccare gli oggetti attivi del profilo utente
def clicca_articoli_attivi(driver):
    humanizer(0)
    button = driver.find_element(By.XPATH, "//span[text()='Attivi']")
    performa_click(driver, button)
    humanizer(0)


# metodo per caricare un sito web
def carica_link(driver, link_destinazione):
    driver.get(link_destinazione)


# Metodo per contare gli articoli all'interno di una pagina del profilo
def conteggio_articoli_profilo(driver):
    nome_elemento = "u-z-index-isolate"
    attesa_caricamento_elemento(driver, 5, By.CSS_SELECTOR, nome_elemento)
    element = WebDriverWait(driver, 10).until(
        EC.visibility_of_element_located((
            By.XPATH,
            "//div[@class='u-flexbox u-justify-content-between u-align-items-center u-flex-grow u-flex-wrap']//h2[contains(., 'articoli')]"
        ))
    )
    text = element.text.strip()
    numero = int(''.join(filter(str.isdigit, text)))
    return numero


# Metodo per Iterare gli articoli, controllare le date e fare tutto quello che serve per caricare o scaricare gli oggetti
# numero= oggetti da iterare
def individuazione_articoli(driver, numero_articoli):
    scroll(driver, numero_articoli)
    humanizer(0)
    articoli = driver.find_elements(By.CSS_SELECTOR,
                                    ".u-position-relative.u-min-height-none.u-flex-auto.new-item-box__image-container")
    array_link_articoli = recupera_link_articoli(articoli, numero_articoli)
    lunghezza_array = len(articoli)
    contatore = 0
    try:
        while contatore < lunghezza_array:
            humanizer(0)
            gestione_articolo(driver, array_link_articoli[contatore])  # TODO riguardare logic
            humanizer(0)
    except Exception:
        pass


# Metodo per recuperare tutti i link degli articoli passati come array di webElements e che li ritorna come array di str
def recupera_link_articoli(articoli, numero_articoli):
    contatore = numero_articoli
    array_link_articoli = []
    try:
        while contatore >= 0:
            href_articolo = articoli[contatore].get_attribute("href")
            array_link_articoli.append(href_articolo)
            contatore -= 1
    except Exception:
        return array_link_articoli
    return array_link_articoli


# TODO - Warning - questo metodo potrebbe non scrollare fino in fondo
# Metodo per scrollare la lista degli articoli fino in fondo
def scroll(driver, numero_articoli):
    humanizer(0)
    volte = int(numero_articoli / 5)
    quanto_y = 450 + int(random.uniform(51, 120))
    volte += 5  # per sicurezza scrolliamo fino in fondo
    azione = ActionChains(driver)
    for i in range(volte):
        azione.scroll_by_amount(0, quanto_y)
        azione.perform()
        humanizer(-0.5)
    humanizer(0)


# Questo metodo serve per aprire il link del articolo passato, controllare se è da eliminare, gestire database locale,
# eliminarlo online come ultima fase
def gestione_articolo(driver, link_articolo):
    humanizer(0)
    driver.get(link_articolo)  # Apre l'articolo nella schermata
    time.sleep(2)
    humanizer(0)
    esito_da_cancellare = controllo_eliminazione_articolo(driver)
    # passo esito booleano e se True apportare le modifiche
    if esito_da_cancellare:
        codice_articolo = recupera_codice_alfanumerico(driver)
        #salva_info_articolo_off(driver, codice_articolo)# non lo salviamo è complicato web->pc
        humanizer(0)
        cancella_articolo_online(driver)
        scadenza_articolo_database(codice_articolo)
        cambia_album(codice_articolo)
    else:
        driver.back()


# Metodo per cambiare identificativo del album in modo da caricare le foto diverse del articolo
def cambia_album(codice):
    # TODO
    pass


# Metodo per recuperare lo stato dell'articolo online e salvarlo nella sua cartella offline per un eventuale rinnovo futuro
def salva_info_articolo_off(driver, codice_articolo):
    # TODO
    #articolo = ArticoloVin()
    attributi_da_settare = []
    # titolo - ok class - driver.find_elements(By.XPATH,"//*[@class='web_ui__Text__text web_ui__Text__title web_ui__Text__left']")
    # setattr(articolo, "")
    #breadcrumb = driver.find_element(By.CSS_SELECTOR, ".breadcrumbs.breadcrumbs--truncated")


def recupero_info_da_sidebar_articolo(web_element):
    # Titolo
    try:
        titolo = web_element.find_element(
            By.XPATH,
            "//div[@class='details-list details-list--main-info']//div[@class='item-page-summary-plugin']//div[@class='summary-max-lines-4']//h1[@class='web_ui__Text__text web_ui__Text__title web_ui__Text__left']"
        ).text
    except:
        titolo = None

    # Prezzo
    try:
        prezzo = web_element.find_element(
            By.CSS_SELECTOR, "p[data-testid='item-price']"
        ).text
    except:
        prezzo = None

    # Brand
    try:
        brand = web_element.find_element(
            By.CSS_SELECTOR, "a[data-testid='item-brand']"
        ).text
    except:
        brand = None

    # Taglia
    try:
        taglia = web_element.find_element(
            By.CSS_SELECTOR, "a[data-testid='item-size']"
        ).text
    except:
        taglia = None

    # Nome venditore
    try:
        venditore = web_element.find_element(
            By.CSS_SELECTOR, "a[data-testid='user-link'] span"
        ).text
    except:
        venditore = None

    # Descrizione (ricerca più flessibile)
    try:
        descrizione = web_element.find_element(
            By.CSS_SELECTOR, "div[itemprop='description']"
        ).text
    except:
        # fallback se cambia struttura
        descrizione = web_element.find_element(
            By.CSS_SELECTOR,
            "span.web_ui__Text__text.web_ui__Text__body.web_ui__Text__left.web_ui__Text__format"
        )

    # --- Risultato finale ---
    print("Titolo:", titolo)
    print("Prezzo:", prezzo)
    print("Brand:", brand)
    print("Taglia:", taglia)
    print("Venditore:", venditore)
    print("Descrizione:", descrizione)


def safe_text(root, css):
    """Trova il primo elemento che corrisponde al CSS selector all’interno di root, oppure restituisce None"""
    try:
        return root.find_element(By.CSS_SELECTOR, css).text.strip()
    except NoSuchElementException:
        return None


def estrai_info_sidebar(sidebar):
    """Estrae titolo, prezzo, brand, taglia e descrizione da un elemento <aside> di Vinted."""
    info = {}

    # Titolo
    info["titolo"] = sidebar.find_element(By.XPATH,
                                          "//*[@class='web_ui__Text__text web_ui__Text__title web_ui__Text__left']").text

    # Prezzo
    info["prezzo"] = sidebar.find_element(By.XPATH,
                                          ".//div[@data-testid='item-price']//p[contains(@class,'web_ui__Text__subtitle')]").text

    # Brand
    info["brand"] = sidebar.find_element(By.XPATH, ".//span[@itemprop='name']").text

    # Taglia
    info["taglia"] = sidebar.find_element(By.XPATH,
                                          ".//div[@data-testid='item-attributes-size']//span[contains(@class,'web_ui__Text__subtitle')]").text

    # Descrizione
    info["descrizione"] = sidebar.find_element(By.XPATH, ".//div[@itemprop='description']").text
    return info


# Metodo che va indietro alla pagina precedente in base al esito della verifica della data, se non è scaduta si va indietro alla lista degli articoli
def indietro_pagina(driver, esito_da_cancellare):
    if esito_da_cancellare:
        return
    else:
        driver.back()


# Metodo per controllare la data del articolo e vedere se dobbiamo eliminarlo oppure no
# return True se è da eliminare
def controllo_eliminazione_articolo(driver):
    caricato_span = WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.XPATH, "//span[normalize-space(text())='Caricato']")))
    upload_date_elem = caricato_span.find_element(By.XPATH, "../../div[@itemprop='upload_date']/span")
    upload_date = upload_date_elem.text
    eta_articolo = ore_trascorse(upload_date)
    if eta_articolo > 72:
        return True
    else:
        return False


# Metodo per convertire il formato del sito web in ore trascorse passando il formato in stringa
def ore_trascorse(testo: str) -> float:
    testo = testo.strip().lower()
    parole_numeri = {
        "un": 1, "una": 1, "un'": 1, "uno": 1,
        "due": 2, "tre": 3, "quattro": 4, "cinque": 5,
        "sei": 6, "sette": 7, "otto": 8, "nove": 9,
        "dieci": 10, "undici": 11, "dodici": 12,
        "tredici": 13, "quattordici": 14, "quindici": 15,
        "sedici": 16, "diciassette": 17, "diciotto": 18,
        "diciannove": 19, "venti": 20, "ventuno": 21,
        "ventidue": 22, "ventitre": 23,
    }
    numero = None
    for parola, valore in parole_numeri.items():
        if testo.startswith(parola):
            numero = valore
            break
    if numero is None:
        # se non è parola, prova a leggere cifre
        num_str = ''.join([c for c in testo if c.isdigit()])
        numero = int(num_str) if num_str else 1
    if "minut" in testo:
        return numero / 60  # minuti → ore
    elif "ora" in testo:
        return numero
    elif "ore" in testo:
        return numero
    elif "giorn" in testo:
        return numero * 24
    elif "settim" in testo:
        return numero * 24 * 7
    elif "mes" in testo:
        return numero * 24 * 30  # approssimazione: 1 mese = 30 giorni
    elif "ann" in testo:
        return numero * 24 * 365  # approssimazione: 1 anno = 365 giorni
    else:
        return 0  # fallback se non riconosce


# Metodo per aprire l'articolo in una nuova finestra
def apertura_articolo_nuova_finestra(driver, articolo):
    humanizer(0)
    # apri in una nuova scheda (CTRL + click)
    articolo.send_keys(Keys.CONTROL + Keys.RETURN)  # su Mac usa Keys.COMMAND
    # aspetta un attimo che la scheda si apra
    time.sleep(4)
    # ottieni tutti gli handle (le schede aperte)
    tabs = driver.window_handles
    # passa all'ultima scheda
    driver.switch_to.window(tabs[-1])
    humanizer(0)
    if articolo_data_scaduta(driver): cancella_articolo_online(driver)
    humanizer(0)
    # ritorno alla scheda principale\
    driver.close()
    driver.switch_to.window(driver.window_handles[0])
    # TODO test se driver.refresh() funziona
    driver.refresh()


# Metodo per controllare gli articoli
def articolo_data_scaduta(driver):
    codice_articolo = recupera_codice_alfanumerico(driver)
    scadenza_articolo_database(codice_articolo)
    pass


def cancella_articolo_online(driver):
    try:
        humanizer(0)
        attesa_caricamento_elemento(driver, 5, By.XPATH, "//button[.//span[text()='Cancella']]")
        button = driver.find_element(By.XPATH, "//button[.//span[text()='Cancella']]")
        azione = ActionChains(driver)
        azione.move_to_element(button)
        azione.perform()
        azione.pause(humanizer(0))
        attesa_caricamento_elemento(driver, 5, By.XPATH, "//button[.//span[text()='Conferma e cancella']]")
        button = driver.find_element(By.XPATH, "//button[.//span[text()='Conferma e cancella']]")
        azione.pause(humanizer(0))
        azione.move_to_element(button)
        azione.pause(humanizer(0))
        azione.perform()
        azione.pause(humanizer(0))
        azione.perform()
    except Exception:
        return Exception


# Recupera codice alfanumerico dal articolo il codice può avere una "a" o "b" d'avanti al numero del articolo e indica
# quale album di fotografie è stato utilizzato
def recupera_codice_alfanumerico(driver):
    desc_element = driver.find_element(
        By.CSS_SELECTOR,
        "span.web_ui__Text__text.web_ui__Text__body.web_ui__Text__left.web_ui__Text__format"
    )
    desc_text = desc_element.text
    # Cerca il codice alfanumerico tipo 'a1921242' o 'b4321'
    match = re.search(r'\b[ab]\d{1,7}\b', desc_text)
    # Recupera il codice trovato
    if match:
        codice = match.group(0)
        return codice
    else:
        return 0


def performa_click(driver, oggetto):
    humanizer(0)
    azione = ActionChains(driver).move_to_element(oggetto)
    azione.pause(humanizer(0))
    azione.click()
    azione.pause(humanizer(0))
    azione.perform()
    humanizer(0)


@DeprecationWarning
# Metodo per reuperare il codice del articolo tramite combinazione di hashtag
def recupera_codice_hashtag(driver):
    # #Vinteditalia #Secondamano #Modasostenibile #Vestiti #Moda #Vintage #Mango #Accessori #Italia #Italy
    span_element = driver.find_element(By.CSS_SELECTOR,
                                       ".web_ui__Text__text.web_ui__Text__body.web_ui__Text__left.web_ui__Text__format")
    hashtags_elements = driver.find_elements(By.XPATH, "//span//a[starts-with(@href, '/catalog?search_text=%23')]")
    all_hashtags = [a.text for a in hashtags_elements]
    first_6_hashtags = all_hashtags[:6]


# Metodo per spostarsi su un oggetto e cliccarlo, bisogna passare il nome del oggetto per argomento


# Metodo che sposta la cartella del prodotto tramite il nome/codice del articolo, la cartella avrà come nome il codice del articolo
def scadenza_articolo_database(codice):
    Database_locale.sposta_dir_articolo(pathlib.Path(controller.path_caricati, codice[1:]),
                                        pathlib.Path(controller.path_da_caricare, codice[1:]))


# Metodo che sposta la cartella del prodotto tramite il nome/codice del articolo, la cartella avrà come nome il codice del articolo
def rinnovo_articolo_database(codice):
    Database_locale.sposta_dir_articolo(pathlib.Path(controller.path_da_caricare, codice[1:]),
                                        pathlib.Path(controller.path_caricati, codice[1:]))


def diagnosi():
    opts = Options()
    opts.add_argument("--start-maximized")
    opts.add_argument("--headless=new")  # NON usare headless per debugging
    # service = Service("/path/to/chromedriver")
    # driver = webdriver.Chrome(service=service, options=opts)
    driver = uc.Chrome(options=opts)

    url = controller.sito_vinted
    # url =
    driver.get(url)
    time.sleep(2)

    # numero di URL navigati in un intervallo breve
    print("Current URL:", driver.current_url)

    src = driver.page_source.lower()
    print("meta refresh:", "http-equiv=\"refresh\"" in src)
    print("settimeout:", "settimeout" in src)
    print("location.reload:", "location.reload" in src)
    print("iframe:", "<iframe" in src)
    # se true ti riconosce come bot
    print(driver.execute_script(
        "return {webdriver: navigator.webdriver, userAgent: navigator.userAgent, plugins: navigator.plugins.length, language: navigator.language};"))
