"""V5 : décider quoi faire, et fabriquer le rapport HTML.

Pour chaque alerte, Vigie propose une décision :
  COMPROMISSION  l'attaquant a fini par se connecter : urgence maximale
  BLOQUER        adresse externe qui attaque : on la bloque au pare-feu
  ENQUETER       adresse interne : on ne bloque pas à l'aveugle, on va voir
                 sur place ce qui se passe (poste infecté ? script oublié ?)

Dans ce fichier, tu écris trois petites fonctions (decider, ligne_tableau,
recommandations). La page complète est construite par construire_rapport.
"""
import html

from outils import formater_date

ECOLE = "Vigie · Démonstration générique"

BLOQUER = "BLOQUER"
ENQUETER = "ENQUETER"
COMPROMISSION = "COMPROMISSION"

LIBELLES = {
    BLOQUER: "Bloquer",
    ENQUETER: "Enquêter",
    COMPROMISSION: "Compromission",
}


def decider(classe, compromis):
    """Rend BLOQUER, ENQUETER ou COMPROMISSION pour une alerte.

    classe     le dictionnaire rendu par classer_ip (clé "type")
    compromis  True si l'attaquant s'est ensuite connecté avec succès
    """
    decision = None  # à toi de la remplir
    # A FAIRE (V5) : Choisis la décision.
    #                - si compromis est vrai : COMPROMISSION
    #                - sinon, si classe["type"] vaut "externe" : BLOQUER
    #                - dans tous les autres cas (interne, interne hors plan) : ENQUETER
    #                - l'ordre des tests compte : la compromission passe avant tout
    if compromis:
        decision = COMPROMISSION
    elif classe["type"] == "externe":
        decision = BLOQUER
    else:
        decision = ENQUETER
    return decision


def ligne_tableau(alerte, classe, decision):
    """Rend le HTML d'une ligne du tableau des alertes (une balise <tr>).

    Les colonnes, dans l'ordre : adresse IP, origine, comptes visés,
    nombre d'échecs, début, fin, décision.

    ATTENTION : le nom de compte vient du journal, donc d'un attaquant.
    Il peut contenir du HTML ou du JavaScript. Passe CHAQUE texte venant du
    journal dans html.escape() avant de l'écrire dans la page.
    """
    ligne = ""
    # A FAIRE (V5) : Fabrique la ligne HTML.
    #                - ip = html.escape(alerte["ip"])
    #                - comptes = html.escape(", ".join(alerte["utilisateurs"]))
    #                - origine : classe["type"] et classe["site"], eux aussi passés dans html.escape
    #                - écris une chaîne <tr> avec 7 cellules <td> dans l'ordre indiqué ci-dessus (formater_date(alerte["debut"]) et formater_date(alerte["fin"]) donnent les dates lisibles)
    #                - la dernière cellule : <span class="badge LA_DECISION">LIBELLE</span> où LA_DECISION est la valeur de decision et LIBELLE vient de LIBELLES[decision]
    ip = html.escape(str(alerte["ip"]))
    comptes = html.escape(", ".join(alerte["utilisateurs"]))
    type_origine = html.escape(str(classe["type"]))
    site = html.escape(str(classe["site"]))
    origine = f"{type_origine} ({site})"
    badge = f'<span class="badge {decision}">{LIBELLES[decision]}</span>'
    ligne = (
        f'<tr><td class="ip">{ip}</td><td>{origine}</td><td>{comptes}</td>'
        f'<td class="n">{alerte["nb_echecs"]}</td>'
        f'<td>{formater_date(alerte["debut"])}</td>'
        f'<td>{formater_date(alerte["fin"])}</td><td>{badge}</td></tr>'
    )
    return ligne


def recommandations(decisions):
    """Rend une liste de phrases de recommandation, une par alerte.

    decisions est une liste de dictionnaires : [{"ip": "203.0.113.45", "decision": "BLOQUER"}, ...]
    Chaque phrase doit contenir l'adresse IP. Une liste vide donne une liste vide.
    """
    phrases = []
    # A FAIRE (V5) : Écris une phrase par décision.
    #                - pour chaque élément d de decisions, regarde d["decision"]
    #                - COMPROMISSION : une phrase d'urgence (changer le mot de passe du compte, fermer les sessions ouvertes)
    #                - BLOQUER : une phrase qui dit de bloquer l'adresse au pare-feu
    #                - ENQUETER : une phrase qui dit d'aller vérifier l'équipement sur place
    #                - chaque phrase contient d["ip"]
    #                - ajoute-les à la liste phrases
    for d in decisions:
        if d["decision"] == COMPROMISSION:
            phrase = f'Urgence : changer le mot de passe du compte et fermer les sessions ouvertes pour {d["ip"]}.'
        elif d["decision"] == BLOQUER:
            phrase = f'Bloquer l’adresse {d["ip"]} au pare-feu.'
        else:
            phrase = f'Aller vérifier sur place l’équipement associé à {d["ip"]}.'
        phrases.append(phrase)
    return phrases


