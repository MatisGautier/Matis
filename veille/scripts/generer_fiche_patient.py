#!/usr/bin/env python3
"""Fiche patient d'une seule page, compréhensible par un enfant de 8 ans.

Usage : python3 generer_fiche_patient.py fiche_patient.json sortie.pdf
"""
import json
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

from reportlab.graphics.shapes import Circle, Drawing, Line, PolyLine, String
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.units import mm
from reportlab.platypus import Paragraph, SimpleDocTemplate, Spacer, Table, TableStyle

from generer_pdf import ECHELLES, POLICE, POLICE_GRAS, esc, reduire

PAGES_MAX = 1
LARGEUR = 176 * mm - 12
ECART = 5 * mm
DEMI = (LARGEUR - ECART) / 2

CARTES = [
    ("cest_quoi", "C'est quoi ?", "C'est quoi ?", "#2f6fd6", "#eaf1fd", "?"),
    ("pourquoi", "Pourquoi ça arrive ?", "Pourquoi ça arrive ?", "#7b5cc4", "#f1ecfb", "!"),
    ("ce_quon_a_decouvert", "Ce que les scientifiques ont découvert",
     "Ce que les scientifiques ont découvert", "#0f7b6c", "#e6f5f2", "loupe"),
    ("ce_que_tu_peux_faire", "Ce que tu peux faire", "Ce que vous pouvez faire",
     "#16a765", "#e8f7ee", "ok"),
    ("comment_ca_va_se_passer", "Comment ça va se passer", "Comment ça va se passer",
     "#d9822b", "#fdf1e4", "horloge"),
]


def icone(sorte, couleur, taille=22):
    d = Drawing(taille, taille)
    r = taille / 2
    d.add(Circle(r, r, r, fillColor=colors.HexColor(couleur), strokeColor=None))
    blanc = colors.white
    if sorte == "ok":
        d.add(PolyLine([r - 6, r, r - 1.5, r - 5, r + 6.5, r + 5],
                       strokeColor=blanc, strokeWidth=2.6))
    elif sorte == "loupe":
        d.add(Circle(r - 1.5, r + 1.5, 5, fillColor=None, strokeColor=blanc,
                     strokeWidth=2.2))
        d.add(Line(r + 2, r - 2, r + 6.5, r - 6.5, strokeColor=blanc, strokeWidth=2.6))
    elif sorte == "horloge":
        d.add(Circle(r, r, 7, fillColor=None, strokeColor=blanc, strokeWidth=2))
        d.add(Line(r, r, r, r + 5, strokeColor=blanc, strokeWidth=2))
        d.add(Line(r, r, r + 4, r, strokeColor=blanc, strokeWidth=2))
    else:
        d.add(String(r, r - 5.5, sorte, fontName=POLICE_GRAS, fontSize=15,
                     fillColor=blanc, textAnchor="middle"))
    return d


def styles():
    return {
        "bandeau": ParagraphStyle("bandeau", fontName=POLICE_GRAS, fontSize=9.5,
                                  leading=12, textColor=colors.white),
        "titre": ParagraphStyle("titre", fontName=POLICE_GRAS, fontSize=21,
                                leading=25, textColor=colors.HexColor("#1b1b1f")),
        "sous_titre": ParagraphStyle("sous_titre", fontName=POLICE, fontSize=11.5,
                                     leading=15, textColor=colors.HexColor("#33333d")),
        "phrase": ParagraphStyle("phrase", fontName=POLICE_GRAS, fontSize=12.5,
                                 leading=17, textColor=colors.HexColor("#1b1b1f")),
        "carte_titre": ParagraphStyle("carte_titre", fontName=POLICE_GRAS,
                                      fontSize=12.5, leading=15),
        "corps": ParagraphStyle("corps", fontName=POLICE, fontSize=11.5, leading=15.5,
                                textColor=colors.HexColor("#1b1b1f")),
        "savais": ParagraphStyle("savais", fontName=POLICE, fontSize=10.5, leading=14,
                                 textColor=colors.HexColor("#1b1b1f")),
        "source": ParagraphStyle("source", fontName=POLICE, fontSize=7.8, leading=10,
                                 textColor=colors.HexColor("#5a5a66")),
    }


def boite(contenu, largeur, fond, bord=None, rembourrage=8):
    t = Table([[contenu]], colWidths=[largeur])
    regles = [
        ("BACKGROUND", (0, 0), (-1, -1), colors.HexColor(fond)),
        ("LEFTPADDING", (0, 0), (-1, -1), rembourrage),
        ("RIGHTPADDING", (0, 0), (-1, -1), rembourrage),
        ("TOPPADDING", (0, 0), (-1, -1), rembourrage - 1),
        ("BOTTOMPADDING", (0, 0), (-1, -1), rembourrage),
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("ROUNDEDCORNERS", [8, 8, 8, 8]),
    ]
    if bord:
        regles.append(("BOX", (0, 0), (-1, -1), 1.2, colors.HexColor(bord)))
    t.setStyle(TableStyle(regles))
    return t


