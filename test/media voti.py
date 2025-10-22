from _pytest import pathlib

analisi1 = (18*9)
geometria= (23*6)
analisi2 = (18*6)
economia = (18*6)
fisica1 = (30*9)
fisica2 = (23*6)
informatica = (18*9)
algebra = (21*6)
elettronica = (24*9)
elettrotecnica = (24*6)
ingsoftware = (28*9)
oop = (30*9)
pmobile= (26*9)
ro = (26*9)
so = (24*9)
tlc = (9*20)
totale = (geometria + analisi1 + analisi2 + economia + fisica1 + fisica2 + informatica + algebra + elettronica + elettrotecnica + ingsoftware + oop + pmobile + ro + so + tlc)
totale_scartato = (geometria + analisi2  + economia + fisica1 + fisica2  + algebra + elettronica + elettrotecnica + ingsoftware + oop + pmobile + ro + so + tlc - 2*18)

media_totale = (totale / 126)
media_totale_scartato = (totale_scartato / 106)
pagina_venditore_casuale = str(pathlib.Path.cwd().joinpath("test").joinpath("framboise614 - member profile _ Vinted.html"))

def calcolo(tot):
    return (tot*110)/30

def stabilizza_blocca_script():
    with open(pagina_venditore_casuale, "r", encoding="utf-8") as f:
        html = f.read()

    # Rimuove i tag script
    import re
    html_no_js = re.sub(r"<script.*?</script>", "", html, flags=re.DOTALL)

    with open("pagina_pulita.html", "w", encoding="utf-8") as f:
        f.write(html_no_js)

print(totale)
print(totale_scartato)
print(media_totale)
print(media_totale_scartato)
print(calcolo(media_totale))
print(calcolo(media_totale_scartato))
stabilizza_blocca_script()








