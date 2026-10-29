#!/bin/bash
# Script d'installation de l'environnement cloud de Matis (à coller dans « Setup script »).
# Il autorise les agents à lancer les scripts PDF de la veille et ceux des diaporamas,
# et seulement ceux-là. Il complète ~/.claude/settings.json sans rien effacer.
mkdir -p ~/.claude
python3 - <<'EOF'
import json, os
chemin = os.path.expanduser("~/.claude/settings.json")
try:
    reglages = json.load(open(chemin))
except Exception:
    reglages = {}
autorises = reglages.setdefault("permissions", {}).setdefault("allow", [])
for regle in (
    "Bash(python3 scripts/generer_pdf.py:*)",
    "Bash(python3 scripts/generer_fiche_patient.py:*)",
    "Bash(python3 scripts/verifier_pdf.py:*)",
    "Bash(python3 scripts/remplir.py:*)",
    "Bash(python3 scripts/ajuster_mise_en_page.py:*)",
):
    if regle not in autorises:
        autorises.append(regle)
json.dump(reglages, open(chemin, "w"), indent=2)
EOF
