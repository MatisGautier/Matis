#!/usr/bin/env python3
"""Génère la fiche PDF d'un article à partir d'un fichier JSON.

Fiche article (consigne de Matis, 16/11/2026) : 3 pages pleines, qui commencent par un
résumé IMRAD d'une demi-page (champ « imrad » : introduction, methode, resultats,
discussion), puis l'article expliqué simplement, avec les mots à connaître.
Synthèse thématique (categorie "Synthèse") : 2 pages, sans IMRAD. Champ facultatif
« titres » pour renommer les sections.

Usage : python3 generer_pdf.py fiche.json sortie.pdf
"""
import json
import re
import sys
from pathlib import Path

# reportlab est fourni dans veille/vendor : aucune installation nécessaire
sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "vendor"))
try:
    from PIL import Image  # noqa: F401  (reportlab l'importe d'office)
except Exception:  # Pillow absent ou compilé pour un autre Python : les fiches n'ont aucune image
    import types
    _pil, _image = types.ModuleType("PIL"), types.ModuleType("PIL.Image")
    _image.Image = type("Image", (), {})
    _pil.Image = _image
    sys.modules.update({"PIL": _pil, "PIL.Image": _image})
from datetime import date

from reportlab.lib import colors
from reportlab.lib.enums import TA_LEFT
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.units import mm
from reportlab.platypus import (
    Flowable,
    KeepTogether,
    ListFlowable,
    ListItem,
    Paragraph,
    SimpleDocTemplate,
    Spacer,
    Table,
    TableStyle,
)

POLICE, POLICE_GRAS = "Helvetica", "Helvetica-Bold"
REMPLACEMENTS = {
    "≥": ">=", "≤": "<=", "→": "->", "←": "<-", "≈": "env. ", "≠": "!=",
    "×": "x", "−": "-", "ı": "i", "ş": "s", "ğ": "g", "Ş": "S", "İ": "I",
    "α": "alpha", "β": "beta", "μ": "u", "’": "'", "‘": "'", " ": " ",
}

COULEURS = {
    # Couleurs de Matis (27/11/2026) : vert HAS, gris Pathos, rouge Pédiatrie, bleu ORL,
    # « transparent » (fond blanc, contour gris) Kiné pratique, orange Synthèse.
    "Kiné pratique": "#55555f",
    "Pathos": "#7a8798",
    "ORL": "#2f6fd6",
    "Pédiatrie ORL": "#d93025",
    "HAS": "#1f9d55",
    "Synthèse": "#f57c00",
}
TRANSPARENT = {"Kiné pratique"}  # bandeau blanc à contour gris, texte sombre

PAGES_ARTICLE = 3
PAGES_SYNTHESE = 2
REMPLISSAGE_CIBLE = 0.75

IMRAD = [
    ("introduction", "Introduction", "Pourquoi cette étude ? La question posée."),
    ("methode", "Méthode", "Qui, combien, comment, ce qui a été mesuré."),
    ("resultats", "Résultats", "Les résultats principaux, avec leurs chiffres."),
    ("discussion", "Discussion", "Ce que les auteurs en concluent, et jusqu'où on peut les suivre."),
]
ECHELLES = (1.0, 0.94, 0.88, 0.82)

SECTIONS = [
    ("rappel_patho", "1. Rappel patho", "#7b5cc4"),
    ("mots_a_connaitre", "Les mots à connaître", "#8a6d1d"),
    ("article", "2. L'article expliqué simplement", "#2f6fd6"),
    ("limites", "3. Les limites", "#d9822b"),
    ("impact_pratique", "4. En quoi ça peut m'impacter", "#16a765"),
    ("a_tester_au_cabinet", "5. À tester au cabinet", "#0f7b6c"),
    ("pour_aller_plus_loin", "6. Pour aller plus loin", "#5a5a66"),
]


