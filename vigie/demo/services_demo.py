"""Ouvre trois ports de démonstration sur TON poste (127.0.0.1 uniquement).

Ça te permet de voir Vigie détecter des ports ouverts (étape V4).
Ctrl+C pour arrêter. Rien n'est accessible depuis un autre ordinateur.
"""
import socket
import threading

ADRESSE = "127.0.0.1"
PORTS = {8080: b"HTTP/1.0 200 OK\r\n\r\nvigie demo\r\n", 3306: b"demo mysql\r\n", 23: b"demo telnet\r\n"}


def servir(ecoute, reponse):
    while True:
        try:
            client, _ = ecoute.accept()
        except OSError:
            return
        try:
            client.sendall(reponse)
        except OSError:
            pass
        client.close()


def main():
    sockets = []
    for port, reponse in PORTS.items():
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        try:
            s.bind((ADRESSE, port))
        except OSError as err:
            print(f"Port {port} : impossible de l'ouvrir ({err}). Un autre programme l'utilise sans doute.")
            s.close()
            continue
        s.listen(5)
        threading.Thread(target=servir, args=(s, reponse), daemon=True).start()
        sockets.append(s)
        print(f"Port {port} ouvert sur {ADRESSE}")
    if not sockets:
        print("Aucun port ouvert. Rien à faire.")
        return
    print("Services de démo actifs. Lance maintenant lancer.bat dans une autre fenêtre.")
    print("Ctrl+C pour arrêter.")
    try:
        threading.Event().wait()
    except KeyboardInterrupt:
        print("\nArrêt des services de démo.")
    for s in sockets:
        s.close()


if __name__ == "__main__":
    main()
