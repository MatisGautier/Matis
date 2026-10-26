#!/usr/bin/env python3
"""Vérifie qu'un PDF est intact avant et après son envoi.

Usage :
  python3 verifier_pdf.py fiche.pdf
      -> nombre de pages, taille en octets, empreinte md5, erreurs éventuelles
  python3 verifier_pdf.py fiche.pdf --taille <octets>
      -> compare avec la taille renvoyée par Google Drive (fileSize)
  python3 verifier_pdf.py fiche.pdf --drive <resultat_download_file_content>
      -> compare avec le fichier relu sur Google Drive (contrôle complet)
  python3 verifier_pdf.py fiche.pdf --mail <resultat_get_message_RAW.json>
      -> compare avec la pièce jointe du mail envoyé

Code de sortie 0 si tout est bon, 1 sinon (le message dit quoi refaire).
"""
import base64
import email
import hashlib
import json
import re
import subprocess
import sys


def controle_local(chemin):
    donnees = open(chemin, "rb").read()
    erreurs = []
    if not donnees.startswith(b"%PDF") or b"%%EOF" not in donnees[-64:]:
        erreurs.append("le fichier n'est pas un PDF complet")
    texte = subprocess.run(["pdftotext", chemin, "/dev/null"],
                           capture_output=True, text=True)
    if "Error" in texte.stderr:
        erreurs.append("pdftotext signale des erreurs : " + texte.stderr.strip()[:200])
    info = subprocess.run(["pdfinfo", chemin], capture_output=True, text=True).stdout
    pages = next((l.split()[-1] for l in info.splitlines() if l.startswith("Pages:")), "?")
    return donnees, pages, erreurs


def pieces_jointes_du_mail(chemin_json):
    d = json.load(open(chemin_json))
    raw = d["raw"] + "=" * (-len(d["raw"]) % 4)
    message = email.message_from_bytes(base64.urlsafe_b64decode(raw))
    return [p.get_payload(decode=True) for p in message.walk()
            if p.get_content_type() == "application/pdf"]


def pdf_telecharge_de_drive(chemin):
    """Retrouve le PDF dans le résultat de download_file_content (texte ou JSON)."""
    texte = open(chemin, encoding="utf-8", errors="replace").read()
    for morceau in re.findall(r"JVBER[A-Za-z0-9+/=_\-\\n]+", texte):
        morceau = morceau.replace("\\n", "").replace("-", "+").replace("_", "/")
        try:
            return base64.b64decode(morceau + "=" * (-len(morceau) % 4))
        except ValueError:
            continue
    return None


def main():
    if len(sys.argv) not in (2, 4):
        sys.exit(__doc__)
    donnees, pages, erreurs = controle_local(sys.argv[1])
    md5 = hashlib.md5(donnees).hexdigest()
    print(f"{sys.argv[1]} : {pages} page(s), {len(donnees)} octets, md5 {md5}")
    if len(sys.argv) == 4:
        option, valeur = sys.argv[2], sys.argv[3]
        if option == "--taille" and int(valeur) != len(donnees):
            erreurs.append(f"Drive a reçu {valeur} octets au lieu de {len(donnees)} : "
                           "base64 mal recopié, mets le fichier à la corbeille et renvoie-le")
        elif option == "--drive":
            recu = pdf_telecharge_de_drive(valeur)
            if recu is None or hashlib.md5(recu).hexdigest() != md5:
                erreurs.append("le fichier relu sur Drive est différent du fichier local : "
                               "mets-le à la corbeille et renvoie-le")
        elif option == "--mail":
            recus = [hashlib.md5(p).hexdigest() for p in pieces_jointes_du_mail(valeur)]
            if md5 not in recus:
                erreurs.append("la pièce jointe reçue est différente du fichier local : "
                               "renvoie le PDF dans le même fil")
    for e in erreurs:
        print("ERREUR :", e)
    print("OK" if not erreurs else "À REFAIRE")
    sys.exit(1 if erreurs else 0)


if __name__ == "__main__":
    main()
