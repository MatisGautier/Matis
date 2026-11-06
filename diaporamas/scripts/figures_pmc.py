#!/usr/bin/env python3
"""Liste les figures réutilisables des articles PubMed Central cités dans un cours.

Usage : python3 scripts/figures_pmc.py PMID [PMID ...] > figures.json

Voie officielle du NCBI (jeu de données « PMC Open Access » sur Amazon S3) :
1. PMID -> PMCID (API idconv de PMC) ;
2. notice JSON de l'article (licence, liste des images) ;
3. XML de l'article : numéro et légende de chaque figure.

Chaque figure a une adresse publique https://pmc-oa-opendata.s3.amazonaws.com/... utilisable telle
quelle dans <image source="…"> sur Notion.

Licences gardées (décision de Matis, 06/11/2026 : le DU n'est pas vendu) : CC0, CC BY, CC BY-SA,
CC BY-NC, CC BY-NC-SA, CC BY-ND, CC BY-NC-ND. Sous chaque image : auteur, revue, année, PMID et
licence. Licence « ND » : image telle quelle, jamais recadrée ni modifiée.
Hôtes nécessaires : pmc.ncbi.nlm.nih.gov, pmc-oa-opendata.s3.amazonaws.com.
"""
import html
import json
import re
import sys
import urllib.request

S3 = "https://pmc-oa-opendata.s3.amazonaws.com"
UA = {"User-Agent": "du-vestibulaire-figures/1.0"}
LICENCES = ("CC0", "CC BY")


def get(url, timeout=40):
    req = urllib.request.Request(url, headers=UA)
    with urllib.request.urlopen(req, timeout=timeout) as r:
        return r.read().decode("utf-8", "replace")


def pmcids(pmids):
    out = {}
    for i in range(0, len(pmids), 100):
        lot = ",".join(pmids[i:i + 100])
        d = json.loads(get(f"https://pmc.ncbi.nlm.nih.gov/tools/idconv/api/v1/articles/?ids={lot}&format=json&tool=du_vestibulaire"))
        for r in d.get("records", []):
            if r.get("pmcid"):
                out[str(r["pmid"])] = r["pmcid"]
    return out


def derniere_version(pmcid):
    liste = get(f"{S3}/?list-type=2&prefix={pmcid}.&delimiter=/")
    versions = re.findall(rf"<Prefix>({pmcid}\.(\d+))/</Prefix>", liste)
    if not versions:
        return None
    return max(versions, key=lambda v: int(v[1]))[0]


def texte(x):
    x = re.sub(r"<[^>]+>", " ", x)
    return re.sub(r"\s+", " ", html.unescape(x)).strip()


def article(pmid, pmcid):
    v = derniere_version(pmcid)
    if not v:
        return {"pmid": pmid, "pmcid": pmcid, "licence": None, "figures": [], "note": "absent du jeu Open Access"}
    meta = json.loads(get(f"{S3}/{v}/{v}.json"))
    lic = meta.get("license_code") or ""
    res = {"pmid": pmid, "pmcid": pmcid, "citation": meta.get("citation", ""), "licence": lic, "figures": []}
    if not lic.startswith(LICENCES) or meta.get("is_retracted"):
        res["note"] = "licence non réutilisable" if not meta.get("is_retracted") else "article rétracté"
        return res
    medias = {}
    for u in meta.get("media_urls", []):
        nom = u.split("/")[-1].split("?")[0]
        medias[nom.rsplit(".", 1)[0]] = f"{S3}/{v}/{nom}"
    xml = get(f"{S3}/{v}/{v}.xml")
    for fig in re.findall(r"<fig\b[^>]*>(.*?)</fig>", xml, re.S):
        g = re.search(r'<graphic[^>]*xlink:href="([^"]+)"', fig)
        if not g:
            continue
        cle = g.group(1).rsplit(".", 1)[0] if "." in g.group(1).split("/")[-1] else g.group(1)
        url = medias.get(cle.split("/")[-1])
        if not url:
            continue
        lab = re.search(r"<label>(.*?)</label>", fig, re.S)
        cap = re.search(r"<caption>(.*?)</caption>", fig, re.S)
        res["figures"].append({
            "figure": texte(lab.group(1)) if lab else "",
            "legende": texte(cap.group(1))[:500] if cap else "",
            "url": url,
        })
    return res


def main():
    pmids = [a for a in sys.argv[1:] if a.isdigit()]
    ids = pmcids(pmids)
    res = []
    for pmid in pmids:
        if pmid in ids:
            try:
                res.append(article(pmid, ids[pmid]))
            except Exception as e:
                res.append({"pmid": pmid, "pmcid": ids[pmid], "licence": None, "figures": [], "note": f"erreur : {e}"})
    json.dump(res, sys.stdout, ensure_ascii=False, indent=1)


if __name__ == "__main__":
    main()
