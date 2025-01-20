from random import randint, expovariate
import tkinter as tk
from tkinter import ttk
from time import sleep
from threading import Thread


class Buffer:
    """
    Classe Buffer

    Cette classe représente une file d'attente pour stocker des paquets de données.
    Elle offre des fonctionnalités pour ajouter, retirer et transmettre des paquets,
    ainsi que pour vérifier l'état de la file d'attente.

    Args:
        * C (int):
            La capacité maximale de la file d'attente.

    Attributs:
        * capacite (int):
            La capacité maximale de la file d'attente, en unités de taille de paquet.
        * file_attente (list):
            Une liste contenant les paquets actuellement stockés dans la file d'attente.

    Méthodes:
        * buffer_plein(self, nouveau_paquet) -> bool:
            Vérifie si l'ajout d'un nouveau paquet rendrait la file d'attente pleine.
            Args:
                * nouveau_paquet (Paquet):
                    Le paquet dont la taille doit être testé
            return:
                * bool:
                    True: si nouvelle taille > à l'ancienne
                    False: si nouvelle taille < à l'ancienne
        * __add__(self, nouveau_paquet) -> Buffer: 
            Surcharge de l'opérateur +. Ajoute un nouveau paquet a la file d'attente s'il n'est pas plein.
            Args:
                * nouveau_paquet (Paquet):
                    Le paquet à ajouter.
            Returns:
                * Buffer:
                    La file d'attente elle-même.
        * __sub__(self, paquet) -> tuple: 
            Retire un paquet de la file d'attente s'il y en a un.
            Args:
                * paquet (Paquet):
                    Le paquet à retirer.
            Returns:
                * tuple:
                    Un tuple contenant (le tampon, le paquet retiré) si le paquet est trouvé, sinon (le tampon, None).
        * transmettre_paquet(self) -> tuple: 
            Transmet le premier paquet du tampon et le retire du tampon.
            Returns:
                * tuple:
                    Un tuple contenant (le paquet transmis, le tampon) si le tampon n'est pas vide, sinon (None, le tampon).
        * pourcentage_rempli(self) -> float: 
            Calcule le pourcentage de remplissage du tampon.
            Returns:
                * float:
                    Le pourcentage de remplissage du tampon (0 si le tampon est vide).
    """
    def __init__(self, C):
        self.capacite = C
        self.file_attente = []

    def buffer_plein(self, nouveau_paquet):
        return (sum(paquet.taille for paquet in self.file_attente) + nouveau_paquet.taille) > self.capacite

    def __add__(self, nouveau_paquet):
        if not self.buffer_plein(nouveau_paquet):
            self.file_attente.append(nouveau_paquet)
        return self

    def __sub__(self, paquet):
        if paquet in self.file_attente:
            self.file_attente.remove(paquet)
            return self, paquet
        return self, None

    def transmettre_paquet(self):
        if self.file_attente:
            paquet_a_transmettre = self.file_attente[0]
            self - paquet_a_transmettre
            return paquet_a_transmettre, self
        return None, self

    def pourcentage_rempli(self):
        if self.file_attente:
            return (sum(paquet.taille for paquet in self.file_attente) / self.capacite) * 100
        else:
            return 0


class Source:
    """
    Classe représentant une source de paquets dans un réseau.

    Args:
        * lambda_param (float): 
            Paramètre de la loi exponentielle qui détermine le taux d'arrivée des paquets.
        * taille_max_paquet (int):
            Taille maximale des paquets générés.
    Attributs:
        * lambda_param (float):
            Paramètre de la loi exponentielle qui détermine le taux d'arrivée des paquets.
        * taille_max_paquet (int):
            Taille maximale des paquets générés.
        * nb_paquet_genere (int):
            Nombre de paquets générés par la source.
        * nb_paquet_perdu (int):
            Nombre de paquets perdus par la source.

    Méthodes:
        * generation_paquet() -> Paquet:
            Génère un nouveau paquet et incrémente le nombre de paquets générés.
            Return:
                * Objet:
                    un objet paquet de taille aléatoire de 1 à self.taille_max_paquet
        * estimation_taux_arrive() -> float:
            Estime le taux d'arrivée des paquets en utilisant la loi exponentielle.
            Returns:
                * float:
                    Le taux d'arrivée estimé.
    """

    def __init__(self, lambda_param, taille_max_paquet):
        self.lambda_param = lambda_param
        self.taille_max_paquet = taille_max_paquet
        self.nb_paquet_genere = 0
        self.nb_paquet_perdu = 0

    def generation_paquet(self):
        self.nb_paquet_genere += 1
        return Paquet(randint(1, self.taille_max_paquet))

    def estimation_taux_arrive(self):
        return 1 / expovariate(self.lambda_param)


