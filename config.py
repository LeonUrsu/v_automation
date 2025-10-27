# variabili globali----------------------------------------------------------------------------------------
#TODO i valori di setup dovrebbero essere posizionati in un luogo differente non hard-coded
#TODO cambiare nome DA CARICARE in CARICARE
from _pytest import pathlib

my_email = "leonardovinted95@gmail.com"
my_password = "3gigio3leo*"
driver_name = "chromedriver.exe"
sito_vinted = "https://www.vinted.it/"
caricati = "CARICATI"
caricare = "DA CARICARE"
cartella_lavoro_bot = "v_bot_file"
path_caricati = pathlib.Path().cwd().joinpath(cartella_lavoro_bot).joinpath(caricati)
path_da_caricare = pathlib.Path().cwd().joinpath(cartella_lavoro_bot).joinpath(caricare)
