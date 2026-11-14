#!/usr/bin/env python3
"""Convertit un plan de cours (JSON, format de construire_diapos.py) en HTML mis en page,
à importer en Google Doc pour obtenir le PDF du cours (notion.md, section 8).

Usage : python3 scripts/plan_vers_html.py plan.json [plan_partie2.json ...] > cours.html

Même contenu et même ordre que la page Notion (plan_vers_notion.py), rien n'est coupé.
Mise en page « cours visuel » (demande de Matis, 14/11/2026) :
- page de garde à la couleur du module, avec le sommaire ;
- chaque partie commence par un grand bandeau coloré numéroté ;
- chaque bloc a un titre avec une barre de couleur ;
- schémas en étapes (cases reliées par des flèches), chiffres clés en grandes cartes,
  colonnes en cartes, tableaux à en-tête coloré et lignes alternées ;
- figures grandes et centrées, légende en dessous ;
- encadrés « À retenir », mini-rappels (bleu), mini-conclusions (jaune), articles phares ;
- puces dans une carte claire et deux lignes vides entre les blocs.
Uniquement du HTML que Google Docs sait importer (tableaux, couleurs de fond, bordures).
"""
import html
import json
import re
import sys

ROUGE = "#c62828"
GRIS = "#6b6b76"

# Couleur principale et couleur claire de chaque module (bandeaux, titres, cartes).
MODULES = {
    "M00": ("#5b4bc4", "#efecfb"), "M01": ("#1e88e5", "#e6f1fc"), "M02": ("#3949ab", "#e9ebf7"),
    "M03": ("#00897b", "#e2f4f2"), "M04": ("#43a047", "#e9f5ea"), "M05": ("#f57c00", "#fef1e3"),
    "M06": ("#e53935", "#fde9e9"), "M07": ("#8e24aa", "#f4e6f8"), "M08": ("#ec407a", "#fde8f0"),
    "M09": ("#6d4c41", "#f1ebe8"), "M10": ("#2e7d32", "#e7f3e8"), "M11": ("#0277bd", "#e1f1fa"),
    "M12": ("#455a64", "#e9eef0"),
}
DEFAUT = ("#5b4bc4", "#efecfb")

# Couleurs des cartes de chiffres et des étapes, en alternance.
PASTELS = [("#e3f2fd", "#1565c0"), ("#e8f5e9", "#2e7d32"), ("#fff3e0", "#e65100"),
           ("#f3e5f5", "#6a1b9a"), ("#fce4ec", "#ad1457"), ("#e0f7fa", "#00838f")]

ENCADRES = {
    "violet": ("#efe7fb", "#6a3fb5"),
    "jaune": ("#fff6d6", "#b58900"),
    "vert": ("#e8f5e9", "#2e7d32"),
    "bleu": ("#e8f0fe", "#1a56c4"),
    "gris": ("#f1f1f4", "#55555f"),
    "rouge": ("#fdecea", ROUGE),
}

C = {"fort": DEFAUT[0], "clair": DEFAUT[1]}  # couleurs du module en cours
# Espace entre deux blocs (demande de Matis, 14/11/2026) : Google Docs ignore les marges CSS.
ESPACE = '<p style="font-size:8pt">&nbsp;</p><p style="font-size:8pt">&nbsp;</p>'
# Google Docs ignore les sauts de page CSS à l'import (testé le 14/11/2026) : simple espace.
SAUT = '<p>&nbsp;</p>'


def inline(txt):
    """**gras** -> <b>, échappe le reste."""
    txt = html.escape(str(txt), quote=False)
    return re.sub(r"\*\*(.+?)\*\*", r"<b>\1</b>", txt)


def source(s):
    """Une source ; si plusieurs sont jointes par « ; », seules les ★ passent en rouge."""
    morceaux = []
    for m in str(s).split(" ; "):
        m = inline(m)
        morceaux.append(f'<span style="color:{ROUGE}"><b>{m}</b></span>' if "★" in m else m)
    return " ; ".join(morceaux)


def table1(contenu, fond, bord=None, gauche=6, pad=10, align="left"):
    """Encadré : tableau à une cellule colorée, barre de couleur à gauche."""
    # Google Docs transforme une bordure gauche en cadre complet : la barre est une
    # cellule étroite colorée, à gauche de la cellule de contenu.
    barre = (f'<td style="width:{gauche}px;background-color:{bord};border:none"></td>'
             if bord else "")
    return (f'<table style="width:100%;border-collapse:collapse;margin:6px 0;border:none"><tr>{barre}'
            f'<td style="background-color:{fond};border:none;padding:{pad}px;text-align:{align}">'
            f"{contenu}</td></tr></table>")


