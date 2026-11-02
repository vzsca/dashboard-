"""V2 : détecter les attaques par force brute.

Une attaque par force brute, c'est un robot qui essaie des mots de passe
à la chaîne. Dans le journal, ça donne beaucoup d'échecs, depuis la même
adresse IP, en très peu de temps.

Règle de Vigie :
  une adresse IP est signalée si elle fait au moins SEUIL_ECHECS échecs
  dans une fenêtre de FENETRE_SECONDES secondes.

Pourquoi pas simplement "plus de 5 échecs au total" ? Parce qu'un employé
qui se trompe de mot de passe une fois par jour finirait par être signalé
au bout d'une semaine. C'est ce qui arrive à 10.30.10.58 dans le journal :
7 échecs, mais étalés sur toute la semaine. Ce n'est pas une attaque.

Une fenêtre, c'est un paquet d'échecs consécutifs d'une même IP, où
(heure du dernier) - (heure du premier) est au plus égal à 60 secondes.
Exactement 60 secondes compte comme dans la fenêtre.
"""

FENETRE_SECONDES = 60
SEUIL_ECHECS = 5


def grouper_echecs_par_ip(evenements):
    """Rend un dictionnaire {ip: liste des événements en échec de cette ip}."""
    groupes = {}
    # A FAIRE (V2) : Remplis le dictionnaire groupes.
    #                - ne regarde que les événements dont le résultat est "echec"
    #                - la clé est l'adresse IP, la valeur est la liste de ses événements
    #                - indice : groupes.setdefault(ip, []).append(evenement) crée la liste au premier passage
    for evenement in evenements:
        if evenement["resultat"] == "echec":
            groupes.setdefault(evenement["ip"], []).append(evenement)
    return groupes


def fabriquer_alerte(ip, fenetre, total):
    """Construit le dictionnaire d'une alerte à partir de la meilleure fenêtre."""
    return {
        "ip": ip,
        "nb_echecs": len(fenetre),
        "debut": fenetre[0]["date"],
        "fin": fenetre[-1]["date"],
        "utilisateurs": sorted({e["utilisateur"] for e in fenetre}),
        "total_echecs": total,
    }


def detecter_alertes(evenements):
    """Rend la liste des alertes, la plus grosse attaque en premier."""
    alertes = []
    groupes = grouper_echecs_par_ip(evenements)
    for ip, echecs in groupes.items():
        echecs = sorted(echecs, key=lambda e: e["date"])  # du plus ancien au plus récent
        meilleure = []  # la plus grosse fenêtre trouvée pour cette adresse
        # A FAIRE (V2) : Trouve la plus grosse fenêtre de cette IP et crée l'alerte si elle atteint le seuil.
        #                - pour chaque échec i, forme une fenêtre qui commence à echecs[i]
        #                - ajoute-y les échecs suivants tant que (date du suivant - date de echecs[i]).total_seconds() <= FENETRE_SECONDES
        #                - garde dans meilleure la fenêtre la plus longue (strictement plus longue que la précédente)
        #                - si len(meilleure) >= SEUIL_ECHECS : alertes.append(fabriquer_alerte(ip, meilleure, len(echecs)))
        for i, premier in enumerate(echecs):
            fenetre = [premier]
            for suivant in echecs[i + 1:]:
                ecart = (suivant["date"] - premier["date"]).total_seconds()
                if ecart > FENETRE_SECONDES:
                    break
                fenetre.append(suivant)
            if len(fenetre) > len(meilleure):
                meilleure = fenetre
        if len(meilleure) >= SEUIL_ECHECS:
            alertes.append(fabriquer_alerte(ip, meilleure, len(echecs)))
    alertes.sort(key=lambda a: (-a["nb_echecs"], a["ip"]))
    return alertes


def ips_compromises(evenements, alertes):
    """Rend l'ensemble des IP qui ont réussi à se connecter APRÈS leur attaque.

    C'est le pire scénario : le robot a fini par trouver le bon mot de passe.
    """
    compromises = set()
    for alerte in alertes:
        for evenement in evenements:
            if (evenement["resultat"] == "succes"
                    and evenement["ip"] == alerte["ip"]
                    and evenement["date"] > alerte["fin"]):
                compromises.add(alerte["ip"])
    return compromises
