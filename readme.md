20 min - pré-prompt
Rôle : Tu es un Développeur Senior Python / Fullstack. 

Contexte :
Je dois créer une application web de Liste de Courses générée à partir de Recettes.
- Contrainte de temps : 1 heure maximum.
- Contrainte de ressources : Version gratuite de l'IA (quota de tokens très restreint).
- Objectif : Avoir une application fonctionnelle dès la fin des 15 premières minutes, puis ajouter des fonctionnalités progressivement (méthode itérative/versionnée) pour ne jamais me retrouver avec un code cassé si mon quota expire.

Besoins fonctionnels :
1. Fiche Recette : Nom, temps de prépa/cuisson, difficulté, prix, utilisation du four (oui/non), saison (été/hiver), végétarien (oui/non).
2. Générateur de liste : Sélection de recettes -> Génération automatique de la liste d'ingrédients pour 5 personnes.
3. Liste de courses : Ingrédients + quantités + système de coche (valider ce qui est dans le caddie).

Mes compétences : Python, FastAPI, SQLAlchemy, PostgreSQL, Docker.
Compétences Frontend : Aucune (débutant). Je veux apprendre une technologie Frontend basée sur Python/FastAPI, moderne, rapide à prendre en main et maintenable à long terme (ex: Streamlit, NiceGUI, Flet, ou HTML/HTMX/Jinja2).

Règles de réponse et d'exécution :
1. Maintien de la qualité : Architecture propre, modulaire et maintenable (pas de code monolithique ou de "bricolage" rapide). Code intégralement commenté.
2. Économie de tokens : 
   - Réponses ultra-concises, va droit au but.
   - Ne régénère JAMAIS des fichiers entiers si une modification mineure suffit. Indique uniquement les blocs de code à ajouter ou modifier.
3. Bonnes pratiques : séparation des responsabilités (routeur, modèles, services).

---

Exécute uniquement la PHASE 1 pour le moment :

PHASE 1 : Choix technologiques & Plan de Versionning
1. Propose la meilleure pile technique (Backend, Frontend Python rapide à apprendre, Base de données de dev légère pour aller vite).
2. Propose un découpage du projet en 4 ou 5 v0.X (ex: v0.1 MVP basique fonctionnel, v0.2, v0.3, etc.).
   - Chaque version doit être un incrément autonome et exécutable.
   - Divise chaque version en micro-étapes (mini-steps) à faible consommation de tokens.

Attends ma confirmation sur la Phase 1 avant de générer la moindre ligne de code.


# Reponse 

Pile Technique Recommandée
Backend / API : FastAPI (Validation Pydantic, rapidité, typage Python)

Base de Données Dev : SQLite + SQLAlchemy 2.0 (Zéro configuration Docker nécessaire, migration simple vers PostgreSQL plus tard)

Frontend Python : NiceGUI

Pourquoi NiceGUI ? 100% Python, s'exécute nativement au-dessus de FastAPI, syntaxe intuitive basée sur Vue.js/Quasar, très réactif sans avoir à gérer de state JavaScript. Idéal pour passer en prod avec FastAPI tout en restant simple à apprendre.

v0.1 — MVP Minimal In-Memory (Objectif 15 min)
Application 100% fonctionnelle sans base de données pour valider le flux UI immédiatement.

- Step 1.1 : Structure du projet & Initialisation FastAPI + NiceGUI.
- Step 1.2 : Formulaire de création rapide d'une recette (données en mémoire).
- Step 1.3 : Affichage de la liste des recettes saisies.

v0.2 — Persistance & Modèles de Données
Mise en place de la base SQLite et séparation propre des couches.

- Step 2.1 : Configuration SQLAlchemy 2.0 (Database session & Base model).
- Step 2.2 : Définition des Modèles (Recipe, Ingredient, RecipeIngredient).
- Step 2.3 : Refactorisation de l'UI v0.1 pour lire/écrire en base SQLite via des services.

v0.3 — Générateur de Liste de Courses & Interactivité
Cœur de métier : sélection de recettes et agrégation pour 5 personnes.

- Step 3.1 : UI de sélection des recettes (checkboxes/multi-select) + calcul du ratio portions (ex: base 1 pers. x 5).
- Step 3.2 : Service d'agrégation des ingrédients (somme des quantités pour mêmes ingrédients).
- Step 3.3 : Vue Liste de Courses interactive avec case à cocher (état validé/dans le caddie).

v0.4 — Filtres Métier & UI Refinement
Enrichissement des critères recettes et UX.

- Step 4.1 : Ajout des métadonnées recettes dans l'UI/Model (Prix, Difficulté, Four, Saison, Végétarien).
- Step 4.2 : Filtres de recherche sur le catalogue de recettes (ex: "Saison = Été", "Végétarien = Oui").

---
# Next
Maintenant que j'ai la stack +/- en tête je demande a l'IA de me genere un prompt opti pour l'utilisation de token 
---
# Prompt pour CLI v0.1: 

Act as a Senior Python Fullstack Developer. Create a working MVP (v0.1) of a Recipe-to-Grocery List web app in Python.

Stack:
- Backend/UI: FastAPI + NiceGUI (integrated)
- Database: In-memory list (NO database for v0.1 to save setup overhead)

Constraints:
- Extremely token-efficient: concise code, no fluff, clear comments.
- Architecture: Modular structure (separate UI components and data structures).
- Output format: Full code for all necessary files to run v0.1 immediately.

Requirements for v0.1:
1. In-memory storage for recipes (name, prep time, cook time, ingredients list).
2. Recipe Form Component: Create a new recipe with name, prep time, cook time, and ingredient list (comma-separated).
3. Recipe List Component: Display created recipes in cards/table.
4. Main entry point wiring FastAPI and NiceGUI on port 8080.

Generate:
1. `requirements.txt`
2. `src/state.py` (In-memory data store + data structures)
3. `src/ui/components.py` (NiceGUI forms and displays)
4. `main.py` (FastAPI + NiceGUI launcher)
5. Execution command to run the app.


