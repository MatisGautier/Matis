#!/usr/bin/env python3
"""Transforme le plan d'un diaporama (JSON) en requêtes Google Slides (batchUpdate).

Usage : python3 construire_diapos.py plan.json dossier_sortie/ [prefixe]
  -> écrit dossier_sortie/diapo_01.json, diapo_02.json… : une liste de requêtes
     par diapo, à envoyer dans l'ordre avec update_presentation ;
  -> affiche les avertissements (texte trop long, source manquante…).
  prefixe (lettres, par défaut « d ») : à changer à chaque reconstruction d'un
  diaporama existant (« v2 », « v3 »…) pour que les identifiants restent uniques.

Format du plan :
{
  "titre": "VPPB",                      # titre du diaporama
  "categorie": "Pathologie",            # Pathologie | Test | Technique | Traitement
  "diapos": [
    {"type": "titre", "titre": "...", "sous_titre": "...", "auteur": "...", "date": "..."},
    {"type": "section", "titre": "2. Physiopathologie"},
    {"type": "contenu", "titre": "...", "puces": ["...", "**gras**", ...],
     "schema": {...} (facultatif), "sources": ["Auteur, Revue année, PMID ..."]},
    {"type": "tableau", "titre": "...", "lignes": [["en-tête", ...], [...]], "sources": [...]},
    {"type": "references", "titre": "Références", "puces": ["...", ...]}
  ]
}
Schémas (dans une diapo « contenu », affichés à droite des puces ; sans puces, en pleine largeur) :
  {"type": "image", "url": "https://upload.wikimedia.org/...", "credit": "Auteur, Wikimedia Commons, CC BY 3.0"}
  {"type": "flux", "sens": "vertical" | "horizontal", "etapes": ["...", "...", ...], "legende": "..."}
  {"type": "chiffres", "elements": [["64 %", "guéris en 1 séance"], ...]}  (3 au maximum)
"""
import json
import re
import sys
from pathlib import Path

L, H = 720, 405                      # taille d'une diapo 16:9, en points
MARGE = 30
COULEURS = {"Pathologie": "#a479e2", "Test": "#4a86e8", "Technique": "#16a765",
            "Traitement": "#16a765", "Synthèse": "#1c4587"}
BLEU_NUIT, GRIS, GRIS_CLAIR = "#1c2b4a", "#5a5a66", "#f2f4f8"
POLICE = "Arial"


def rgb(hexa):
    hexa = hexa.lstrip("#")
    return {"opaqueColor": {"rgbColor": {k: round(int(hexa[i:i + 2], 16) / 255, 3) for k, i in
                                          (("red", 0), ("green", 2), ("blue", 4))}}}


def cadre(page, x, y, w, h):
    return {"pageObjectId": page,
            "size": {"width": {"magnitude": round(w, 1), "unit": "PT"},
                     "height": {"magnitude": round(h, 1), "unit": "PT"}},
            "transform": {"scaleX": 1, "scaleY": 1, "translateX": round(x, 1),
                          "translateY": round(y, 1),
                          "unit": "PT"}}