class Paquet:
    """
    Classe représentant un paquet de données dans un réseau.

    Args:
        * taille (int): Taille du paquet en octets.
    Attributs:
        * taille (int): Taille du paquet en octets.
    """
    def __init__(self, taille):
        self.taille = taille


class Interface():
    """
    Représente l'interface utilisateur pour une simulation de réseau.

    Cette classe gère la création et la gestion des éléments de l'interface graphique (widgets)
    utilisés pour interagir avec les paramètres de la simulation et visualiser les résultats.

    Attributs:
        * maitre (tk.Tk): La fenêtre principale de l'application Tkinter.
        * parametre (dict): Un dictionnaire contenant les paramètres de simulation par défaut.
            Clés :
                * "lambda_param" : Paramètre de taux d'arrivée pour la génération de paquets (float).
                *  "taille_max_paquet" : Taille maximale des paquets (int).
                * "capacite_buffer" : Capacité du buffer principal (int).
                * "taux_transmission" : Taux de transmission du réseau (float).
                * "nb_paquet" : Nombre total de paquets à générer (int).
                * "nb_buffer" : Nombre de sous-buffers (int).
                * "capacite_sous_buffer" : Capacité de chaque sous-buffer (int).
        * mode_ (int): Index de sélection courant pour le mode de simulation (0, 1 ou 2).
        * liste_mode (list): Liste des modes de simulation disponibles (chaînes de caractères).
        * widgets (méthode): Crée et organise les widgets de l'interface.

    Méthodes:
        * widgets() -> None:
            Initialise la disposition de l'interface avec des étiquettes, des champs de saisie,
            des boutons, une barre de progression, des étiquettes et un canevas pour la visualisation.

        * representation() -> None:
            Dessine la représentation visuelle initiale des buffers en fonction
            des paramètres de simulation actuels.

        * demarrer_sim() -> None:
            Lance le thread de simulation, récupère les valeurs des paramètres saisis par l'utilisateur,
            crée des objets sources et buffers, et initialise le thread de simulation
            avec tous les composants et paramètres nécessaires.

        * mode() -> None:
            Parcourt les modes de simulation disponibles et met à jour l'étiquette du mode en conséquence.

        * stop_sim() -> None:
            Arrête en toute sécurité le thread de simulation en cours s'il existe.

        * compteur_paquet() -> None:
            Met à jour l'étiquette affichant le nombre restant de paquets à générer.

        * rafraichissement_barre_chargement() -> None:
            Met à jour la barre de progression pour refléter le pourcentage d'utilisation actuel du buffer.

        * rafraichissement_label_paquet_perdu() -> None:
            Calcule et met à jour l'étiquette affichant le pourcentage de perte de paquets.
    """
    def __init__(self, master):
        """
        Constructeur de la classe Interface.

        Args:
            * maitre (tk.Tk): La fenêtre principale de l'application Tkinter.
        """
        self.master = master
        self.parametre = {
            "lambda_param": 1,
            "taille_max_paquet": 1,
            "capacite_buffer": 1,
            "taux_transmission": 1,
            "nb_buffer": 1,
            "nb_paquet": 50,
            "capacite_sous_buffer": 1
        }
        self.mode_ = 0
        self.liste_mode = ["chacun son tour", "aléatoire", "la plus pleine"]
        self.widgets()


    def widgets(self):
        labels = [
            "Lambda paramètre:", "Taille max des paquets:",
            "Capacité du buffer:", "Taux de transmission:",
            "Nombre de paquets:", "Nombre de sous buffer et source:",
            "Capacité max des sous buffers: "
        ]
        entries = [
            "lambda_param", "taille_max_paquet", "capacite_buffer",
            "taux_transmission", "nb_paquet", "nb_buffer", "capacite_sous_buffer"
        ]
        for i, label_text in enumerate(labels):
            tk.Label(self.master, text=label_text).grid(row=i, column=0)
            # Crée dynamiquement un attribut nommé f"saisie_{entrees[i]}" sur self
            setattr(self, f"saisie_{entries[i]}", tk.Entry(self.master, textvariable=tk.StringVar(value=self.parametre[entries[i]])))
            # fonction intégrée qui permet d'accéder dynamiquement à un attribut d'un objet
            # en utilisant son nom sous forme de chaîne de caractères.
            getattr(self, f"saisie_{entries[i]}").grid(row=i, column=1)

        tk.Button(self.master, text="Démarrer la simulation", command=self.demarrer_sim).grid(row=7, column=0)
        tk.Button(self.master, text="Arrêter la simulation", command=self.stop_sim).grid(row=7, column=1)

        self.label_buffer_utilisation = tk.Label(self.master, text="Buffer Utilisation: 0%")
        self.label_buffer_utilisation.grid(row=8, column=0)
        self.barre_chargement = ttk.Progressbar(self.master, orient="horizontal", mode="determinate", length=200)
        self.barre_chargement.grid(row=8, column=1)

        self.label_paquet_perdu = tk.Label(self.master, text="Paquet perdu: 0%")
        self.label_paquet_perdu.grid(row=9, column=0)
        self.compteur = tk.Label(self.master, text=f"Paquets restants: {self.parametre['nb_paquet']}")
        self.compteur.grid(row=9, column=1)

        tk.Button(self.master, text="Changer le mode", command=self.mode).grid(row=10, column=0)
        self.mode_label = tk.Label(self.master, text=f"Mode : {self.liste_mode[self.mode_]}")
        self.mode_label.grid(row=10, column=1)

    def representation(self):
        self.canvas.grid(column=0, row=11, columnspan=10)
        for i in range(len(self.buffers)):
            self.canvas.create_rectangle(10, 200+i*50, 410, 220+i*50, fill="white", outline="black")
            self.canvas.create_text(300,  200+i*50-10, text=f"Sous Buffer {i+1}")
            for j in range(20, 400, 20):
                self.canvas.create_line(10+j, 200+i*50, 10+j, 220+i*50, fill="black", width=1)

            self.canvas.create_line(410, 200+i*50, 560, 270, fill="black", width=2)
        self.canvas.create_rectangle(560, 250, 960, 270, fill="white", outline="black")
        for i in range(20, 400, 20):
            self.canvas.create_line(560+i, 250, 560+i, 270, fill="black", width=1)
        self.canvas.create_text(750, 140, text="Buffer")

    def demarrer_sim(self):
        self.params = {key: float(getattr(self, f"saisie_{key}").get()) for key in self.parametre.keys()}
        self.nb_sous_buffer = int(self.params.pop("nb_buffer"))

        self.sources = [Source(randint(1, self.params['lambda_param']), self.params['taille_max_paquet']) for _ in range(self.nb_sous_buffer)]
        self.buffers = [Buffer(randint(1, self.params["capacite_sous_buffer"])) for _ in range(self.nb_sous_buffer)]
        self.buffer = Buffer(self.params["capacite_buffer"])

        self.sim_thread = SimulationThread(self, self.sources, self.buffers, self.params["taux_transmission"], self.params["nb_paquet"], self.buffer, self.nb_sous_buffer, self.liste_mode[self.mode_])
        self.canvas = tk.Canvas(self.master, width=1600, height=600, bg="white") 
        self.representation()
        self.sim_thread.start()

    def mode(self):
        self.mode_ = (self.mode_ + 1) % 3
        self.mode_label.config(text=f"mode : {self.liste_mode[self.mode_]}")

    def stop_sim(self):
        if self.sim_thread:
            self.sim_thread.stop()

    def compteur_paquet(self):
        self.nb_paquets_restant = int(self.params["nb_paquet"]) - self.sources[0].nb_paquet_genere
        self.compteur.config(text=f"Paquets restants: {self.nb_paquets_restant}")

    def rafraichissement_barre_chargement(self):
        valeur = self.buffer.pourcentage_rempli()
        self.barre_chargement["value"] = valeur
        self.label_buffer_utilisation.config(text=f"Buffer Utilization: {valeur:.1f}%")

    def rafraichissement_label_paquet_perdu(self):
        nb_paquet_genere = sum(source.nb_paquet_genere for source in self.sources)
        nb_paquet_perdu = sum(source.nb_paquet_perdu for source in self.sources)
        valeur = nb_paquet_perdu / nb_paquet_genere * 100 if nb_paquet_genere != 0 else 0
        self.label_paquet_perdu.config(text=f"Paquet perdu: {valeur:.1f}%")


