"""Vérifie tes étapes. Usage : verifier.bat V1  (V2 ... V6, ou tout)."""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

try:
    sys.stdout.reconfigure(encoding="utf-8")
except Exception:
    pass

import verif

TOUTES = dict(verif.ETAPES)


def lancer(nom):
    if nom in verif.ETAPES:
        return verif.lancer(nom)
    return [(False, f"{nom} : étape inconnue")]


def main(argv):
    choix = [a.upper() for a in argv[1:]] or ["TOUT"]
    if "TOUT" in choix:
        choix = list(verif.ETAPES)
    inconnues = [c for c in choix if c not in TOUTES]
    if inconnues:
        print("Étape inconnue :", ", ".join(inconnues))
        print("Utilise : verifier.bat V1  (V1 à V6) ou verifier.bat tout")
        return 2
    total = bons = 0
    etapes_ok = 0
    for nom in choix:
        print(f"\n--- {nom} ---")
        resultats = lancer(nom)
        for ok, message in resultats:
            total += 1
            bons += ok
            print(("  OK     " if ok else "  ECHEC  ") + message)
        if all(ok for ok, _ in resultats):
            etapes_ok += 1
            print(f"  => {nom} validée")
        else:
            print(f"  => {nom} : il reste des échecs, relis la consigne du trou")
    print(f"\nRésultat : {bons} / {total} contrôles OK, {etapes_ok} / {len(choix)} étapes validées")
    return 0 if bons == total else 1


if __name__ == "__main__":
    sys.exit(main(sys.argv))
