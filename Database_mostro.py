#Metodi CRUD
#Metodi sposta
import shutil
from pathlib import Path




#Metodo per spostare una cartella di un articolo da un path all'altro
def sposta_dir_articolo(old_file_path, new_file_path):
    old_file_path.rename(new_file_path)


#Metodo per spostare gli articoli da una cartella all'altra
def sposta_articoli_database(sorgente, destinazione):
    destinazione.mkdir(parents=True, exist_ok=True)
    for item in sorgente.iterdir():
        if item.is_dir():
            dest_path = destinazione / item.name
            shutil.move(str(item), str(dest_path))


#Metodo per creare una cartella di articolo e articolo
def create_dir_articolo():
    pass

#Metodo per recuperare l'articolo
def read_dir_articolo():
    pass

#Metodo per aggiornare un articolo con le info nuove
def update_dir_articolo():
    pass

#Metodo per cancellare una cartella di articolo
def delete_dir_articolo():
    pass

