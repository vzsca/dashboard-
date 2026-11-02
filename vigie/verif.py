"""Les vérifications de Vigie (ce fichier sert à verifier.bat et à main.py).

Tu n'as rien à modifier ici. Chaque vérification lance ta fonction sur un
cas dont la réponse est connue, puis compare. Si ton code plante, le
message te dit quelle erreur Python a été levée.
"""
import os
import socket
from datetime import datetime, timedelta

import outils

_cas_courants = []


def cas(libelle, calcul, attendu, comparer=None):
    """Lance calcul() et compare avec attendu. Rend (ok, message)."""
    try:
        obtenu = calcul()
    except Exception as err:
        return False, f"{libelle} : ton code a planté : {type(err).__name__} : {err}"
    bon = comparer(obtenu, attendu) if comparer else obtenu == attendu
    if bon:
        return True, libelle
    return False, f"{libelle}\n       attendu : {attendu!r}\n       obtenu  : {obtenu!r}"


def doit_lever(libelle, calcul, type_erreur):
    """Réussit seulement si calcul() lève type_erreur."""
    try:
        calcul()
    except type_erreur:
        return True, libelle
    except Exception as err:
        return False, f"{libelle} : mauvais type d'erreur : {type(err).__name__} (attendu : {type_erreur.__name__})"
    return False, f"{libelle} : aucune erreur levée, alors qu'il en fallait une"


def _chemin(nom):
    return os.path.join(outils.DOSSIER_DONNEES, nom)


# ---------------------------------------------------------------- V1
def verifier_v1():
    import journal
    res = []
    p = journal.parse_ligne
    base = "Oct 27 07:55:42 srv-files-01 sshd[23688]: "

    res.append(cas("échec simple",
                   lambda: (lambda e: (e["resultat"], e["ip"], e["utilisateur"], e["hote"]))(
                       p(base + "Failed password for user03 from 10.30.10.58 port 43574 ssh2")),
                   ("echec", "10.30.10.58", "user03", "srv-files-01")))
    res.append(cas("échec sur un compte qui n'existe pas (invalid user)",
                   lambda: (lambda e: (e["resultat"], e["ip"], e["utilisateur"]))(
                       p("Oct 29 03:12:08 srv-web-01 sshd[2211]: Failed password for invalid user admin from 203.0.113.45 port 50122 ssh2")),
                   ("echec", "203.0.113.45", "admin")))
    res.append(cas("connexion réussie, jour sur un chiffre (Nov  1)",
                   lambda: (lambda e: (e["resultat"], e["ip"], e["utilisateur"], e["date"]))(
                       p("Nov  1 09:05:10 srv-app-01 sshd[900]: Accepted password for user01 from 10.50.10.15 port 39418 ssh2")),
                   ("succes", "10.50.10.15", "user01", datetime(2026, 11, 1, 9, 5, 10))))
    res.append(cas("la date est une vraie date Python",
                   lambda: p(base + "Failed password for x from 10.1.1.1 port 1 ssh2")["date"],
                   datetime(2026, 10, 27, 7, 55, 42)))
    res.append(cas("ligne de bruit (déconnexion) : None",
                   lambda: p("Oct 27 07:55:50 srv-files-01 sshd[1]: Received disconnect from 10.30.10.58 port 43574:11: disconnected by user"),
                   None))
    res.append(cas("ligne de bruit (session PAM) : None",
                   lambda: p("Oct 27 07:48:53 srv-app-01 sshd[22390]: pam_unix(sshd:session): session opened for user user01(uid=1008) by (uid=0)"),
                   None))
    res.append(cas("ligne vide : None", lambda: p("\n"), None))

    def vrai():
        evs = journal.lire_journal(_chemin("auth.log"))
        return (sum(e["resultat"] == "echec" for e in evs), sum(e["resultat"] == "succes" for e in evs))
    res.append(cas("vrai journal : (échecs, réussites)", vrai, (136, 38)))
    return res


# ---------------------------------------------------------------- V2
def _echecs(ip, secondes, user="admin"):
    debut = datetime(2026, 10, 28, 12, 0, 0)
    return [{"date": debut + timedelta(seconds=s), "hote": "srv-web-01", "resultat": "echec",
             "ip": ip, "utilisateur": user} for s in secondes]


