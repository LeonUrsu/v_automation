import os
import pathlib
import re
import shutil
from multiprocessing.spawn import old_main_modules

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

import Database
import Database_mostro
import config


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

# TODO verificare se l'album viene cambiato correttamente durante le interazioni

#TODo quando si arica un articolo online,so potrebe veridicare la sua presenza nella pagina del profilo se è stato veramente caricato si potrebbe vedere se l'articolo è effettivamente presente nel negozio

def processo_rinnovo_articoli_online(config):
    try:
        driver = avvio_browser(config)
        apertura_pagina_profilo(driver, config.pagina_profilo)
        clicca_articoli_attivi(driver)
        iterazione_articoli_profilo_online(config, driver)
        # TODO test sposta_articoli_database
        # Gli articoli venduti online sono spostati nella cartella cancellati
        Database_locale.sposta_articoli_database(config.path_caricati, config.path_cestinati)
        # Gli articoli staged che non andavano eliminati online (per la loro data)ora tornano nella cartella caricati
        Database_locale.sposta_articoli_database(config.path_rinnovo_non_necessario, config.path_caricati)
        driver.close()
        processo_carica_articoli_online(config, config.path_articoli)  # carica online articoli che sono da rinnovare
        processo_carica_articoli_online(config, config.path_nuovi_articoli)  # carica online articoli nuovi
        print("Resoconto: SUCCESSO")
    except Exception:
        print("Resoconto: ERRORE")
    print("- - - Software Terminato - - -")


# Metodo per caricare articoli sun profilo del sito web, dalla cartella DA CARICARE
def processo_carica_articoli_online(config):
    driver = avvio_browser(config)
    codici_articoli_da_caricare = Database.recupera_codici_articoli_da_inserire()
    for codice in codici_articoli_da_caricare:
        try:
            json_articolo = Database.read_articolo_database(
                config.path_articoli.joinpath(codice).joinpath("articolo.text"))
            if json_articolo["stato"] != "offline" or json_articolo["stato"] != "new":
                raise Exception
            apertura_pagina_vendita(driver)
            inserimento_dati_articolo_pagina_vendita(driver,
                                                     json_articolo)  # TODO DA CONTROLLARE ACCURATAMENTE fare con agganciamento ad una pagina già presente
            click_carica_articolo_pagina_vendita(driver)
            esito = verifica_click_carica_articolo_pagina_vendita(config, driver)
            if esito:
                json_articolo["stato"] = "online"
                Database.update_articolo_database(config, json_articolo)
            else:
                raise Exception
        except Exception:
            print(f"{codice} - Articolo Non Inserito")
    driver.close()


# Metodo per unire due dizionari in uno solo
def merge_two_dicts(x, y):
    z = x.copy()  # start with keys and values of x
    z.update(y)  # modifies z with keys and values of y
    return z


# Metodo per creare un dizionario con i dati dell'articolo dai dati disponibili nei path
# questo metodo deve essere rivisto se cambiamo il modo di archiviazione dell'articolo offline
def creazione_dizionario_dati_articolo(path_articolo, codice):
    dati_articolo = {}
    dati_articolo["titolo"] = next((d for d in path_articolo.joinpath("titolo").iterdir() if d.is_dir()), None).name
    dati_articolo["colore"] = next((d for d in path_articolo.joinpath("colore").iterdir() if d.is_dir()), None).name
    dati_articolo["condizioni"] = next((d for d in path_articolo.joinpath("condizioni").iterdir() if d.is_dir()),
                                       None).name
    dati_articolo["descrizione"] = ""
    with open(path_articolo.joinpath("descrizione").joinpath("descrizione.txt"), encoding='utf8') as f:
        dati_articolo["descrizione"] = f.read()
    lettera_album_selezionato = ""
    if path_articolo.joinpath("foto").joinpath("is_a").is_dir():
        lettera_album_selezionato = "a"
    elif path_articolo.joinpath("foto").joinpath("is_b").is_dir():
        lettera_album_selezionato = "b"
    dati_articolo["album_foto_path"] = path_articolo.joinpath("foto").joinpath(lettera_album_selezionato)
    dati_articolo["codice_alfanumerico"] = lettera_album_selezionato + codice
    dati_articolo["pacco"] = next((d for d in path_articolo.joinpath("pacco").iterdir() if d.is_dir()), None).name
    dati_articolo["prezzo"] = next((d for d in path_articolo.joinpath("prezzo").iterdir() if d.is_dir()), None).name
    dati_articolo["taglia"] = next((d for d in path_articolo.joinpath("taglia").iterdir() if d.is_dir()), None).name
    return dati_articolo


