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

Ce module permet de construire un **graphe orienté et pondéré**, de définir un état initial et un état objectif, puis d'exécuter différents algorithmes de recherche dans un espace d'états.

Il regroupe deux catégories d'algorithmes :

| **Catégorie** | **Algorithmes** |
|---|---|
| Recherche non informée | BFS, DFS, UCS |
| Recherche informée | Gloutonne (Greedy Best-First Search), A* |

### Fonctionnalités

- Création et suppression de sommets représentant les différents états du problème.
- Ajout et suppression d'arcs orientés entre les sommets.
- Association d'un coût numérique à chaque arc.
- Définition du sommet initial et du sommet objectif.
- Saisie des valeurs heuristiques `h(n)` pour les algorithmes de recherche informée.
- Choix de la catégorie de recherche et de l'algorithme à exécuter.
- Visualisation du graphe avec distinction entre les sommets explorés, les sommets en attente et le chemin final.
- Affichage du déroulement de la recherche étape par étape.
- Présentation du chemin trouvé et de son coût total.
- Gestion des cas où aucun chemin n'existe entre le départ et l'objectif.

### Algorithmes implémentés

#### A. Recherche non informée

Ces algorithmes explorent le graphe sans utiliser d'heuristique pour guider la recherche.

| **Algorithme** | **Principe** | **Structure utilisée** |
|---|---|---|
| **BFS** (Breadth-First Search) | Explore les sommets niveau par niveau, en commençant par les plus proches du sommet initial. | File FIFO |
| **DFS** (Depth-First Search) | Explore une branche aussi profondément que possible avant de revenir en arrière. | Pile LIFO |
| **UCS** (Uniform-Cost Search) | Explore en priorité le sommet ayant le coût cumulé le plus faible depuis le départ. | File de priorité |

#### B. Recherche informée

Ces algorithmes utilisent une fonction heuristique `h(n)` pour orienter l'exploration vers l'objectif.

| **Algorithme** | **Principe** | **Fonction de priorité** |
|---|---|---|
| **Gloutonne** (Greedy Best-First Search) | Choisit le sommet estimé le plus proche de l'objectif selon l'heuristique. | `h(n)` |
| **A*** (A-Star) | Combine le coût déjà parcouru et l'estimation du coût restant pour choisir le prochain sommet. | `f(n) = g(n) + h(n)` |

Avec :

- `g(n)` : coût réel du chemin entre le sommet initial et le sommet `n`.
- `h(n)` : estimation du coût restant entre `n` et l'objectif.
- `f(n)` : estimation du coût total d'un chemin passant par `n`.

**Remarque :** UCS et A* prennent en compte les coûts des arcs. BFS et DFS ne les utilisent pas pour guider leur exploration. La recherche gloutonne utilise l'heuristique, mais ne tient pas compte du coût déjà parcouru.

### Déroulement d'une recherche

1. Sur le menu principal, accéder à **Algorithmes de recherche**.
2. Construire le graphe en ajoutant les sommets et les arcs avec leurs coûts.
3. Sélectionner le sommet initial et le sommet objectif.
4. Choisir la catégorie de recherche :
   - Recherche non informée : BFS, DFS ou UCS.
   - Recherche informée : Gloutonne ou A*.
5. Pour une recherche informée, renseigner les valeurs heuristiques des sommets.
6. Cliquer sur **Lancer la recherche**.
7. Consulter les étapes de l'exploration et suivre l'évolution de la frontière.
8. Consulter le résultat final : chemin trouvé, coût total et sommets explorés.

### Exemple de graphe

Le graphe suivant illustre un exemple de recherche entre le sommet initial `A` et le sommet objectif `G`.

| **Arc** | **Coût** |
|---|---:|
| A → B | 4 |
| A → C | 2 |
| B → D | 5 |
| B → G | 12 |
| C → D | 8 |
| C → E | 3 |
| E → D | 2 |
| D → G | 3 |
| E → G | 7 |

Pour les algorithmes informés, des valeurs heuristiques sont associées aux sommets afin d'estimer leur distance restante jusqu'à l'objectif.

### Résultats et visualisation

À la fin de l'exécution, l'application présente notamment :

- Le statut de la recherche : chemin trouvé ou aucun chemin trouvé.
- Le chemin obtenu entre le sommet initial et l'objectif.
- Le coût total du chemin.
- Les sommets développés pendant l'exploration.
- La trace détaillée des étapes de recherche.
- Une représentation graphique du graphe mettant en évidence le chemin final.

### Choix de conception

- **Séparation de la logique métier et de l'interface** : les algorithmes sont développés indépendamment de Streamlit et peuvent être testés séparément.
- **Représentation du graphe** : utilisation de `NetworkX` pour gérer les sommets, les arcs orientés et leurs poids.
- **Visualisation** : utilisation de `Matplotlib` pour représenter graphiquement le graphe et les résultats de recherche.
- **Trace structurée** : chaque algorithme produit une trace contenant les sommets examinés, la frontière et les informations nécessaires au suivi de l'exécution.
- **Reconstruction du chemin** : les prédécesseurs des sommets permettent de reconstruire le chemin final et de calculer son coût.
- **Gestion des cycles** : des mécanismes de détection des sommets déjà explorés ou de mise à jour des meilleurs coûts évitent les explorations infinies.

### Limites et conditions

- Le graphe utilisé est orienté : un arc `A → B` ne crée pas automatiquement un arc `B → A`.
- Les coûts des arcs doivent être numériques et non négatifs.
- Les algorithmes informés nécessitent des valeurs heuristiques valides.
- BFS garantit un chemin avec un nombre minimal d'arcs, mais pas nécessairement un coût minimal.
- DFS ne garantit pas un chemin optimal.
- UCS trouve un chemin de coût minimal lorsque les coûts des arcs sont non négatifs.
- La recherche gloutonne ne garantit pas l'optimalité.
- A* garantit l'optimalité sous les conditions appropriées sur l'heuristique, notamment son admissibilité, et avec une implémentation adaptée.

### Tests

Les algorithmes et le modèle du graphe sont testés indépendamment de l'interface avec `pytest`.

Les tests couvrent notamment :

- La création des sommets et des arcs orientés.
- La validation des coûts et des valeurs heuristiques.
- Le fonctionnement de BFS et DFS.
- La recherche du chemin de coût minimal avec UCS.
- Le fonctionnement de la recherche gloutonne.
- L'optimalité de A* lorsque les conditions requises sont respectées.
- La reconstruction du chemin et le calcul de son coût.
- La gestion des cycles et des graphes sans chemin accessible.