def verifier_v2():
    import detection
    import journal
    res = []
    d = detection.detecter_alertes

    res.append(cas("5 échecs en 40 secondes : 1 alerte de 5",
                   lambda: [(a["ip"], a["nb_echecs"]) for a in d(_echecs("203.0.113.1", [0, 10, 20, 30, 40]))],
                   [("203.0.113.1", 5)]))
    res.append(cas("4 échecs en 30 secondes : rien",
                   lambda: d(_echecs("203.0.113.2", [0, 10, 20, 30])), []))
    res.append(cas("6 échecs espacés de 100 secondes : rien",
                   lambda: d(_echecs("203.0.113.3", [0, 100, 200, 300, 400, 500])), []))
    res.append(cas("bord : 5 échecs de 0 à 60 s inclus : alerte",
                   lambda: [a["nb_echecs"] for a in d(_echecs("203.0.113.4", [0, 15, 30, 45, 60]))], [5]))
    res.append(cas("bord : 5 échecs de 0 à 61 s : rien",
                   lambda: d(_echecs("203.0.113.5", [0, 15, 30, 45, 61])), []))
    mixte = _echecs("203.0.113.6", [0, 5, 10, 15, 20])
    mixte.append(dict(mixte[0], resultat="succes", date=mixte[0]["date"] + timedelta(seconds=22)))
    res.append(cas("les réussites ne comptent pas",
                   lambda: [a["nb_echecs"] for a in d(mixte)], [5]))
    deux = _echecs("203.0.113.7", [0, 10, 20, 30, 40]) + _echecs("203.0.113.8", [5, 15, 25, 35, 45, 55])
    deux.sort(key=lambda e: e["date"])
    res.append(cas("deux adresses mélangées : la plus grosse d'abord",
                   lambda: [(a["ip"], a["nb_echecs"]) for a in d(deux)],
                   [("203.0.113.8", 6), ("203.0.113.7", 5)]))
    comptes = _echecs("203.0.113.9", [0, 10, 20], "root") + _echecs("203.0.113.9", [30, 40, 50], "admin")
    res.append(cas("début, fin, comptes triés sans doublon",
                   lambda: (lambda a: (a["debut"].second, a["fin"].second, a["utilisateurs"]))(d(comptes)[0]),
                   (0, 50, ["admin", "root"])))
    res.append(cas("grouper_echecs_par_ip : clés et tailles",
                   lambda: {ip: len(v) for ip, v in detection.grouper_echecs_par_ip(deux + mixte[-1:]).items()},
                   {"203.0.113.7": 5, "203.0.113.8": 6}))

    def vrai():
        evs = journal.lire_journal(_chemin("auth.log"))
        al = d(evs)
        return (len(al), max(a["nb_echecs"] for a in al) if al else 0)
    res.append(cas("vrai journal : (nombre d'alertes, plus grosse attaque)", vrai, (5, 40)))
    return res


# ---------------------------------------------------------------- V3
def verifier_v3():
    import reseau
    res = []
    plan_res = {}

    def plan():
        if "p" not in plan_res:
            plan_res["p"] = reseau.charger_plan(_chemin("plan-adressage.csv"))
        return plan_res["p"]

    def cl(ip):
        c = reseau.classer_ip(ip, plan())
        return (c["type"], c["site"], c["famille"])

    res.append(cas("plan chargé : 16 lignes", lambda: len(plan()), 16))
    res.append(cas("la valeur reseau est un objet réseau",
                   lambda: type(plan()[0]["reseau"]).__name__, "IPv4Network"))
    res.append(cas("clés d'une ligne du plan",
                   lambda: sorted(plan()[0].keys()), ["description", "famille", "reseau", "site"]))
    res.append(cas("10.30.40.7", lambda: cl("10.30.40.7"), ("interne", "Site B", "scanners")))
    res.append(cas("10.10.10.34", lambda: cl("10.10.10.34"), ("interne", "Site A", "postes fixes")))
    res.append(cas("10.99.0.12", lambda: cl("10.99.0.12")[0:1], ("interne",)))
    res.append(cas("10.50.20.3", lambda: cl("10.50.20.3"), ("interne", "Site C", "imprimantes")))
    for ip in ("192.168.1.14", "10.77.0.1", "172.16.5.4"):
        res.append(cas(f"{ip} : privée mais hors plan", lambda ip=ip: cl(ip),
                       ("interne hors plan", "inconnu", "inconnue")))
    for ip in ("203.0.113.45", "172.32.0.1"):
        res.append(cas(f"{ip} : externe", lambda ip=ip: cl(ip), ("externe", "-", "-")))
    return res


# ---------------------------------------------------------------- V4
def verifier_v4():
    import ports
    res = []
    res.append(cas("l'adresse testée est 127.0.0.1", lambda: ports.ADRESSE, "127.0.0.1"))
    res.append(doit_lever("un port hors liste est refusé (ValueError)", lambda: ports.tester_port(9), ValueError))

    ecoute = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    ecoute.bind(("127.0.0.1", 0))
    ecoute.listen(50)
    port_test = ecoute.getsockname()[1]
    libre = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    libre.bind(("127.0.0.1", 0))
    port_ferme = libre.getsockname()[1]
    libre.close()
    ports.PORTS_SURVEILLES[port_test] = "port de test"
    ports.PORTS_SURVEILLES[port_ferme] = "port fermé de test"
    try:
        res.append(cas("un port qui écoute : True", lambda: ports.tester_port(port_test), True))
        res.append(cas("un port fermé : False", lambda: ports.tester_port(port_ferme), False))

        def scan():
            liste = ports.scanner_ports()
            noms = sorted(liste[0].keys()) if liste else []
            trouve = {p["port"]: p["ouvert"] for p in liste}
            return (noms, trouve.get(port_test), trouve.get(port_ferme),
                    [p["port"] for p in liste] == sorted(p["port"] for p in liste))
        res.append(cas("scanner_ports : clés, port test ouvert, port fermé, tri croissant",
                       scan, (["ouvert", "port", "service"], True, False, True)))
    finally:
        ports.PORTS_SURVEILLES.pop(port_test, None)
        ports.PORTS_SURVEILLES.pop(port_ferme, None)
        ecoute.close()
    return res


