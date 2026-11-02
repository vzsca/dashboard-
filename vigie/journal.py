"""V1 : lire le journal d'authentification SSH.

Le fichier donnees/auth.log est le journal du service SSH des serveurs.
Une ligne de connexion ressemble à ça :

  Oct 27 07:55:42 srv-files-01 sshd[23688]: Failed password for user03 from 10.30.10.58 port 43574 ssh2

Si tu la coupes avec split(), tu obtiens une liste de morceaux numérotés
à partir de 0 :

   0 Oct        1 27          2 07:55:42     3 srv-files-01   4 sshd[23688]:
   5 Failed     6 password    7 for          8 user03 9 from
  10 10.30.10.58  11 port     12 43574       13 ssh2

Quand le compte n'existe pas, la ligne contient deux mots de plus :

  Oct 29 03:12:08 srv-web-01 sshd[2211]: Failed password for invalid user admin from 203.0.113.45 port 50122 ssh2

Le nom du compte n'est alors plus au même endroit (morceau 10 au lieu de 8).
C'est le piège de cette étape : cherche les repères "for", "user" et "from"
plutôt que de compter les positions.

Le journal contient aussi du bruit (déconnexions, sessions PAM, "Invalid user"...).
On ne garde que deux sortes de lignes : "Failed password" et "Accepted".
"""
from outils import lire_date


def parse_ligne(ligne):
    """Transforme une ligne du journal en dictionnaire, ou rend None.

    Le dictionnaire rendu a cinq clés :
      "date"        une vraie date Python (voir lire_date)
      "hote"        le nom du serveur, par exemple "srv-files-01"
      "resultat"    "echec" ou "succes"
      "ip"          l'adresse IP d'où vient la connexion
      "utilisateur" le compte visé
    Pour une ligne qui n'est ni un échec ni une réussite, on rend None.
    """
    evenement = None  # reste None tant que tu n'as rien décidé
    # A FAIRE (V1) : Remplis la variable evenement pour une ligne de connexion.
    #                - 1) coupe la ligne en morceaux : morceaux = ligne.split()
    #                - 2) échec si les morceaux 5 et 6 valent "Failed" et "password", réussite si le morceau 5 vaut "Accepted", sinon return None
    #                - 3) l'IP est le morceau juste après "from" : morceaux.index("from") te donne sa place
    #                - 4) le compte suit "user" si la ligne contient "invalid", sinon il suit "for"
    #                - 5) evenement = dictionnaire avec les 5 clés ci-dessus (la date vient de lire_date avec les morceaux 0, 1 et 2)
    #                - indice : une ligne trop courte doit aussi rendre None
    morceaux = ligne.split()
    if len(morceaux) < 6:
        return None
    if morceaux[5] == "Failed" and len(morceaux) > 6 and morceaux[6] == "password":
        resultat = "echec"
    elif morceaux[5] == "Accepted":
        resultat = "succes"
    else:
        return None

    try:
        position_from = morceaux.index("from")
        position_compte = morceaux.index("user") + 1 if "invalid" in morceaux else morceaux.index("for") + 1
        ip = morceaux[position_from + 1]
        utilisateur = morceaux[position_compte]
        date = lire_date(morceaux[0], morceaux[1], morceaux[2])
        hote = morceaux[3]
    except (ValueError, IndexError):
        return None

    evenement = {
        "date": date,
        "hote": hote,
        "resultat": resultat,
        "ip": ip,
        "utilisateur": utilisateur,
    }
    return evenement


def lire_journal(chemin):
    """Lit tout le fichier et rend la liste des événements (un par ligne utile)."""
    evenements = []
    # A FAIRE (V1) : Lis le fichier ligne par ligne et remplis la liste evenements.
    #                - ouvre le fichier avec : with open(chemin, encoding="utf-8") as f:
    #                - parcours-le avec : for ligne in f:
    #                - appelle parse_ligne(ligne) et ajoute le résultat à la liste seulement s'il n'est pas None
    with open(chemin, encoding="utf-8") as f:
        for ligne in f:
            evenement = parse_ligne(ligne)
            if evenement is not None:
                evenements.append(evenement)
    return evenements