def contenu_carte(titre, items, couleur, sorte, st, largeur):
    entete = Table([[icone(sorte, couleur),
                     Paragraph(esc(titre), ParagraphStyle(
                         "t", parent=st["carte_titre"],
                         textColor=colors.HexColor(couleur)))]],
                   colWidths=[9 * mm, largeur - 9 * mm - 16])
    entete.setStyle(TableStyle([
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("LEFTPADDING", (0, 0), (-1, -1), 0),
        ("RIGHTPADDING", (0, 0), (-1, -1), 0),
        ("TOPPADDING", (0, 0), (-1, -1), 0),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 3),
    ]))
    return [entete] + [
        Paragraph(f"<font color='{couleur}'><b>•</b></font>&nbsp;&nbsp;{esc(i)}",
                  st["corps"]) for i in items]


def carte(titre, items, couleur, fond, sorte, st, largeur):
    return boite(contenu_carte(titre, items, couleur, sorte, st, largeur),
                 largeur, fond)


def rangee(cartes, st):
    cellules, regles = [], [
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("LEFTPADDING", (0, 0), (-1, -1), 8),
        ("RIGHTPADDING", (0, 0), (-1, -1), 8),
        ("TOPPADDING", (0, 0), (-1, -1), 7),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 8),
    ]
    for n, (titre, items, couleur, fond, sorte) in enumerate(cartes):
        col = 2 * n
        if n:
            cellules.append("")
        cellules.append(contenu_carte(titre, items, couleur, sorte, st, DEMI))
        regles.append(("BACKGROUND", (col, 0), (col, 0), colors.HexColor(fond)))
    largeurs = [DEMI, ECART, DEMI][:len(cellules)]
    t = Table([cellules], colWidths=largeurs, hAlign="LEFT")
    t.setStyle(TableStyle(regles))
    return t


def construire(fiche, sortie, echelle=1.0):
    st = reduire(styles(), echelle)
    enfant = fiche.get("public") == "enfant"
    doc = SimpleDocTemplate(sortie, pagesize=A4, leftMargin=17 * mm,
                            rightMargin=17 * mm, topMargin=12 * mm,
                            bottomMargin=11 * mm, title=esc(fiche.get("titre", "")),
                            author="Votre kinésithérapeute")
    public = "POUR LES ENFANTS ET LEURS PARENTS" if enfant else "POUR LES PATIENTS"
    bandeau = f"FICHE INFO VERTIGES ET ÉQUILIBRE · {public}"
    if fiche.get("cabinet"):
        bandeau += f"<br/><font name='{POLICE}'>{esc(fiche['cabinet'])}</font>"
    flux = [boite(Paragraph(bandeau, st["bandeau"]), LARGEUR, "#0f7b6c", rembourrage=6),
            Spacer(1, 7),
            Paragraph(esc(fiche.get("titre", "")), st["titre"])]
    if fiche.get("sous_titre"):
        flux += [Spacer(1, 3), Paragraph(esc(fiche["sous_titre"]), st["sous_titre"])]
    if fiche.get("en_une_phrase"):
        flux += [Spacer(1, 7), boite(Paragraph(esc(fiche["en_une_phrase"]),
                                               st["phrase"]),
                                     LARGEUR, "#fff6d6", "#f2c94c")]

    cartes = [(t_enf if enfant else t_adu, fiche[cle], couleur, fond, sorte)
              for cle, t_enf, t_adu, couleur, fond, sorte in CARTES if fiche.get(cle)]
    savais_tu = fiche.get("le_savais_tu")
    if savais_tu and len(cartes) % 2:
        cartes.append(("Le savais-tu ?", [savais_tu], "#5a5a66", "#f3f3f7", "i"))
        savais_tu = None
    flux.append(Spacer(1, 8))
    for i in range(0, len(cartes), 2):
        flux += [rangee(cartes[i:i + 2], st), Spacer(1, ECART)]

    if fiche.get("alerte"):
        titre_alerte = ("Préviens tout de suite un adulte si :" if enfant
                        else "Appelez vite un médecin (ou le 15) si :")
        flux.append(carte(titre_alerte, fiche["alerte"], "#d93025", "#fdecea", "!",
                          st, LARGEUR))
    if savais_tu:
        flux += [Spacer(1, ECART), boite(Paragraph(
            f"<b>Le savais-tu ?</b> {esc(savais_tu)}", st["savais"]),
            LARGEUR, "#f3f3f7")]

    sources = "".join(f"<br/>{n}. {esc(s)}"
                      for n, s in enumerate(fiche.get("sources", []), 1))
    remis_par = esc(fiche.get("remis_par") or "votre kinésithérapeute")
    flux += [Spacer(1, 7), Paragraph(
        "<b>Sources scientifiques :</b>" + sources + f"<br/>Fiche remise par <b>{remis_par}</b>. "
        "Elle ne remplace pas l'avis de votre médecin. "
        f"Fiche du {date.today():%d/%m/%Y}.", st["source"])]
    doc.build(flux)
    return doc.page


def generer(fiche, sortie):
    for echelle in ECHELLES:
        pages = construire(fiche, sortie, echelle)
        if pages <= PAGES_MAX:
            break
    return pages


if __name__ == "__main__":
    if len(sys.argv) != 3:
        sys.exit(__doc__)
    with open(sys.argv[1], encoding="utf-8") as f:
        pages = generer(json.load(f), sys.argv[2])
    print(f"{sys.argv[2]} : {pages} page(s)")
    if pages > PAGES_MAX:
        print("TROP LONG : raccourcir la fiche patient (1 page maximum).")