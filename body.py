import pickle

import undetected_chromedriver as uc
import random

from selenium import webdriver
from selenium.common import NoSuchElementException, TimeoutException
from selenium.webdriver import ActionChains, Keys
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
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
    except Exception: pass


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
    #controlla_data_articolo()
    #gestione_database_locale()
    #cancella_articolo(driver)
    pass


#Metodo per controllare la data del articolo e vedere se dobbiamo eliminarlo oppure no
def controlla_data_articolo():
    pass

#Metodo per gestire gli articoli salvati in locale e farli cambiare di categoria visto che vengono eliminati ad esempio
def gestione_database_locale():
    pass

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




#Metodo per spostare gli articoli nelle cartelle del pc
def sposta_articolo():
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
        sposta_articolo()
    except Exception: return Exception

#Metodo per spostarsi su un oggetto e cliccarlo, bisogna passare il nome del oggetto per argomento
def performa_click(driver, oggetto):
    humanizer(0)
    azione = ActionChains(driver).move_to_element(oggetto)
    azione.pause(humanizer(0))
    azione.click()
    azione.pause(humanizer(0))
    azione.perform()
    humanizer(0)



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
