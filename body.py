import pathlib
import pickle
import re

import undetected_chromedriver as uc
import random
from dateutil.relativedelta import relativedelta
import yaml
from datetime import datetime, timedelta
from selenium import webdriver
from selenium.common import NoSuchElementException, TimeoutException
from selenium.webdriver import ActionChains, Keys
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time

import Database_locale

#-----------------------------------------------------------------------------------------------------------------------
#TODO check versioni chromedriver e chrome

#TODO aggiungere tempi di attesa per rendere il programma random

#TODO implementareaction chains

#TODO offset dei click

#TODO evitare sempre la stessa sequenza di azioni

#TODO SI potrebbero utilizzare le librerie (PyAutoGUI, pynput) per simulare lo spostamento del mouse, purtroppo
# queste librerie interagiscono con il sistema operativo e non con il web browser quindi bisognerebbe calcolare gli offset manualmente
# Queste sono le coordinate della finestra del browser angolo sx-up-(x=0 ,y=139) e dx-down-(x=1904, y=1031) quindi y invertita oppure
# si potrebbe implementare semplicemente il movimento del mouse per simulare un movimento semplice

#TODO aggiungere repository remote

#TODO ricorda che CLASS_NAME non possono avere spazi nei nomi perciò non si lavora cosi, So if you have spaces in your class attribute, switch to CSS_SELECTOR or XPATH

#TODO il caricamento di un nuovo articolo va fatto con due album di foto diverse in modo che vinted non si accorge che sono le stesse foto???

#TODO Fare un metodo per verificare se gli href cambiano nel tempo su vinted se no, si potrebbe salvare a priori il link del
# articolo e andare direttamente al link per eliminarlo senza fare la verifica online ma in locale dellla data di caricamento vistop che la si può salvare durante il caricamento

import pickle


@DeprecationWarning
def per_ora_non_serve():
    class ArticoloVin:
        def __init__(self, name):
            self.name = name

    # Create an instance
    my_object = ArticoloVin('Example')

    # Save the instance to a file
    with open('class_info.pkl', 'wb') as f:
        pickle.dump(my_object, f)


    #load the instance from the file
    def leggi_articolo(path_articolo):
        with open(path_articolo, 'rb') as f:
            loaded_object = pickle.load(f)
            return loaded_object  # Output: Example






#variabili globali
my_email = "leonardovinted95@gmail.com"
my_password = "3gigio3leo*"
driver_name = "chromedriver.exe"
sito_vinted = "https://www.vinted.it/"


#QUESTO é IL METODO PRINCIPALE DELLA CLASSE
def processo():
    try:
        driver = start_browser(sito_vinted)
        accetta_consensi_cookie(driver)
        carica_pagina_login(driver)
        load_cookies(driver)
        login(driver)
        recati_al_profilo(driver, "https://www.vinted.it/member/168504727")
        clicca_articoli_attivi(driver)
        classe_numero_articoli = "u-flexbox u-justify-content-between u-align-items-center u-flex-grow u-flex-wrap"
        numero_articoli = conteggio_articoli_profilo(driver, classe_numero_articoli) #TODO controllo del numero
        iterazione_controllo_articoli(driver, numero_articoli)
        print("Resoconto: SUCCESSO")
        time.sleep(20)
    except Exception: print("Resoconto: ERRORE")
    print( "- - - Software Terminato - - -")

#serve per accendere il browser, metterlo a schermo intero e andare ad un sito web passato per parametro
def start_browser(sito_web):
    options = webdriver.ChromeOptions()
    options.add_argument(r'--user-data-dir=C:\Users\Leon\AppData\Local\Google\Chrome\User Data\Default')
    driver = uc.Chrome(options=options)
    driver.get(sito_web)
    humanizer(3)
    driver.maximize_window()
    return driver

#Metodo per gestire le scelte dei cookie
def accetta_consensi_cookie(driver):
    gestisci_cookie_button_id = "onetrust-pc-btn-handler"
    finestra_conferma_cookie = "onetrust-pc-sdk"
    conferma_scelte_button_class = ".save-preference-btn-handler.onetrust-close-btn-handler"
    try:
        humanizer(0)
        attesa_caricamento_elemento(driver, 5, By.ID, gestisci_cookie_button_id)  #click su gestisci cookie
        elemento_cookie = driver.find_element(By.ID, gestisci_cookie_button_id)
        elemento_cookie.click()
        humanizer(0)
        attesa_caricamento_elemento(driver, 5, By.ID, finestra_conferma_cookie)  #click su conferma le mie scelte
        elemento_cookie = driver.find_element(By.CSS_SELECTOR, conferma_scelte_button_class)
        elemento_cookie.click()
        humanizer(-0.5)
    except Exception:
        pass


