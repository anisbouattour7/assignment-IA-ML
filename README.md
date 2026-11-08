# Assignment 1 — Systèmes experts et algorithmes de recherche

Projet du module **IA et Machine Learning** (II2, ENSI, 2026-2027).
Application interactive développée en **Python** avec une interface **Streamlit**, composée de deux modules accessibles depuis un menu principal :

| Module | État |
| --- | --- |
| 1. Systèmes experts (chaînage avant et arrière) | ✅ Terminé |
| 2. Algorithmes de recherche dans les espaces d'états | 🚧 En cours de développement |

**Auteur :** Anis Bouattour

---

## 1. Module 1 — Systèmes experts

Ce module permet de construire et d'exécuter un système expert fondé sur une **base de faits** et une **base de règles** (logique propositionnelle, conditions reliées par `ET`).

### Fonctionnalités

- Affichage de la base de faits initiale et des règles sous la forme `SI conditions ALORS conclusion`.
- Choix de l'objectif à démontrer, avec indication de sa présence éventuelle dans la base de faits.
- Choix de la méthode : **chaînage avant** ou **chaînage arrière**.
- Exécution interactive : la trace du raisonnement s'affiche **pas à pas** (bouton « Étape suivante »), ou d'un coup (« Tout afficher »).
- Changement d'objectif ou de méthode **sans relancer l'application**.
- Gestion des connaissances : ajout, modification et suppression de faits et de règles depuis l'interface.
- Sauvegarde et rechargement d'une base de connaissances au format JSON.
- Résultat final : statut (démontré / non démontré), règles appliquées et faits déduits.

---

## 2. Prérequis

- **Python 3.10 ou plus récent** (développé avec Python 3.14)
- `pip` et le module `venv` (inclus avec Python)
- Un navigateur web
- Git (pour cloner le dépôt)

## 3. Installation

```bash
# 1. Récupérer le projet
git clone https://github.com/anisbouattour7/assignment-IA-ML.git
cd assignment-IA-ML

# 2. Créer un environnement virtuel
python -m venv .venv

# 3. L'activer
#    Windows (PowerShell) :
.venv\Scripts\Activate.ps1
#    Linux / macOS :
source .venv/bin/activate

# 4. Installer les dépendances
pip install -r requirements.txt
```

> Sous Windows, si PowerShell refuse d'activer l'environnement, exécutez une fois :
> `Set-ExecutionPolicy -Scope CurrentUser RemoteSigned`

## 4. Lancement de l'application

Depuis la **racine du projet**, avec l'environnement virtuel activé :

```bash
streamlit run app.py
```

L'application s'ouvre dans le navigateur à l'adresse `http://localhost:8501`.
Au tout premier lancement, Streamlit peut demander une adresse e-mail : appuyez simplement sur **Entrée** pour ignorer.

Pour arrêter l'application : `Ctrl+C` dans le terminal, ou le bouton **Quitter** du menu principal.

## 5. Utilisation du module Systèmes experts

