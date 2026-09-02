from fastapi import FastAPI
from nicegui import ui
from src.ui.components import recipe_form_component, recipe_list_component

# Initialize FastAPI application
app = FastAPI(title="Recipe to Grocery App")

# Define UI page layout
@ui.page('/')
def main_page():
    with ui.header().classes('bg-blue-700 text-white p-4 justify-between items-center shadow-md'):
        ui.label('🥗 Recipe-to-Grocery App (v0.1)').classes('text-xl font-bold tracking-wide')

    with ui.row().classes('w-full p-4 justify-center items-start gap-6'):
        refresh_list = recipe_list_component()
        recipe_form_component(on_added_callback=refresh_list)

# Mount NiceGUI onto FastAPI
ui.run_with(app, mount_path='/')

if __name__ in {"__main__", "__mp_main__"}:
    ui.run(port=8080, title="Recipe App")