#Metodo per attendere il caricamento della pagina in caso un elemento ancora non è stato caricato
#integer tempo = secondi dopo di cui lanciare un eccezione NoSuchElementException
#string elemento = elemento da attendere nella pagina di caricamento
def attesa_caricamento_elemento(driver, tempo, tipo_elemento, nome_elemento, ):
    WebDriverWait(driver, tempo).until(EC.presence_of_element_located((tipo_elemento, nome_elemento)))


#metodo che non fa nulla per un determinato numero di secondi e rotorna il valore
def humanizer(offset):
    ran = random.uniform(0.9 + offset, 1.8 + offset)
    time.sleep(ran)
    return ran


#Metodo per attendere il tempo tra la premuta di un tasto e l'altro
def typing_humanizer():
    humanizer(0)
    ran = random.uniform(0.166, 0.254)
    time.sleep(ran)
    humanizer(0)
    return ran


#Questo metodo serve per accedere alla pagina del login
def carica_pagina_login(driver):
    nome_classe = ".web_ui__Button__button.web_ui__Button__outlined.web_ui__Button__small.web_ui__Button__primary.web_ui__Button__truncated"
    try:
        attesa_caricamento_elemento(driver, 5, By.CSS_SELECTOR, nome_classe)
        elemento_accedi = driver.find_element(By.CSS_SELECTOR, nome_classe)
    except (NoSuchElementException, TimeoutException) as e:
        return
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


#serve per accedere al account specificato dalla finestra che appare dopo aver cliccato di accedere tramite email
def login(driver):
    try:
        attesa_caricamento_elemento(driver, 2,By.ID, "username")
        email_element = driver.find_element(By.ID, "username")
        email_element.clear()
        send_delayed_keys(email_element, my_email)
        humanizer(0)
        password_element = driver.find_element(By.ID, "password")
        password_element.clear()
        send_delayed_keys(password_element, my_password)
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
    except Exception: humanizer(5) #TODO cambiare con attesa_caricamento_elemento

#Metodo per salvare i cookies del utente, è stato utiulizzato solo una volta perchè abbiamo già i cookie,
#TODO sarebbe da implementare un controllo per vedere se abbiamo il file cookies.pkl e se non lo abbiamo lo creiamo con questo metodo
def save_cookies(driver):
    cookies =driver.get_cookies()
    pickle.dump(cookies, open("cookies.pkl", "wb"))
    driver.get(sito_vinted)

#Metodo per cariacare i cookie nel browser
def load_cookies(driver):
    cookies = pickle.load(open("cookies.pkl", "rb"))
    for cookie in cookies:
        cookie["domain"] = ".vinted.it"
        try:
            driver.add_cookie(cookie)
            driver.refresh()
        except Exception: pass

#Metodo per fare ingresso di caratteri con un delay umano
def send_delayed_keys(input_element, text_to_input):
    for character in text_to_input:
        input_element.send_keys(character)
        typing_humanizer()


#metodo per recarsi profilo del sito
def recati_al_profilo(driver,link ):
    #nome = "user-menu-button"
    #oggetto = driver.find_element(By.ID, nome)
    #performa_click(driver,oggetto)
    humanizer(0)
    carica_link(driver, link) #TODO da modificare e mettere un action chains invece di carica_link
    humanizer(0)

#Metodo per cliccare gli oggetti attivi del profilo utente
def clicca_articoli_attivi(driver):
    humanizer(0)
    button = driver.find_element(By.XPATH, "//span[text()='Attivi']")
    performa_click(driver,button)
    humanizer(0)

#metodo per caricare un sito web
def carica_link(driver, link_destinazione):
    driver.get(link_destinazione)

