#!/usr/bin/env python3
"""Construit un cours à partir des diapos modèles (présentation copiée de « Modèle DU »).

Usage : python3 remplir.py plan.json dossier_sortie/ [prefixe] [premiere_diapo]
  -> dossier_sortie/paquet_01.json, paquet_02.json… : 10 diapos par paquet, chacun à
     envoyer avec UN update_presentation (requests = contenu du fichier, à l'identique) ;
  premiere_diapo (défaut 1) : pour reprendre un cours commencé (ex. 12 -> diapos 12 et suivantes).

Même format de plan que construire_diapos.py. Chaque diapo = duplication d'un modèle
+ remplacement des textes : environ 15 fois plus court que de dessiner les formes.
"""
import json
import re
import sys
from pathlib import Path


MAX_PUCES = {"Mtexte": 360, "Mplan": 600, "Mrefs": 2500, "Mimage": 300, "Mfluxv": 300, "Mchiffres": 300,
             "Mretenir": 320, "Mcolonnes2": 380}


def nettoyer(t):
    return re.sub(r"\*\*(.+?)\*\*", r"\1", str(t))


def corps_et_gras(lignes):
    """Texte brut des puces et plages en gras (indices dans la zone de texte)."""
    brut, gras = "", []
    for i, ligne in enumerate(lignes):
        if i:
            brut += "\n"
        pos = 0
        for m in re.finditer(r"\*\*(.+?)\*\*", ligne):
            brut += ligne[pos:m.start()]
            debut = len(brut)
            brut += m.group(1)
            gras.append((debut, len(brut)))
            pos = m.end()
        brut += ligne[pos:]
    return brut, gras


def choisir_modele(s, avert, num):
    genre = s.get("type", "contenu")
    if genre in ("titre", "section"):
        return "M" + genre
    if genre == "plan":
        return "Mplan"
    if genre in ("cle", "retenir"):
        return "Mretenir"
    if genre == "colonnes":
        if len(s.get("colonnes", [])) != 2:
            avert.append(f"Diapo {num} : colonnes : exactement 2 colonnes")
        return "Mcolonnes2"
    if genre == "references":
        return "Mrefs"
    if genre == "tableau":
        nc = max(len(r) for r in s["lignes"])
        if nc > 3 or len(s["lignes"]) > 9:
            avert.append(f"Diapo {num} : tableau trop grand (3 colonnes et 9 lignes au maximum)")
        return f"Mtab{min(max(nc, 2), 3)}"
    sch = s.get("schema")
    if not sch:
        return "Mtexte"
    t = sch.get("type")
    if t == "cercles":
        n = len(sch["elements"])
        if not 3 <= n <= 4:
            avert.append(f"Diapo {num} : cercles : 3 ou 4 éléments")
        if s.get("puces"):
            avert.append(f"Diapo {num} : cercles : pas de puces sur cette diapo")
        return f"Mcercles{min(max(n, 3), 4)}"
    if t == "image":
        return "Mimage" if s.get("puces") else "Mimageseule"
    if t == "chiffres":
        n = len(sch["elements"])
        if not 2 <= n <= 3:
            avert.append(f"Diapo {num} : chiffres clés : 2 ou 3 éléments")
        return f"Mchiffres{min(max(n, 2), 3)}"
    if t == "flux":
        n = len(sch["etapes"])
        if s.get("puces"):
            if n > 5:
                avert.append(f"Diapo {num} : flux à droite des puces : 5 étapes au maximum")
            return f"Mfluxv{min(max(n, 3), 5)}"
        if n > 5:
            avert.append(f"Diapo {num} : flux : 5 étapes au maximum")
        return f"Mfluxh{min(max(n, 3), 5)}"
    avert.append(f"Diapo {num} : schéma inconnu « {t} »")
    return "Mtexte"


def remplacer(page, cle, valeur):
    return {"replaceAllText": {"containsText": {"text": "{{" + cle + "}}", "matchCase": True},
                               "replaceText": valeur, "pageObjectIds": [page]}}


