import xlrd


document = xlrd.open_workbook("JLPT_3.xls")


print("Nombre de feuilles: "+str(document.nsheets))
print("Noms des feuilles: "+str(document.sheet_names()))

feuille_1 = document.sheet_by_index(0)
cols = feuille_1.ncols
rows = feuille_1.nrows

print("Format de la feuille 1:")
print("Nom: "+str(feuille_1.name))
print("Nombre de lignes: "+str(feuille_1.nrows))
print("Nombre de colonnes: "+str(feuille_1.ncols))

X = []
Y= []
for r in range(1, 5):
    X += [feuille_1.cell_value(rowx=r, colx=0)]
    X += [feuille_1.cell_value(rowx=r, colx=1)]
    X += [feuille_1.cell_value(rowx=r, colx=2)]
    X += [feuille_1.cell_value(rowx=r, colx=3)]
    X += [feuille_1.cell_value(rowx=r, colx=4)]
    
print(X)