def conteggio_articoli_profilo(driver, classe):
    nome_elemento = "h2.web_ui__Text__title"
    attesa_caricamento_elemento(driver, 5, By.CSS_SELECTOR, nome_elemento)
    element = WebDriverWait(driver, 10).until(
        EC.visibility_of_element_located((
            By.XPATH,
            "//div[@class='web_ui__Container__container']//h2[contains(., 'articoli')]"
        ))
    )
    text = element.text.strip()
    numero = int(''.join(filter(str.isdigit, text)))
    return numero



#Metodo per Iterare gli articoli, controllare le date e fare tutto quello che serve per caricare o scaricare gli oggetti
#numero= oggetti da iterare
def iterazione_controllo_articoli(driver, numero_articoli):
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
            #gestione_articolo(driver, array_link_articoli[contatore])#TODO riguardare logic
            humanizer(0)
    except Exception:
        pass


#Metodo per recuperare tutti i link degli articoli passati come array di webElements e che li ritorna come array di str
def recupera_link_articoli(articoli, numero_articoli):
    contatore = numero_articoli
    array_link_articoli = []
    try:
        while contatore >=0:
            href_articolo = articoli[contatore].get_attribute("href")
            array_link_articoli.append(href_articolo)
            contatore -= 1
    except Exception:
        return array_link_articoli
    return array_link_articoli

#TODO - Warning - questo metodo potrebbe non scrollare fino in fondo
#Metodo per scrollare la lista degli articoli fino in fondo
def scroll(driver, numero_articoli):
    humanizer(0)
    volte = int(numero_articoli/5)
    quanto_y = 450 + int(random.uniform(51, 120 ))
    volte += 5 # per sicurezza scrolliamo fino in fondo
    azione = ActionChains(driver)
    for i in range(volte):
        azione.scroll_by_amount(0, quanto_y)
        azione.perform()
        humanizer(-0.5)
    humanizer(0)

#Questo metodo serve per aprire il link del articolo passato, controllare se è da eliminare, gestire database locale,
#eliminarlo come ultima fase
def gestione_articolo(driver, link_articolo):
    humanizer(0)
    driver.get(link_articolo)
    time.sleep(2)
    humanizer(0)
    esito_da_cancellare = controllo_eliminazione_articolo(driver)
    #passo esito booleano e se True apportare le modifiche
    if esito_da_cancellare:
        #cancella_articolo(esito_da_cancellare)
        pass
    else: driver.back()


#Metodo che va indietro alla pagina precedente in base al esito della verifica della data, se non è scaduta si va indietro alla lista degli articoli
def indietro_pagina(driver, esito_da_cancellare):
    if esito_da_cancellare: return
    else: driver.back()

#Metodo per controllare la data del articolo e vedere se dobbiamo eliminarlo oppure no
#return True se è da eliminare
def controllo_eliminazione_articolo(driver):
    caricato_span = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.XPATH, "//span[normalize-space(text())='Caricato']")))
    upload_date_elem = caricato_span.find_element(By.XPATH, "../../div[@itemprop='upload_date']/span")
    upload_date = upload_date_elem.text
    eta_articolo = ore_trascorse(upload_date)
    if eta_articolo > 72: return True
    else: return False



#Metodo per convertire il formato del sito web in ore trascorse passando il formato in stringa
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


#Metodo per controllare la data del articolo e controllare se cancellarlo e rimetterlo
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
    if articolo_data_scaduta(driver): cancella_articolo(driver)
    humanizer(0)
    #ritorno alla scheda principale\
    driver.close()
    driver.switch_to.window(driver.window_handles[0])
    driver.refresh()


#Metodo per controllare gli articoli
def articolo_data_scaduta(driver):
    pass


def cancella_articolo(driver):
    try:
        humanizer(0)
        attesa_caricamento_elemento(driver, 5, By.XPATH, "//button[.//span[text()='Cancella']]")
        button = driver.find_element(By.XPATH, "//button[.//span[text()='Cancella']]")
        azione = ActionChains(driver)
        azione.move_to_element(button)
        humanizer(0)
        azione.perform()
        humanizer(0)
        attesa_caricamento_elemento(driver, 5, By.XPATH, "//button[.//span[text()='Conferma e cancella']]")
        button = driver.find_element(By.XPATH, "//button[.//span[text()='Conferma e cancella']]")
        humanizer(0)
        azione.move_to_element(button)
        humanizer(0)
        azione.perform()
        humanizer(0)
        azione.perform()
        #recupera_codice
        #sposta_articolo(codice)
    except Exception: return Exception