class Repere(Flowable):
    """Flowable invisible qui note la page et la hauteur restante où il tombe."""

    def __init__(self, registre):
        super().__init__()
        self.registre = registre

    def wrap(self, largeur, hauteur):
        self.restant = hauteur
        return (0, 0)

    def draw(self):
        self.registre["page"] = self.canv.getPageNumber()
        self.registre["restant"] = self.restant


def reduire(st, echelle):
    for style in st.values():
        for attr in ("fontSize", "leading", "spaceBefore", "spaceAfter"):
            setattr(style, attr, getattr(style, attr) * echelle)
    return st


def styles():
    base = dict(fontName=POLICE, fontSize=9.5, leading=13.5, alignment=TA_LEFT)
    return {
        "bandeau": ParagraphStyle("bandeau", fontName=POLICE_GRAS, fontSize=9,
                                  textColor=colors.white, leading=12),
        "titre": ParagraphStyle("titre", fontName=POLICE_GRAS, fontSize=15,
                                leading=19, textColor=colors.HexColor("#1b1b1f"),
                                spaceAfter=3),
        "sous_titre": ParagraphStyle("sous_titre", fontName=POLICE, fontSize=9,
                                     leading=12, textColor=colors.HexColor("#5a5a66"),
                                     spaceAfter=8),
        "meta": ParagraphStyle("meta", fontName=POLICE, fontSize=8.5, leading=11.5,
                               textColor=colors.HexColor("#33333d")),
        "h2": ParagraphStyle("h2", fontName=POLICE_GRAS, fontSize=11.5, leading=15,
                             spaceBefore=10, spaceAfter=4),
        "corps": ParagraphStyle("corps", **base),
        "bref": ParagraphStyle("bref", fontName=POLICE, fontSize=10, leading=14.5,
                               textColor=colors.HexColor("#1b1b1f")),
        "chiffre": ParagraphStyle("chiffre", fontName=POLICE_GRAS, fontSize=13,
                                  leading=16, textColor=colors.HexColor("#1b1b1f")),
        "imrad_lib": ParagraphStyle("imrad_lib", fontName=POLICE_GRAS, fontSize=9.5,
                                    leading=12.5, textColor=colors.white),
        "pied": ParagraphStyle("pied", fontName=POLICE, fontSize=7.5, leading=10,
                               textColor=colors.HexColor("#7a7a85")),
    }


def esc(texte):
    texte = str(texte)
    for avant, apres in REMPLACEMENTS.items():
        texte = texte.replace(avant, apres)
    texte = texte.encode("cp1252", "replace").decode("cp1252")
    texte = texte.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
    return re.sub(r"\*\*(.+?)\*\*", r"<b>\1</b>", texte)


def puces(items, style, couleur):
    return ListFlowable(
        [ListItem(Paragraph(esc(i), style), leftIndent=12) for i in items],
        bulletType="bullet", start="•", bulletColor=colors.HexColor(couleur),
        bulletFontName=POLICE_GRAS, bulletFontSize=9, leftIndent=12,
    )


def encadre(contenu, fond, bord):
    t = Table([[contenu]], colWidths=[176 * mm])
    t.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, -1), colors.HexColor(fond)),
        ("LINEBEFORE", (0, 0), (0, -1), 3, colors.HexColor(bord)),
        ("LEFTPADDING", (0, 0), (-1, -1), 9),
        ("RIGHTPADDING", (0, 0), (-1, -1), 9),
        ("TOPPADDING", (0, 0), (-1, -1), 7),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 7),
    ]))
    return t


def tuiles(chiffres, st, accent):
    chiffres = chiffres[:4]
    cellules = [[Paragraph(esc(valeur), st["chiffre"]),
                 Paragraph(esc(libelle), st["meta"])] for libelle, valeur in chiffres]
    largeur = 176 * mm / len(chiffres)
    t = Table([cellules], colWidths=[largeur] * len(chiffres))
    t.setStyle(TableStyle([
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("LINEABOVE", (0, 0), (-1, 0), 2, colors.HexColor(accent)),
        ("BACKGROUND", (0, 0), (-1, -1), colors.HexColor("#f7f7fa")),
        ("LINEAFTER", (0, 0), (-2, -1), 0.5, colors.white),
        ("LEFTPADDING", (0, 0), (-1, -1), 7),
        ("TOPPADDING", (0, 0), (-1, -1), 6),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
    ]))
    return t


