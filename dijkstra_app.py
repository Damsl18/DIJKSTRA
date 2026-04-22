"""
Application de graphe pondéré non orienté avec algorithme de Dijkstra.
Interface graphique avec tkinter, visualisation avec matplotlib/networkx.
"""

import tkinter as tk
from tkinter import messagebox, simpledialog, ttk
import networkx as nx
import matplotlib
matplotlib.use("TkAgg")
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import heapq


class DijkstraApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Graphe Pondéré - Algorithme de Dijkstra")
        self.root.geometry("900x700")
        self.root.configure(bg="#f0f0f0")

        self.sommets = []
        self.aretes = []  # list of (u, v, poids)
        self.graph = nx.Graph()

        self.current_frame = None
        self.etape1_nombre_sommets()

    def clear_frame(self):
        if self.current_frame:
            self.current_frame.destroy()

    # ===================== ÉTAPE 1 : Nombre de sommets =====================
    def etape1_nombre_sommets(self):
        self.clear_frame()
        self.current_frame = tk.Frame(self.root, bg="#f0f0f0")
        self.current_frame.pack(expand=True)

        tk.Label(self.current_frame, text="Insérez le nombre de sommets :",
                 font=("Arial", 14, "bold"), bg="#f0f0f0").pack(pady=20)

        self.entry_nb = tk.Entry(self.current_frame, font=("Arial", 14), width=10, justify="center")
        self.entry_nb.pack(pady=10)
        self.entry_nb.focus_set()

        self.lbl_err1 = tk.Label(self.current_frame, text="", fg="red", bg="#f0f0f0", font=("Arial", 11))
        self.lbl_err1.pack(pady=5)

        tk.Button(self.current_frame, text="Suivant", font=("Arial", 12),
                  command=self.valider_nb_sommets, bg="#4CAF50", fg="white",
                  padx=20, pady=5).pack(pady=10)

        self.entry_nb.bind("<Return>", lambda e: self.valider_nb_sommets())

    def valider_nb_sommets(self):
        txt = self.entry_nb.get().strip()
        try:
            n = int(txt)
        except ValueError:
            self.lbl_err1.config(text="ERREUR. Veuillez entrer un nombre entier valide.")
            return
        if n < 2:
            self.lbl_err1.config(text="ERREUR. Le graphe doit avoir au moins 2 sommets.")
            return
        self.nb_sommets = n
        self.sommets = []
        self.etape2_nommer_sommets()

    # ===================== ÉTAPE 2 : Nommer les sommets =====================
    def etape2_nommer_sommets(self):
        self.clear_frame()
        self.current_frame = tk.Frame(self.root, bg="#f0f0f0")
        self.current_frame.pack(expand=True)

        tk.Label(self.current_frame, text="Nommez chacun des sommets :",
                 font=("Arial", 14, "bold"), bg="#f0f0f0").pack(pady=15)

        self.entries_sommets = []
        container = tk.Frame(self.current_frame, bg="#f0f0f0")
        container.pack(pady=5)

        for i in range(self.nb_sommets):
            row = tk.Frame(container, bg="#f0f0f0")
            row.pack(pady=3)
            tk.Label(row, text=f"Sommet{i+1} : ", font=("Arial", 12), bg="#f0f0f0", width=10, anchor="e").pack(side="left")
            e = tk.Entry(row, font=("Arial", 12), width=15)
            e.pack(side="left")
            self.entries_sommets.append(e)

        if self.entries_sommets:
            self.entries_sommets[0].focus_set()

        self.lbl_err2 = tk.Label(self.current_frame, text="", fg="red", bg="#f0f0f0", font=("Arial", 11))
        self.lbl_err2.pack(pady=5)

        tk.Button(self.current_frame, text="Suivant", font=("Arial", 12),
                  command=self.valider_sommets, bg="#4CAF50", fg="white",
                  padx=20, pady=5).pack(pady=10)

    def valider_sommets(self):
        noms = []
        for i, e in enumerate(self.entries_sommets):
            nom = e.get().strip()
            if nom == "":
                self.lbl_err2.config(text="ERREUR. Le nom du sommet ne peut pas être vide.")
                e.focus_set()
                return
            if nom in noms:
                self.lbl_err2.config(text=f"ERREUR. Le sommet '{nom}' existe déjà.")
                e.focus_set()
                return
            noms.append(nom)
        self.sommets = noms
        self.aretes = []
        self.etape3_inserer_aretes()

    # ===================== ÉTAPE 3 : Insérer les arêtes =====================
    def etape3_inserer_aretes(self):
        self.clear_frame()
        self.current_frame = tk.Frame(self.root, bg="#f0f0f0")
        self.current_frame.pack(expand=True)

        tk.Label(self.current_frame, text="Insérez les arêtes",
                 font=("Arial", 14, "bold"), bg="#f0f0f0").pack(pady=10)

        tk.Label(self.current_frame, text=f"Sommets disponibles : {', '.join(self.sommets)}",
                 font=("Arial", 11), bg="#f0f0f0", fg="#555").pack(pady=5)

        # Liste des arêtes déjà ajoutées
        self.frame_liste_aretes = tk.Frame(self.current_frame, bg="#f0f0f0")
        self.frame_liste_aretes.pack(pady=5)
        self.lbl_aretes_titre = tk.Label(self.frame_liste_aretes, text="Arêtes ajoutées :",
                                          font=("Arial", 11, "bold"), bg="#f0f0f0")
        self.lbl_aretes_liste = tk.Label(self.frame_liste_aretes, text="(aucune)",
                                          font=("Arial", 11), bg="#f0f0f0", fg="#333")

        self.lbl_aretes_titre.pack()
        self.lbl_aretes_liste.pack()

        # Formulaire d'arête
        form = tk.Frame(self.current_frame, bg="#f0f0f0")
        form.pack(pady=10)

        self.arete_num = len(self.aretes) + 1
        self.lbl_arete_num = tk.Label(form, text=f"Arête {self.arete_num} :",
                                       font=("Arial", 12, "bold"), bg="#f0f0f0")
        self.lbl_arete_num.grid(row=0, column=0, columnspan=2, pady=5)

        tk.Label(form, text="Extrémité 1 :", font=("Arial", 12), bg="#f0f0f0").grid(row=1, column=0, sticky="e", padx=5)
        self.entry_ext1 = tk.Entry(form, font=("Arial", 12), width=15)
        self.entry_ext1.grid(row=1, column=1, padx=5, pady=3)

        tk.Label(form, text="Extrémité 2 :", font=("Arial", 12), bg="#f0f0f0").grid(row=2, column=0, sticky="e", padx=5)
        self.entry_ext2 = tk.Entry(form, font=("Arial", 12), width=15)
        self.entry_ext2.grid(row=2, column=1, padx=5, pady=3)

        tk.Label(form, text="Pondération :", font=("Arial", 12), bg="#f0f0f0").grid(row=3, column=0, sticky="e", padx=5)
        self.entry_poids = tk.Entry(form, font=("Arial", 12), width=15)
        self.entry_poids.grid(row=3, column=1, padx=5, pady=3)

        self.entry_ext1.focus_set()

        self.lbl_err3 = tk.Label(self.current_frame, text="", fg="red", bg="#f0f0f0", font=("Arial", 11))
        self.lbl_err3.pack(pady=5)

        btn_frame = tk.Frame(self.current_frame, bg="#f0f0f0")
        btn_frame.pack(pady=10)

        tk.Button(btn_frame, text="Ajouter l'arête", font=("Arial", 12),
                  command=self.ajouter_arete, bg="#2196F3", fg="white",
                  padx=15, pady=5).pack(side="left", padx=10)

        tk.Button(btn_frame, text="Terminer (passer à la suite)", font=("Arial", 12),
                  command=self.terminer_aretes, bg="#FF9800", fg="white",
                  padx=15, pady=5).pack(side="left", padx=10)

        self.maj_liste_aretes()

    def maj_liste_aretes(self):
        if self.aretes:
            txt = "\n".join([f"  {u} — {v}  (poids: {p})" for u, v, p in self.aretes])
            self.lbl_aretes_liste.config(text=txt)
        else:
            self.lbl_aretes_liste.config(text="(aucune)")

    def ajouter_arete(self):
        ext1 = self.entry_ext1.get().strip()
        ext2 = self.entry_ext2.get().strip()
        poids_txt = self.entry_poids.get().strip()

        if ext1 == "" or ext2 == "" or poids_txt == "":
            self.lbl_err3.config(text="ERREUR. Veuillez remplir tous les champs.")
            return

        if ext1 not in self.sommets:
            self.lbl_err3.config(text=f"ERREUR. Le sommet {ext1} n'existe pas.")
            self.entry_ext1.focus_set()
            return
        if ext2 not in self.sommets:
            self.lbl_err3.config(text=f"ERREUR. Le sommet {ext2} n'existe pas.")
            self.entry_ext2.focus_set()
            return

        if ext1 == ext2:
            self.lbl_err3.config(text="ERREUR. Les deux extrémités doivent être différentes.")
            return

        try:
            poids = float(poids_txt)
            if poids <= 0:
                self.lbl_err3.config(text="ERREUR. La pondération doit être un nombre positif.")
                return
        except ValueError:
            self.lbl_err3.config(text="ERREUR. La pondération doit être un nombre valide.")
            return

        # Vérifier si l'arête existe déjà (non orienté)
        for u, v, _ in self.aretes:
            if (u == ext1 and v == ext2) or (u == ext2 and v == ext1):
                self.lbl_err3.config(text=f"ERREUR. L'arête {ext1} — {ext2} existe déjà.")
                return

        self.aretes.append((ext1, ext2, poids))
        self.lbl_err3.config(text="")
        self.arete_num += 1
        self.lbl_arete_num.config(text=f"Arête {self.arete_num} :")
        self.entry_ext1.delete(0, tk.END)
        self.entry_ext2.delete(0, tk.END)
        self.entry_poids.delete(0, tk.END)
        self.entry_ext1.focus_set()
        self.maj_liste_aretes()

    def terminer_aretes(self):
        if len(self.aretes) == 0:
            self.lbl_err3.config(text="ERREUR. Il faut l'existence d'au moins une arete pour calculer le plus court chemin.")
            return
        self.etape4_modifier_valider()

    # ===================== ÉTAPE 4 : Modifier / Valider =====================
    def etape4_modifier_valider(self):
        self.clear_frame()
        self.current_frame = tk.Frame(self.root, bg="#f0f0f0")
        self.current_frame.pack(expand=True)

        tk.Label(self.current_frame, text="Récapitulatif du graphe",
                 font=("Arial", 14, "bold"), bg="#f0f0f0").pack(pady=10)

        tk.Label(self.current_frame, text=f"Sommets : {', '.join(self.sommets)}",
                 font=("Arial", 12), bg="#f0f0f0").pack(pady=5)

        tk.Label(self.current_frame, text="Arêtes :", font=("Arial", 12, "bold"), bg="#f0f0f0").pack(pady=5)
        for u, v, p in self.aretes:
            tk.Label(self.current_frame, text=f"  {u} — {v}  (poids: {p})",
                     font=("Arial", 11), bg="#f0f0f0").pack()

        btn_frame = tk.Frame(self.current_frame, bg="#f0f0f0")
        btn_frame.pack(pady=20)

        tk.Button(btn_frame, text="Modifier", font=("Arial", 13, "bold"),
                  command=self.modifier_graphe, bg="#FF5722", fg="white",
                  padx=30, pady=8).pack(side="left", padx=20)

        tk.Button(btn_frame, text="Valider", font=("Arial", 13, "bold"),
                  command=self.valider_graphe, bg="#4CAF50", fg="white",
                  padx=30, pady=8).pack(side="left", padx=20)

    def modifier_graphe(self):
        """Ouvre une fenêtre de modification."""
        win = tk.Toplevel(self.root)
        win.title("Modifier le graphe")
        win.geometry("500x500")
        win.configure(bg="#f0f0f0")

        tk.Label(win, text="Modification du graphe", font=("Arial", 14, "bold"), bg="#f0f0f0").pack(pady=10)

        # Modifier sommets
        tk.Label(win, text="Renommer un sommet :", font=("Arial", 12, "bold"), bg="#f0f0f0").pack(pady=5)
        frame_s = tk.Frame(win, bg="#f0f0f0")
        frame_s.pack(pady=5)

        tk.Label(frame_s, text="Ancien nom :", font=("Arial", 11), bg="#f0f0f0").grid(row=0, column=0, padx=5)
        entry_old = tk.Entry(frame_s, font=("Arial", 11), width=10)
        entry_old.grid(row=0, column=1, padx=5)

        tk.Label(frame_s, text="Nouveau nom :", font=("Arial", 11), bg="#f0f0f0").grid(row=1, column=0, padx=5)
        entry_new = tk.Entry(frame_s, font=("Arial", 11), width=10)
        entry_new.grid(row=1, column=1, padx=5)

        lbl_err_mod = tk.Label(win, text="", fg="red", bg="#f0f0f0", font=("Arial", 10))
        lbl_err_mod.pack(pady=3)

        def renommer_sommet():
            old = entry_old.get().strip()
            new = entry_new.get().strip()
            if old not in self.sommets:
                lbl_err_mod.config(text=f"ERREUR. Le sommet {old} n'existe pas.")
                return
            if new == "":
                lbl_err_mod.config(text="ERREUR. Le nom du sommet ne peut pas être vide.")
                return
            if new in self.sommets and new != old:
                lbl_err_mod.config(text=f"ERREUR. Le sommet {new} existe déjà.")
                return
            idx = self.sommets.index(old)
            self.sommets[idx] = new
            self.aretes = [(new if u == old else u, new if v == old else v, p) for u, v, p in self.aretes]
            lbl_err_mod.config(text=f"Sommet '{old}' renommé en '{new}'.", fg="green")

        tk.Button(frame_s, text="Renommer", command=renommer_sommet, bg="#2196F3", fg="white").grid(row=2, column=0, columnspan=2, pady=5)

        # Modifier arête
        tk.Label(win, text="Modifier la pondération d'une arête :", font=("Arial", 12, "bold"), bg="#f0f0f0").pack(pady=10)
        frame_a = tk.Frame(win, bg="#f0f0f0")
        frame_a.pack(pady=5)

        tk.Label(frame_a, text="Extrémité 1 :", font=("Arial", 11), bg="#f0f0f0").grid(row=0, column=0, padx=5)
        entry_ae1 = tk.Entry(frame_a, font=("Arial", 11), width=10)
        entry_ae1.grid(row=0, column=1, padx=5)

        tk.Label(frame_a, text="Extrémité 2 :", font=("Arial", 11), bg="#f0f0f0").grid(row=1, column=0, padx=5)
        entry_ae2 = tk.Entry(frame_a, font=("Arial", 11), width=10)
        entry_ae2.grid(row=1, column=1, padx=5)

        tk.Label(frame_a, text="Nouveau poids :", font=("Arial", 11), bg="#f0f0f0").grid(row=2, column=0, padx=5)
        entry_ap = tk.Entry(frame_a, font=("Arial", 11), width=10)
        entry_ap.grid(row=2, column=1, padx=5)

        lbl_err_mod2 = tk.Label(win, text="", fg="red", bg="#f0f0f0", font=("Arial", 10))
        lbl_err_mod2.pack(pady=3)

        def modifier_arete():
            e1 = entry_ae1.get().strip()
            e2 = entry_ae2.get().strip()
            p_txt = entry_ap.get().strip()
            try:
                p = float(p_txt)
                if p <= 0:
                    lbl_err_mod2.config(text="ERREUR. La pondération doit être positive.", fg="red")
                    return
            except ValueError:
                lbl_err_mod2.config(text="ERREUR. Pondération invalide.", fg="red")
                return

            for i, (u, v, _) in enumerate(self.aretes):
                if (u == e1 and v == e2) or (u == e2 and v == e1):
                    self.aretes[i] = (u, v, p)
                    lbl_err_mod2.config(text=f"Arête {e1}—{e2} modifiée (poids: {p}).", fg="green")
                    return
            lbl_err_mod2.config(text=f"ERREUR. L'arête {e1}—{e2} n'existe pas.", fg="red")

        tk.Button(frame_a, text="Modifier", command=modifier_arete, bg="#FF9800", fg="white").grid(row=3, column=0, columnspan=2, pady=5)

        # Supprimer une arête
        tk.Label(win, text="Supprimer une arête :", font=("Arial", 12, "bold"), bg="#f0f0f0").pack(pady=10)
        frame_d = tk.Frame(win, bg="#f0f0f0")
        frame_d.pack(pady=5)

        tk.Label(frame_d, text="Extrémité 1 :", font=("Arial", 11), bg="#f0f0f0").grid(row=0, column=0, padx=5)
        entry_de1 = tk.Entry(frame_d, font=("Arial", 11), width=10)
        entry_de1.grid(row=0, column=1, padx=5)

        tk.Label(frame_d, text="Extrémité 2 :", font=("Arial", 11), bg="#f0f0f0").grid(row=1, column=0, padx=5)
        entry_de2 = tk.Entry(frame_d, font=("Arial", 11), width=10)
        entry_de2.grid(row=1, column=1, padx=5)

        lbl_err_mod3 = tk.Label(win, text="", fg="red", bg="#f0f0f0", font=("Arial", 10))
        lbl_err_mod3.pack(pady=3)

        def supprimer_arete():
            e1 = entry_de1.get().strip()
            e2 = entry_de2.get().strip()
            for i, (u, v, _) in enumerate(self.aretes):
                if (u == e1 and v == e2) or (u == e2 and v == e1):
                    self.aretes.pop(i)
                    lbl_err_mod3.config(text=f"Arête {e1}—{e2} supprimée.", fg="green")
                    return
            lbl_err_mod3.config(text=f"ERREUR. L'arête {e1}—{e2} n'existe pas.", fg="red")

        tk.Button(frame_d, text="Supprimer", command=supprimer_arete, bg="#f44336", fg="white").grid(row=2, column=0, columnspan=2, pady=5)

        def fermer_et_rafraichir():
            win.destroy()
            self.etape4_modifier_valider()

        tk.Button(win, text="Fermer et revenir au récapitulatif", command=fermer_et_rafraichir,
                  font=("Arial", 11), bg="#607D8B", fg="white", padx=15, pady=5).pack(pady=15)

    # ===================== ÉTAPE 5 : Valider et afficher le graphe =====================
    def valider_graphe(self):
        if len(self.aretes) == 0:
            messagebox.showerror("Erreur", "ERREUR. Il faut l'existence d'au moins une arete pour calculer le plus court chemin.")
            return

        self.graph = nx.Graph()
        self.graph.add_nodes_from(self.sommets)
        for u, v, p in self.aretes:
            self.graph.add_edge(u, v, weight=p)

        self.clear_frame()
        self.current_frame = tk.Frame(self.root, bg="#f0f0f0")
        self.current_frame.pack(fill="both", expand=True)

        tk.Label(self.current_frame, text="Graphe pondéré non orienté",
                 font=("Arial", 14, "bold"), bg="#f0f0f0").pack(pady=5)

        fig, ax = plt.subplots(figsize=(7, 5))
        self.pos = nx.spring_layout(self.graph, seed=42)
        nx.draw(self.graph, self.pos, ax=ax, with_labels=True,
                node_color="#4FC3F7", node_size=700, font_size=13, font_weight="bold",
                edge_color="#888", width=2)
        edge_labels = nx.get_edge_attributes(self.graph, 'weight')
        nx.draw_networkx_edge_labels(self.graph, self.pos, edge_labels=edge_labels,
                                      ax=ax, font_size=11, font_color="red")
        ax.set_title("Graphe correspondant", fontsize=13)
        fig.tight_layout()

        canvas = FigureCanvasTkAgg(fig, master=self.current_frame)
        canvas.draw()
        canvas.get_tk_widget().pack(fill="both", expand=True)

        btn_frame = tk.Frame(self.current_frame, bg="#f0f0f0")
        btn_frame.pack(pady=10)

        tk.Button(btn_frame, text="Calculer le PCC", font=("Arial", 13, "bold"),
                  command=self.etape6_calculer_pcc, bg="#9C27B0", fg="white",
                  padx=25, pady=8).pack()

    # ===================== ÉTAPE 6 : Calculer le PCC (Dijkstra) =====================
    def etape6_calculer_pcc(self):
        """Demande source et destination, puis calcule et affiche le PCC."""
        win = tk.Toplevel(self.root)
        win.title("Calculer le Plus Court Chemin")
        win.geometry("400x250")
        win.configure(bg="#f0f0f0")

        tk.Label(win, text="Plus Court Chemin (Dijkstra)", font=("Arial", 13, "bold"), bg="#f0f0f0").pack(pady=10)
        tk.Label(win, text=f"Sommets : {', '.join(self.sommets)}", font=("Arial", 10), bg="#f0f0f0", fg="#555").pack()

        form = tk.Frame(win, bg="#f0f0f0")
        form.pack(pady=10)

        tk.Label(form, text="Sommet source :", font=("Arial", 12), bg="#f0f0f0").grid(row=0, column=0, padx=5, pady=5)
        entry_src = tk.Entry(form, font=("Arial", 12), width=10)
        entry_src.grid(row=0, column=1, padx=5, pady=5)

        tk.Label(form, text="Sommet destination :", font=("Arial", 12), bg="#f0f0f0").grid(row=1, column=0, padx=5, pady=5)
        entry_dst = tk.Entry(form, font=("Arial", 12), width=10)
        entry_dst.grid(row=1, column=1, padx=5, pady=5)

        lbl_err = tk.Label(win, text="", fg="red", bg="#f0f0f0", font=("Arial", 10))
        lbl_err.pack(pady=3)

        def calculer():
            src = entry_src.get().strip()
            dst = entry_dst.get().strip()

            if src not in self.sommets:
                lbl_err.config(text=f"ERREUR. Le sommet {src} n'existe pas.")
                return
            if dst not in self.sommets:
                lbl_err.config(text=f"ERREUR. Le sommet {dst} n'existe pas.")
                return
            if src == dst:
                lbl_err.config(text="ERREUR. La source et la destination doivent être différentes.")
                return

            # Dijkstra manuel
            distances, predecesseurs = self.dijkstra(src)

            if distances[dst] == float('inf'):
                lbl_err.config(text=f"ERREUR. Aucun chemin entre {src} et {dst}.")
                return

            # Reconstruire le chemin
            chemin = []
            courant = dst
            while courant is not None:
                chemin.append(courant)
                courant = predecesseurs[courant]
            chemin.reverse()

            win.destroy()
            self.afficher_pcc(chemin, distances[dst])

        tk.Button(win, text="Calculer", font=("Arial", 12, "bold"),
                  command=calculer, bg="#9C27B0", fg="white",
                  padx=20, pady=5).pack(pady=10)

    def dijkstra(self, source):
        """Implémentation manuelle de l'algorithme de Dijkstra."""
        distances = {s: float('inf') for s in self.sommets}
        predecesseurs = {s: None for s in self.sommets}
        distances[source] = 0
        visite = set()

        # File de priorité : (distance, sommet)
        file = [(0, source)]

        while file:
            dist_courante, u = heapq.heappop(file)

            if u in visite:
                continue
            visite.add(u)

            # Parcourir les voisins
            for voisin in self.graph.neighbors(u):
                poids = self.graph[u][voisin]['weight']
                nouvelle_dist = dist_courante + poids

                if nouvelle_dist < distances[voisin]:
                    distances[voisin] = nouvelle_dist
                    predecesseurs[voisin] = u
                    heapq.heappush(file, (nouvelle_dist, voisin))

        return distances, predecesseurs

    # ===================== ÉTAPE 7 : Afficher le PCC dans une nouvelle fenêtre =====================
    def afficher_pcc(self, chemin, distance_totale):
        """Affiche le graphe avec le plus court chemin mis en évidence dans une nouvelle fenêtre."""
        win = tk.Toplevel(self.root)
        win.title("Plus Court Chemin - Résultat")
        win.geometry("800x650")
        win.configure(bg="#f0f0f0")

        chemin_str = " → ".join(chemin)
        tk.Label(win, text=f"Plus Court Chemin : {chemin_str}",
                 font=("Arial", 13, "bold"), bg="#f0f0f0", fg="#1B5E20").pack(pady=5)
        tk.Label(win, text=f"Distance totale : {distance_totale}",
                 font=("Arial", 12), bg="#f0f0f0", fg="#333").pack(pady=3)

        # Construire les arêtes du chemin
        aretes_chemin = set()
        for i in range(len(chemin) - 1):
            aretes_chemin.add((chemin[i], chemin[i+1]))
            aretes_chemin.add((chemin[i+1], chemin[i]))

        fig, ax = plt.subplots(figsize=(7, 5))

        # Couleurs des nœuds
        node_colors = []
        for n in self.graph.nodes():
            if n in chemin:
                node_colors.append("#66BB6A")  # vert pour les nœuds du chemin
            else:
                node_colors.append("#BDBDBD")  # gris pour les autres

        # Couleurs et épaisseurs des arêtes
        edge_colors = []
        edge_widths = []
        for u, v in self.graph.edges():
            if (u, v) in aretes_chemin:
                edge_colors.append("#E53935")  # rouge pour le PCC
                edge_widths.append(4)
            else:
                edge_colors.append("#CCCCCC")
                edge_widths.append(1.5)

        nx.draw(self.graph, self.pos, ax=ax, with_labels=True,
                node_color=node_colors, node_size=700, font_size=13, font_weight="bold",
                edge_color=edge_colors, width=edge_widths)

        edge_labels = nx.get_edge_attributes(self.graph, 'weight')
        nx.draw_networkx_edge_labels(self.graph, self.pos, edge_labels=edge_labels,
                                      ax=ax, font_size=11, font_color="red")

        ax.set_title(f"Plus Court Chemin : {chemin_str} (distance: {distance_totale})", fontsize=12)
        fig.tight_layout()

        canvas = FigureCanvasTkAgg(fig, master=win)
        canvas.draw()
        canvas.get_tk_widget().pack(fill="both", expand=True)

        tk.Button(win, text="Fermer", font=("Arial", 12),
                  command=win.destroy, bg="#607D8B", fg="white",
                  padx=20, pady=5).pack(pady=10)


if __name__ == "__main__":
    root = tk.Tk()
    app = DijkstraApp(root)
    root.mainloop()