# Metodo per avviare il browser, login e cookie
def avvio_browser(config):
    driver = start_browser(config.sito_vinted)
    accetta_consensi_cookie(driver)
    apertura_pagina_login(driver)
    load_cookies(driver)
    login(driver)
    return driver


# TODO to TEST
# Metodo per inserire i dati dell'articolo nella pagina di vendita
def inserimento_dati_articolo_pagina_vendita(driver, dati_articolo):
    carica_foto_pagina_vendita(driver.find_element(By.ID, "photos").find_element(By.CLASS_NAME, "u-hidden")
                               , dati_articolo["album_foto_path"])
    carica_titolo_pagina_vendita(driver, dati_articolo["titolo"])
    carica_descrizione_pagina_vendita(driver, dati_articolo)
    # seleziona_opzione_drop_menu_consigliata_articolo_pagina_vendita(driver, "category", "[id*='catalog-suggestion-']")
    seleziona_categoria_standard_pagina_vendita(driver)
    seleziona_opzione_drop_menu_consigliata_articolo_pagina_vendita(driver, "brand",
                                                                    "[id*='suggested-brand-radio-']")
    seleziona_opzione_drop_menu_articolo_pagina_vendita(driver, "size", dati_articolo["taglia"])
    seleziona_opzione_drop_menu_articolo_pagina_vendita(driver, "condition", dati_articolo["condizioni"])
    seleziona_opzione_drop_menu_consigliata_articolo_pagina_vendita(driver, "color",
                                                                    ".web_ui__Checkbox__button.web_ui__Checkbox__button-left text-top")
    # seleziona_opzione_drop_menu_articolo_pagina_vendita(driver, "material", dati_articolo["material"])
    seleziona_dimensione_pacco_articolo_pagina_vendita(driver, dati_articolo["pacco"])
    seleziona_prezzo_di_vendita_nuovo_articolo(driver, dati_articolo["prezzo"])
    return True


# Metodo che verifica se ci troviamo sulla pagina di inserimento dati del articolo oppure no
def verifica_click_carica_articolo_pagina_vendita(config, driver):
    humanizer(2)
    current_url = driver.current_url
    if current_url == config.sito_vinted + "/items/new":
        return False
    else:
        return True


# Metodo per caricare premere il pulsante di carica articolo sulla pagina vendita e che verifica se è stato caricato se
def click_carica_articolo_pagina_vendita(driver):
    humanizer(0)
    elemento = driver.find_element(By.CSS_SELECTOR, "button[data-test-id='upload-form-save-button']")
    offset_move_and_click_like_human(driver, elemento)
    humanizer(0)


# Metodo per selezionare la dimensione del pacco di destinazione
# dimensione = {1, 2, 3} una delle precedenti, 3 è il più grande
def seleziona_dimensione_pacco_articolo_pagina_vendita(driver, dimensione):
    id_dimensione = f"package-size-{str(dimensione)}"
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
# cosa_cercare = esempio "size", "category"...
# text_oggetto = Xl, L sono le taglie che abbiamo inserito
def seleziona_opzione_drop_menu_articolo_pagina_vendita(driver, cosa_cercare, text_oggetto):
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
    except Exception as e:
        print(e)


# Metodo DRY (Don't Repeat Yourself) per spostarso come un umano su un elemento web passato e cliccarci sopra con un delay
# tra le azioni
def move_and_click_like_human(driver, elemento):
    small_humanizer()
    azione = ActionChains(driver)
    azione.pause(small_humanizer())
    azione.move_to_element(elemento)
    azione.pause(humanizer(0))
    azione.click(elemento)
    azione.pause(small_humanizer())
    azione.perform()
    small_humanizer()


# Metodo per performare un click su un oggetto web passato per parametro
def performa_click(driver, oggetto):
    small_humanizer()
    azione = ActionChains(driver).move_to_element(oggetto)
    azione.pause(humanizer(0))
    azione.click()
    azione.pause(humanizer(0))
    azione.perform()
    small_humanizer()