def bloc_imrad(imrad, st, accent):
    """Résumé IMRAD : un tableau à 4 lignes, libellé coloré à gauche."""
    lignes = []
    for cle, libelle, _ in IMRAD:
        texte = imrad.get(cle)
        if texte:
            if isinstance(texte, list):
                texte = " ".join(texte)
            lignes.append([Paragraph(f"<b>{libelle}</b>", st["imrad_lib"]),
                           Paragraph(esc(texte), st["corps"])])
    if not lignes:
        return []
    t = Table(lignes, colWidths=[30 * mm, 146 * mm])
    t.setStyle(TableStyle([
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("BACKGROUND", (0, 0), (0, -1), colors.HexColor(accent)),
        ("BACKGROUND", (1, 0), (1, -1), colors.HexColor("#f7f7fa")),
        ("LINEBELOW", (0, 0), (-1, -2), 1.5, colors.white),
        ("LEFTPADDING", (0, 0), (-1, -1), 7),
        ("RIGHTPADDING", (0, 0), (-1, -1), 7),
        ("TOPPADDING", (0, 0), (-1, -1), 6),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
    ]))
    titre = Paragraph("Résumé de l'article (IMRAD)", ParagraphStyle(
        "hi", parent=st["h2"], textColor=colors.HexColor(accent), spaceBefore=4))
    return [KeepTogether([titre, t]), Spacer(1, 8)]


