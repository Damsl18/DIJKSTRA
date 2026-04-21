import networkx as nx
import matplotlib.pyplot as plt


g = nx.Graph()

def graphe():
    n = 0
    while n <= 1:
        n = int(input("Entrer le nombre de noeuds supérieur à 1 : "))

    for i in range(n):
        noeuds = input(f"Entrer le noeuds {i + 1} : ")
        g.add_node(noeuds)

    decision = True

def arete():
    print("Entrez les arêtes pour vos noeuds")
    while decision:
        n1 = input("Entrer le premier noeuds: ")
        n2 = input("Entrer le second noeuds: ")
        pond = input("Entrer la pondération: ")
        g.add_edge(n1, n2, weight=pond)
        choix = input("Voulez-vous ajouter d'autres arêtes ? o/n ")
        if choix.lower() == "n":
            decision = False
    nx.draw(g, with_labels=True)
    plt.show()

