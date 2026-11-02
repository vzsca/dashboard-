# Vigie — Console de surveillance réseau

Vigie est un outil Python de démonstration qui analyse un journal d’authentification SSH, repère les rafales d’échecs, classe les adresses selon un plan réseau d’exemple et produit un rapport HTML.

Les journaux, comptes, sites et réseaux fournis sont fictifs et anonymisés. Les adresses publiques d’exemple appartiennent aux plages de documentation RFC 5737 ; elles ne désignent pas des machines réelles.

## Fonctionnalités

| Étape | Fichier | Fonction |
|---|---|---|
| V1 | `vigie/journal.py` | Analyse les événements d’authentification |
| V2 | `vigie/detection.py` | Détecte au moins 5 échecs en 60 secondes |
| V3 | `vigie/reseau.py` | Classe les adresses à partir du plan d’exemple |
| V4 | `vigie/ports.py` | Teste une liste fermée de ports sur `127.0.0.1` |
| V5 | `vigie/rapport.py` | Génère le tableau de bord et les pages de détail |
| V6 | `vigie/pare_feu.py` | Affiche des règles proposées sans les exécuter |

## Exécution sous Windows

Le projet utilise le Python portable inclus dans `python\`.

1. Extraire le dossier complet sans déplacer `lancer.bat`.
2. Lancer `lancer.bat` pour générer `rapport.html`, `alertes.html`, `origines.html` et `ports.html` dans `rapports\`.
3. Lancer `verifier.bat tout` pour exécuter les contrôles des six étapes.

## Données de démonstration

- `donnees\auth.log` : journal synthétique avec comptes et noms de serveurs génériques.
- `donnees\plan-adressage.csv` : exemple de réseau réparti sur trois sites fictifs et un accès VPN de démonstration.
- L’identité visuelle Vigie est générée dans le rapport et ne dépend d’aucun logo externe.

Pour analyser des journaux ou un plan réels, remplacez les données d’exemple par des fichiers autorisés et vérifiez les résultats avant toute action. Le scan de ports reste limité à la machine locale, et les commandes de pare-feu sont affichées seulement.
