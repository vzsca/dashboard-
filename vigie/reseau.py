"""V3 : savoir d'où vient une adresse IP.

Une adresse IP peut être de trois sortes :
  - "interne"            elle est dans le plan d'adressage de l'entreprise
  - "interne hors plan"  elle ressemble à une adresse privée, mais personne
                         ne l'a déclarée dans le plan : un équipement inconnu
  - "externe"            elle vient d'Internet

Les adresses privées (RFC 1918) sont réservées aux réseaux d'entreprise :
  10.0.0.0/8   172.16.0.0/12   192.168.0.0/16
On les liste ici explicitement. N'utilise pas ip.is_private : cette propriété
est aussi vraie pour les adresses de documentation (203.0.113.x, 198.51.100.x,
192.0.2.x) que le journal utilise pour représenter Internet.
"""
import csv
import ipaddress

RESEAUX_PRIVES = [
    ipaddress.ip_network("10.0.0.0/8"),
    ipaddress.ip_network("172.16.0.0/12"),
    ipaddress.ip_network("192.168.0.0/16"),
]


def charger_plan(chemin):
    """Lit donnees/plan-adressage.csv et rend une liste de dictionnaires.

    Le fichier a quatre colonnes séparées par des points-virgules :
      reseau;site;famille;description
    Chaque dictionnaire rendu a les mêmes quatre clés. La valeur de "reseau"
    doit être un vrai objet réseau (ipaddress.ip_network), pas un texte.
    """
    plan = []
    # A FAIRE (V3) : Lis le fichier CSV et remplis la liste plan.
    #                - ouvre-le avec : with open(chemin, encoding="utf-8", newline="") as f:
    #                - lecteur = csv.DictReader(f, delimiter=";") donne une ligne = un dictionnaire
    #                - pour chaque ligne, ajoute à plan un dictionnaire avec les clés reseau, site, famille, description
    #                - pour la clé reseau, utilise ipaddress.ip_network(ligne["reseau"])
    with open(chemin, encoding="utf-8", newline="") as f:
        lecteur = csv.DictReader(f, delimiter=";")
        for ligne in lecteur:
            plan.append({
                "reseau": ipaddress.ip_network(ligne["reseau"]),
                "site": ligne["site"],
                "famille": ligne["famille"],
                "description": ligne["description"],
            })
    return plan


def classer_ip(ip, plan):
    """Rend un dictionnaire {"type", "site", "famille"} pour une adresse IP.

    Exemples attendus :
      "10.30.40.7"   {"type": "interne", "site": "Site B", "famille": "scanners"}
      "192.168.1.14" {"type": "interne hors plan", "site": "inconnu", "famille": "inconnue"}
      "203.0.113.45" {"type": "externe", "site": "-", "famille": "-"}
    """
    adresse = ipaddress.ip_address(ip)
    classe = {"type": "externe", "site": "-", "famille": "-"}
    # A FAIRE (V3) : Décide dans quelle catégorie tombe l'adresse.
    #                - adresse = ipaddress.ip_address(ip)
    #                - par défaut, classe vaut {"type": "externe", "site": "-", "famille": "-"}
    #                - si l'adresse est dans un des RESEAUX_PRIVES (test : adresse in reseau), classe devient {"type": "interne hors plan", "site": "inconnu", "famille": "inconnue"}
    #                - ensuite parcours le plan : si l'adresse est dans ligne["reseau"], classe devient {"type": "interne", "site": ligne["site"], "famille": ligne["famille"]} et tu sors de la boucle avec break
    for reseau in RESEAUX_PRIVES:
        if adresse in reseau:
            classe = {"type": "interne hors plan", "site": "inconnu", "famille": "inconnue"}
            break
    for ligne in plan:
        if adresse in ligne["reseau"]:
            classe = {"type": "interne", "site": ligne["site"], "famille": ligne["famille"]}
            break
    return classe
