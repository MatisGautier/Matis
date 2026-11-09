#!/usr/bin/env python3
"""Convertit un plan de cours (JSON, format de construire_diapos.py) en HTML simple,
à importer en Google Doc pour obtenir le PDF du cours (notion.md, section 8).

Usage : python3 scripts/plan_vers_html.py plan.json [plan_partie2.json ...] > cours.html

Même contenu et même ordre que la page Notion (plan_vers_notion.py), en HTML que
Google Docs sait importer : titres, puces, tableaux, encadrés colorés, images par URL.
Les dépliants de Notion (approfondissement, corrigé, références) sont ouverts.
"""
import html
import json
import re
import sys

ROUGE = "#c62828"
ENCADRES = {
    "violet": ("#efe7fb", "#6a3fb5"),
    "jaune": ("#fff6d6", "#b58900"),
    "vert": ("#e8f5e9", "#2e7d32"),
    "bleu": ("#e8f0fe", "#1a56c4"),
    "gris": ("#f1f1f4", "#55555f"),
    "rouge": ("#fdecea", ROUGE),
}


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


def encadre(couleur, contenu):
    fond, bord = ENCADRES[couleur]
    return (f'<table style="width:100%;border-collapse:collapse"><tr>'
            f'<td style="background-color:{fond};border-left:4px solid {bord};padding:8px">'
            f"{contenu}</td></tr></table>")


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
        out.append(f"<li>{inline(p)}</li>")
    if sous:
        out.append("</ul>")
    out.append("</ul>")
    return "".join(out)


def sources(d):
    src = d.get("sources") or []
    if not src:
        return ""
    return ('<p style="color:#777777;font-size:9pt">Sources : '
            + " · ".join(source(s) for s in src) + "</p>")


def schema(sc):
    if not sc:
        return ""
    t = sc.get("type")
    if t == "image":
        cap = inline(sc.get("credit", ""))
        return (f'<p><img src="{html.escape(sc["url"])}" style="max-width:100%;width:440px"></p>'
                f'<p style="color:#777777;font-size:9pt"><i>{cap}</i></p>')
    if t == "flux":
        etapes = " → ".join(inline(e).replace("\n", " ") for e in sc.get("etapes", []))
        leg = f"<br><i>{inline(sc['legende'])}</i>" if sc.get("legende") else ""
        return encadre("bleu", f"🔀 {etapes}{leg}")
    if t in ("cercles", "chiffres"):
        cellules = "".join(
            f'<td style="background-color:#f1f1f4;padding:8px;text-align:center">'
            f'<b style="font-size:14pt">{inline(c)}</b><br>{inline(txt)}</td>'
            for c, txt in sc.get("elements", []))
        return f'<table style="width:100%;border-collapse:collapse"><tr>{cellules}</tr></table>'
    return ""


def tableau(lignes):
    if not lignes:
        return ""
    td = 'style="border:1px solid #cccccc;padding:4px;vertical-align:top"'
    out = ['<table style="width:100%;border-collapse:collapse">']
    out.append("<tr>" + "".join(f'<td {td}><b>{inline(c)}</b></td>' for c in lignes[0]) + "</tr>")
    for r in lignes[1:]:
        out.append("<tr>" + "".join(f"<td {td}>{inline(c)}</td>" for c in r) + "</tr>")
    out.append("</table>")
    return "".join(out)


def bloc(d):
    t = d.get("type")
    titre = inline(d.get("titre", ""))
    if t == "contenu":
        out = f"<h3>{titre}</h3>" + puces(d.get("puces")) + schema(d.get("schema"))
        if d.get("conclusion"):
            out += encadre("jaune", "👉 " + inline(d["conclusion"].lstrip("> ")))
    elif t == "colonnes":
        cols = "".join(
            f'<td style="vertical-align:top;padding:4px;width:{100 // max(1, len(d.get("colonnes", [])))}%">'
            f"<b>{inline(c.get('titre', ''))}</b>{puces(c.get('puces'))}</td>"
            for c in d.get("colonnes", []))
        out = f"<h3>{titre}</h3>" + f'<table style="width:100%;border-collapse:collapse"><tr>{cols}</tr></table>'
    elif t == "tableau":
        out = f"<h3>{titre}</h3>" + tableau(d.get("lignes"))
    elif t == "retenir":
        out = encadre("vert", f"📌 <b>{titre}</b><br>{inline(d.get('message', ''))}{puces(d.get('puces'))}")
    elif t == "phares":
        items = "".join(f'<li><span style="color:{ROUGE}"><b>{inline(p).replace("<b>", "").replace("</b>", "")}</b></span></li>'
                        for p in d.get("puces", []))
        return encadre("rouge", f'⭐ <span style="color:{ROUGE}"><b>{titre}</b></span><ul>{items}</ul>')
    elif t == "references":
        items = "".join(f'<li style="font-size:9pt">{source(p)}</li>' for p in d.get("puces", []))
        return f"<h3>📚 {titre}</h3><ul>{items}</ul>"
    else:
        return ""
    return out + sources(d)


def convertir(plans):
    diapos = []
    for p in plans:
        diapos += p.get("diapos", [])
    titre = next((d for d in diapos if d.get("type") == "titre"), {})
    nom = inline(titre.get("titre") or (plans[0].get("titre", "") if plans else ""))
    out = ['<html><head><meta charset="utf-8"></head><body style="font-family:Arial;font-size:11pt">',
           f"<h1>{nom}</h1>",
           encadre("violet", f"🎓 <b>{inline(titre.get('sous_titre', ''))}</b><br>"
                             f"{inline(titre.get('auteur', ''))}<br>Version du {inline(titre.get('date', ''))}")]
    profondeur = False
    for d in diapos:
        t = d.get("type")
        if t in ("titre", "plan"):
            continue
        tit = d.get("titre", "")
        sur = (d.get("surtitre") or "").lower()
        if t == "section":
            profondeur = "profondeur" in tit.lower()
            out.append("<h2>🔬 Pour aller plus en profondeur</h2>" if profondeur else f"<h2>{inline(tit)}</h2>")
            continue
        if ("profondeur" in sur or tit.startswith("Approfondir")) and not profondeur:
            out.append("<h2>🔬 Pour aller plus en profondeur</h2>")
            profondeur = True
        elif profondeur and (t in ("phares", "references") or tit.startswith(("Testez", "Corrigé", "Liens", "Nouveautés", "Historique"))):
            profondeur = False
        out.append(bloc(d))
    out.append("</body></html>")
    return "\n".join(x for x in out if x) + "\n"


def main():
    plans = [json.load(open(a, encoding="utf-8")) for a in sys.argv[1:]]
    if not plans:
        sys.exit(__doc__)
    sys.stdout.write(convertir(plans))


if __name__ == "__main__":
    main()
