"""Corrige la mise en page d'un cours déjà construit (modèles version 3).

Usage : python3 scripts/ajuster_mise_en_page.py presentation.json requetes.json

presentation.json : sortie de read_presentation avec
  fields = ["slides(objectId,pageElements(objectId,transform,shape(shapeType,text.textElements.textRun.content)))"]
requetes.json : requêtes à passer à update_presentation (par paquets de 200 au plus).

Les zones sont reconnues à leur géométrie (identique à celle du Modèle DU) :
- Mtexte : corps agrandi (228 pt de haut), conclusion descendue et réduite à 20 pt,
  corps passé en 19 pt si le texte ne tient pas en 22 pt ;
- colonnes : texte 17 pt, titres 18 pt ;
- retenir : puces 20 pt ;
- références : 11 pt.
Les diapos modèles masquées (identifiants commençant par « M ») sont traitées comme les autres.
"""
import json
import math
import sys

EMU_PT = 12700


def proche(a, b, tol=0.01):
    return abs(a - b) <= tol


def texte(e):
    return "".join(t.get("textRun", {}).get("content", "")
                   for t in e.get("shape", {}).get("text", {}).get("textElements", []))


def lignes(t, par_ligne):
    return sum(max(1, math.ceil(len(p) / par_ligne)) for p in t.split("\n") if p.strip())


def style(oid, taille):
    return {"updateTextStyle": {"objectId": oid, "textRange": {"type": "ALL"},
                                "style": {"fontSize": {"magnitude": taille, "unit": "PT"}},
                                "fields": "fontSize"}}


def place(oid, t, sy, ty):
    return {"updatePageElementTransform": {"objectId": oid, "applyMode": "ABSOLUTE", "transform": {
        "scaleX": t["scaleX"], "scaleY": sy, "shearX": 0, "shearY": 0,
        "translateX": t["translateX"], "translateY": ty, "unit": "EMU"}}}


def requetes(pres):
    req = []
    for s in pres["slides"]:
        els = s.get("pageElements", [])
        concl = None
        for e in els:
            t = e.get("transform", {})
            if proche(t.get("scaleX", 0), 2.794) and proche(t.get("scaleY", 0), 0.1693) \
                    and t.get("translateY") in (3759200, 4064000):
                concl = e
        for e in els:
            t = e.get("transform", {})
            sx, sy, ty = t.get("scaleX", 0), t.get("scaleY", 0), t.get("translateY", 0)
            contenu = texte(e)
            plein = bool(contenu.strip())
            if e is concl:
                req.append(place(e["objectId"], t, 0.127, 4064000))
                if plein:
                    req.append(style(e["objectId"], 20))
            elif proche(sx, 2.794) and proche(sy, 0.8467) and ty == 1117600:      # corps Mtexte
                req.append(place(e["objectId"], t, 0.9652, 1117600))
                if plein and lignes(contenu, 55) > 8:                             # 8 lignes tiennent en 22 pt
                    req.append(style(e["objectId"], 19))
            elif proche(sx, 1.2361) and proche(sy, 0.9525) and plein:             # colonnes : texte
                req.append(style(e["objectId"], 17))
            elif proche(sx, 1.2361) and proche(sy, 0.1101) and plein:             # colonnes : titres
                req.append(style(e["objectId"], 18))
            elif proche(sx, 2.54) and proche(sy, 0.5503) and ty == 2667000 and plein:  # retenir
                req.append(style(e["objectId"], 20))
            elif proche(sx, 2.7093) and proche(sy, 1.1218) and plein:             # références
                req.append(style(e["objectId"], 11))
    return req


if __name__ == "__main__":
    donnees = json.load(open(sys.argv[1]))
    donnees = donnees.get("content", donnees)
    r = requetes(donnees)
    json.dump(r, open(sys.argv[2], "w"), ensure_ascii=False)
    print(len(r), "requêtes")
