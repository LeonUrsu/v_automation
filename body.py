import pickle

import undetected_chromedriver as uc
import random

from selenium import webdriver
from selenium.common import NoSuchElementException, TimeoutException
from selenium.webdriver import ActionChains, Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time

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
#variabili globali
my_email = "leonardovinted95@gmail.com"
my_password = "3gigio3leo*"
driver_name = "chromedriver.exe"


#QUESTO é IL METODO PRINCIPALE DELLA CLASSE
def processo():
    driver = start_browser("https://www.vinted.it/")
    accetta_consensi_cookie(driver)
    carica_pagina_login(driver)
    login(driver)
    save_cookies(driver)
    load_cookies(driver)
    recati_al_profilo(driver, "https://www.vinted.it/member/168504727")
    clicca_articoli_attivi(driver)
    classe_numero_articoli = "u-flexbox u-justify-content-between u-align-items-center u-flex-grow u-flex-wrap"
    numero_articoli = conteggio_articoli_profilo(driver, classe_numero_articoli) #TODO controllo del numero
    #iterazione_controllo_articoli(driver, numero_articoli)


    print("<---------- Software Terminato !!!")
    time.sleep(20)
    #TODO una volta fatti i metodi bisogna sbloccarli
    pass


#serve per accendere il browser, metterlo a schermo intero e andare ad un sito web passato per parametro
def start_browser(sito_web):
    options = webdriver.ChromeOptions()
    options.add_argument(r'--user-data-dir=C:\Users\Leon\AppData\Local\Google\Chrome\User Data\Default')
    driver = uc.Chrome(options=options)
    driver.get(sito_web)
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
    except Exception: humanizer(5) #TODO cambiare con attesa_caricamento_elemento

#Metodo per salvare i cookies del utente, è stato utiulizzato solo una volta perchè abbiamo già i cookie,
#TODO sarebbe da implementare un controllo per vedere se abbiamo il file cookies.pkl e se non lo abbiamo lo creiamo con questo metodo
def save_cookies(driver):
    cookies =driver.get_cookies()
    pickle.dump(cookies, open("cookies.pkl", "wb"))


#Metodo per cariacare i cookie nel browser
def load_cookies(driver):
    cookies = pickle.load(open("cookies.pkl", "rb"))
    for cookie in cookies:
        cookie["domain"] = ".vinted.it"
        try:
            driver.add_cookie(cookie)
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
    articoli = driver.find_elements(By.CSS_SELECTOR,
                                    ".u-position-relative.u-min-height-none.u-flex-auto.new-item-box__image-container")
    contatore = numero_articoli
    # Store the ID of the original window
    original_window = driver.current_window_handle
    while contatore >= 0:
        apertura_articolo(driver, original_window, articoli[contatore])
        contatore -= 1



#Metodo per controllare la data del articolo e controllare se cancellarlo e rimetterlo
def apertura_articolo(driver, original_windows, articolo):
    humanizer(0)
    # apri in una nuova scheda (CTRL + click)
    articolo.send_keys(Keys.CONTROL + Keys.RETURN)  # su Mac usa Keys.COMMAND
    # aspetta un attimo che la scheda si apra
    time.sleep(4)
    # ottieni tutti gli handle (le schede aperte)
    tabs = driver.window_handles
    # passa all'ultima scheda
    driver.switch_to.window(tabs[-1])
    #TODO qui fare il metodo per controllare l'articolo--------
    #ritorno alla scheda principale
    driver.close()
    driver.switch_to.window(driver.window_handles[0])

#Metodo per controllare gli articoli
def controllo_articolo():
    pass



#Metodo per spostarsi su un oggetto e cliccarlo, bisogna passare il nome del oggetto per argomento
def performa_click(driver, oggetto):
    humanizer(0)
    azione = ActionChains(driver).move_to_element(oggetto)
    azione.pause(humanizer(0))
    azione.click()
    azione.pause(humanizer(0))
    azione.perform()
    humanizer(0)

