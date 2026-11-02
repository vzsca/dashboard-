"""Petites fonctions utilitaires de Vigie.

Tu n'as rien à modifier dans ce fichier. Les autres fichiers s'en servent.
"""
import os
import ipaddress
from datetime import datetime

# Le kit, c'est le dossier qui contient le dossier "vigie".
# On le calcule à partir de l'emplacement de ce fichier : comme ça,
# Vigie marche où que tu aies extrait le zip.
RACINE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DOSSIER_DONNEES = os.path.join(RACINE, "donnees")
DOSSIER_RAPPORTS = os.path.join(RACINE, "rapports")

# Les mois tels qu'ils sont écrits dans un journal Linux (syslog).
MOIS = {
    "Jan": 1, "Feb": 2, "Mar": 3, "Apr": 4, "May": 5, "Jun": 6,
    "Jul": 7, "Aug": 8, "Sep": 9, "Oct": 10, "Nov": 11, "Dec": 12,
}


def lire_date(mois, jour, heure, annee=2026):
    """Transforme les trois morceaux d'une date de journal en vraie date Python.

    Exemple : lire_date("Oct", "27", "07:55:42") donne le 27 octobre 2026 à 07:55:42.
    Un journal syslog ne contient pas l'année, on la fixe donc à 2026.
    """
    h, m, s = heure.split(":")
    return datetime(annee, MOIS[mois], int(jour), int(h), int(m), int(s))


def formater_date(date):
    """Écrit une date lisible pour le rapport : 27/10 07:55:42."""
    return date.strftime("%d/%m %H:%M:%S")


def ip_valide(texte):
    """Vrai si le texte est une adresse IP correcte, faux sinon.

    Cette fonction sert de barrière : on ne laisse jamais passer un texte
    qui n'est pas exactement une adresse IP.
    """
    if not isinstance(texte, str):
        return False
    try:
        ipaddress.ip_address(texte)
    except ValueError:
        return False
    return True