class Diapo:
    def __init__(self, num, avert, prefixe="d"):
        self.page = f"{prefixe}{num:03d}diapo"
        self.req = [{"createSlide": {"objectId": self.page,
                                     "slideLayoutReference": {"predefinedLayout": "BLANK"}}}]
        self.n = 0
        self.avert = avert
        self.num = num

    def ident(self, prefixe):
        self.n += 1
        return f"{self.page}_{prefixe}{self.n:02d}"

    def fond(self, couleur):
        self.req.append({"updatePageProperties": {
            "objectId": self.page,
            "pageProperties": {"pageBackgroundFill": {"solidFill": {"color": rgb(couleur)["opaqueColor"]}}},
            "fields": "pageBackgroundFill.solidFill.color"}})

    def rectangle(self, x, y, w, h, couleur, forme="RECTANGLE", contour=None):
        oid = self.ident("forme")
        self.req.append({"createShape": {"objectId": oid, "shapeType": forme,
                                         "elementProperties": cadre(self.page, x, y, w, h)}})
        props = {"shapeBackgroundFill": {"solidFill": {"color": rgb(couleur)["opaqueColor"]}},
                 "outline": {"propertyState": "NOT_RENDERED"} if not contour else
                 {"outlineFill": {"solidFill": {"color": rgb(contour)["opaqueColor"]}},
                  "weight": {"magnitude": 1.2, "unit": "PT"}}}
        self.req.append({"updateShapeProperties": {
            "objectId": oid, "shapeProperties": props,
            "fields": "shapeBackgroundFill.solidFill.color,outline"}})
        return oid

    def texte(self, x, y, w, h, contenu, taille, couleur=BLEU_NUIT, gras=False,
              puces=False, centre=False, oid=None, forme_existante=False):
        if not forme_existante:
            oid = self.ident("texte")
            self.req.append({"createShape": {"objectId": oid, "shapeType": "TEXT_BOX",
                                             "elementProperties": cadre(self.page, x, y, w, h)}})
        lignes = contenu if isinstance(contenu, list) else [contenu]
        brut, gras_plages = "", []
        for i, ligne in enumerate(lignes):
            if i:
                brut += "\n"
            pos = 0
            for m in re.finditer(r"\*\*(.+?)\*\*", ligne):
                brut += ligne[pos:m.start()]
                debut = len(brut)
                brut += m.group(1)
                gras_plages.append((debut, len(brut)))
                pos = m.end()
            brut += ligne[pos:]
        if not brut:
            return oid
        taille = self.ajuster(brut, len(lignes), w, h, taille)
        self.req.append({"insertText": {"objectId": oid, "text": brut}})
        self.req.append({"updateTextStyle": {
            "objectId": oid, "textRange": {"type": "ALL"},
            "style": {"fontFamily": POLICE, "fontSize": {"magnitude": taille, "unit": "PT"},
                      "bold": gras, "foregroundColor": rgb(couleur)},
            "fields": "fontFamily,fontSize,bold,foregroundColor"}})
        for debut, fin in gras_plages:
            self.req.append({"updateTextStyle": {
                "objectId": oid,
                "textRange": {"type": "FIXED_RANGE", "startIndex": debut, "endIndex": fin},
                "style": {"bold": True}, "fields": "bold"}})
        if centre or puces:
            para = {"alignment": "CENTER"} if centre else {
                "spaceBelow": {"magnitude": 6, "unit": "PT"}}
            self.req.append({"updateParagraphStyle": {
                "objectId": oid, "textRange": {"type": "ALL"}, "style": para,
                "fields": ",".join(para)}})
        if puces:
            self.req.append({"createParagraphBullets": {
                "objectId": oid, "textRange": {"type": "ALL"},
                "bulletPreset": "BULLET_DISC_CIRCLE_SQUARE"}})
        return oid

    def ajuster(self, brut, nb_paragraphes, w, h, taille, minimum=10):
        """Réduit la police si le texte risque de déborder du cadre."""
        while True:
            par_ligne = max(1, int(w / (taille * 0.52)))
            lignes = sum(max(1, -(-len(p) // par_ligne)) for p in brut.split("\n"))
            if lignes * taille * 1.35 + nb_paragraphes * 4 <= h or taille <= minimum:
                break
            taille -= 1
        if lignes * taille * 1.35 + nb_paragraphes * 4 > h:
            self.avert.append(f"Diapo {self.num} : texte trop long, à raccourcir ou à couper en deux diapos")
        return taille

    def ligne(self, x1, y1, x2, y2, couleur):
        oid = self.ident("fleche")
        x, y = min(x1, x2), min(y1, y2)
        w, h = max(abs(x2 - x1), 1), max(abs(y2 - y1), 1)
        self.req.append({"createLine": {"objectId": oid, "lineCategory": "STRAIGHT",
                                        "elementProperties": cadre(self.page, x, y, w, h)}})
        self.req.append({"updateLineProperties": {
            "objectId": oid,
            "lineProperties": {"endArrow": "FILL_ARROW",
                               "weight": {"magnitude": 2, "unit": "PT"},
                               "lineFill": {"solidFill": {"color": rgb(couleur)["opaqueColor"]}}},
            "fields": "endArrow,weight,lineFill"}})


def entete(d, titre, accent):
    d.texte(MARGE, 16, L - 2 * MARGE, 40, titre, 22, BLEU_NUIT, gras=True)
    d.rectangle(MARGE, 58, 90, 3, accent)


def pied(d, sources, numero, total_titre):
    if sources:
        d.texte(MARGE, H - 38, L - 2 * MARGE - 60, 30, "Sources : " + " ; ".join(sources),
                8, GRIS)
    else:
        d.avert.append(f"Diapo {d.num} : aucune source (obligatoire sur chaque diapo de contenu)")
    d.texte(L - MARGE - 50, H - 26, 50, 16, f"{numero}", 8, GRIS, centre=True)


def schema(d, s, x, y, w, h, accent):
    genre = s.get("type")
    if genre == "image":
        oid = d.ident("image")
        d.req.append({"createImage": {"objectId": oid, "url": s["url"],
                                      "elementProperties": cadre(d.page, x, y, w, h - 18)}})
        if s.get("credit"):
            d.texte(x, y + h - 16, w, 14, "Image : " + s["credit"], 7, GRIS)
        else:
            d.avert.append(f"Diapo {d.num} : image sans crédit (auteur, licence)")
    elif genre == "flux":
        etapes = s["etapes"]
        n = len(etapes)
        vertical = s.get("sens", "vertical") == "vertical"
        espace = 16
        legende_h = 16 if s.get("legende") else 0
        if vertical:
            bh = min(52, (h - legende_h - espace * (n - 1)) / n)
            for i, etape in enumerate(etapes):
                by = y + i * (bh + espace)
                oid = d.rectangle(x, by, w, bh, GRIS_CLAIR, "ROUND_RECTANGLE", accent)
                d.texte(0, 0, w - 10, bh, etape, 12, BLEU_NUIT, centre=True,
                        oid=oid, forme_existante=True)
                if i < n - 1:
                    d.ligne(x + w / 2, by + bh, x + w / 2, by + bh + espace, accent)
        else:
            bw = (w - espace * (n - 1)) / n
            bh = min(90, h - legende_h)
            for i, etape in enumerate(etapes):
                bx = x + i * (bw + espace)
                oid = d.rectangle(bx, y, bw, bh, GRIS_CLAIR, "ROUND_RECTANGLE", accent)
                d.texte(0, 0, bw - 8, bh, etape, 11, BLEU_NUIT, centre=True,
                        oid=oid, forme_existante=True)
                if i < n - 1:
                    d.ligne(bx + bw, y + bh / 2, bx + bw + espace, y + bh / 2, accent)
        if s.get("legende"):
            d.texte(x, y + h - 14, w, 14, s["legende"], 8, GRIS, centre=True)
    elif genre == "chiffres":
        elements = s["elements"][:3]
        bh = (h - 10 * (len(elements) - 1)) / len(elements)
        for i, (valeur, libelle) in enumerate(elements):
            by = y + i * (bh + 10)
            d.rectangle(x, by, w, bh, GRIS_CLAIR, "ROUND_RECTANGLE")
            d.texte(x + 10, by + 6, w - 20, bh * 0.5, valeur, 26, accent, gras=True, centre=True)
            d.texte(x + 10, by + bh * 0.52, w - 20, bh * 0.45, libelle, 11, BLEU_NUIT, centre=True)
    else:
        d.avert.append(f"Diapo {d.num} : type de schéma inconnu « {genre} »")


def tableau(d, lignes, x, y, w, h, accent):
    oid = d.ident("tableau")
    nl, nc = len(lignes), max(len(r) for r in lignes)
    d.req.append({"createTable": {"objectId": oid, "rows": nl, "columns": nc,
                                  "elementProperties": cadre(d.page, x, y, w, h)}})
    taille = 11 if nl * nc <= 20 else 9
    for i, rang in enumerate(lignes):
        for j, cellule in enumerate(rang):
            if not cellule:
                continue
            texte = re.sub(r"\*\*(.+?)\*\*", r"\1", str(cellule))
            d.req.append({"insertText": {"objectId": oid, "cellLocation":
                                         {"rowIndex": i, "columnIndex": j}, "text": texte}})
            d.req.append({"updateTextStyle": {
                "objectId": oid, "cellLocation": {"rowIndex": i, "columnIndex": j},
                "textRange": {"type": "ALL"},
                "style": {"fontFamily": POLICE, "fontSize": {"magnitude": taille, "unit": "PT"},
                          "bold": i == 0,
                          "foregroundColor": rgb("#ffffff" if i == 0 else BLEU_NUIT)},
                "fields": "fontFamily,fontSize,bold,foregroundColor"}})
    d.req.append({"updateTableCellProperties": {
        "objectId": oid, "tableRange": {"location": {"rowIndex": 0, "columnIndex": 0},
                                        "rowSpan": 1, "columnSpan": nc},
        "tableCellProperties": {"tableCellBackgroundFill": {"solidFill": {"color": rgb(accent)["opaqueColor"]}}},
        "fields": "tableCellBackgroundFill.solidFill.color"}})
    if nl * 22 > h:
        d.avert.append(f"Diapo {d.num} : tableau trop haut, réduire le nombre de lignes")


def construire(plan, prefixe="d"):
    accent = COULEURS.get(plan.get("categorie"), "#4a86e8")
    avert, sorties = [], []
    for num, s in enumerate(plan["diapos"], 1):
        d = Diapo(num, avert, prefixe)
        genre = s.get("type", "contenu")
        if genre == "titre":
            d.fond(BLEU_NUIT)
            d.rectangle(MARGE, 150, 120, 4, accent)
            d.texte(MARGE, 70, L - 2 * MARGE, 80, s["titre"], 34, "#ffffff", gras=True)
            d.texte(MARGE, 165, L - 2 * MARGE, 70, s.get("sous_titre", ""), 16, "#d0d6e4")
            d.texte(MARGE, 320, L - 2 * MARGE, 50,
                    [s.get("auteur", ""), s.get("date", "")], 12, "#d0d6e4")
        elif genre == "section":
            d.fond(accent)
            d.texte(MARGE, 150, L - 2 * MARGE, 70, s["titre"], 30, "#ffffff", gras=True)
            if s.get("sous_titre"):
                d.texte(MARGE, 220, L - 2 * MARGE, 60, s["sous_titre"], 15, "#ffffff")
        elif genre == "tableau":
            entete(d, s["titre"], accent)
            tableau(d, s["lignes"], MARGE, 76, L - 2 * MARGE, H - 130, accent)
            pied(d, s.get("sources"), num, plan["titre"])
        elif genre == "references":
            entete(d, s.get("titre", "Références"), accent)
            d.texte(MARGE, 72, L - 2 * MARGE, H - 100, s["puces"], 10, BLEU_NUIT, puces=True)
            d.texte(L - MARGE - 50, H - 26, 50, 16, f"{num}", 8, GRIS, centre=True)
        else:
            entete(d, s["titre"], accent)
            corps_h = H - 76 - 44
            if s.get("schema") and s.get("puces"):
                d.texte(MARGE, 74, 390, corps_h, s["puces"], 15, puces=True)
                schema(d, s["schema"], 440, 74, L - MARGE - 440, corps_h, accent)
            elif s.get("schema"):
                schema(d, s["schema"], 120, 74, L - 240, corps_h, accent)
            else:
                d.texte(MARGE, 74, L - 2 * MARGE, corps_h, s.get("puces", []), 16, puces=True)
            pied(d, s.get("sources"), num, plan["titre"])
        sorties.append(d.req)
    return sorties, avert


def main():
    if len(sys.argv) not in (3, 4):
        sys.exit(__doc__)
    prefixe = sys.argv[3] if len(sys.argv) == 4 else "d"
    plan = json.load(open(sys.argv[1], encoding="utf-8"))
    sortie = Path(sys.argv[2])
    sortie.mkdir(parents=True, exist_ok=True)
    diapos, avert = construire(plan, prefixe)
    for i, requetes in enumerate(diapos, 1):
        (sortie / f"diapo_{i:02d}.json").write_text(
            json.dumps(requetes, ensure_ascii=False), encoding="utf-8")
    print(f"{len(diapos)} diapos -> {sortie}/diapo_XX.json")
    for a in avert:
        print("ATTENTION :", a)
    print("OK" if not avert else "À CORRIGER avant envoi")


if __name__ == "__main__":
    main()