# Metodo per spostarsi su un elemento con un piccolo offset e cliccarlo
def offset_move_and_click_like_human(driver, elemento):
    small_humanizer()
    azione = ActionChains(driver)
    azione.pause(small_humanizer())
    azione.move_to_element_with_offset(elemento, random.randint(-5, 5), random.randint(-5, 5))
    azione.pause(small_humanizer())
    azione.click(elemento)
    azione.pause(small_humanizer())
    azione.perform()
    small_humanizer()


# TODO finire
# Metodo per spostarsi sul centro di un elemento con un piccolo offset e cliccarlo a sinistra e destra, sotto e sopra
def offset_move_and_click_like_human_v2(driver, elemento, x_offset, y_offset):
    small_humanizer()
    azione = ActionChains(driver)
    azione.pause(small_humanizer())
    azione.move_to_element_with_offset(elemento, random.randint(-x_offset / 2, x_offset / 2),
                                       random.randint(-y_offset / 2, y_offset / 2))
    azione.pause(small_humanizer())
    azione.click(elemento)
    azione.pause(small_humanizer())
    azione.perform()
    small_humanizer()


# Questo metodo serve per DRY (Don't Repeat Yourself)
# cosa_cercare = "category", "size", "material"
def selettore_elementi_multipli_pagina_di_vendita(driver, cosa_cercare):
    elemento = driver.find_element(By.ID, cosa_cercare)
    elementi_trovati = elemento.find_elements(By.CSS_SELECTOR,
                                              "li.web_ui__Item__item.web_ui__Item__with-divider")
    return elementi_trovati


# TODO - testare con aggancio dinamico alla pagina
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


# TODO verificare se è case-sensitive, testare con aggancio dinamico alla pagina
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
def seleziona_opzione_drop_menu_consigliata_articolo_pagina_vendita(driver, id_opzione_input, css_opzioni_suggerite):
    elemento = driver.find_element(By.ID, id_opzione_input)
    genitore_elemento = elemento.find_element_by_xpath('..')
    performa_click(driver, genitore_elemento)
    # qui troviamo le cose suggerite quando apriamo il menu delle opzioni
    opzioni_suggerite = genitore_elemento.find_element(By.CSS_SELECTOR, css_opzioni_suggerite)
    button_opzione = opzioni_suggerite.find_element(By.CLASS_NAME, "web_ui__Radio__button")
    performa_click(opzioni_suggerite, button_opzione)


# TODO da testare, importantissimo per il rinnnovo che il codice sia presente in modo e formato corretto, testare con aggancio del driver alla pagina aperta
# Metodo per caricare la descrizione e il codice del articolo
def carica_descrizione_pagina_vendita(driver, dati_articolo):
    elemento = driver.find_element(By.ID, "description")
    performa_click(driver, elemento)
    humanizer(0)
    send_delayed_keys(elemento, dati_articolo["descrizione"] + " " + dati_articolo["codice_alfanumerico"])
    humanizer(1)


# Metodo per selezionare il prezzo di vendita dell'articolo nella pagina di vendita nuovo articolo del sito
def seleziona_prezzo_di_vendita_nuovo_articolo(driver, prezzo):
    elemento = driver.find_element(By.ID, "price")
    performa_click(driver, elemento)
    humanizer(0)
    elemento.send_keys(prezzo)
    humanizer(1)


# Metodo per caricare il titolo del articolo passato nella pagina di vendita
def carica_titolo_pagina_vendita(driver, titolo):
    elemento = driver.find_element(By.ID, "title")
    send_delayed_keys(elemento, titolo)
    humanizer(1)


# Metodo per selezionare la categoria consigliata da vinted per il nostro articolo solo se nella categoria nel campo text
# è presente la parola uomo
def seleziona_categoria_standard_pagina_vendita(driver):
    elemento = driver.find_element(By.ID, "category")
    genitore_elemento = elemento.find_element(By.XPATH, '..')
    performa_click(driver, genitore_elemento)
    opzioni_suggerite = genitore_elemento.find_elements(By.XPATH, '//*[starts-with(@id, "catalog-suggestion-")]')
    # opzioni_suggerite = driver.find_element(By.CSS_SELECTOR, '[id^="catalog-suggestion-"]') alterativa a quello sopra
    opzione_suggerita_trovata = None
    for opzione in opzioni_suggerite:
        testo = opzione.text
        if "Uomo" in testo:
            opzione_suggerita_trovata = opzione
    button_opzione = opzione_suggerita_trovata.find_element(By.CLASS_NAME, "web_ui__Radio__button")
    performa_click(driver, button_opzione)