def encadre(couleur, contenu):
    fond, bord = ENCADRES[couleur]
    return table1(contenu, fond, bord)


def puces(items):
    if not items:
        return ""
    out, sous = ["<ul>"], False
    for p in items:
        p = str(p)
        if p.startswith("- "):
            if not sous:
                out.append("<ul>")
                sous = True
            out.append(f"<li>{inline(p[2:])}</li>")
            continue
        if sous:
            out.append("</ul>")
            sous = False
        out.append(f'<li style="margin-bottom:3px">{inline(p)}</li>')
    if sous:
        out.append("</ul>")
    out.append("</ul>")
    return "".join(out)


def sources(d):
    src = d.get("sources") or []
    if not src:
        return ""
    return (f'<p style="color:{GRIS};font-size:8pt;margin-top:2px">📎 Sources : '
            + " · ".join(source(s) for s in src) + "</p>")


def titre_bloc(titre, icone=""):
    """Titre de bloc : barre de couleur du module à gauche, fond clair."""
    return table1(f'<span style="font-size:13pt;color:{C["fort"]}"><b>{icone}{titre}</b></span>',
                  C["clair"], C["fort"], gauche=8, pad=7)


def flux(sc):
    etapes = [inline(e).replace("\n", "<br>") for e in sc.get("etapes", [])]
    if not etapes:
        return ""
    lignes = []
    par_ligne = 4 if len(etapes) > 4 else len(etapes)
    for i in range(0, len(etapes), par_ligne):
        cellules = []
        for j, e in enumerate(etapes[i:i + par_ligne]):
            k = i + j
            fond, fort = PASTELS[k % len(PASTELS)]
            if j:
                cellules.append(f'<td style="width:4%;text-align:center;color:{C["fort"]};'
                                f'font-size:16pt"><b>➜</b></td>')
            cellules.append(
                f'<td style="background-color:{fond};border:2px solid {fort};padding:8px;'
                f'text-align:center;vertical-align:middle;width:{int(92 / par_ligne)}%">'
                f'<span style="color:{fort};font-size:9pt"><b>ÉTAPE {k + 1}</b></span><br>'
                f'<span style="font-size:10pt">{e}</span></td>')
        lignes.append(f'<table style="width:100%;border-collapse:separate;border-spacing:0;'
                      f'margin:4px 0"><tr>{"".join(cellules)}</tr></table>')
        if i + par_ligne < len(etapes):
            lignes.append(f'<p style="text-align:center;color:{C["fort"]};font-size:16pt;'
                          f'margin:0"><b>⬇</b></p>')
    leg = (f'<p style="text-align:center;color:{GRIS};font-size:9pt"><i>{inline(sc["legende"])}</i></p>'
           if sc.get("legende") else "")
    return "".join(lignes) + leg


def cartes(elements):
    """Chiffres clés : grandes cartes colorées, 4 par ligne au plus."""
    out = []
    for i in range(0, len(elements), 4):
        rang = elements[i:i + 4]
        cellules = []
        for j, (c, txt) in enumerate(rang):
            fond, fort = PASTELS[(i + j) % len(PASTELS)]
            cellules.append(
                f'<td style="background-color:{fond};border-top:5px solid {fort};padding:10px;'
                f'text-align:center;vertical-align:top;width:{int(100 / len(rang))}%">'
                f'<span style="font-size:22pt;color:{fort}"><b>{inline(c)}</b></span><br>'
                f'<span style="font-size:9.5pt">{inline(txt)}</span></td>')
        out.append(f'<table style="width:100%;border-collapse:separate;border-spacing:6px 0;'
                   f'margin:6px 0"><tr>{"".join(cellules)}</tr></table>')
    return "".join(out)


def schema(sc):
    if not sc:
        return ""
    t = sc.get("type")
    if t == "image":
        cap = inline(sc.get("credit", ""))
        return (f'<p style="text-align:center;margin:8px 0 2px 0">'
                f'<img src="{html.escape(sc["url"])}" style="max-width:100%;width:560px"></p>'
                + table1(f'<span style="font-size:8.5pt;color:{GRIS}">🖼️ <i>{cap}</i></span>',
                         "#f6f6f8", pad=5, align="center"))
    if t == "flux":
        return flux(sc)
    if t in ("cercles", "chiffres"):
        return cartes(sc.get("elements", []))
    return ""


