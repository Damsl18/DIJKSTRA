"""
Application de graphe pondéré non orienté avec algorithme de Dijkstra.
Interface graphique avec tkinter, visualisation avec matplotlib/networkx.
"""

import tkinter as tk
from tkinter import messagebox, ttk
import networkx as nx
import matplotlib
matplotlib.use("TkAgg")
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import heapq


class DijkstraApp:
    BG = "#f0f0f0"
    FONT = ("Arial", 12)
    FONT_B = ("Arial", 14, "bold")
    FONT_S = ("Arial", 11)
    BTN_COLORS = {
        "green": ("#4CAF50", "white"),
        "blue": ("#2196F3", "white"),
        "orange": ("#FF9800", "white"),
        "red": ("#f44336", "white"),
        "purple": ("#9C27B0", "white"),
        "gray": ("#607D8B", "white"),
        "dark_red": ("#FF5722", "white"),
    }

    def __init__(self, root):
        self.root = root
        self.root.title("Graphe Pondéré - Algorithme de Dijkstra")
        self.root.geometry("900x700")
        self.root.configure(bg=self.BG)

        self.sommets = []
        self.aretes = []
        self.nb_sommets = 0
        self.graph = nx.Graph()
        self.pos = None
        self.current_frame = None
        self.etape1_nombre_sommets()

    # ===================== HELPERS =====================
    def clear_frame(self):
        if self.current_frame:
            self.current_frame.destroy()

    def make_scrollable_frame(self):
        """Crée un frame scrollable et retourne le frame intérieur."""
        self.clear_frame()
        outer = tk.Frame(self.root, bg=self.BG)
        outer.pack(fill="both", expand=True)
        self.current_frame = outer

        canvas = tk.Canvas(outer, bg=self.BG, highlightthickness=0)
        scrollbar = ttk.Scrollbar(outer, orient="vertical", command=canvas.yview)
        inner = tk.Frame(canvas, bg=self.BG)

        inner.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
        canvas.create_window((0, 0), window=inner, anchor="n")
        canvas.configure(yscrollcommand=scrollbar.set)

        # Centrer le contenu horizontalement
        def _center(event):
            canvas.itemconfig("all", width=event.width)
        canvas.bind("<Configure>", lambda e: canvas.coords(canvas.find_all()[0], e.width / 2, 0) if canvas.find_all() else None)

        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        # Molette souris
        def _on_mousewheel(event):
            canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")
        canvas.bind_all("<MouseWheel>", _on_mousewheel)
        canvas.bind_all("<Button-4>", lambda e: canvas.yview_scroll(-1, "units"))
        canvas.bind_all("<Button-5>", lambda e: canvas.yview_scroll(1, "units"))

        return inner

    def make_label(self, parent, text, font=None, fg=None, **kw):
        font = font or self.FONT
        return tk.Label(parent, text=text, font=font, bg=self.BG, fg=fg, **kw)

    def make_button(self, parent, text, command, color="green", **kw):
        bg, fg = self.BTN_COLORS.get(color, self.BTN_COLORS["green"])
        return tk.Button(parent, text=text, font=self.FONT, command=command,
                         bg=bg, fg=fg, padx=15, pady=5, **kw)

    def make_entry(self, parent, width=15):
        return tk.Entry(parent, font=self.FONT, width=width)

    def make_error_label(self, parent):
        return tk.Label(parent, text="", fg="red", bg=self.BG, font=self.FONT_S)

    # ===================== NAVIGATION PANEL (édition globale) =====================
    def add_navigation_panel(self, parent, current_step, show_back=True):
        """Ajoute un panneau de navigation avec Retour + accès rapide aux étapes."""
        nav = tk.Frame(parent, bg="#e0e0e0", pady=5)
        nav.pack(fill="x", pady=(0, 10))

        if show_back and current_step > 1:
            back_targets = {
                2: self.etape1_nombre_sommets,
                3: self.etape2_nommer_sommets,
                4: self.etape3_inserer_aretes,
                5: self.etape4_modifier_valider,
            }
            target = back_targets.get(current_step)
            if target:
                self.make_button(nav, "← Retour", target, color="gray").pack(side="left", padx=10)

        # Boutons d'accès rapide (seulement les étapes déjà franchies)
        if current_step >= 2 and self.nb_sommets >= 2:
            self.make_button(nav, "Modifier sommets", self._go_edit_nb_sommets, color="blue").pack(side="right", padx=5)
        if current_step >= 3 and self.sommets:
            self.make_button(nav, "Modifier noms", self._go_edit_noms, color="blue").pack(side="right", padx=5)

        return nav

    def _go_edit_nb_sommets(self):
        self.etape1_nombre_sommets()

    def _go_edit_noms(self):
        self.etape2_nommer_sommets()

    # ===================== ÉTAPE 1 : Nombre de sommets =====================
    def etape1_nombre_sommets(self):
        inner = self.make_scrollable_frame()

        self.make_label(inner, "Insérez le nombre de sommets :", font=self.FONT_B).pack(pady=20)

        self.entry_nb = self.make_entry(inner, width=10)
        self.entry_nb.pack(pady=10)
        if self.nb_sommets > 0:
            self.entry_nb.insert(0, str(self.nb_sommets))
        self.entry_nb.focus_set()

        self.lbl_err1 = self.make_error_label(inner)
        self.lbl_err1.pack(pady=5)

        btn_frame = tk.Frame(inner, bg=self.BG)
        btn_frame.pack(pady=10)

        self.make_button(btn_frame, "Valider", self.valider_nb_sommets, color="green").pack(side="left", padx=10)

        self.entry_nb.bind("<Return>", lambda e: self.valider_nb_sommets())

        # Afficher état actuel si données existantes
        if self.sommets:
            self.make_label(inner, f"Sommets actuels : {', '.join(self.sommets)}",
                           font=self.FONT_S, fg="#555").pack(pady=5)
        if self.aretes:
            txt = "Arêtes actuelles :\n" + "\n".join(f"  {u}—{v} (poids: {p})" for u, v, p in self.aretes)
            self.make_label(inner, txt, font=self.FONT_S, fg="#555").pack(pady=5)

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

        old_nb = self.nb_sommets
        self.nb_sommets = n

        # Ajuster les sommets existants
        if len(self.sommets) > n:
            removed = self.sommets[n:]
            self.sommets = self.sommets[:n]
            # Supprimer les arêtes liées aux sommets supprimés
            self.aretes = [(u, v, p) for u, v, p in self.aretes
                          if u not in removed and v not in removed]
        self.etape2_nommer_sommets()

    # ===================== ÉTAPE 2 : Nommer les sommets =====================
    def etape2_nommer_sommets(self):
        inner = self.make_scrollable_frame()
        self.add_navigation_panel(inner, current_step=2)

        self.make_label(inner, "Nommez chacun des sommets :", font=self.FONT_B).pack(pady=15)

        self.entries_sommets = []
        container = tk.Frame(inner, bg=self.BG)
        container.pack(pady=5)

        for i in range(self.nb_sommets):
            row = tk.Frame(container, bg=self.BG)
            row.pack(pady=3)
            self.make_label(row, f"Sommet{i+1} : ", width=10, anchor="e").pack(side="left")
            e = self.make_entry(row)
            e.pack(side="left")
            # Pré-remplir si existant
            if i < len(self.sommets):
                e.insert(0, self.sommets[i])
            self.entries_sommets.append(e)

        if self.entries_sommets:
            self.entries_sommets[0].focus_set()

        self.lbl_err2 = self.make_error_label(inner)
        self.lbl_err2.pack(pady=5)

        self.make_button(inner, "Suivant", self.valider_sommets, color="green").pack(pady=10)

        # Afficher arêtes existantes
        if self.aretes:
            txt = "Arêtes actuelles :\n" + "\n".join(f"  {u}—{v} (poids: {p})" for u, v, p in self.aretes)
            self.make_label(inner, txt, font=self.FONT_S, fg="#555").pack(pady=5)

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

        # Mettre à jour les arêtes si des sommets ont été renommés
        old_sommets = self.sommets
        mapping = {}
        for i, new_name in enumerate(noms):
            if i < len(old_sommets) and old_sommets[i] != new_name:
                mapping[old_sommets[i]] = new_name

        if mapping:
            new_aretes = []
            for u, v, p in self.aretes:
                nu = mapping.get(u, u)
                nv = mapping.get(v, v)
                if nu in noms and nv in noms:
                    new_aretes.append((nu, nv, p))
            self.aretes = new_aretes

        # Supprimer arêtes référençant des sommets supprimés
        self.aretes = [(u, v, p) for u, v, p in self.aretes if u in noms and v in noms]

        self.sommets = noms
        self.etape3_inserer_aretes()

    # ===================== ÉTAPE 3 : Insérer les arêtes =====================
    def etape3_inserer_aretes(self):
        inner = self.make_scrollable_frame()
        self.add_navigation_panel(inner, current_step=3)

        self.make_label(inner, "Insérez les arêtes", font=self.FONT_B).pack(pady=10)
        self.make_label(inner, f"Sommets disponibles : {', '.join(self.sommets)}",
                       font=self.FONT_S, fg="#555").pack(pady=5)

        # Liste des arêtes
        self.frame_liste_aretes = tk.Frame(inner, bg=self.BG)
        self.frame_liste_aretes.pack(pady=5)
        self.make_label(self.frame_liste_aretes, "Arêtes ajoutées :", font=("Arial", 11, "bold")).pack()
        self.lbl_aretes_liste = self.make_label(self.frame_liste_aretes, "(aucune)", fg="#333")
        self.lbl_aretes_liste.pack()

        # Formulaire
        form = tk.Frame(inner, bg=self.BG)
        form.pack(pady=10)

        self.arete_num = len(self.aretes) + 1
        self.lbl_arete_num = self.make_label(form, f"Arête {self.arete_num} :",
                                              font=("Arial", 12, "bold"))
        self.lbl_arete_num.grid(row=0, column=0, columnspan=2, pady=5)

        for i, label_text in enumerate(["Extrémité 1 :", "Extrémité 2 :", "Pondération :"], 1):
            self.make_label(form, label_text).grid(row=i, column=0, sticky="e", padx=5)

        self.entry_ext1 = self.make_entry(form)
        self.entry_ext1.grid(row=1, column=1, padx=5, pady=3)
        self.entry_ext2 = self.make_entry(form)
        self.entry_ext2.grid(row=2, column=1, padx=5, pady=3)
        self.entry_poids = self.make_entry(form)
        self.entry_poids.grid(row=3, column=1, padx=5, pady=3)
        self.entry_ext1.focus_set()

        self.lbl_err3 = self.make_error_label(inner)
        self.lbl_err3.pack(pady=5)

        btn_frame = tk.Frame(inner, bg=self.BG)
        btn_frame.pack(pady=10)

        self.make_button(btn_frame, "Ajouter l'arête", self.ajouter_arete, color="blue").pack(side="left", padx=10)
        self.make_button(btn_frame, "Terminer (passer à la suite)", self.terminer_aretes, color="orange").pack(side="left", padx=10)

        self.maj_liste_aretes()

    def maj_liste_aretes(self):
        if self.aretes:
            txt = "\n".join(f"  {u} — {v}  (poids: {p})" for u, v, p in self.aretes)
        else:
            txt = "(aucune)"
        self.lbl_aretes_liste.config(text=txt)

    def ajouter_arete(self):
        ext1 = self.entry_ext1.get().strip()
        ext2 = self.entry_ext2.get().strip()
        poids_txt = self.entry_poids.get().strip()

        if not all([ext1, ext2, poids_txt]):
            self.lbl_err3.config(text="ERREUR. Veuillez remplir tous les champs.")
            return

        for s, entry in [(ext1, self.entry_ext1), (ext2, self.entry_ext2)]:
            if s not in self.sommets:
                self.lbl_err3.config(text=f"ERREUR. Le sommet {s} n'existe pas.")
                entry.focus_set()
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

        for u, v, _ in self.aretes:
            if {u, v} == {ext1, ext2}:
                self.lbl_err3.config(text=f"ERREUR. L'arête {ext1} — {ext2} existe déjà.")
                return

        self.aretes.append((ext1, ext2, poids))
        self.lbl_err3.config(text="")
        self.arete_num += 1
        self.lbl_arete_num.config(text=f"Arête {self.arete_num} :")
        for entry in [self.entry_ext1, self.entry_ext2, self.entry_poids]:
            entry.delete(0, tk.END)
        self.entry_ext1.focus_set()
        self.maj_liste_aretes()

    def terminer_aretes(self):
        if not self.aretes:
            self.lbl_err3.config(text="ERREUR. Il faut l'existence d'au moins une arete pour calculer le plus court chemin.")
            return
        self.etape4_modifier_valider()

    # ===================== ÉTAPE 4 : Modifier / Valider =====================
    def etape4_modifier_valider(self):
        inner = self.make_scrollable_frame()
        self.add_navigation_panel(inner, current_step=4)

        self.make_label(inner, "Récapitulatif du graphe", font=self.FONT_B).pack(pady=10)
        self.make_label(inner, f"Nombre de sommets : {self.nb_sommets}", font=self.FONT_S).pack(pady=3)
        self.make_label(inner, f"Sommets : {', '.join(self.sommets)}").pack(pady=5)

        self.make_label(inner, "Arêtes :", font=("Arial", 12, "bold")).pack(pady=5)
        for u, v, p in self.aretes:
            self.make_label(inner, f"  {u} — {v}  (poids: {p})", font=self.FONT_S).pack()

        btn_frame = tk.Frame(inner, bg=self.BG)
        btn_frame.pack(pady=20)

        self.make_button(btn_frame, "Modifier", self.modifier_graphe, color="dark_red").pack(side="left", padx=20)
        self.make_button(btn_frame, "Valider", self.valider_graphe, color="green").pack(side="left", padx=20)

    def modifier_graphe(self):
        win = tk.Toplevel(self.root)
        win.title("Modifier le graphe")
        win.geometry("550x650")
        win.configure(bg=self.BG)

        # Scrollable
        canvas = tk.Canvas(win, bg=self.BG, highlightthickness=0)
        scrollbar = ttk.Scrollbar(win, orient="vertical", command=canvas.yview)
        inner = tk.Frame(canvas, bg=self.BG)
        inner.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
        canvas.create_window((0, 0), window=inner, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        canvas.bind_all("<MouseWheel>", lambda e: canvas.yview_scroll(int(-1 * (e.delta / 120)), "units"))

        self.make_label(inner, "Modification du graphe", font=self.FONT_B).pack(pady=10)

        # État actuel
        self.lbl_etat_mod = self.make_label(inner, self._etat_graphe_txt(), font=self.FONT_S, fg="#333")
        self.lbl_etat_mod.pack(pady=5)

        # --- Renommer sommet ---
        self.make_label(inner, "Renommer un sommet :", font=("Arial", 12, "bold")).pack(pady=5)
        frame_s = tk.Frame(inner, bg=self.BG)
        frame_s.pack(pady=5)

        self.make_label(frame_s, "Ancien nom :").grid(row=0, column=0, padx=5)
        entry_old = self.make_entry(frame_s, 10)
        entry_old.grid(row=0, column=1, padx=5)

        self.make_label(frame_s, "Nouveau nom :").grid(row=1, column=0, padx=5)
        entry_new = self.make_entry(frame_s, 10)
        entry_new.grid(row=1, column=1, padx=5)

        lbl_msg1 = self.make_label(inner, "")
        lbl_msg1.pack(pady=3)

        def renommer_sommet():
            old, new = entry_old.get().strip(), entry_new.get().strip()
            if old not in self.sommets:
                lbl_msg1.config(text=f"ERREUR. Le sommet {old} n'existe pas.", fg="red")
                return
            if not new:
                lbl_msg1.config(text="ERREUR. Le nom du sommet ne peut pas être vide.", fg="red")
                return
            if new in self.sommets and new != old:
                lbl_msg1.config(text=f"ERREUR. Le sommet {new} existe déjà.", fg="red")
                return
            idx = self.sommets.index(old)
            self.sommets[idx] = new
            self.aretes = [(new if u == old else u, new if v == old else v, p)
                          for u, v, p in self.aretes]
            lbl_msg1.config(text=f"Sommet '{old}' renommé en '{new}'.", fg="green")
            self.lbl_etat_mod.config(text=self._etat_graphe_txt())

        self.make_button(frame_s, "Renommer", renommer_sommet, color="blue").grid(row=2, column=0, columnspan=2, pady=5)

        # --- Modifier une arête ---
        self.make_label(inner, "Modifier une arête :", font=("Arial", 12, "bold")).pack(pady=10)
        frame_a = tk.Frame(inner, bg=self.BG)
        frame_a.pack(pady=5)

        labels_a = ["Extrémité 1 :", "Extrémité 2 :", "Nouveau poids :"]
        entries_a = []
        for i, lt in enumerate(labels_a):
            self.make_label(frame_a, lt).grid(row=i, column=0, padx=5)
            e = self.make_entry(frame_a, 10)
            e.grid(row=i, column=1, padx=5)
            entries_a.append(e)

        lbl_msg2 = self.make_label(inner, "")
        lbl_msg2.pack(pady=3)

        def modifier_arete():
            e1, e2, p_txt = [e.get().strip() for e in entries_a]
            try:
                p = float(p_txt)
                if p <= 0:
                    lbl_msg2.config(text="ERREUR. La pondération doit être positive.", fg="red")
                    return
            except ValueError:
                lbl_msg2.config(text="ERREUR. Pondération invalide.", fg="red")
                return
            for i, (u, v, _) in enumerate(self.aretes):
                if {u, v} == {e1, e2}:
                    self.aretes[i] = (u, v, p)
                    lbl_msg2.config(text=f"Arête {e1}—{e2} modifiée (poids: {p}).", fg="green")
                    self.lbl_etat_mod.config(text=self._etat_graphe_txt())
                    return
            lbl_msg2.config(text=f"ERREUR. L'arête {e1}—{e2} n'existe pas.", fg="red")

        self.make_button(frame_a, "Modifier", modifier_arete, color="orange").grid(row=3, column=0, columnspan=2, pady=5)

        # --- Supprimer une arête ---
        self.make_label(inner, "Supprimer une arête :", font=("Arial", 12, "bold")).pack(pady=10)
        frame_d = tk.Frame(inner, bg=self.BG)
        frame_d.pack(pady=5)

        self.make_label(frame_d, "Extrémité 1 :").grid(row=0, column=0, padx=5)
        entry_de1 = self.make_entry(frame_d, 10)
        entry_de1.grid(row=0, column=1, padx=5)
        self.make_label(frame_d, "Extrémité 2 :").grid(row=1, column=0, padx=5)
        entry_de2 = self.make_entry(frame_d, 10)
        entry_de2.grid(row=1, column=1, padx=5)

        lbl_msg3 = self.make_label(inner, "")
        lbl_msg3.pack(pady=3)

        def supprimer_arete():
            e1, e2 = entry_de1.get().strip(), entry_de2.get().strip()
            for i, (u, v, _) in enumerate(self.aretes):
                if {u, v} == {e1, e2}:
                    self.aretes.pop(i)
                    lbl_msg3.config(text=f"Arête {e1}—{e2} supprimée.", fg="green")
                    self.lbl_etat_mod.config(text=self._etat_graphe_txt())
                    return
            lbl_msg3.config(text=f"ERREUR. L'arête {e1}—{e2} n'existe pas.", fg="red")

        self.make_button(frame_d, "Supprimer", supprimer_arete, color="red").grid(row=2, column=0, columnspan=2, pady=5)

        self.make_button(inner, "Fermer et revenir au récapitulatif",
                        lambda: (win.destroy(), self.etape4_modifier_valider()),
                        color="gray").pack(pady=15)

    def _etat_graphe_txt(self):
        txt = f"Sommets : {', '.join(self.sommets)}\n"
        if self.aretes:
            txt += "Arêtes :\n" + "\n".join(f"  {u}—{v} (poids: {p})" for u, v, p in self.aretes)
        else:
            txt += "Arêtes : (aucune)"
        return txt

    # ===================== ÉTAPE 5 : Valider et afficher le graphe =====================
    def valider_graphe(self):
        if not self.aretes:
            messagebox.showerror("Erreur", "ERREUR. Il faut l'existence d'au moins une arete pour calculer le plus court chemin.")
            return

        self.graph = nx.Graph()
        self.graph.add_nodes_from(self.sommets)
        for u, v, p in self.aretes:
            self.graph.add_edge(u, v, weight=p)

        self.clear_frame()
        self.current_frame = tk.Frame(self.root, bg=self.BG)
        self.current_frame.pack(fill="both", expand=True)

        # Navigation
        nav = tk.Frame(self.current_frame, bg="#e0e0e0", pady=5)
        nav.pack(fill="x")
        self.make_button(nav, "← Retour", self.etape4_modifier_valider, color="gray").pack(side="left", padx=10)

        self.make_label(self.current_frame, "Graphe pondéré non orienté", font=self.FONT_B).pack(pady=5)

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

        self.make_button(self.current_frame, "Calculer le PCC", self.etape6_calculer_pcc,
                        color="purple").pack(pady=10)

    # ===================== ÉTAPE 6 : Calculer le PCC (Dijkstra) =====================
    def etape6_calculer_pcc(self):
        win = tk.Toplevel(self.root)
        win.title("Calculer le Plus Court Chemin")
        win.geometry("450x250")
        win.configure(bg=self.BG)

        self.make_label(win, "Plus Court Chemin (Dijkstra)", font=("Arial", 13, "bold")).pack(pady=10)
        self.make_label(win, f"Sommets : {', '.join(self.sommets)}", font=("Arial", 10), fg="#555").pack()

        form = tk.Frame(win, bg=self.BG)
        form.pack(pady=10)

        self.make_label(form, "Sommet source :").grid(row=0, column=0, padx=5, pady=5)
        entry_src = self.make_entry(form, 10)
        entry_src.grid(row=0, column=1, padx=5, pady=5)

        lbl_err = self.make_error_label(win)
        lbl_err.pack(pady=3)

        def calculer():
            src = entry_src.get().strip()
            if src not in self.sommets:
                lbl_err.config(text=f"ERREUR. Le sommet {src} n'existe pas.")
                return

            distances, predecesseurs = self.dijkstra(src)
            win.destroy()
            self.afficher_pcc_tous(src, distances, predecesseurs)

        self.make_button(win, "Calculer", calculer, color="purple").pack(pady=10)

    def dijkstra(self, source):
        distances = {s: float('inf') for s in self.sommets}
        predecesseurs = {s: None for s in self.sommets}
        distances[source] = 0
        visite = set()
        file = [(0, source)]

        while file:
            dist_courante, u = heapq.heappop(file)
            if u in visite:
                continue
            visite.add(u)

            for voisin in self.graph.neighbors(u):
                poids = self.graph[u][voisin]['weight']
                nouvelle_dist = dist_courante + poids
                if nouvelle_dist < distances[voisin]:
                    distances[voisin] = nouvelle_dist
                    predecesseurs[voisin] = u
                    heapq.heappush(file, (nouvelle_dist, voisin))

        return distances, predecesseurs

    def reconstruire_chemin(self, predecesseurs, destination):
        chemin = []
        courant = destination
        while courant is not None:
            chemin.append(courant)
            courant = predecesseurs[courant]
        chemin.reverse()
        return chemin

    # ===================== ÉTAPE 7 : Afficher PCC vers tous les sommets =====================
    def afficher_pcc_tous(self, source, distances, predecesseurs):
        win = tk.Toplevel(self.root)
        win.title(f"Plus Court Chemin depuis {source}")
        win.geometry("900x750")
        win.configure(bg=self.BG)

        # Scrollable
        canvas_scroll = tk.Canvas(win, bg=self.BG, highlightthickness=0)
        scrollbar = ttk.Scrollbar(win, orient="vertical", command=canvas_scroll.yview)
        inner = tk.Frame(canvas_scroll, bg=self.BG)
        inner.bind("<Configure>", lambda e: canvas_scroll.configure(scrollregion=canvas_scroll.bbox("all")))
        canvas_scroll.create_window((0, 0), window=inner, anchor="nw")
        canvas_scroll.configure(yscrollcommand=scrollbar.set)
        canvas_scroll.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        canvas_scroll.bind_all("<MouseWheel>", lambda e: canvas_scroll.yview_scroll(int(-1 * (e.delta / 120)), "units"))

        self.make_label(inner, f"Plus Court Chemin depuis '{source}' vers tous les sommets",
                       font=self.FONT_B).pack(pady=10)

        # Tableau des résultats
        table_frame = tk.Frame(inner, bg=self.BG)
        table_frame.pack(pady=10, padx=20)

        headers = ["Destination", "Distance", "Chemin"]
        for j, h in enumerate(headers):
            tk.Label(table_frame, text=h, font=("Arial", 11, "bold"), bg="#ddd",
                    relief="ridge", width=20, padx=5, pady=3).grid(row=0, column=j, sticky="nsew")

        row_idx = 1
        # Collecter toutes les arêtes du PCC pour la visualisation
        all_pcc_edges = set()

        for dest in self.sommets:
            if dest == source:
                continue
            dist = distances[dest]
            if dist == float('inf'):
                chemin_str = "Aucun chemin"
                dist_str = "∞"
            else:
                chemin = self.reconstruire_chemin(predecesseurs, dest)
                chemin_str = " → ".join(chemin)
                dist_str = str(dist)
                for i in range(len(chemin) - 1):
                    all_pcc_edges.add((chemin[i], chemin[i + 1]))
                    all_pcc_edges.add((chemin[i + 1], chemin[i]))

            for j, val in enumerate([dest, dist_str, chemin_str]):
                bg_color = "#e8f5e9" if dist != float('inf') else "#ffebee"
                tk.Label(table_frame, text=val, font=self.FONT_S, bg=bg_color,
                        relief="ridge", width=20, padx=5, pady=3).grid(row=row_idx, column=j, sticky="nsew")
            row_idx += 1

        # Graphe avec PCC mis en évidence
        fig, ax = plt.subplots(figsize=(7, 5))

        node_colors = ["#66BB6A" if n == source else "#4FC3F7" for n in self.graph.nodes()]

        edge_colors = []
        edge_widths = []
        for u, v in self.graph.edges():
            if (u, v) in all_pcc_edges:
                edge_colors.append("#E53935")
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

        ax.set_title(f"Arbre des plus courts chemins depuis '{source}'", fontsize=12)
        fig.tight_layout()

        canvas = FigureCanvasTkAgg(fig, master=inner)
        canvas.draw()
        canvas.get_tk_widget().pack(fill="both", expand=True, padx=10, pady=10)

        self.make_button(inner, "Fermer", win.destroy, color="gray").pack(pady=10)


if __name__ == "__main__":
    root = tk.Tk()
    app = DijkstraApp(root)
    root.mainloop()