# ----------------------------------------------------------------------
# La page complète est générée ici.
# ----------------------------------------------------------------------

CSS = """
:root{color-scheme:dark;--ink:#eceaf4;--muted:#a6a2b3;--navy:#f4f1fa;--blue:#c1afff;--teal:#d4f06b;--line:#3a3746;--paper:#25232d;--canvas:#19181e}
*{box-sizing:border-box}
body{font-family:"Segoe UI",Arial,sans-serif;margin:0;background:radial-gradient(ellipse at 50% -20%,#393047 0%,transparent 55%),var(--canvas);color:var(--ink);line-height:1.6}
header{background:#1d1b24;color:#fff;padding:20px max(24px,calc((100% - 1180px)/2));display:flex;align-items:center;gap:18px;border-bottom:1px solid #3a3746;box-shadow:none}
.brand-mark{display:grid;place-items:center;flex:none;width:46px;height:46px;border:1px solid #554774;border-radius:12px;background:#30283d;color:#d4b8ff;font-size:23px;font-weight:800;letter-spacing:-.08em}
header h1{margin:0;font-size:clamp(22px,3vw,30px);letter-spacing:-.04em}
header p{margin:5px 0 0;color:#b9b4c6;font-size:13px}
main{max-width:1120px;margin:0 auto;padding:46px 32px 72px}
.avert{background:#31291e;border:1px solid #55432e;border-left:3px solid #d5ae60;padding:14px 17px;margin:0 0 26px;border-radius:8px;color:#e8d8b8;font-size:14px}
.overview{margin:28px 0 22px;padding:26px 28px;background:linear-gradient(125deg,#292532,#211f27 68%);border:1px solid #3c3748;border-radius:13px}
.overview.status-critical{border-color:#71404c}
.overview.status-warning{border-color:#68543a}
.overview-top{display:flex;align-items:flex-start;justify-content:space-between;gap:24px}
.overview-title .eyebrow{color:#bda4ef;font-size:10px;letter-spacing:.17em}
.overview-title h2{font-size:30px;letter-spacing:-.05em}
.overview-lead{margin:7px 0 0;color:var(--muted);font-size:13px}
.overview-message{max-width:740px;margin:19px 0 0;color:#d6d1df;font-size:13px}
.overview-state{display:grid;grid-template-columns:auto 1fr;align-items:center;column-gap:10px;min-width:220px;padding:13px 15px;background:#1d1b24;border:1px solid #403a4b;border-radius:9px}
.status-dot{grid-row:span 2;width:9px;height:9px;border-radius:50%;background:#e8b75b;box-shadow:0 0 10px #e8b75b50}
.overview.status-critical .status-dot{background:#e57583;box-shadow:0 0 10px #e5758350}
.overview.status-clear .status-dot{background:var(--teal);box-shadow:0 0 10px #d4f06b50}
.status-label{color:var(--navy);font-size:10px;font-weight:800;letter-spacing:.08em}
.status-detail{grid-column:2;margin-top:3px;color:var(--muted);font-size:11px}
.overview-metrics{display:grid;grid-template-columns:repeat(4,minmax(0,1fr));margin-top:24px;padding-top:18px;border-top:1px solid #403a4b}
.overview-metric{display:flex;flex-direction:column;gap:5px;padding:0 18px;border-left:1px solid #403a4b;color:var(--ink);text-decoration:none}
.overview-metric:first-child{padding-left:0;border-left:0}
.overview-metric span{color:var(--muted);font-size:11px}
.overview-metric strong{color:var(--navy);font-size:25px;line-height:1.1;font-variant-numeric:tabular-nums}
.overview-metric:hover strong{color:#d7c2ff}
.overview-metric:focus-visible,.tab:focus-visible{outline:3px solid var(--teal);outline-offset:3px}
.dashboard-section{min-width:0;margin:0 0 18px;padding:22px 23px;background:#201e26;border:1px solid #37343f;border-radius:11px}
.dashboard-section-heading{display:flex;align-items:flex-end;justify-content:space-between;gap:18px;margin:0 0 17px}
.dashboard-section-heading h2{font-size:19px}
.dashboard-section-heading p{margin:4px 0 0;color:var(--muted);font-size:12px}
.dashboard-section-heading a{flex:none;color:#b7a4ee;font-size:11px;font-weight:700;text-decoration:none}
.dashboard-section-heading a:hover{text-decoration:underline}
.dashboard-bottom{display:grid;grid-template-columns:1fr 1fr;gap:18px}
.dashboard-table{overflow-x:auto;border-radius:9px}
.dashboard-table table{min-width:100%}
.eyebrow{margin:0 0 5px;color:var(--blue);font-size:10px;font-weight:800;letter-spacing:.14em;text-transform:uppercase}
h2{margin:0;color:var(--navy);font-size:24px;letter-spacing:-.035em}
.tabs{display:flex;gap:5px;overflow-x:auto;padding:5px;background:#211f27;border:1px solid #393641;border-radius:9px;scrollbar-width:thin}
.tab{flex:none;padding:9px 14px;border:1px solid transparent;border-radius:6px;color:var(--muted);font-size:12px;font-weight:650;text-decoration:none;transition:background .18s ease,color .18s ease}
.tab:hover{color:#dfd2ff}
.tab[aria-current=page]{background:#383244;color:#eee8ff;box-shadow:none}
.page-content{padding-top:26px}
.panel-heading{display:flex;align-items:end;justify-content:space-between;gap:20px;margin-bottom:20px}
.panel-heading h2{font-size:20px}
.panel-heading p{margin:4px 0 0;color:var(--muted);font-size:13px}
table{width:100%;border-collapse:separate;border-spacing:0;background:#24222b;border:1px solid #393641;border-radius:9px;overflow:hidden;font-size:13px;box-shadow:none}
th{background:#2d2a35;color:#c9c4d2;text-align:left;padding:12px 14px;font-size:10px;text-transform:uppercase;letter-spacing:.07em}
td{padding:12px 14px;border-top:1px solid #393641;vertical-align:top}
tr:hover td{background:#2d2934}
td.ip{font-family:Consolas,monospace;font-weight:700;color:#c1afff}
td.n{text-align:right;font-variant-numeric:tabular-nums}
.badge{display:inline-block;padding:4px 10px;border-radius:20px;font-size:11px;font-weight:700;letter-spacing:.02em;color:#fff}
.badge.BLOQUER{background:#85533c}
.badge.ENQUETER{background:#514b5d}
.badge.COMPROMISSION{background:#873f4a}
.risque{color:#f18a95;font-weight:700}
.ouvert{font-weight:700;color:#d4f06b}
.vide{color:var(--muted);font-style:italic;background:#24222b;border:1px dashed var(--line);padding:16px;border-radius:9px}
footer{text-align:center;color:var(--muted);font-size:11px;padding:25px;border-top:1px solid #34313c}
@media(max-width:900px){.overview-top{flex-direction:column}.overview-state{width:100%}.dashboard-bottom{grid-template-columns:1fr}}
@media(max-width:600px){header{padding:18px 16px;align-items:flex-start}header img{height:36px;max-width:100px}header p{font-size:12px}main{padding:27px 18px 46px}.overview{margin-top:22px;padding:20px 18px}.overview-title h2{font-size:26px}.overview-metrics{grid-template-columns:repeat(2,minmax(0,1fr));gap:17px 0;margin-top:20px;padding-top:16px}.overview-metric{padding:0 12px}.overview-metric:nth-child(odd){padding-left:0;border-left:0}.overview-metric strong{font-size:23px}.dashboard-section{padding:18px 15px}.dashboard-section-heading{align-items:flex-start}.dashboard-section-heading h2{font-size:17px}.dashboard-section-heading a{font-size:10px}.panel-heading{align-items:flex-start;flex-direction:column}table{display:block;overflow-x:auto;white-space:nowrap}.tabs{margin-right:-18px}}
@media(max-width:360px){.overview-metrics{grid-template-columns:1fr}.overview-metric{padding:0;border-left:0}}
@media(prefers-reduced-motion:reduce){*,*::before,*::after{scroll-behavior:auto!important;transition:none!important;animation:none!important}}
"""


