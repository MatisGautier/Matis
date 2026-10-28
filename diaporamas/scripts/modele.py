#!/usr/bin/env python3
"""Crée les diapos modèles du DU (à faire une seule fois, dans la présentation « Modèle DU »).

Usage : python3 modele.py sortie.json
  -> sortie.json : liste de requêtes batchUpdate qui créent les diapos modèles
     (identifiants fixes « M… », textes à remplacer « {{…}} »), puis les marquent
     « ignorées » pour qu'elles n'apparaissent pas en mode présentation.

Chaque cours est ensuite une copie de « Modèle DU » : remplir.py duplique ces
modèles et remplace les textes, sans recréer les formes une à une.
"""
import json
import sys

from construire_diapos import (BLEU_NUIT, GRIS, GRIS_CLAIR, H, L, MARGE, Diapo, cadre)

ACCENT = "#1c4587"
CORPS_H = H - 76 - 44
FLUX_V = (3, 4, 5)          # flux vertical à droite des puces
FLUX_H = (3, 4, 5)          # flux horizontal pleine largeur
CHIFFRES = (2, 3)
TAB_LIGNES = 9              # 1 en-tête + 8 lignes


class Modele(Diapo):
    def __init__(self, nom):
        super().__init__(0, [], "M")
        self.page = nom
        self.req = [{"createSlide": {"objectId": nom,
                                     "slideLayoutReference": {"predefinedLayout": "BLANK"}}}]
        self.nom_suivant = None

    def ident(self, prefixe):
        if self.nom_suivant:
            nom, self.nom_suivant = self.nom_suivant, None
            return nom
        return super().ident(prefixe)

    def nomme(self, suffixe):
        self.nom_suivant = f"{self.page}_{suffixe}"
        return self

    def ajuster(self, brut, nb_paragraphes, w, h, taille, minimum=10):
        return taille


def entete(m):
    m.nomme("titre").texte(MARGE, 16, L - 2 * MARGE, 40, "{{TITRE}}", 22, BLEU_NUIT, gras=True)
    m.rectangle(MARGE, 58, 90, 3, ACCENT)


def pied(m, sources=True):
    if sources:
        m.nomme("src").texte(MARGE, H - 38, L - 2 * MARGE - 60, 30, "Sources : {{SOURCES}}", 8, GRIS)
    m.nomme("num").texte(L - MARGE - 50, H - 26, 50, 16, "{{NUM}}", 8, GRIS, centre=True)


def corps(m, x, w, taille=16):
    m.nomme("corps").texte(x, 74, w, CORPS_H, "{{PUCES}}", taille, puces=True)


def boite(m, x, y, w, h, texte, taille):
    oid = m.rectangle(x, y, w, h, GRIS_CLAIR, "ROUND_RECTANGLE", ACCENT)
    m.texte(0, 0, w - 8, h, texte, taille, BLEU_NUIT, centre=True, oid=oid, forme_existante=True)


def legende(m, x, y, w):
    m.nomme("leg").texte(x, y, w, 14, "{{LEGENDE}}", 8, GRIS, centre=True)


