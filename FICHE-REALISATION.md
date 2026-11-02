# Présentation du projet Vigie

## Objectif

Vigie est une démonstration locale de surveillance des connexions SSH. Elle transforme un journal d’exemple en indicateurs et en pages HTML consultables, sans contacter de serveur distant.

## Parcours d’analyse

1. Lire les événements de connexion et distinguer échecs et réussites.
2. Détecter les rafales d’échecs par adresse IP.
3. Comparer les adresses privées au plan réseau fictif.
4. Tester une liste fixe de ports sur `127.0.0.1`.
5. Générer un tableau de bord, les alertes, la répartition des origines et les ports.
6. Afficher des propositions de règles de pare-feu sans les lancer.

## Données

Les fichiers de `donnees\` sont des exemples synthétiques. Les noms de comptes, de serveurs et de sites sont génériques ; les adresses publiques sont réservées à la documentation. Le plan contient trois sites fictifs et un réseau VPN de démonstration.

## Limites et précautions

- Le test de ports cible uniquement la machine locale.
- Les règles de pare-feu proposées sont du texte et ne sont jamais exécutées par Vigie.
- Le rapport sert à illustrer une analyse ; toute alerte sur un environnement réel doit être vérifiée par un administrateur.
- N’utiliser que des journaux et des réseaux pour lesquels vous avez une autorisation.
