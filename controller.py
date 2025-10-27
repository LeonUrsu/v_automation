# Controller del programma
from _pytest import pathlib
import model
import view




# Metodo principale del controller per avviare il programma:
def avvio_programma_controller():
    while True:
        input_utente =  view.avvio_programma()
        if input_utente == "1": #rinnova gli articoli
            # model.processo_rinnovo_articoli()
            print("opzione non disponibile")
        elif input_utente == "2": #carica nuovi articoli
            #model.processo_carica_articoli_online()
            print("opzione non disponibile")
        elif input_utente == "3": #cancella tutti gli articoli
            print("opzione non disponibile")
        elif input_utente == "4": #cancella articolo con codice
            print("opzione non disponibile")
        elif input_utente == "e":
            return view.fine_programma()
        else:
            view.errore_input()