def sous_puces(page, brut):
    """Les lignes « - … » sont des sous-points : sans puce, en retrait (comme dans les cours du DIU)."""
    req, pos = [], 0
    for ligne in brut.split("\n"):
        fin = pos + len(ligne)
        if ligne.startswith("- "):
            plage = {"type": "FIXED_RANGE", "startIndex": pos, "endIndex": fin}
            req.append({"deleteParagraphBullets": {"objectId": f"{page}_corps", "textRange": plage}})
            req.append({"updateParagraphStyle": {"objectId": f"{page}_corps", "textRange": plage, "style": {
                "indentStart": {"magnitude": 36, "unit": "PT"}, "indentFirstLine": {"magnitude": 36, "unit": "PT"}},
                "fields": "indentStart,indentFirstLine"}})
        pos = fin + 1
    return req


def diapo(s, num, prefixe, avert, surtitre=""):
    modele = choisir_modele(s, avert, num)
    page = f"{prefixe}{num:03d}diapo"
    ids = {modele: page}
    if modele.startswith(("Mtexte", "Mplan", "Mrefs", "Mfluxv", "Mchiffres", "Mretenir")) or modele == "Mimage":
        ids[f"{modele}_corps"] = f"{page}_corps"
    if modele == "Mcolonnes2":
        ids.update({"Mcolonnes2_c1": f"{page}_c1", "Mcolonnes2_c2": f"{page}_c2"})
    if modele.startswith("Mtab"):
        ids = {modele: page, f"{modele}_tab": f"{page}_tab"}
    ids[f"{modele}_titre"] = f"{page}_titre"     # tous les modèles ont une zone <modèle>_titre
    req = [{"duplicateObject": {"objectId": modele, "objectIds": ids}},
           {"updateSlidesPosition": {"slideObjectIds": [page], "insertionIndex": num - 1}},
           {"updateSlideProperties": {"objectId": page, "slideProperties": {"isSkipped": False},
                                      "fields": "isSkipped"}}]
    r = lambda cle, val: req.append(remplacer(page, cle, val))
    genre = s.get("type", "contenu")
    titre = nettoyer(s.get("titre", ""))
    r("TITRE", titre if genre in ("titre", "section") else titre.upper())
    if genre == "titre":
        r("SOUS_TITRE", s.get("sous_titre", ""))
        r("AUTEUR", s.get("auteur", ""))
        r("DATE", s.get("date", ""))
        return req
    if genre == "section":
        return req
    if len(titre) > 34:                       # au-delà, le titre en 26 pt passe sur deux lignes
        req.append({"updateTextStyle": {"objectId": f"{page}_titre", "textRange": {"type": "ALL"},
                                        "style": {"fontSize": {"magnitude": 19, "unit": "PT"}},
                                        "fields": "fontSize"}})
    r("NUM", str(num))
    r("SURTITRE", nettoyer(s.get("surtitre", surtitre)))
    if modele == "Mtexte":
        r("CONCLUSION", "> " + nettoyer(s["conclusion"]) if s.get("conclusion") else "")
    if modele not in ("Mplan", "Mrefs"):
        sources = s.get("sources")
        if not sources:
            avert.append(f"Diapo {num} : aucune source (obligatoire sur chaque diapo de contenu)")
        r("SOURCES", " ; ".join(sources or []))
    if modele.startswith("Mtab"):
        lignes = s["lignes"][:9]
        nc = int(modele[-1])
        for i in range(len(lignes)):          # les lignes en trop sont supprimées plus bas
            for j in range(nc):
                val = nettoyer(lignes[i][j]) if i < len(lignes) and j < len(lignes[i]) else ""
                r(f"{'abcdefghi'[i]}{j + 1}", val)
        for i in range(8, len(lignes) - 1, -1):
            req.append({"deleteTableRow": {"tableObjectId": f"{page}_tab",
                                           "cellLocation": {"rowIndex": i, "columnIndex": 0}}})
        return req
    if modele == "Mretenir":
        r("MESSAGE", nettoyer(s.get("message", "")))
    if modele == "Mcolonnes2":
        for i, col in enumerate((s.get("colonnes") or [{}, {}])[:2], 1):
            r(f"T{i}", nettoyer(col.get("titre", "")))
            brut, gras = corps_et_gras(col.get("puces", []))
            if len(brut) > MAX_PUCES["Mcolonnes2"]:
                avert.append(f"Diapo {num} : colonne {i} trop longue ({len(brut)} caractères, "
                             f"{MAX_PUCES['Mcolonnes2']} au maximum)")
            r(f"P{i}", brut)
            for debut, fin in gras:
                req.append({"updateTextStyle": {"objectId": f"{page}_c{i}",
                                                "textRange": {"type": "FIXED_RANGE", "startIndex": debut, "endIndex": fin},
                                                "style": {"bold": True}, "fields": "bold"}})
        return req
    if "corps" in "".join(ids.values()):
        brut, gras = corps_et_gras(s.get("puces", []))
        limite = next((v for k, v in MAX_PUCES.items() if modele.startswith(k)), 900)
        if len(brut) > limite:
            avert.append(f"Diapo {num} : texte trop long ({len(brut)} caractères, {limite} au maximum)")
        r("PUCES", brut)
        req.extend(sous_puces(page, brut))
        for debut, fin in gras:
            req.append({"updateTextStyle": {"objectId": f"{page}_corps",
                                            "textRange": {"type": "FIXED_RANGE", "startIndex": debut, "endIndex": fin},
                                            "style": {"bold": True}, "fields": "bold"}})
    sch = s.get("schema") or {}
    if modele.startswith("Mimage"):
        if not sch.get("credit"):
            avert.append(f"Diapo {num} : image sans crédit (auteur, licence)")
        r("CREDIT", sch.get("credit", ""))
        req.append({"replaceAllShapesWithImage": {
            "imageUrl": sch["url"], "imageReplaceMethod": "CENTER_INSIDE", "pageObjectIds": [page],
            "containsText": {"text": "{{IMAGE}}", "matchCase": True}}})
    elif modele.startswith("Mflux"):
        for i, etape in enumerate(sch["etapes"][:5], 1):
            r(f"E{i}", nettoyer(etape))
        for i in range(len(sch["etapes"]) + 1, int(modele[-1]) + 1):
            r(f"E{i}", "")
        r("LEGENDE", sch.get("legende", ""))
    elif modele.startswith("Mcercles"):
        for i, (valeur, libelle) in enumerate(sch["elements"][:4], 1):
            r(f"C{i}", valeur)
            r(f"L{i}", libelle)
    elif modele.startswith("Mchiffres"):
        for i, (valeur, libelle) in enumerate(sch["elements"][:3], 1):
            r(f"C{i}", valeur)
            r(f"L{i}", libelle)
    return req


