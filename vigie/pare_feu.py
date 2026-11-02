"""V6 (bonus) : écrire des règles de pare-feu Windows.

Vigie ne bloque rien lui-même. Il écrit le texte des commandes que
l'administrateur pourrait lancer, et le rapport les affiche. Elles ne sont
jamais exécutées par le programme : c'est un humain qui relit, puis décide.
(Pour cette raison, ce fichier n'appelle aucun programme externe.)

Une règle ressemble à ça :
  netsh advfirewall firewall add rule name="Vigie bloque 203.0.113.45" dir=in action=block remoteip=203.0.113.45
"""
from outils import ip_valide


def regle_netsh(ip):
    """Rend le texte de la commande netsh qui bloque une adresse IP entrante.

    Si ip n'est pas une adresse IP correcte, lève ValueError : on ne
    fabrique jamais une commande à partir d'un texte qu'on n'a pas vérifié.
    """
    if not ip_valide(ip):
        raise ValueError("Adresse IP invalide : " + str(ip))
    return f'netsh advfirewall firewall add rule name="Vigie bloque {ip}" dir=in action=block remoteip={ip}'
    #                - si ip_valide(ip) est faux : raise ValueError("Adresse IP invalide : " + str(ip))
    #                - sinon rends la chaîne : f'netsh advfirewall firewall add rule name="Vigie bloque {ip}" dir=in action=block remoteip={ip}'


def regles_pare_feu(ips):
    """Rend la liste des règles pour une liste d'adresses, sans doublon, triée."""
    regles = []
    # A FAIRE (V6) : Fabrique une règle par adresse, sans doublon.
    #                - set(ips) enlève les doublons
    #                - sorted(...) les range dans l'ordre
    #                - pour chaque adresse, ajoute regle_netsh(adresse) à la liste regles
    for adresse in sorted(set(ips)):
        regles.append(regle_netsh(adresse))
    return regles
