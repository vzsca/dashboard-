"""V4 : voir quels ports sont ouverts sur TON poste.

Un service réseau (site web, base de données...) écoute sur un numéro de
port. Un port "ouvert" veut dire : un programme répond quand on frappe à la porte.

Règle absolue de cet atelier : Vigie ne teste QUE la machine locale,
127.0.0.1, et QUE les ports de la liste PORTS_SURVEILLES ci-dessous.
Il n'existe aucune option pour viser autre chose, et le code refuse
tout port qui n'est pas dans la liste. Ne cherche pas à contourner ça :
sonder le réseau de l'école ou le poste de quelqu'un d'autre est un délit
(article 323-1 du Code pénal), même "pour voir".
"""
import socket

ADRESSE = "127.0.0.1"  # écrit en dur, volontairement

PORTS_SURVEILLES = {
    21: "FTP",
    22: "SSH",
    23: "Telnet",
    80: "HTTP",
    135: "RPC Windows",
    139: "NetBIOS",
    443: "HTTPS",
    445: "SMB (partage de fichiers)",
    3306: "MySQL",
    3389: "Bureau à distance (RDP)",
    5432: "PostgreSQL",
    8080: "HTTP alternatif",
}

# Ports dont l'ouverture est risquée : protocoles anciens ou non chiffrés.
PORTS_RISQUES = {21, 23, 135, 139, 445, 3389}

DELAI = 0.3  # secondes d'attente maximum par port


def tester_port(port):
    """Rend True si un programme écoute sur ce port de 127.0.0.1, sinon False."""
    if port not in PORTS_SURVEILLES:
        raise ValueError(f"Port {port} refusé : il n'est pas dans la liste surveillée")
    ouvert = False
    # A FAIRE (V4) : Teste le port avec un socket et mets le résultat dans ouvert.
    #                - ouvre un socket : with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
    #                - limite l'attente avec s.settimeout(DELAI)
    #                - s.connect_ex((ADRESSE, port)) rend 0 quand la connexion réussit
    #                - ouvert vaut donc True si connect_ex(...) == 0
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.settimeout(DELAI)
        ouvert = s.connect_ex((ADRESSE, port)) == 0
    return ouvert


def scanner_ports():
    """Teste tous les ports surveillés. Rend une liste de dictionnaires triée par port.

    Chaque dictionnaire : {"port": 22, "service": "SSH", "ouvert": False}
    """
    resultats = []
    # A FAIRE (V4) : Remplis la liste resultats.
    #                - parcours les numéros de port dans l'ordre croissant : for port in sorted(PORTS_SURVEILLES):
    #                - pour chacun, ajoute un dictionnaire avec les clés port, service (PORTS_SURVEILLES[port]) et ouvert (le résultat de tester_port(port))
    for port in sorted(PORTS_SURVEILLES):
        resultats.append({
            "port": port,
            "service": PORTS_SURVEILLES[port],
            "ouvert": tester_port(port),
        })
    return resultats
