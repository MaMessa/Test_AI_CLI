from fastapi import FastAPI
from nicegui import ui
from src.services import initialize_database
from src.ui.pages_recipes import render_recipes_page
from src.ui.pages_grocery import render_grocery_page
from src.ui.pages_ingredients import render_ingredients_page

# Initialiser la base de données et les données exemple immédiatement
initialize_database()

# Créer l'application FastAPI
app = FastAPI(title="Application Recettes & Liste de Courses")

# --- Routes des Pages ---

@ui.page('/')
@ui.page('/recipes')
def recipes_page():
    render_recipes_page()

@ui.page('/grocery')
def grocery_page():
    render_grocery_page()

@ui.page('/ingredients')
def ingredients_page():
    render_ingredients_page()

# Monter NiceGUI sur FastAPI
ui.run_with(app, mount_path='/')

if __name__ in {"__main__", "__mp_main__"}:
    # Écoute sur 0.0.0.0 pour autoriser le réseau local (téléphone) et les conteneurs Docker
    ui.run(host='0.0.0.0', port=8080, title="Application Recettes & Liste de Courses")
