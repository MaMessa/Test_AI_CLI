from contextlib import asynccontextmanager
from typing import Set
from fastapi import FastAPI
from nicegui import ui
from src.services import initialize_database
from src.ui.components import recipe_form_component, recipe_list_component, grocery_list_component

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Initialize SQLite database tables on app startup
    initialize_database()
    yield

# Create FastAPI app with lifespan handler
app = FastAPI(title="Recipe to Grocery App", lifespan=lifespan)

@ui.page('/')
def main_page():
    # Local state tracking checked recipes for the grocery list
    selected_recipe_ids: Set[int] = set()

    with ui.header().classes('bg-blue-700 text-white p-4 justify-between items-center shadow-md'):
        ui.label('🥗 Recipe-to-Grocery App (v0.3)').classes('text-xl font-bold tracking-wide')

    with ui.row().classes('w-full p-4 justify-center items-start gap-4 wrap'):
        # Grocery List Component (Right/Center)
        refresh_grocery = grocery_list_component(selected_recipe_ids)
        
        # Recipe List Component with Selection Checkboxes (Center/Left)
        refresh_recipe_list = recipe_list_component(selected_recipe_ids, on_selection_change=refresh_grocery)
        
        # Recipe Creator Form Component (Left)
        recipe_form_component(on_saved_callback=refresh_recipe_list)

# Mount NiceGUI on FastAPI
ui.run_with(app, mount_path='/')

if __name__ in {"__main__", "__mp_main__"}:
    ui.run(port=8080, title="Recipe to Grocery App")
