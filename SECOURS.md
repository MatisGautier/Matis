# Plan de secours des consignes des agents

Consigne de Matis du 23/11/2026 : si la branche `veille` ne marche plus, les agents récupèrent leurs consignes ailleurs, dans cet ordre.

1. **Branche `veille`** du dépôt `MatisGautier/Matis` : la source normale.
2. **Branche `secours`** : une copie de `veille`, au même commit.
3. **Archive Google Drive** « consignes_agents.tar.gz », dans le dossier Drive « Consignes des agents (secours) » de Matis : `tar xzf consignes_agents.tar.gz -C /home/user` donne `/home/user/depot`, avec la même organisation que le dépôt (dont `veille/vendor`).

Un agent qui a dû passer par un secours le signale dans son bilan (onglet `Bilans`). Mage le met alors en ⚠️ dans le rapport du matin.

## Mise à jour

Chaque soir, la ronde de Mage compare `veille` et `secours`. Si elles diffèrent, Mage :

- pousse `veille` sur `secours` ;
- refait l'archive Drive en remplaçant le même fichier ;
- note la nouvelle version dans le LISEZ-MOI du dossier Drive.

Si `veille` a disparu, Mage ne la recrée pas : il prévient Matis par mail.