1. Sur le **menu principal**, cliquez sur **Systèmes experts**.
2. Onglet **Raisonnement** :
   - consultez les faits initiaux et les règles ;
   - choisissez un **objectif** (un message indique s'il est déjà présent dans les faits) ;
   - choisissez la **méthode** (chaînage avant ou arrière) ;
   - cliquez sur **Lancer le raisonnement**, puis sur **Étape suivante** pour dérouler la trace.
3. Onglet **Gestion des connaissances** :
   - ajoutez, modifiez ou supprimez des faits et des règles (les conditions d'une règle sont séparées par des virgules) ;
   - sauvegardez la base dans `data/` ou rechargez une base existante.
   Toute modification efface la trace en cours.

### Exemple (base fournie : `data/example_knowledge_base.json`)

Faits : `ordinateur_ne_demarre_pas`, `voyant_alimentation_eteint`, `cable_branche`

| Règle | Définition |
| --- | --- |
| R1 | SI `voyant_alimentation_eteint` ET `cable_branche` ALORS `probleme_alimentation` |
| R2 | SI `probleme_alimentation` ALORS `verifier_bloc_alimentation` |
| R3 | SI `ordinateur_ne_demarre_pas` ET `probleme_alimentation` ALORS `panne_probable_alimentation` |

Pour l'objectif `panne_probable_alimentation` :

- **Chaînage avant** : applique R1, puis R2, puis R3 (première règle applicable dans l'ordre de la base).
- **Chaînage arrière** : ne remonte que ce qui est nécessaire, donc utilise uniquement R1 puis R3.

## 6. Tests

Les moteurs, le modèle et le service sont couverts par des tests unitaires `pytest` :

```bash
pytest
```

Les tests couvrent notamment : règles applicables ou non, validation de la base, chaînage avant et arrière, objectif déjà connu, objectif non démontrable, cycles de règles, non-modification des faits initiaux et cohérence entre les deux moteurs.

## 7. Architecture

```
assignment-IA-ML/
├── app.py                          # Point d'entrée Streamlit : menu principal et navigation
├── expert_system/                  # Logique métier, indépendante de l'interface
│   ├── models/
│   │   ├── fact.py                 # Fait (proposition atomique)
│   │   ├── rule.py                 # Règle SI conditions ALORS conclusion
│   │   ├── knowledge_base.py       # Faits + règles, validation, import/export JSON
│   │   ├── inference_step.py       # Étape de la trace de raisonnement
│   │   └── inference_result.py     # Résultat complet d'une exécution
│   ├── engines/
│   │   ├── inference_engine.py     # Contrat commun des moteurs (classe abstraite)
│   │   ├── forward_chaining.py     # Chaînage avant
│   │   └── backward_chaining.py    # Chaînage arrière
│   └── services/
│       └── expert_system.py        # Point d'entrée applicatif : validation et choix du moteur
├── ui/
│   ├── expert_system_page.py       # Page Streamlit du module 1
│   └── knowledge_management.py     # Onglet de gestion des connaissances
├── data/
│   └── example_knowledge_base.json # Base d'exemple
├── tests/                          # Tests unitaires pytest
├── pyproject.toml                  # Configuration pytest et ruff
└── requirements.txt
```

L'interface n'appelle que le service `ExpertSystem` ; les moteurs ne dépendent pas de Streamlit et se testent seuls.

## 8. Choix de conception

- **Copie de travail** : chaque exécution part des faits initiaux ; les moteurs n'y ajoutent jamais les faits déduits. Changer d'objectif ne pollue donc pas l'exécution suivante.
- **Chaînage avant** : à chaque cycle, on applique la première règle applicable (dans l'ordre de la base) qui produit un **nouveau fait**, puis on repart du début. Arrêt dès que l'objectif est atteint ou qu'aucune règle n'apporte plus rien. La terminaison est garantie, même avec des règles circulaires.
- **Chaînage arrière** : récursif. Pour prouver un but, on essaie les règles qui le concluent ; chaque condition devient un sous-but. Les **cycles** sont détectés grâce au chemin courant (pile des buts en cours). Les buts déjà démontrés sont mémorisés.
- **Trace structurée** : chaque étape est un objet (`InferenceStep`) avec sa règle, ses faits utilisés, le fait obtenu, une explication et une profondeur. L'interface s'en sert pour indenter l'arbre de preuve du chaînage arrière.

### Cas particuliers gérés

| Cas | Comportement |
| --- | --- |
| Objectif déjà dans les faits initiaux | Succès immédiat, aucune règle appliquée |
| Objectif non démontrable | Résultat « non démontré » avec trace de l'échec |
| Règles circulaires (A → B → A) | Pas de boucle infinie (cycle détecté ou aucun nouveau fait) |
| Plusieurs règles pour un même but | Essayées dans l'ordre, la suivante est tentée si la première échoue |
| Fait vide, règle sans condition ou sans conclusion | Refus avec message d'erreur explicite |
| Identifiant de règle en double | Refus avec message d'erreur explicite |
| Fichier JSON invalide | Message d'erreur, la base courante n'est pas modifiée |

## 9. Format de la base de connaissances (JSON)

```json
{
  "facts": ["ordinateur_ne_demarre_pas", "voyant_alimentation_eteint", "cable_branche"],
  "rules": [
    {"id": "R1", "conditions": ["voyant_alimentation_eteint", "cable_branche"], "conclusion": "probleme_alimentation"},
    {"id": "R2", "conditions": ["probleme_alimentation"], "conclusion": "verifier_bloc_alimentation"}
  ]
}
```

## 10. Limites connues

- Logique **propositionnelle** : pas de variables ni de prédicats, pas de négation, pas de facteur de certitude.
- Les conditions d'une règle sont uniquement reliées par `ET`.
- Renommer un fait ne met pas à jour les règles qui l'utilisent.

## 11. Module 2 — Algorithmes de recherche

*À venir : construction d'un graphe orienté pondéré, recherche non informée et informée, visualisation pas à pas.*

## 12. Démonstration

Vidéo de démonstration : *(lien à ajouter)*