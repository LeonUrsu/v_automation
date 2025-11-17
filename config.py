# variabili globali----------------------------------------------------------------------------------------
#TODO i valori di setup dovrebbero essere posizionati in un luogo differente non hard-coded
#TODO cambiare nome DA CARICARE in CARICARE
from _pytest import pathlib

my_email = "leonardovinted95@gmail.com"
my_password = "3gigio3leo*"
driver_name = "chromedriver.exe"
sito_vinted = "https://www.vinted.it/"
pagina_profilo = "https://www.vinted.it/member/168504727"

caricati = "CARICATI"
caricare = "CARICARE"
cestinati = "CESTINATI"
articoli_nuovi = "ARTICOLI NUOVI"
articoli = "ARTICOLI"
rinnovo_non_necessario = "RINNOVO NON NECESSARIO"

cartella_lavoro_bot = "v_bot_file"

path_caricati = pathlib.Path().cwd().joinpath(cartella_lavoro_bot).joinpath(caricati)
path_da_caricare = pathlib.Path().cwd().joinpath(cartella_lavoro_bot).joinpath(caricare)
path_cestinati = pathlib.Path().cwd().joinpath(cartella_lavoro_bot).joinpath(cestinati)
path_rinnovo_non_necessario = pathlib.Path().cwd().joinpath(cartella_lavoro_bot).joinpath(rinnovo_non_necessario)

path_articoli_nuovi = pathlib.Path().cwd().joinpath(articoli_nuovi)
path_articoli = pathlib.Path().cwd().joinpath(articoli)
