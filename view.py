# View del mio programma
import time
import sys

# Codici colore ANSI
RED = "\033[91m"
RESET = "\033[0m"
BOLD = "\033[1m"


def avvio_programma():
    futuristic_print("program - start")
    head_print()


# Metodo per printare le opzioni di avvio e restituisce l'input immesso nel sistema
def opzioni_di_avvio():
    print("scegli l'opzione da eseguire, premi il numero e invio:")
    print(" 1 : rinnova gli articoli")
    print(" 2 : carica nuovi articoli")
    # print(" 3 : cancella tutti gli articoli")
    # print(" 4 : cancella articolo con codice")
    print(" e : termina il programma")
    print("attesa input:")
    input_utente = str(input())
    return input_utente


def futuristic_print(text, delay=0.05):
    """Stampa lettera per lettera per effetto tipico da terminal futuristico"""
    for char in text:
        sys.stdout.write(RED + char + RESET)
        sys.stdout.flush()
        time.sleep(delay)
    print()  # a capo alla fine


def head_print():
    header = r"""
#     _   _   _           _                _    ______           _   
#    | | | | (_)         | |              | |   | ___ \         | |  
#    | | | |  _   _ __   | |_    ___    __| |   | |_/ /   ___   | |_ 
#    | | | | | | | '_ \  | __|  / _ \  / _` |   | ___ \  / _ \  | __|
#    \ \_/ / | | | | | | | |_  |  __/ | (_| |   | |_/ / | (_) | | |_ 
#     \___/  |_| |_| |_|  \__|  \___|  \__,_|   \____/   \___/   \__|
#                                                                    
    """
    print(RED + BOLD + header + RESET)
    futuristic_print(">>> Tipo programma avviato...", 0.03)
    futuristic_print(">>> Inizializzando moduli...", 0.03)
    futuristic_print(">>> Preparando scraping...", 0.03)
    time.sleep(0.5)
    futuristic_print(">>> Pronto 🚀", 0.03)


# Metodo che viene eseguito alla fine del programma prima della chiusura
def fine_programma():
    print("program - exit")
    return None


def errore_input():
    print(RED + BOLD + "errore input" + RESET)


def stampa_opzioni():
    return opzioni_di_avvio()