# ---------------------------------------------------------------- V5
def verifier_v5():
    import rapport
    res = []
    ext = {"type": "externe", "site": "-", "famille": "-"}
    interne = {"type": "interne", "site": "Site C", "famille": "imprimantes"}
    hors = {"type": "interne hors plan", "site": "inconnu", "famille": "inconnue"}
    res.append(cas("externe sans compromission : BLOQUER", lambda: rapport.decider(ext, False), "BLOQUER"))
    res.append(cas("externe compromise : COMPROMISSION", lambda: rapport.decider(ext, True), "COMPROMISSION"))
    res.append(cas("interne : ENQUETER", lambda: rapport.decider(interne, False), "ENQUETER"))
    res.append(cas("interne hors plan : ENQUETER", lambda: rapport.decider(hors, False), "ENQUETER"))

    alerte = {"ip": "198.51.100.200", "nb_echecs": 5, "utilisateurs": ["<script>x</script>"],
              "debut": datetime(2026, 10, 29, 3, 0, 0), "fin": datetime(2026, 10, 29, 3, 0, 40), "total_echecs": 5}
    ligne = {}

    def fabriquer():
        if "l" not in ligne:
            ligne["l"] = rapport.ligne_tableau(alerte, ext, "BLOQUER")
        return ligne["l"]
    res.append(cas("ligne_tableau : 7 cellules", lambda: fabriquer().count("<td"), 7))
    res.append(cas("ligne_tableau : le compte est échappé (&lt;script&gt;)",
                   lambda: "&lt;script&gt;" in fabriquer(), True))
    res.append(cas("ligne_tableau : aucune balise <script> brute",
                   lambda: "<script>" in fabriquer(), False))
    res.append(cas("ligne_tableau : l'adresse apparaît", lambda: "198.51.100.200" in fabriquer(), True))
    res.append(cas("ligne_tableau : la date est lisible (29/10 03:00:40)",
                   lambda: "29/10 03:00:40" in fabriquer(), True))

    liste = [{"ip": "203.0.113.45", "decision": "BLOQUER"}, {"ip": "192.0.2.19", "decision": "COMPROMISSION"},
             {"ip": "192.168.1.14", "decision": "ENQUETER"}]
    res.append(cas("recommandations : une phrase par décision, avec l'IP",
                   lambda: (lambda r: (len(r), all(d["ip"] in r[i] for i, d in enumerate(liste))))(
                       rapport.recommandations(liste)), (3, True)))
    res.append(cas("recommandations : liste vide", lambda: rapport.recommandations([]), []))
    return res


# ---------------------------------------------------------------- V6
def verifier_v6():
    import pare_feu
    res = []
    res.append(cas("règle netsh exacte",
                   lambda: pare_feu.regle_netsh("203.0.113.45"),
                   'netsh advfirewall firewall add rule name="Vigie bloque 203.0.113.45" dir=in action=block remoteip=203.0.113.45'))
    res.append(doit_lever("texte piégé refusé (ValueError)",
                          lambda: pare_feu.regle_netsh("203.0.113.45 & del"), ValueError))
    res.append(doit_lever("adresse impossible refusée (ValueError)",
                          lambda: pare_feu.regle_netsh("999.1.1.1"), ValueError))
    res.append(cas("deux adresses, un doublon : 2 règles triées",
                   lambda: [r.split("remoteip=")[1] for r in
                            pare_feu.regles_pare_feu(["203.0.113.45", "198.51.100.77", "203.0.113.45"])],
                   ["198.51.100.77", "203.0.113.45"]))
    res.append(cas("liste vide : aucune règle", lambda: pare_feu.regles_pare_feu([]), []))

    def source_sure():
        with open(os.path.join(os.path.dirname(os.path.abspath(__file__)), "pare_feu.py"), encoding="utf-8") as f:
            texte = f.read()
        return ("subprocess" in texte, "os.system" in texte)
    res.append(cas("pare_feu.py n'exécute rien (ni subprocess ni os.system)", source_sure, (False, False)))
    return res


ETAPES = {
    "V1": verifier_v1, "V2": verifier_v2, "V3": verifier_v3,
    "V4": verifier_v4, "V5": verifier_v5, "V6": verifier_v6,
}

_memo = {}


def lancer(etape):
    """Rend la liste de (ok, message) d'une étape. Un module cassé donne un seul échec."""
    try:
        return ETAPES[etape]()
    except Exception as err:
        return [(False, f"{etape} : impossible de lancer les vérifications : {type(err).__name__} : {err}")]


def resume():
    """Rend {"V1": True/False, ...} : une étape est vraie si tous ses cas passent."""
    return {nom: all(ok for ok, _ in lancer(nom)) for nom in ETAPES}
