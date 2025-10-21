


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

def calcolo(tot):
    return (tot*110)/30
print(totale)
print(totale_scartato)
print(media_totale)
print(media_totale_scartato)
print(calcolo(media_totale))
print(calcolo(media_totale_scartato))





