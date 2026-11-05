#!/usr/bin/env python3
"""Convertit un plan de cours (JSON, format de construire_diapos.py) en page Notion.

Usage : python3 scripts/plan_vers_notion.py plan.json [plan_partie2.json ...] [--slides URL] > page.md

Sortie : Notion-flavored Markdown, prêt à passer en `content` de notion-create-pages.
Règles reprises de regles.md : vocabulaire au début, parties en titres, encadrés
« À retenir », « Pour aller plus en profondeur » en dépliant, corrigé en dépliant,
articles phares (★) en rouge et gras, sources sous chaque bloc.
"""
import json
import re
import sys

ROUGE = "red"


def inline(txt):
    """**gras** -> <b>, ★ ... en rouge gras, échappe les balises."""
    txt = str(txt).replace("<", "&lt;").replace(">", "&gt;")
    txt = re.sub(r"\*\*(.+?)\*\*", r"<b>\1</b>", txt)
    return txt


def source(s):
    s = inline(s)
    if "★" in s:
        return f'<span color="{ROUGE}"><b>{s}</b></span>'
    return s


def puces(items, prof=0):
    out = []
    for p in items or []:
        p = str(p)
        if p.startswith("- "):
            out.append("\t" + "- " + inline(p[2:]))
        elif re.match(r"^\d+\. ", p):
            out.append(inline(p))
        else:
            out.append("- " + inline(p))
    return out


def sources(diapo):
    src = diapo.get("sources") or []
    if not src:
        return []
    return ['<p color="gray">Sources : ' + " · ".join(source(s) for s in src) + "</p>"]


def schema(sc):
    if not sc:
        return []
    t = sc.get("type")
    if t == "image":
        cap = inline(sc.get("credit", ""))
        return [f'<image source="{sc["url"]}">{cap}</image>']
    if t == "flux":
        etapes = [inline(e).replace("\n", " ") for e in sc.get("etapes", [])]
        lignes = [f'<callout icon="🔀" color="blue_bg">', " → ".join(etapes)]
        if sc.get("legende"):
            lignes += ["", f"<i>{inline(sc['legende'])}</i>"]
        lignes.append("</callout>")
        return lignes
    if t in ("cercles", "chiffres"):
        cols = ["<columns>"]
        for chiffre, texte in sc.get("elements", []):
            cols += [
                "<column>",
                f'<callout icon="📊" color="gray_bg">',
                f"<b>{inline(chiffre)}</b>\\",
                inline(texte),
                "</callout>",
                "</column>",
            ]
        cols.append("</columns>")
        return cols
    return []


def tableau(lignes):
    if not lignes:
        return []
    def cell(c):
        return inline(c).replace("|", "\\|").replace("\n", " ")
    out = ["| " + " | ".join(cell(c) for c in lignes[0]) + " |",
           "| " + " | ".join("---" for _ in lignes[0]) + " |"]
    for r in lignes[1:]:
        out.append("| " + " | ".join(cell(c) for c in r) + " |")
    return out


def bloc(d):
    """Une diapo -> liste de lignes Markdown (sans le titre de section)."""
    t = d.get("type")
    titre = inline(d.get("titre", ""))
    out = []
    if t == "contenu":
        out.append(f"### {titre}")
        out += puces(d.get("puces"))
        out += schema(d.get("schema"))
        if d.get("conclusion"):
            out += [f'<callout icon="👉" color="yellow_bg">', inline(d["conclusion"].lstrip("> ")), "</callout>"]
    elif t == "colonnes":
        out.append(f"### {titre}")
        out.append("<columns>")
        for c in d.get("colonnes", []):
            out += ["<column>", f"<b>{inline(c.get('titre', ''))}</b>", ""] + puces(c.get("puces")) + ["</column>"]
        out.append("</columns>")
    elif t == "tableau":
        out.append(f"### {titre}")
        out += tableau(d.get("lignes"))
    elif t == "retenir":
        out += [f'<callout icon="📌" color="green_bg">', f"<b>{titre}</b>", "", inline(d.get("message", ""))]
        if d.get("puces"):
            out.append("")
            out += puces(d.get("puces"))
        out.append("</callout>")
    elif t == "phares":
        out += [f'<callout icon="⭐" color="red_bg">', f'<span color="{ROUGE}"><b>{titre}</b></span>', ""]
        out += [f'- <span color="{ROUGE}"><b>{inline(p).replace("<b>", "").replace("</b>", "")}</b></span>' for p in d.get("puces", [])]
        out.append("</callout>")
        return out  # pas de ligne de sources
    elif t == "references":
        out += ['<toggle heading="h3">', f"📚 {titre}", ""]
        for p in d.get("puces", []):
            out.append("- " + source(p))
        out.append("</toggle>")
        return out
    elif t == "plan":
        return []  # remplacé par la table des matières
    else:
        return []
    out += sources(d)
    return out


def convertir(plans, slides=None):
    diapos = []
    for p in plans:
        diapos += p.get("diapos", [])
    titre = next((d for d in diapos if d.get("type") == "titre"), {})
    out = []
    intro = inline(titre.get("sous_titre", ""))
    out += ['<callout icon="🎓" color="purple_bg">', f"<b>{intro}</b>\\", inline(titre.get("auteur", "")) + "\\",
            f"Version du {inline(titre.get('date', ''))}", "</callout>", ""]
    if slides:
        out += ['<toggle heading="h3">', "🖥️ Voir le diaporama", "", f"<embed source=\"{slides}\">Diaporama du cours</embed>", "</toggle>", ""]
    out += ["<table-of-contents />", ""]

    profondeur = False  # dans le dépliant « Pour aller plus en profondeur »
    corrige = False
    def fermer():
        nonlocal profondeur, corrige
        if profondeur or corrige:
            out.extend(["</toggle>", ""])
        profondeur = corrige = False

    for d in diapos:
        t = d.get("type")
        if t == "titre":
            continue
        titre = d.get("titre", "")
        sur = (d.get("surtitre") or "").lower()
        if t == "section":
            fermer()
            if "profondeur" in titre.lower():
                out += ['<toggle heading="h2">', "🔬 Pour aller plus en profondeur", ""]
                profondeur = True
            else:
                out += ["---", f"## {inline(titre)}", ""]
            continue
        est_prof = "profondeur" in sur or titre.startswith("Approfondir")
        est_corrige = titre.startswith("Corrigé")
        if est_prof and not profondeur:
            fermer()
            out += ['<toggle heading="h2">', "🔬 Pour aller plus en profondeur", ""]
            profondeur = True
        elif est_corrige and not corrige:
            fermer()
            out += ['<toggle heading="h3">', "✅ Corrigé (cliquer pour afficher)", ""]
            corrige = True
        elif profondeur and not est_prof and not titre.startswith("Approfondir"):
            fermer()
        elif corrige and not est_corrige:
            fermer()
        lignes = bloc(d)
        if lignes:
            out += lignes + [""]
    fermer()
    return "\n".join(out).rstrip() + "\n"


def main():
    args = sys.argv[1:]
    slides = None
    if "--slides" in args:
        i = args.index("--slides")
        slides = args[i + 1]
        del args[i:i + 2]
    plans = [json.load(open(a, encoding="utf-8")) for a in args]
    sys.stdout.write(convertir(plans, slides))


if __name__ == "__main__":
    main()