def tableau(lignes):
    if not lignes:
        return ""
    th = (f'style="background-color:{C["fort"]};color:#ffffff;border:1px solid {C["fort"]};'
          f'padding:6px;vertical-align:top"')
    out = ['<table style="width:100%;border-collapse:collapse;margin:6px 0">']
    out.append("<tr>" + "".join(f"<td {th}><b>{inline(c)}</b></td>" for c in lignes[0]) + "</tr>")
    for i, r in enumerate(lignes[1:]):
        fond = C["clair"] if i % 2 else "#ffffff"
        td = (f'style="background-color:{fond};border:1px solid #d5d5dc;padding:5px;'
              f'vertical-align:top;font-size:10pt"')
        cells = [f"<td {td}><b>{inline(c)}</b></td>" if k == 0 else f"<td {td}>{inline(c)}</td>"
                 for k, c in enumerate(r)]
        out.append("<tr>" + "".join(cells) + "</tr>")
    out.append("</table>")
    return "".join(out)


def colonnes(cols):
    n = max(1, len(cols))
    cellules = []
    for i, c in enumerate(cols):
        fond, fort = PASTELS[i % len(PASTELS)]
        cellules.append(
            f'<td style="vertical-align:top;background-color:{fond};border-top:5px solid {fort};'
            f'padding:8px;width:{100 // n}%">'
            f'<span style="color:{fort};font-size:11pt"><b>{inline(c.get("titre", ""))}</b></span>'
            f'{puces(c.get("puces"))}</td>')
    return (f'<table style="width:100%;border-collapse:separate;border-spacing:6px 0;margin:6px 0">'
            f'<tr>{"".join(cellules)}</tr></table>')


def icone_titre(tit):
    t = tit.lower()
    for mots, ic in ((("testez",), "❓ "), (("corrigé",), "✅ "), (("cas clinique",), "🩺 "),
                     (("ce que ça change", "en pratique", "pratique"), "🛠️ "),
                     (("vocabulaire",), "📖 "), (("objectifs",), "🎯 "),
                     (("piège", "attention", "alerte", "drapeau"), "⚠️ "),
                     (("liens",), "🔗 "), (("nouveautés",), "🆕 "), (("historique",), "🕓 ")):
        if any(m in t for m in mots):
            return ic
    return ""


def bloc(d):
    t = d.get("type")
    tit = d.get("titre", "")
    titre = inline(tit)
    if t == "contenu":
        corps = puces(d.get("puces"))
        if corps:
            corps = table1(corps, "#fafafc", pad=8)
        out = titre_bloc(titre, icone_titre(tit)) + corps + schema(d.get("schema"))
        if d.get("conclusion"):
            out += encadre("jaune", "👉 <b>" + inline(d["conclusion"].lstrip("> ")) + "</b>")
    elif t == "colonnes":
        out = titre_bloc(titre, icone_titre(tit)) + colonnes(d.get("colonnes", []))
    elif t == "tableau":
        out = titre_bloc(titre, icone_titre(tit) or "📋 ") + tableau(d.get("lignes"))
    elif t == "retenir":
        if tit.lower().startswith("rappel"):
            fond, fort, ic = "#e8f0fe", "#1a56c4", "🔁 "
        elif tit.lower().startswith(("en résumé", "en resume", "résumé")):
            fond, fort, ic = "#fff6d6", "#b58900", "✅ "
        else:
            fond, fort, ic = "#e8f5e9", "#2e7d32", "📌 "
        out = table1(f'<span style="font-size:12pt;color:{fort}"><b>{ic}{titre}</b></span><br>'
                     f'{inline(d.get("message", ""))}{puces(d.get("puces"))}',
                     fond, fort, gauche=8, pad=12)
    elif t == "phares":
        items = "".join(f'<li><span style="color:{ROUGE}"><b>{inline(p).replace("<b>", "").replace("</b>", "")}</b></span></li>'
                        for p in d.get("puces", []))
        return table1(f'<span style="font-size:13pt;color:{ROUGE}"><b>⭐ {titre}</b></span><ul>{items}</ul>',
                      "#fdecea", ROUGE, gauche=8, pad=12)
    elif t == "references":
        items = "".join(f'<li style="font-size:8.5pt;margin-bottom:2px">{source(p)}</li>'
                        for p in d.get("puces", []))
        return titre_bloc(titre, "📚 ") + f"<ol>{items}</ol>"
    else:
        return ""
    return out + sources(d)


