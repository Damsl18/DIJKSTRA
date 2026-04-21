from tkinter import *
root = Tk()
root.title("Graph")
root.geometry("600x600")

label = Label(root, text="ALGORITHME DE DIJKSTRA")
label.pack()
description = Label(root, text="Ce programme permet de calculer le plus court chemin dans un graphe non orienté")
description.pack()

label = Label(root, text="Inserez le nombre de noeuds")
label.pack()

input = Entry(root)
input.pack()
a = []
def disparition():
    a.append(input.get())
    print(a)
    label.destroy()
    input.destroy()
    btn.destroy()
btn = Button(root, command=disparition, text="Valider")
btn.pack()

print(a)


root.mainloop()
