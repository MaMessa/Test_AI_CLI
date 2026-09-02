from typing import List
from nicegui import ui
from src.ui.layout import header_nav
from src.services import get_all_recipes, create_recipe, delete_recipe, get_all_master_ingredients
from src.models import RecipeCreate, IngredientCreate

def render_recipes_page():
    """Page layout for recipe catalogue and creation with autocompletion."""
    header_nav(active_page='recipes')

    with ui.column().classes('w-full max-w-6xl mx-auto p-4'):
        ui.label('📖 Recipe Catalogue & Creation').classes('text-2xl font-bold text-slate-800 mb-4')

        with ui.row().classes('w-full gap-6 items-start wrap'):
            # Left Column: Recipe Form with Master Ingredient Autocomplete
            with ui.card().classes('w-full max-w-md p-4 shadow-md'):
                ui.label('➕ Create Recipe (Base 4 Servings)').classes('text-xl font-bold text-slate-800 mb-2')

                name_input = ui.input('Recipe Name', placeholder='e.g., Pasta Carbonara').classes('w-full')
                
                with ui.row().classes('w-full gap-2'):
                    prep_input = ui.number('Prep (m)', value=15, min=0).classes('flex-1')
                    cook_input = ui.number('Cook (m)', value=20, min=0).classes('flex-1')
                    servings_input = ui.number('Base Servings', value=4, min=1).classes('flex-1')

                ui.separator().classes('my-3')
                ui.label('Add Ingredients from Master Pool').classes('text-sm font-bold text-slate-700')

                # Fetch master ingredients for dropdown autocomplete
                master_ingredients = get_all_master_ingredients()
                master_options = {m.name: f"{m.name} ({m.default_unit})" for m in master_ingredients}
                master_units = {m.name: m.default_unit for m in master_ingredients}

                selected_master = ui.select(
                    options=master_options,
                    with_input=True,
                    label='Search Ingredient'
                ).classes('w-full')

                with ui.row().classes('w-full gap-2 items-center'):
                    amount_input = ui.number('Amount', value=100, min=0.1).classes('flex-1')
                    unit_input = ui.input('Unit', value='g').classes('w-24')

                def on_master_change(e):
                    if e.value and e.value in master_units:
                        unit_input.value = master_units[e.value]

                selected_master.on('update:model-value', on_master_change)

                # Local draft ingredients for current recipe
                draft_ingredients: List[IngredientCreate] = []
                draft_container = ui.column().classes('w-full my-2')

                def refresh_draft():
                    draft_container.clear()
                    with draft_container:
                        for idx, ing in enumerate(draft_ingredients):
                            with ui.row().classes('justify-between items-center w-full bg-slate-50 p-2 rounded border'):
                                ui.label(f"{ing.name} — {ing.amount:g} {ing.unit}").classes('text-xs font-semibold')
                                
                                def remove_ing(i=idx):
                                    draft_ingredients.pop(i)
                                    refresh_draft()

                                ui.button(icon='close', on_click=remove_ing).props('flat round color=red size=xs')

                def add_to_draft():
                    if not selected_master.value:
                        ui.notify('Select an ingredient from the list', type='warning')
                        return
                    draft_ingredients.append(IngredientCreate(
                        name=selected_master.value,
                        amount=float(amount_input.value or 1),
                        unit=unit_input.value or ''
                    ))
                    refresh_draft()
                    selected_master.value = None

                ui.button('Add Ingredient Item', on_click=add_to_draft).classes('w-full bg-slate-200 text-slate-800 text-xs font-semibold mb-2')

                def save_recipe():
                    if not name_input.value or not name_input.value.strip():
                        ui.notify('Recipe name is required', type='warning')
                        return
                    if not draft_ingredients:
                        ui.notify('Add at least one ingredient item', type='warning')
                        return

                    recipe_data = RecipeCreate(
                        name=name_input.value.strip(),
                        prep_time=int(prep_input.value or 0),
                        cook_time=int(cook_input.value or 0),
                        base_servings=int(servings_input.value or 4),
                        ingredients=draft_ingredients
                    )

                    create_recipe(recipe_data)

                    # Reset Form
                    name_input.value = ''
                    prep_input.value = 15
                    cook_input.value = 20
                    servings_input.value = 4
                    draft_ingredients.clear()
                    refresh_draft()

                    ui.notify('Recipe created successfully!', type='positive')
                    refresh_recipe_list()

                ui.button('Save Recipe', on_click=save_recipe).classes('mt-2 w-full bg-blue-600 text-white font-bold')

            # Right Column: Recipe List / Cards
            list_container = ui.column().classes('flex-1 max-w-2xl')

            def refresh_recipe_list():
                list_container.clear()
                recipes = get_all_recipes()
                with list_container:
                    ui.label(f'Stored Recipes ({len(recipes)})').classes('text-xl font-bold text-slate-800 mb-2')
                    if not recipes:
                        ui.label('No recipes stored yet. Create one on the left!').classes('text-gray-500 italic p-4')
                        return

                    for recipe in recipes:
                        with ui.card().classes('w-full mb-3 p-4 border border-gray-200 shadow-sm'):
                            with ui.row().classes('justify-between items-center w-full'):
                                ui.label(recipe.name).classes('text-lg font-bold text-slate-900')
                                
                                def handle_delete(rid=recipe.id):
                                    delete_recipe(rid)
                                    ui.notify('Recipe deleted', type='info')
                                    refresh_recipe_list()

                                ui.button(icon='delete', on_click=handle_delete).props('flat color=red').classes('text-xs')

                            ui.label(f'⏱️ Prep: {recipe.prep_time}m | Cook: {recipe.cook_time}m | 👥 Base: {recipe.base_servings} people').classes('text-xs text-gray-500 mb-2')
                            ui.separator()

                            with ui.row().classes('gap-1 wrap mt-2'):
                                for ing in recipe.ingredients:
                                    unit_str = f" {ing.unit}" if ing.unit else ""
                                    ui.chip(f"{ing.name}: {ing.amount:g}{unit_str}", icon='restaurant').classes('text-xs bg-slate-100')

            refresh_recipe_list()
