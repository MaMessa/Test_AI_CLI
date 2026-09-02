from contextlib import asynccontextmanager
from fastapi import FastAPI
from nicegui import ui
from src.services import initialize_database
from src.ui.pages_recipes import render_recipes_page
from src.ui.pages_grocery import render_grocery_page
from src.ui.pages_ingredients import render_ingredients_page

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Initialize DB tables and seed data on startup
    initialize_database()
    yield

# Create FastAPI app
app = FastAPI(title="Recipe to Grocery App", lifespan=lifespan)

# --- Page Routes ---

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

# Mount NiceGUI on FastAPI
ui.run_with(app, mount_path='/')

if __name__ in {"__main__", "__mp_main__"}:
    ui.run(port=8080, title="Recipe to Grocery App")