# Metodo per caricare le foto nella finestra della pagina vendi articolo, si passa il driver e il path delle foto da caricare
def carica_foto_pagina_vendita(elemento_photos, path_foto):
    # Lista completa delle immagini
    file_list = [
        os.path.join(path_foto, f)
        for f in os.listdir(path_foto)
        if os.path.isfile(os.path.join(path_foto, f))
    ]
    if not file_list:
        raise ValueError("Nessun file trovato in " + path_foto)
    # input_file = elemento_photos.find_element(By.CSS_SELECTOR, 'input[data-testid="add-photos-input"]')
    files_to_upload = r"\n".join(file_list)
    elemento_photos.send_keys(files_to_upload)
    attesa_caricamento_elemento(elemento_photos, 10, By.CLASS_NAME, "photo-box")
    """
    pyautogui.write(r"C:\path\to\foto1.jpg")
pyautogui.press('enter')
time.sleep(1)
button.click()
pyautogui.write(r"C:\path\to\foto2.jpg")
pyautogui.press('enter')


oppure     
    pyautogui.write(r'"C:\path\to\foto1.jpg" "C:\path\to\foto2.jpg"')
pyautogui.press('enter')

    
    
    """


# Metodo per aprire la pagina per caricare l'articolo di vendita, perchè funzioni correttamente questo metodo deve
# essere chiamato da un luogo in cui è presente la foto del profilo e il tasto di vendi subito
def apertura_pagina_vendita(driver):
    humanizer(0)
    immagine_profilo = driver.find_element(By.ID, "user-menu-button")
    azione = ActionChains(driver)
    azione.move_to_element_with_offset(immagine_profilo, 50 + random.randint(0, 60), random.randint(0, 10))
    azione.pause(medium_random())
    azione.click()
    azione.pause(medium_random())
    azione.perform()
    humanizer(5)
    # routine di fallback
    try:
        attesa_caricamento_elemento(driver, 5, By.ID, "photos")
    except NoSuchElementException:
        humanizer(0)
        driver.get("https://www.vinted.it/items/new")
        humanizer(0)


# serve per accendere il browser, metterlo a schermo intero e andare a un sito web passato per parametro
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
def attesa_caricamento_elemento(driver, tempo, tipo_elemento, nome_elemento):
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
        send_delayed_keys(email_element, config.my_email)
        humanizer(0)
        password_element = driver.find_element(By.ID, "password")
        password_element.clear()
        send_delayed_keys(password_element, config.my_password)
        humanizer(0)
        button = driver.find_element(By.XPATH, "//button[.//span[text()='Continua']]")
        azione = ActionChains(driver)
        azione.move_to_element(button)
        humanizer(0)
        humanizer(0)
        azione.click(button)
        azione.perform()
        time.sleep(5)
        save_cookies(config, driver)
    except Exception:
        attesa_caricamento_elemento(driver, 2, By.ID, "user-menu-button")


# Metodo per salvare i cookies del utente, è stato utiulizzato solo una volta perchè abbiamo già i cookie,
# TODO sarebbe da implementare un controllo per vedere se abbiamo il file cookies.pkl e se non lo abbiamo lo creiamo con questo metodo
def save_cookies(config, driver):
    cookies = driver.get_cookies()
    pickle.dump(cookies, open("cookies.pkl", "wb"))
    driver.get(config.sito_vinted)


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
    try:
        elemento = driver.find_element(By.ID, "user-menu-button")
        move_and_click_like_human(elemento, link)
    except Exception:
        carica_link(driver, link)
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


# Metodo che itera gli articoli presenti nella pagina profilo del sito
def iterazione_articoli_profilo_online(config, driver):
    scrolla_fondo_pagina_versione_2(driver)
    humanizer(0)
    elemento = driver.find_element(By.ID, "tabs")
    genitore = elemento.find_element(By.XPATH, "..")
    articoli = genitore.find_elements(By.CSS_SELECTOR, "[data-testid='grid-item']")
    array_link_articoli = recupera_link_articoli_versione_2(config, articoli)
    try:
        for link in array_link_articoli:
            humanizer(0)
            gestisci_stato_articolo(config, driver, link)
            humanizer(0)
    except Exception as e:
        print(e)