def bandeau(numero, titre, icone=""):
    """Début de partie : grand bandeau à la couleur du module."""
    num = (f'<span style="font-size:11pt;color:#ffffff">PARTIE {numero}</span><br>' if numero else "")
    return (SAUT + f'<table style="width:100%;border-collapse:collapse;margin-bottom:10px"><tr>'
            f'<td style="background-color:{C["fort"]};padding:16px">{num}'
            f'<span style="font-size:20pt;color:#ffffff"><b>{icone}{titre}</b></span></td></tr></table>')


def garde(titre, plan):
    """Page de garde : bandeau, sous-titre, auteur, sommaire."""
    st = inline(titre.get("sous_titre", ""))
    out = [f'<table style="width:100%;border-collapse:collapse"><tr>'
           f'<td style="background-color:{C["fort"]};padding:28px">'
           f'<span style="font-size:11pt;color:#ffffff">🎓 {st}</span><br><br>'
           f'<span style="font-size:24pt;color:#ffffff"><b>{inline(titre.get("titre", ""))}</b></span>'
           f'</td></tr></table>',
           table1(f'<b>{inline(titre.get("auteur", ""))}</b><br>'
                  f'<span style="color:{GRIS}">Version du {inline(titre.get("date", ""))}</span>',
                  C["clair"], C["fort"], gauche=8, pad=12)]
    if plan and plan.get("puces"):
        lignes = "".join(
            f'<tr><td style="padding:5px 8px;border-bottom:1px solid #e3e3ea;font-size:11pt">'
            f'<span style="color:{C["fort"]}"><b>▸</b></span> {inline(p)}</td></tr>'
            for p in plan["puces"])
        out.append(f'<p style="font-size:15pt;color:{C["fort"]};margin-top:18px"><b>🗺️ Sommaire</b></p>'
                   f'<table style="width:100%;border-collapse:collapse">{lignes}</table>')
    return "".join(out)


def convertir(plans):
    diapos = []
    for p in plans:
        diapos += p.get("diapos", [])
    titre = next((d for d in diapos if d.get("type") == "titre"), {})
    if not titre.get("titre") and plans:
        titre = dict(titre, titre=plans[0].get("titre", ""))
    plan = next((d for d in diapos if d.get("type") == "plan"), None)
    m = re.search(r"\bM(\d\d)\b", titre.get("sous_titre", "") + " " + str(plans[0].get("categorie", "")))
    C["fort"], C["clair"] = MODULES.get(f"M{m.group(1)}", DEFAUT) if m else DEFAUT
    out = ['<html><head><meta charset="utf-8"></head>'
           '<body style="font-family:Arial;font-size:10.5pt;line-height:1.35">',
           garde(titre, plan)]
    profondeur, n = False, 0
    for d in diapos:
        t = d.get("type")
        if t in ("titre", "plan"):
            continue
        tit = d.get("titre", "")
        sur = (d.get("surtitre") or "").lower()
        if t == "section":
            profondeur = "profondeur" in tit.lower()
            if profondeur:
                out.append(bandeau(None, "Pour aller plus en profondeur", "🔬 "))
            else:
                n += 1
                out.append(bandeau(n, inline(re.sub(r"^\d+[.)]\s*", "", tit))))
            continue
        if ("profondeur" in sur or tit.startswith("Approfondir")) and not profondeur:
            out.append(bandeau(None, "Pour aller plus en profondeur", "🔬 "))
            profondeur = True
        elif profondeur and (t in ("phares", "references") or tit.startswith(("Testez", "Corrigé", "Liens", "Nouveautés", "Historique"))):
            profondeur = False
        b = bloc(d)
        if b:
            out.append(b + ESPACE)
    out.append("</body></html>")
    return "\n".join(x for x in out if x) + "\n"


def main():
    plans = [json.load(open(a, encoding="utf-8")) for a in sys.argv[1:]]
    if not plans:
        sys.exit(__doc__)
    sys.stdout.write(convertir(plans))


if __name__ == "__main__":
    main()