def modeles():
    sortie = []

    m = Modele("Mtitre")
    m.fond(BLEU_NUIT)
    m.rectangle(MARGE, 150, 120, 4, ACCENT)
    m.nomme("titre").texte(MARGE, 70, L - 2 * MARGE, 80, "{{TITRE}}", 34, "#ffffff", gras=True)
    m.texte(MARGE, 165, L - 2 * MARGE, 70, "{{SOUS_TITRE}}", 16, "#d0d6e4")
    m.texte(MARGE, 320, L - 2 * MARGE, 50, ["{{AUTEUR}}", "{{DATE}}"], 12, "#d0d6e4")
    sortie.append(m)

    m = Modele("Msection")
    m.fond(ACCENT)
    m.nomme("titre").texte(MARGE, 150, L - 2 * MARGE, 70, "{{TITRE}}", 30, "#ffffff", gras=True)
    sortie.append(m)

    for nom, taille, sources in (("Mtexte", 16, True), ("Mplan", 16, False), ("Mrefs", 10, False)):
        m = Modele(nom)
        entete(m)
        if nom == "Mrefs":
            m.nomme("corps").texte(MARGE, 72, L - 2 * MARGE, H - 100, "{{PUCES}}", taille, puces=True)
        else:
            corps(m, MARGE, L - 2 * MARGE, taille)
        pied(m, sources)
        sortie.append(m)

    m = Modele("Mimage")
    entete(m)
    corps(m, MARGE, 390, 15)
    boite(m, 440, 74, L - MARGE - 440, CORPS_H - 18, "{{IMAGE}}", 8)
    m.texte(440, 74 + CORPS_H - 16, L - MARGE - 440, 14, "Image : {{CREDIT}}", 7, GRIS)
    pied(m)
    sortie.append(m)

    m = Modele("Mimageseule")
    entete(m)
    boite(m, 120, 74, L - 240, CORPS_H - 18, "{{IMAGE}}", 8)
    m.texte(120, 74 + CORPS_H - 16, L - 240, 14, "Image : {{CREDIT}}", 7, GRIS)
    pied(m)
    sortie.append(m)

    for n in FLUX_V:
        m = Modele(f"Mfluxv{n}")
        entete(m)
        corps(m, MARGE, 390, 15)
        x, w, esp = 440, L - MARGE - 440, 16
        bh = min(52, (CORPS_H - 16 - esp * (n - 1)) / n)
        for i in range(n):
            by = 74 + i * (bh + esp)
            boite(m, x, by, w, bh, f"{{{{E{i + 1}}}}}", 12)
            if i < n - 1:
                m.ligne(x + w / 2, by + bh, x + w / 2, by + bh + esp, ACCENT)
        legende(m, x, 74 + CORPS_H - 14, w)
        pied(m)
        sortie.append(m)

    for n in FLUX_H:
        m = Modele(f"Mfluxh{n}")
        entete(m)
        x, w, esp = MARGE, L - 2 * MARGE, 16
        bw, bh, y = (w - esp * (n - 1)) / n, 110, 74 + (CORPS_H - 110) / 2 - 10
        for i in range(n):
            bx = x + i * (bw + esp)
            boite(m, bx, y, bw, bh, f"{{{{E{i + 1}}}}}", 12)
            if i < n - 1:
                m.ligne(bx + bw, y + bh / 2, bx + bw + esp, y + bh / 2, ACCENT)
        legende(m, x, y + bh + 12, w)
        pied(m)
        sortie.append(m)

    for n in CHIFFRES:
        m = Modele(f"Mchiffres{n}")
        entete(m)
        corps(m, MARGE, 390, 15)
        x, w = 440, L - MARGE - 440
        bh = (CORPS_H - 10 * (n - 1)) / n
        for i in range(n):
            by = 74 + i * (bh + 10)
            m.rectangle(x, by, w, bh, GRIS_CLAIR, "ROUND_RECTANGLE")
            m.texte(x + 10, by + 6, w - 20, bh * 0.5, f"{{{{C{i + 1}}}}}", 26, ACCENT, gras=True, centre=True)
            m.texte(x + 10, by + bh * 0.52, w - 20, bh * 0.45, f"{{{{L{i + 1}}}}}", 11, BLEU_NUIT, centre=True)
        pied(m)
        sortie.append(m)

    for nc in (2, 3):
        m = Modele(f"Mtab{nc}")
        entete(m)
        oid = f"{m.page}_tab"
        m.req.append({"createTable": {"objectId": oid, "rows": TAB_LIGNES, "columns": nc,
                                      "elementProperties": cadre(m.page, MARGE, 76, L - 2 * MARGE, TAB_LIGNES * 26)}})
        for i in range(TAB_LIGNES):
            for j in range(nc):
                m.req.append({"insertText": {"objectId": oid, "cellLocation": {"rowIndex": i, "columnIndex": j},
                                             "text": f"{{{{{'abcdefghi'[i]}{j + 1}}}}}"}})
                m.req.append({"updateTextStyle": {
                    "objectId": oid, "cellLocation": {"rowIndex": i, "columnIndex": j},
                    "textRange": {"type": "ALL"},
                    "style": {"fontFamily": "Arial", "fontSize": {"magnitude": 10, "unit": "PT"},
                              "bold": i == 0,
                              "foregroundColor": {"opaqueColor": {"rgbColor": (
                                  {"red": 1, "green": 1, "blue": 1} if i == 0 else
                                  {"red": 0.11, "green": 0.169, "blue": 0.29})}}},
                    "fields": "fontFamily,fontSize,bold,foregroundColor"}})
        m.req.append({"updateTableCellProperties": {
            "objectId": oid, "tableRange": {"location": {"rowIndex": 0, "columnIndex": 0},
                                            "rowSpan": 1, "columnSpan": nc},
            "tableCellProperties": {"tableCellBackgroundFill": {"solidFill": {"color": {"rgbColor": {
                "red": 0.11, "green": 0.271, "blue": 0.529}}}}},
            "fields": "tableCellBackgroundFill.solidFill.color"}})
        pied(m)
        sortie.append(m)

    requetes = [r for m in sortie for r in m.req]
    requetes += [{"updateSlideProperties": {"objectId": m.page, "slideProperties": {"isSkipped": True},
                                            "fields": "isSkipped"}} for m in sortie]
    return requetes, [m.page for m in sortie]


def main():
    if len(sys.argv) != 2:
        sys.exit(__doc__)
    requetes, noms = modeles()
    json.dump(requetes, open(sys.argv[1], "w", encoding="utf-8"), ensure_ascii=False, separators=(",", ":"))
    print(f"{len(noms)} modèles, {len(requetes)} requêtes -> {sys.argv[1]}")


if __name__ == "__main__":
    main()