@DeprecationWarning
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


# TESTED
# Metodo per recuperare tutti i link degli articoli passati come array di webElements e che li ritorna come array di str
def recupera_link_articoli_versione_2(config, articoli):
    array_link_articoli = []
    for item in articoli:
        try:
            link_element = item.find_element(By.CSS_SELECTOR, "a[data-testid$='--overlay-link']")
            href = link_element.get_attribute("href")
            link = config.sito_vinted.join(href)
            array_link_articoli.append(link)
        except NoSuchElementException as e:
            print(e)  # se non c'è un link, ignora
    return array_link_articoli


@DeprecationWarning
# Metodo per scrollare la lista degli articoli fino in fondo
def scrolla_fondo_pagina(driver, numero_articoli):
    humanizer(0)
    volte = int(numero_articoli / 5)
    quanto_y = 450 + int(random.uniform(51, 120))
    volte += 5  # per sicurezza scrolliamo fino in fondo
    azione = ActionChains(driver)
    for i in range(volte):
        azione.scroll_by_amount(0, quanto_y)
        azione.pause(small_humanizer())
        azione.perform()
    humanizer(0)


# TODO correggere offset click like human


# Tested
# Metodo per scrollare la lista degli articoli fino in fondo
def scrolla_fondo_pagina_versione_2(driver):
    small_humanizer()
    position_before = 0
    azione = ActionChains(driver)
    while True:
        quanto_y = 450 + int(random.uniform(51, 120))
        azione.pause(small_humanizer())
        azione.scroll_by_amount(0, quanto_y)
        azione.perform()
        position_now = driver.execute_script("return window.pageYOffset + window.innerHeight")
        if position_now == position_before:
            small_humanizer()
            return True
        else:
            position_before = position_now


# Questo metodo serve per aprire il link del articolo passato, controllare se è da eliminare, gestire database locale,
# eliminarlo online come ultima fase
def gestisci_stato_articolo(config, driver, link_articolo):
    small_humanizer()
    driver.get(link_articolo)  # Apre l'articolo nella schermata
    attesa_caricamento_elemento(driver, 10, By.ID, "sidebar")
    esito_di_cancellazione = controllo_eliminazione_articolo(driver)
    codice_articolo = recupera_codice_alfanumerico(driver)
    if esito_di_cancellazione:
        humanizer(0)
        cancella_articolo_online(driver)
        Database.update_stato_articolo_to_offline(config, codice_articolo)


# Metodo per cambiare identificativo del album in modo da caricare le foto diverse del articolo
def cambia_album_nel_codice(codice):
    codice_esaminato = codice
    if codice_esaminato[0] == 'a':
        codice_esaminato = codice_esaminato.replace('a', 'b')
    elif codice_esaminato[0] == 'b':
        codice_esaminato = codice_esaminato.replace('b', 'a')
    return codice_esaminato


# Metodo per cambiare nome del album da in uso all'interno del database, si passa iol path ai articoli, da ricaricare o caricati
# path_ai_articoli = path ai articoli da caricare o caricati
# codice_alfanumerico = vecchio codice alfanumerico del articolo
def cambia_album_nel_database(path_ai_articoli, codice_alfanumerico):
    try:
        nuovo_codice_alfanumerico = cambia_album_nel_codice(codice_alfanumerico)
        path_parziale = pathlib.Path(path_ai_articoli.joinpath(codice_alfanumerico[1:]).joinpath("foto"))
        path = path_parziale.joinpath(f"is_{codice_alfanumerico[0]}")
        path.rename(path_parziale.joinpath(f"is_{nuovo_codice_alfanumerico[0]}"))
    except Exception as e:
        print(e)


# Metodo per recuperare lo stato dell'articolo online e salvarlo nella sua cartella offline per un eventuale rinnovo futuro
def salva_info_articolo_off(driver, codice_articolo):
    # articolo = ArticoloVin()
    attributi_da_settare = []
    # titolo - ok class - driver.find_elements(By.XPATH,"//*[@class='web_ui__Text__text web_ui__Text__title web_ui__Text__left']")
    # setattr(articolo, "")
    # breadcrumb = driver.find_element(By.CSS_SELECTOR, ".breadcrumbs.breadcrumbs--truncated")


