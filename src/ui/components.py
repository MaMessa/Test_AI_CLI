from nicegui import ui
from src.state import state

def recipe_form_component(on_added_callback):
    """Component for creating a new recipe."""
    with ui.card().classes('w-full max-w-md p-4 m-2 shadow-md'):
        ui.label('Add New Recipe').classes('text-xl font-bold mb-3 text-slate-800')
        
        name_input = ui.input('Recipe Name', placeholder='e.g., Spaghetti Carbonara').classes('w-full')
        prep_input = ui.number('Prep Time (mins)', value=15, min=0).classes('w-full')
        cook_input = ui.number('Cook Time (mins)', value=20, min=0).classes('w-full')
        ingredients_input = ui.textarea('Ingredients (comma-separated)', placeholder='Pasta, Eggs, Guanciale, Pecorino').classes('w-full')

        def submit():
            if not name_input.value or not name_input.value.strip():
                ui.notify('Please enter a recipe name', type='warning')
                return
            
            state.add_recipe(
                name=name_input.value.strip(),
                prep_time=int(prep_input.value or 0),
                cook_time=int(cook_input.value or 0),
                ingredients_raw=ingredients_input.value or ''
            )
            
            # Reset fields
            name_input.value = ''
            prep_input.value = 15
            cook_input.value = 20
            ingredients_input.value = ''
            
            ui.notify('Recipe saved successfully!', type='positive')
            if on_added_callback:
                on_added_callback()

        ui.button('Save Recipe', on_click=submit).classes('mt-4 w-full bg-blue-600 text-white font-semibold')


def recipe_list_component():
    """Component for displaying the list of recipes in cards."""
    container = ui.column().classes('w-full max-w-xl m-2')

    def refresh():
        container.clear()
        recipes = state.get_all()
        with container:
            ui.label('Saved Recipes').classes('text-xl font-bold mb-3 text-slate-800')
            if not recipes:
                ui.label('No recipes created yet. Fill out the form to add your first recipe!').classes('text-gray-500 italic p-4')
                return

            for recipe in recipes:
                with ui.card().classes('w-full mb-3 p-4 border border-gray-200 shadow-sm'):
                    with ui.row().classes('justify-between items-center w-full'):
                        ui.label(recipe.name).classes('text-lg font-bold text-slate-900')
                        ui.label(f'⏱️ Prep: {recipe.prep_time}m | Cook: {recipe.cook_time}m').classes('text-sm text-gray-600')
                    
                    ui.separator().classes('my-2')
                    
                    ui.label('Ingredients:').classes('text-xs font-semibold text-gray-500 uppercase tracking-wider mb-1')
                    with ui.row().classes('gap-1 wrap'):
                        for ingredient in recipe.ingredients:
                            ui.chip(ingredient, icon='check').classes('text-xs bg-slate-100 text-slate-700')

    refresh()
    return refresh
