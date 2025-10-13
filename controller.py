# Controller del programma
import os

import model
import view
from model import cancella_articolo_online


# Metodo pricipale del controller per avviare il programma:
def avvio_programma_controller():
    """
    print(" 1 : rinnova gli articoli")
    print("  : carica nuovi articoli")
    #print(" 3 : cancella tutti gli articoli")
    #print(" 4 : cancella articolo con codice")
    print(" e : termina il programma")
    """
    view.avvio_programma()

    while True:
        input_utente = view.opzioni_di_avvio()
        if input_utente == "1":
            # model.processo_rinnovo_articoli()
            print("rinnovo degli articoli")
        elif input_utente == "e":
            return view.fine_programma()
        else:
            view.errore_input()
# Metodo per caricare gli articoli gli articoli dal locale al sito web, bisonga seguire una sintassi ben definita,
# schema cartelle
# DA CARICARE/articolo/foto/now a
# DA CARICARE/articolo/foto/a #primo album di foto
# DA CARICARE/articolo/foto/b #secondo album di foto
# DA CARICARE/articolo/titolo/titolo_articolo
# DA CARICARE/articolo/prezzo/prezzo_articolo
# DA CARICARE/articolo/brand/brand_articolo
# DA CARICARE/articolo/taglia/taglia_articolo
# DA CARICARE/articolo/condizioni/condizioni_articolo
# DA CARICARE/articolo/colore/colore_articolo
# DA CARICARE/articolo/descrizione/descrizione.txt
# DA CARICARE/articolo/pacco/pacco.txt