# Metodo per recuperare la sidebar dal profilo personale
def recupera_sidebar_da_pagina_profilo(driver):
    sidebar = driver.find_element(By.ID, "sidebar")
    return sidebar


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


# testato
# Metodo per controllare la data del articolo e vedere se dobbiamo eliminarlo oppure no
# return True se è da eliminare
def controllo_eliminazione_articolo(driver):
    caricato_span = WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.ID, "sidebar")))
    label = caricato_span.find_element(By.XPATH, ".//span[normalize-space(text())='Caricato']")
    tempo_element = label.find_element(By.XPATH, "../../div/span[contains(@class,'web_ui__Text__bold')]")
    tempo = tempo_element.text.strip()
    eta_articolo = ore_trascorse_formato_vinted(tempo)
    if eta_articolo > 72:
        return True
    else:
        return False


# Metodo per convertire il formato del sito web in ore trascorse passando il formato in stringa
def ore_trascorse_formato_vinted(testo: str) -> float:
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
    """
    #ritorno alla scheda principale\
    driver.close()
    driver.switch_to.window(driver.window_handles[0])
    driver.refresh()
    """


# Metodo per controllare gli articoli
def articolo_data_scaduta(driver):
    codice_articolo = recupera_codice_alfanumerico(driver)
    scadenza_articolo_database(config, codice_articolo)
    pass


# Metodo per cancellare il prodotto nella sua pagina, la cancellazione riporta alla lista dei prodotti
def cancella_articolo_online(driver):
    try:
        humanizer(0)
        attesa_caricamento_elemento(driver, 5, By.XPATH, "//button[.//span[text()='Cancella']]")
        button = driver.find_element(By.XPATH, "//button[.//span[text()='Cancella']]")
        offset_move_and_click_like_human(driver, button)
        attesa_caricamento_elemento(driver, 5, By.XPATH, "//button[.//span[text()='Conferma e cancella']]")
        button = driver.find_element(By.XPATH, "//button[.//span[text()='Conferma e cancella']]")
        offset_move_and_click_like_human(driver, button)
    except Exception:
        return Exception


# Passed
# TODO ma si comporta in modo strano alcune volte ha fallito senza cambiare nulla, non caricava il codice del
# del articolo anche se era presente nell html di prova
# Recupera codice alfanumerico dal articolo il codice può avere una "a" o "b" d'avanti al numero del articolo e indica
# quale album di fotografie è stato utilizzato
def recupera_codice_alfanumerico(driver):
    sidebar = recupera_sidebar_da_pagina_profilo(driver)
    desc_element = sidebar.find_element(
        By.CSS_SELECTOR,
        ".web_ui__Text__text.web_ui__Text__body.web_ui__Text__left.web_ui__Text__format span"
    )
    # elemento = sidebar.find_element(By.CSS_SELECTOR, ".nome-classe span")
    desc_text = desc_element.text
    # Cerca il codice alfanumerico tipo 'a1921242' o 'b4321'
    match = re.search(r'\b[ab]\d{1,7}\b', desc_text)
    # Recupera il codice trovato
    if match is not None:
        codice = match.group(0)
        return codice
    else:
        return 0


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
def scadenza_articolo_database(config, codice):
    path_partenza = pathlib.Path(config.path_caricati, codice[1:])
    path_destinazione = pathlib.Path(config.path_da_caricare, codice[1:])
    cambia_album_nel_database(path_partenza, codice)
    Database_locale.sposta_dir_articolo(path_partenza, path_destinazione)


# Metodo che sposta la cartella del prodotto tramite il nome/codice del articolo, la cartella avrà come nome il codice del articolo
def rinnovo_articolo_database(config, codice):
    path_partenza = pathlib.Path(config.path_da_caricare, codice[1:])
    path_destinazione = pathlib.Path(config.path_caricati, codice[1:])
    Database_locale.sposta_dir_articolo(path_partenza, path_destinazione)


def diagnosi():
    opts = Options()
    opts.add_argument("--start-maximized")
    opts.add_argument("--headless=new")  # NON usare headless per debugging
    # service = Service("/path/to/chromedriver")
    # driver = webdriver.Chrome(service=service, options=opts)
    driver = uc.Chrome(options=opts)

    url = config.sito_vinted
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