#Metodo per spostare gli articoli nel database locale da articoli_online ad articoli_non_caricato
def sposta_articolo(codice):
    Database_locale.sposta_dir_articolo(codice)

#Recupera codice alfanumerico dal articolo il codice può avere una "a" o "b" d'avanti al numero del articolo e indica
#quale album di fotografie è stato utilizzato
def recupera_codice_alfanumerico(driver):
    desc_element = driver.find_element(
        By.CSS_SELECTOR,
        "span.web_ui__Text__text.web_ui__Text__body.web_ui__Text__left.web_ui__Text__format"
    )
    desc_text = desc_element.text
    #Cerca il codice alfanumerico tipo 'a1921242' o 'b4321'
    match = re.search(r'\b[ab]\d{1,7}\b', desc_text)
    #Recupera il codice trovato
    if match:
        codice = match.group(0)
        return codice
    else:
        return 0


#Metodo per reuperare il codice del articolo tramite combinazione di hashtag
def recupera_codice_hashtag(driver):
    # #Vinteditalia #Secondamano #Modasostenibile #Vestiti #Moda #Vintage #Mango #Accessori #Italia #Italy
    span_element = driver.find_element(By.CSS_SELECTOR, ".web_ui__Text__text.web_ui__Text__body.web_ui__Text__left.web_ui__Text__format")

    hashtags_elements = driver.find_elements(By.XPATH, "//span//a[starts-with(@href, '/catalog?search_text=%23')]")
    all_hashtags = [a.text for a in hashtags_elements]
    first_6_hashtags = all_hashtags[:6]




#Metodo per spostarsi su un oggetto e cliccarlo, bisogna passare il nome del oggetto per argomento
def performa_click(driver, oggetto):
    humanizer(0)
    azione = ActionChains(driver).move_to_element(oggetto)
    azione.pause(humanizer(0))
    azione.click()
    azione.pause(humanizer(0))
    azione.perform()
    humanizer(0)

#TODO questo codice funzionerà solo su questo pc non su altri perchè la gestione dei path non è corretta bisogna
# cambiare alla fine dello sviluppo la gestione dei path e farlo relativo alla cartella dove gira il programma
#Metodo che sposta la cartella del prodotto tramit il nome/codice del articolo, la cartella avrà come nome il codice del articolo
def scadenza_articolo(codice):
    old_path = r"C:\Users\Leon\OneDrive - Università Politecnica delle Marche\_Vinted\CARICATI"
    new_path = r"C:\Users\Leon\OneDrive - Università Politecnica delle Marche\_Vinted\DA CARICARE"
    Database_locale.sposta_dir_articolo(pathlib.Path(old_path, codice), pathlib.Path(new_path, codice))

#Metodo che sposta la cartella del prodotto tramit il nome/codice del articolo, la cartella avrà come nome il codice del articolo
def rinnovo_articolo(codice):
    new_path = r"C:\Users\Leon\OneDrive - Università Politecnica delle Marche\_Vinted\CARICATI"
    old_path = r"C:\Users\Leon\OneDrive - Università Politecnica delle Marche\_Vinted\DA CARICARE"
    Database_locale.sposta_dir_articolo(pathlib.Path(old_path, codice), pathlib.Path(new_path, codice))


def diagnosi():
    opts = Options()
    opts.add_argument("--start-maximized")
    opts.add_argument("--headless=new")   # NON usare headless per debugging
    #service = Service("/path/to/chromedriver")
    #driver = webdriver.Chrome(service=service, options=opts)
    driver = uc.Chrome(options=opts)

    url = sito_vinted
    #url =
    driver.get(url)
    time.sleep(2)

    # numero di URL navigati in un intervallo breve
    print("Current URL:", driver.current_url)

    src = driver.page_source.lower()
    print("meta refresh:", "http-equiv=\"refresh\"" in src)
    print("settimeout:", "settimeout" in src)
    print("location.reload:", "location.reload" in src)
    print("iframe:", "<iframe" in src)
    #se true ti riconosce come bot
    print(driver.execute_script(
        "return {webdriver: navigator.webdriver, userAgent: navigator.userAgent, plugins: navigator.plugins.length, language: navigator.language};"))