def main():
    if not 3 <= len(sys.argv) <= 5:
        sys.exit(__doc__)
    plan = json.load(open(sys.argv[1], encoding="utf-8"))
    sortie = Path(sys.argv[2])
    sortie.mkdir(parents=True, exist_ok=True)
    prefixe = sys.argv[3] if len(sys.argv) > 3 else "d"
    premiere = int(sys.argv[4]) if len(sys.argv) > 4 else 1
    avert, diapos = [], []
    surtitre = plan.get("surtitre", "")          # par défaut : le titre de la dernière section
    for num, s in enumerate(plan["diapos"], 1):
        if s.get("type") == "section":
            surtitre = re.sub(r"^\s*\d+[.)]\s*", "", nettoyer(s.get("titre", "")))
        req = diapo(s, num, prefixe, avert, surtitre)
        if num >= premiere:
            diapos.append(req)
    for n, debut in enumerate(range(0, len(diapos), 10), 1):
        paquet = [x for d in diapos[debut:debut + 10] for x in d]
        (sortie / f"paquet_{n:02d}.json").write_text(json.dumps(paquet, ensure_ascii=False,
                                                                 separators=(",", ":")), encoding="utf-8")
    print(f"{len(plan['diapos'])} diapos dans le plan, {len(diapos)} à envoyer en "
          f"{-(-len(diapos) // 10)} paquet(s) -> {sortie}/paquet_XX.json")
    for a in avert:
        print("ATTENTION :", a)
    print("OK" if not avert else "À CORRIGER avant envoi")


if __name__ == "__main__":
    main()