class SimulationThread(Thread):
    """
    Simule un réseau ou un système de communication, en gérant la génération, la
    transmission et la perte potentielle de paquets de données.

    Cette classe s'exécute en tant que thread distinct et interagit avec une interface
    utilisateur graphique (GUI) pour visualiser le processus de simulation.

    Args:
        * interface -> objet:
            L'objet GUI pour la visualisation et les mises à jour des données.
        * sources -> liste: 
            Une liste d'objets représentant les sources de paquets.
        * buffers -> liste: 
            Une liste d'objets représentant des tampons pour le stockage temporaire des paquets.
        * taux_transmission -> float:
            Le taux de transmission du réseau (paquets par unité de temps).
        * nb_paquet -> int:
            Le nombre total de paquets à simuler.
        * buffer -> objet:
            Un objet représentant un tampon central pouvant recevoir des paquets.
        * nb_source -> int:
            Le nombre d'objets source.
        * mode -> str:
            La stratégie de sélection du tampon vers lequel envoyer les paquets:
                - "chacun son tour": Sélectionne chaque buffer a tour de rôle.
                - "aléatoire" : Sélection aléatoirement un buffer.
                - "la plus pleine" : Sélectionne le buffer le plus plein.

    Attributs:
        * running (bool):
            Indicateur indiquant si la simulation est en cours.
        * conter (int):
            Compteur du nombre de paquets simulés.
        * x2 (int):
            Variable interne probablement utilisée à des fins d'animation.
        * paquet (liste):
            Liste pour stocker les représentations graphiques des paquets.
        * transmits (liste):
            Liste pour stocker les représentations graphiques des paquets en transit.
        * couleur (liste):
            Liste contenant des noms de couleurs pour la visualisation des paquets.
        * abscisse (liste):
            Liste contenant les coordonnées x initiales pour la visualisation des paquets.
    
    Methods:
        * show_paquets(abscisse, i) -> None:
            Gère la représentation visuelle des paquets et leur mouvement simulé.
            Cette méthode crée des rectangles pour représenter les paquets et anime
            leur déplacement sur l'interface graphique.
            Args:
                * abscisse (liste):
                    Liste des coordonnées x pour les paquets.
                * i (int):
                    Indice de la file d'attente considéré.

        * run() -> None:
            Boucle principale de la simulation, gérant la génération de paquets,
            leur interaction avec les tampons, la transmission et la perte potentielle.
            Cette méthode contrôle le déroulement de la simulation jusqu'à ce que le nombre
            de paquets simulé atteigne la valeur définie dans 'nb_paquet'.
    """
    def __init__(self, interface, sources, buffers, taux_transmission, nb_paquet, buffer, nb_source, mode):
        # un appel à la méthode __init__ de la classe parent (Thread). 
        # Cet appel garantit que la méthode __init__ de la classe parent est exécutée en premier,
        # initialisant tous les attributs ou effectuant les tâches de configuration requises par la classe Thread.
        super().__init__()
        self.interface = interface
        self.buffers = buffers
        self.sources = sources
        self.buffer = buffer
        self.taux_transmission = taux_transmission
        self.nb_paquet = nb_paquet
        self.nb_source = nb_source
        self.running = True
        self.conter = 0
        self.mode = mode
        self.x2=550
        self.paquet=[]
        self.transmits=[]
        couleur=['blue','green','red','yellow']
        self.couleur=[couleur[i % 4] for i in range(len(buffers))]
        self.abscisse=[410 for _ in range(len(buffers))]

    def show_paquets(self,abscisse,i):
        if abscisse[i] >= 20:
            paq=self.interface.canvas.create_rectangle(abscisse[i]-20,200+50*i,abscisse[i],220+50*i,fill=self.couleur[i])
            paq
            self.paquet.append(paq)
            abscisse[i]-=20
        sleep(0.1)
        if len(self.paquet)!=0:
            elem=self.paquet.pop(0)
            self.transmits.append(elem)
            if self.x2>=0:
                self.interface.canvas.move(elem,self.x2,50-i*50)
                self.x2-=20
                abscisse[i]+=20
        if len(self.transmits)>20:
            self.x2+=20
            a_supp=self.transmits.pop(0)
            self.interface.canvas.delete(a_supp)
            for p in self.transmits:
                z1, w1, z2, w2 = self.interface.canvas.coords(p)
                self.interface.canvas.coords(p, z1+20, w1, z1+40, w2)

    def run(self):
        while self.running:
            estimation = 0
            k = 0
            for source, buffer in zip(self.sources, self.buffers):      
                paquet = source.generation_paquet()
                if source.estimation_taux_arrive() > self.taux_transmission:
                    if buffer.buffer_plein(paquet):
                        source.nb_paquet_perdu += 1
                    else:
                        buffer += paquet
                else:
                    estimation += source.estimation_taux_arrive()

                if self.mode == "aléatoire":
                    val=randint(0, len(self.buffers) - 1)
                    buffer = self.buffers[val]
                    self.show_paquets(self.abscisse,val)
                elif self.mode == "la plus pleine":
                    buffer = max(self.buffers, key=lambda buf: buf.pourcentage_rempli())
                    c = [z for z in range(len(self.buffers)) if buffer == self.buffers[z]]
                    self.show_paquets(self.abscisse, c[0])
                else:
                    self.show_paquets(self.abscisse, k)
                if buffer.file_attente:
                    if not self.buffer.buffer_plein(buffer.file_attente[0]):
                        paquet_transmit, _ = buffer.transmettre_paquet()
                        self.buffer += paquet_transmit
                k += 1
            if self.buffer and estimation > self.taux_transmission:
                self.buffer.transmettre_paquet()

            self.conter += 1
            if self.conter == self.nb_paquet:
                self.stop()

            if len(self.transmits)>20:
                self.x2+=20
                a_supp=self.transmits.pop(0)
                self.interface.canvas.delete(a_supp)
                for p in self.transmits:
                    z1, w1, z2, w2 = self.interface.canvas.coords(p)
                    self.interface.canvas.coords(p, z1+20, w1, z1+40, w2)
            
            
            self.interface.compteur_paquet()
            self.interface.rafraichissement_barre_chargement()
            self.interface.rafraichissement_label_paquet_perdu()
            self.interface.master.update()
            sleep(0.1)

        for buf in self.buffers:
            while buf.file_attente:
                transmi, _ = buf.transmettre_paquet()
                self.buffer += transmi
                while self.buffer.file_attente:
                    self.buffer.transmettre_paquet()
                    self.interface.rafraichissement_barre_chargement()
                    self.interface.master.update()
                    sleep(0.1)
        
        if len(self.paquet)==0 and len(self.transmits)!=0:
            while len(self.transmits)!=0:
                a_supp=self.transmits.pop(0)
                self.interface.canvas.delete(a_supp)
                for p in self.transmits:
                    z1, w1, z2, w2 = self.interface.canvas.coords(p)
                    self.interface.canvas.coords(p, z1+20, w1, z1+40, w2)
                sleep(0.1)
        self.interface.canvas.destroy()

    def stop(self):
        self.running = False


if __name__ == '__main__':
    """
    Lance l'interface graphique de la simulation de réseau.

    Cette fonction crée une instance de la classe `Tk` de la bibliothèque tkinter,
    qui sert de base pour l'interface graphique (GUI). Ensuite, elle crée une instance
    de la classe `Interface` définie dans le même module, en lui passant la référence
    à la fenêtre racine (`root`). Cette instance de `Interface` est responsable de
    la création et de la gestion des éléments visuels de l'interface. Enfin, elle
    démarre la boucle principale de l'interface graphique en appelant la méthode `mainloop()`
    de l'objet `root`.
    """
    root = tk.Tk()
    Interface(root)
    root.mainloop()