def _tableau_vide(texte):
    return f'<p class="vide">{html.escape(texte)}</p>'


def construire_rapport(info, page="dashboard"):
    """Construit le tableau de bord complet ou une page de détail du rapport."""
    e = html.escape
    alertes = info.get("alertes") or []
    classes = info.get("classes") or {}
    decisions = info.get("decisions") or {}
    ports = info.get("ports") or []
    origine = info.get("origine") or {}
    etapes = info.get("etapes") or {}

    manquantes = [v for v, ok in sorted(etapes.items()) if not ok]
    bandeau = ""
    if manquantes:
        bandeau = ('<div class="avert">Ce rapport est incomplet : les étapes '
                   + e(", ".join(manquantes))
                   + " ne sont pas encore terminées. Lance verifier.bat pour savoir où ça coince.</div>")

    ouverts = [p for p in ports if p.get("ouvert")]

    # Tableau des alertes
    if alertes:
        lignes = []
        for a in alertes:
            classe = classes.get(a["ip"]) or {"type": "?", "site": "?", "famille": "?"}
            decision = decisions.get(a["ip"]) or ENQUETER
            try:
                lignes.append(ligne_tableau(a, classe, decision) or "")
            except Exception:
                lignes.append(f'<tr><td colspan="7">{e(a["ip"])} : ligne_tableau a planté</td></tr>')
        tab_alertes = ("<table><tr><th>Adresse IP</th><th>Origine</th><th>Comptes visés</th>"
                       "<th>Échecs</th><th>Début</th><th>Fin</th><th>Décision</th></tr>"
                       + "".join(lignes) + "</table>")
    else:
        tab_alertes = _tableau_vide("Aucune alerte pour le moment.")

    # Origine des échecs
    if origine:
        lignes = "".join(f"<tr><td>{e(str(k))}</td><td class=\"n\">{v}</td></tr>" for k, v in sorted(origine.items()))
        tab_origine = f"<table><tr><th>Origine de l'adresse</th><th>Échecs</th></tr>{lignes}</table>"
    else:
        tab_origine = _tableau_vide("Origine des échecs non calculée.")

    # Ports
    if ports:
        lignes = []
        for p in ports:
            etat = "OUVERT" if p.get("ouvert") else "fermé"
            risque = ""
            if p.get("ouvert") and p.get("risque"):
                risque = '<span class="risque">service à risque</span>'
            classe_css = "ouvert" if p.get("ouvert") else ""
            lignes.append(f'<tr><td class="n">{p["port"]}</td><td>{e(str(p["service"]))}</td>'
                          f'<td class="{classe_css}">{etat}</td><td>{risque}</td></tr>')
        tab_ports = ("<table><tr><th>Port</th><th>Service</th><th>État</th><th>Remarque</th></tr>"
                     + "".join(lignes) + "</table>")
    else:
        tab_ports = _tableau_vide("Scan des ports non réalisé.")

    img = '<span class="brand-mark" aria-hidden="true">V</span>'

    titres_pages = {
        "dashboard": "Tableau de bord",
        "alertes": "Alertes",
        "origines": "Origines",
        "ports": "Ports",
    }
    if page not in titres_pages:
        raise ValueError(f"Page de rapport inconnue : {page}")

    sections = {
        "alertes": f"""<section class="page-content">
<div class="panel-heading"><div><p class="eyebrow">Détection</p><h2>Alertes de force brute</h2><p>Adresses, comptes visés et décision recommandée pour chaque alerte.</p></div></div>
{tab_alertes}
</section>""",
        "origines": f"""<section class="page-content">
<div class="panel-heading"><div><p class="eyebrow">Répartition</p><h2>D’où viennent les échecs</h2><p>Nombre d’échecs regroupés par origine d’adresse.</p></div></div>
{tab_origine}
</section>""",
        "ports": f"""<section class="page-content">
<div class="panel-heading"><div><p class="eyebrow">Machine locale</p><h2>Ports testés sur ce poste (127.0.0.1)</h2><p>État des services vérifiés par Vigie sur la machine locale.</p></div></div>
{tab_ports}
</section>""",
    }

    navigation = (
        ("dashboard", "Tableau de bord", "rapport.html"),
        ("alertes", "Alertes", "alertes.html"),
        ("origines", "Origines", "origines.html"),
        ("ports", "Ports", "ports.html"),
    )
    liens_navigation = "".join(
        f'<a class="tab" href="{fichier}"'
        + (' aria-current="page"' if cle == page else "")
        + f'>{libelle}</a>'
        for cle, libelle, fichier in navigation
    )

    alertes_compromises = sum(1 for decision in decisions.values() if decision == COMPROMISSION)
    if alertes_compromises:
        statut_classe = "status-critical"
        statut_titre = "COMPROMISSION DÉTECTÉE"
    elif alertes:
        statut_classe = "status-warning"
        statut_titre = "ACTIVITÉ DÉTECTÉE"
    else:
        statut_classe = "status-clear"
        statut_titre = "AUCUNE ALERTE"
    statut_detail = (
        f"{len(alertes)} alerte{'s' if len(alertes) != 1 else ''} · "
        f"{alertes_compromises} compromission{'s' if alertes_compromises != 1 else ''}"
        if alertes or alertes_compromises
        else "Aucune alerte · aucune compromission"
    )

    if alertes_compromises:
        statut_message = (
            "Une connexion a réussi après plusieurs échecs. Vérifiez immédiatement "
            "le compte et les sessions concernés."
        )
    elif alertes:
        statut_message = (
            "Des tentatives répétées ont été détectées. Consultez les adresses "
            "et les comptes visés dans le tableau ci-dessous."
        )
    else:
        statut_message = "Aucune tentative répétée détectée dans les journaux analysés."

    dashboard = f"""<section class="overview {statut_classe}" aria-labelledby="dashboard-title">
<div class="overview-top">
<div class="overview-title"><p class="eyebrow">VIGIE / CENTRE DE SURVEILLANCE</p>
<h2 id="dashboard-title">Situation du réseau</h2>
<p class="overview-lead">Synthèse des événements SSH et des services détectés sur le poste.</p></div>
<div class="overview-state" role="status"><span class="status-dot"></span>
<span class="status-label">{statut_titre}</span><span class="status-detail">{statut_detail}</span></div>
</div>
<p class="overview-message">{statut_message}</p>
<div class="overview-metrics" aria-label="Chiffres clés">
<a class="overview-metric" href="origines.html"><span>Échecs SSH</span><strong>{e(str(info.get("nb_echecs", "?")))}</strong></a>
<a class="overview-metric" href="alertes.html"><span>Alertes</span><strong>{len(alertes)}</strong></a>
<a class="overview-metric" href="alertes.html"><span>Compromissions</span><strong>{alertes_compromises}</strong></a>
<a class="overview-metric" href="ports.html"><span>Ports ouverts</span><strong>{len(ouverts)}</strong></a>
</div>
</section>
<section class="dashboard-section" aria-labelledby="dashboard-alerts-title">
<div class="dashboard-section-heading"><div><p class="eyebrow">À examiner</p>
<h2 id="dashboard-alerts-title">Alertes détectées</h2>
<p>Adresses sources, comptes visés et décision associée.</p></div>
<a href="alertes.html">Page des alertes →</a></div>
<div class="dashboard-table">{tab_alertes}</div>
</section>
<div class="dashboard-bottom">
<section class="dashboard-section" aria-labelledby="dashboard-origins-title">
<div class="dashboard-section-heading"><div><p class="eyebrow">Répartition</p>
<h2 id="dashboard-origins-title">Origines des échecs</h2>
<p>Volume regroupé par type d’adresse.</p></div>
<a href="origines.html">Détails →</a></div>
<div class="dashboard-table">{tab_origine}</div>
</section>
<section class="dashboard-section" aria-labelledby="dashboard-ports-title">
<div class="dashboard-section-heading"><div><p class="eyebrow">Poste local</p>
<h2 id="dashboard-ports-title">Services détectés</h2>
<p>Ports testés sur la machine locale.</p></div>
<a href="ports.html">Détails →</a></div>
<div class="dashboard-table">{tab_ports}</div>
</section>
</div>"""
    contenu = dashboard if page == "dashboard" else sections[page]

    return f"""<!DOCTYPE html>
<html lang="fr"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<meta name="theme-color" content="#19181e">
<title>Vigie — {titres_pages[page]}</title>
<style>{CSS}</style></head><body>
<header>{img}<div><h1>Vigie — Centre de surveillance</h1>
<p>Surveillance réseau · Analyse des journaux d'authentification SSH</p></div></header>
<main class="{'dashboard' if page == 'dashboard' else 'detail-page'}">
{bandeau}
<nav class="tabs" aria-label="Pages du rapport">{liens_navigation}</nav>
{contenu}
</main>
<footer>{e(ECOLE)}</footer>
</body></html>
"""


def construire_pages_rapport(info):
    """Rend tous les fichiers HTML du rapport, tableau de bord compris."""
    pages = {
        "rapport.html": "dashboard",
        "alertes.html": "alertes",
        "origines.html": "origines",
        "ports.html": "ports",
    }
    return {fichier: construire_rapport(info, page) for fichier, page in pages.items()}