def construire(fiche, sortie, echelle=1.0):
    categorie = fiche.get("categorie", "Pathos")
    accent = COULEURS.get(categorie, "#4a86e8")
    st = reduire(styles(), echelle)
    doc = SimpleDocTemplate(sortie, pagesize=A4, leftMargin=17 * mm,
                            rightMargin=17 * mm, topMargin=14 * mm,
                            bottomMargin=14 * mm,
                            title=esc(fiche.get("titre_fr", "Fiche veille")),
                            author="Veille vestibulaire")
    flux = []

    bandeau_texte = f"VEILLE VESTIBULAIRE · {esc(categorie).upper()}"
    if fiche.get("type_etude"):
        bandeau_texte += f" · {esc(fiche['type_etude'])}"
    if fiche.get("score") not in (None, ""):
        bandeau_texte += f" · Pertinence {esc(fiche['score'])}/10"
    transparent = categorie in TRANSPARENT
    st_bandeau = st["bandeau"]
    if transparent:
        st_bandeau = ParagraphStyle("bandeau_t", parent=st_bandeau,
                                    textColor=colors.HexColor("#33333d"))
    bandeau = Table([[Paragraph(bandeau_texte, st_bandeau)]], colWidths=[176 * mm])
    bandeau.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, -1), colors.white if transparent else colors.HexColor(accent)),
        ("BOX", (0, 0), (-1, -1), 1.2 if transparent else 0, colors.HexColor(accent)),
        ("LEFTPADDING", (0, 0), (-1, -1), 8),
        ("TOPPADDING", (0, 0), (-1, -1), 5),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
    ]))
    flux += [bandeau, Spacer(1, 8)]

    flux.append(Paragraph(esc(fiche.get("titre_fr", "")), st["titre"]))
    flux.append(Paragraph(esc(fiche.get("titre_original", "")), st["sous_titre"]))

    meta = [
        ("Auteurs", fiche.get("auteurs", "")),
        ("Revue", f"{fiche.get('revue', '')} — {fiche.get('date', '')}"),
        ("Population", fiche.get("population", "")),
        ("Niveau de preuve", fiche.get("niveau_preuve", "")),
        ("Réf.", " · ".join(x for x in [
            f"PMID {fiche['pmid']}" if fiche.get("pmid") else "",
            f"DOI {fiche['doi']}" if fiche.get("doi") else "",
        ] if x)),
        ("Lien", fiche.get("lien", "")),
    ]
    t = Table([[Paragraph(f"<b>{k}</b>", st["meta"]), Paragraph(esc(v), st["meta"])]
               for k, v in meta if v], colWidths=[32 * mm, 144 * mm])
    t.setStyle(TableStyle([
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("LINEBELOW", (0, 0), (-1, -2), 0.3, colors.HexColor("#e2e2e8")),
        ("TOPPADDING", (0, 0), (-1, -1), 2.5),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 2.5),
    ]))
    flux += [t, Spacer(1, 8)]

    if fiche.get("imrad") and categorie != "Synthèse":
        flux += bloc_imrad(fiche["imrad"], st, accent)

    if fiche.get("en_bref"):
        flux.append(encadre(Paragraph(
            f"<b>En bref :</b> {esc(fiche['en_bref'])}", st["bref"]),
            "#f2f6fd", accent))

    if fiche.get("chiffres_cles"):
        flux += [Spacer(1, 6), tuiles(fiche["chiffres_cles"], st, accent)]

    for cle, titre, couleur in SECTIONS:
        items = fiche.get(cle) or []
        if not items:
            continue
        titre = fiche.get("titres", {}).get(cle, titre)
        h = ParagraphStyle("h", parent=st["h2"], textColor=colors.HexColor(couleur))
        flux.append(KeepTogether([Paragraph(titre, h),
                                  puces(items, st["corps"], couleur)]))

    if fiche.get("mots_cles"):
        flux += [Spacer(1, 10), Paragraph(
            "<b>Mots-clés :</b> " + esc(", ".join(fiche["mots_cles"])), st["meta"])]

    flux += [Spacer(1, 12), Paragraph(
        f"Fiche générée automatiquement le {date.today():%d/%m/%Y} à partir du "
        "résumé et, si disponible, du texte intégral. Synthèse d'aide à la "
        "réflexion : toujours vérifier l'article source avant de modifier une "
        "pratique clinique.", st["pied"])]

    registre = {}
    flux.append(Repere(registre))
    doc.build(flux)
    remplissage = 1 - registre.get("restant", 0) / doc.height
    return doc.page, remplissage


def pages_max(fiche):
    return PAGES_SYNTHESE if fiche.get("categorie") == "Synthèse" else PAGES_ARTICLE


def generer(fiche, sortie):
    fiche = dict(fiche)
    while True:
        for echelle in ECHELLES:
            pages, remplissage = construire(fiche, sortie, echelle)
            if pages <= pages_max(fiche):
                return pages, remplissage
        cle = max((c for c, _, _ in SECTIONS), key=lambda c: len(fiche.get(c) or []))
        if len(fiche.get(cle) or []) <= 1:
            return pages, remplissage
        fiche[cle] = fiche[cle][:-1]


if __name__ == "__main__":
    if len(sys.argv) != 3:
        sys.exit(__doc__)
    with open(sys.argv[1], encoding="utf-8") as f:
        fiche = json.load(f)
    pages, remplissage = generer(fiche, sys.argv[2])
    cible = pages_max(fiche)
    print(f"{sys.argv[2]} : {pages} page(s), dernière page remplie à "
          f"{remplissage:.0%}")
    if fiche.get("categorie") != "Synthèse" and not fiche.get("imrad"):
        print("À ENRICHIR : il manque le résumé IMRAD (champ « imrad »).")
    if pages < cible or remplissage < REMPLISSAGE_CIBLE:
        print(f"À ENRICHIR : la fiche doit occuper {cible} pages pleines "
              "(expliquer davantage l'article, ajouter des chiffres et des pistes cliniques).")
