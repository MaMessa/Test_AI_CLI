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