"""Vigie : le programme principal. Tu n'as rien à modifier ici.

Il appelle tes fonctions dans l'ordre (V1 à V6), affiche ce qu'elles
trouvent, puis écrit le rapport dans le dossier rapports/.
Si une de tes fonctions plante, le programme continue avec les autres
et te dit laquelle a posé problème.
"""
import os
import sys
import traceback

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

try:
    sys.stdout.reconfigure(encoding="utf-8")
    sys.stderr.reconfigure(encoding="utf-8")
except Exception:
    pass


def importer(nom):
    """Importe un module de Vigie. S'il a une faute de syntaxe, on l'explique."""
    try:
        return __import__(nom)
    except Exception as err:
        print(f"\nImpossible de charger {nom}.py : {type(err).__name__} : {err}")
        print(f"Ouvre vigie\\{nom}.py, corrige la ligne indiquée, puis relance.")
        sys.exit(1)


outils = importer("outils")
journal = importer("journal")
detection = importer("detection")
reseau = importer("reseau")
ports = importer("ports")
rapport = importer("rapport")
pare_feu = importer("pare_feu")
verif = importer("verif")


def essayer(etape, fonction, defaut):
    """Lance fonction(). Si elle plante, affiche l'erreur et rend defaut."""
    try:
        return fonction()
    except Exception as err:
        derniere = traceback.extract_tb(err.__traceback__)[-1]
        print(f"     {etape} : ton code a planté : {type(err).__name__} : {err}")
        print(f"     (fichier {os.path.basename(derniere.filename)}, ligne {derniere.lineno})")
        return defaut


def main():
    print("=== Vigie : démonstration générique de surveillance réseau ===")
    chemin_log = os.path.join(outils.DOSSIER_DONNEES, "auth.log")
    chemin_plan = os.path.join(outils.DOSSIER_DONNEES, "plan-adressage.csv")

    # ---- V1 : lecture du journal
    evenements = essayer("V1", lambda: journal.lire_journal(chemin_log), [])
    evenements = evenements or []
    nb_echecs = sum(1 for e in evenements if e["resultat"] == "echec")
    nb_succes = sum(1 for e in evenements if e["resultat"] == "succes")
    print(f"[V1] Journal lu : {len(evenements)} événements utiles ({nb_echecs} échecs, {nb_succes} réussites)")

    # ---- V2 : détection
    alertes = essayer("V2", lambda: detection.detecter_alertes(evenements), []) or []
    compromis = essayer("V2", lambda: detection.ips_compromises(evenements, alertes), set()) or set()
    print(f"[V2] Alertes de force brute : {len(alertes)}")
    for a in alertes:
        marque = "  COMPROMISE" if a["ip"] in compromis else ""
        print(f"       {a['ip']:<16}{a['nb_echecs']:>3} échecs sur {len(a['utilisateurs'])} compte(s) "
              f"({a['total_echecs']} au total){marque}")

    # ---- V3 : origine des adresses
    plan = essayer("V3", lambda: reseau.charger_plan(chemin_plan), []) or []
    classes = {}
    origine = {}
    cache = {}

    def classer(ip):
        if ip not in cache:
            cache[ip] = reseau.classer_ip(ip, plan)
        return cache[ip]

    for ip in sorted({e["ip"] for e in evenements if e["resultat"] == "echec"}):
        classe = essayer("V3", lambda ip=ip: classer(ip), None)
        if classe is None:
            break
        classes[ip] = classe
    for e in evenements:
        if e["resultat"] == "echec" and e["ip"] in classes:
            type_ip = classes[e["ip"]]["type"]
            origine[type_ip] = origine.get(type_ip, 0) + 1
    print(f"[V3] Plan d'adressage : {len(plan)} réseaux connus")
    for type_ip, n in sorted(origine.items()):
        print(f"       {type_ip:<18}{n:>4} échecs")

    # ---- V4 : ports
    liste_ports = essayer("V4", ports.scanner_ports, []) or []
    for p in liste_ports:
        p["risque"] = p["port"] in ports.PORTS_RISQUES
    ouverts = [p for p in liste_ports if p["ouvert"]]
    print(f"[V4] Ports testés sur {ports.ADRESSE} : {len(liste_ports)}, ouverts : {len(ouverts)}")
    for p in ouverts:
        print(f"       {p['port']:>5}  {p['service']}" + ("   (à risque)" if p["risque"] else ""))

    # ---- V5 : décisions et rapport
    decisions = {}
    for a in alertes:
        classe = classes.get(a["ip"])
        if classe is None:
            continue
        decision = essayer("V5", lambda a=a, classe=classe: rapport.decider(classe, a["ip"] in compromis), None)
        if decision:
            decisions[a["ip"]] = decision
    liste = [{"ip": ip, "decision": d} for ip, d in decisions.items()]
    reco = essayer("V5", lambda: rapport.recommandations(liste), []) or []

    # ---- V6 : règles de pare-feu (texte seulement)
    a_bloquer = [ip for ip, d in decisions.items()
                 if d in (rapport.BLOQUER, rapport.COMPROMISSION) and classes[ip]["type"] == "externe"]
    regles = essayer("V6", lambda: pare_feu.regles_pare_feu(a_bloquer), []) or []
    regles = [r for r in regles if r]

    etapes = essayer("verif", verif.resume, {}) or {}
    info = {
        "nb_echecs": nb_echecs, "alertes": alertes, "classes": classes, "decisions": decisions,
        "ports": liste_ports, "regles": regles, "origine": origine,
        "recommandations": reco, "etapes": etapes,
    }
    pages = essayer("V5", lambda: rapport.construire_pages_rapport(info), {})
    sortie = None
    if pages:
        os.makedirs(outils.DOSSIER_RAPPORTS, exist_ok=True)
        try:
            ancienne_page_actions = os.path.join(outils.DOSSIER_RAPPORTS, "actions.html")
            try:
                os.remove(ancienne_page_actions)
            except FileNotFoundError:
                pass
            for nom, contenu in pages.items():
                chemin = os.path.join(outils.DOSSIER_RAPPORTS, nom)
                with open(chemin, "w", encoding="utf-8") as f:
                    f.write(contenu)
                if nom == "rapport.html":
                    sortie = chemin
            print(f"[V5] {len(pages)} pages de rapport écrites dans : {outils.DOSSIER_RAPPORTS}")
        except OSError as err:
            sortie = None
            print(f"[V5] Impossible de mettre à jour les pages du rapport : {err}")
    print(f"[V6] Règles de pare-feu proposées, jamais exécutées : {len(regles)}")

    if etapes:
        etat = "  ".join(f"{v} {'OK' if ok else 'A FAIRE'}" for v, ok in sorted(etapes.items()))
        print(f"\nTes étapes : {etat}")
        if not all(etapes.values()):
            print("Lance verifier.bat pour voir ce qui manque.")

    if sortie and os.environ.get("VIGIE_SANS_NAVIGATEUR") != "1":
        try:
            import webbrowser
            webbrowser.open("file:///" + sortie.replace("\\", "/"))
        except Exception:
            pass
    return 0


if __name__ == "__main__":
    sys.exit(main())
