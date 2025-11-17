import json
import pathlib

import config


# Metodo per aprire un json
# Ora 'data' è un dizionario o una lista Python (a seconda del JSON)
def read_json(file_path):
    with open(file_path, "r", encoding="utf-8") as file:
        data = json.load(file)
        return data


def update_json(file_path, dati):
    with open(file_path, "w", encoding="utf-8") as f:
        json.dump(dati, f, indent=4)


# Metodo che sposta la cartella del prodotto tramite il nome/codice del articolo, la cartella avrà come nome il codice del articolo
def update_articolo_database(path_articolo, nuovo_json):
    update_json(path_articolo, nuovo_json)


# Metodo per spostare una cartella di un articolo da un path all'altro
def sposta_dir_articolo(old_file_path, new_file_path):
    old_file_path.rename(new_file_path)


# Metodo per recuperare i dati di un articolo dal database locale
def read_articolo_database(path_articolo):
    return read_json(path_articolo)


# Metodo che recupera i nomi(codici) delle cartelle degli articoli,
def recupera_codici_articoli_da_inserire():
    codici_articoli_da_caricare = [item.name for item in config.path_articoli.iterdir() if item.is_dir()]
    return codici_articoli_da_caricare


def update_stato_articolo_to_offline(codice):
    json_articolo = read_json(config.path_articoli.joinpath(codice).joinpath("articolo.json"))
    json_articolo["stato"] = "offline"


def update_stato_articolo_to_online(codice):
    path_articolo = config.path_articoli.joinpath(codice).joinpath("articolo.json")
    json_articolo = read_json(path_articolo)
    json_articolo["stato"] = "online"
    update_articolo_database(path_articolo, json_articolo)

"""
import json

# 1️⃣ Apri il file in modalità lettura
with open("dati.text", "r", encoding="utf-8") as file:
    # 2️⃣ Carica il contenuto JSON in un oggetto Python
    data = json.load(file)

# 3️⃣ Ora 'data' è un dizionario o una lista Python (a seconda del JSON)
print("Contenuto JSON:", data)

# 4️⃣ Esempi di metodi utili
# - accedere a un elemento
if isinstance(data, dict):
    print("Chiavi disponibili:", list(data.keys()))
    print("Valore di 'nome' se esiste:", data.get("nome"))

# - iterare su una lista se il JSON è una lista di oggetti
if isinstance(data, list):
    for i, item in enumerate(data):
        print(f"Elemento {i}:", item)

# 5️⃣ Salvare modifiche in un altro file JSON
data["nuova_chiave"] = "valore"
with open("dati_modificati.text", "w", encoding="utf-8") as f:
    json.dump(data, f, indent=4)  # indent=4 per formattazione leggibile





| Metodo                             | Descrizione                                                                         |
| ---------------------------------- | ----------------------------------------------------------------------------------- |
| `data.get("nome")`                 | Restituisce il valore della chiave `"nome"`. Non da errore se la chiave non esiste. |
| `data.keys()`                      | Lista (vista) di tutte le chiavi del dizionario                                     |
| `data.values()`                    | Lista (vista) di tutti i valori                                                     |
| `data.items()`                     | Lista di tuple `(chiave, valore)`                                                   |
| `data.pop("nome")`                 | Rimuove la chiave `"nome"` e ne restituisce il valore                               |
| `data.update({"cognome": "Urso"})` | Aggiunge o aggiorna chiavi/valori                                                   |
| `"nome" in data`                   | Controlla se esiste la chiave `"nome"`                                              |
| `data.clear()`                     | Pulisce tutto il dizionario                                                         |



"""
