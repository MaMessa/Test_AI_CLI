from typing import Set, List
from nicegui import ui
from src.services import get_all_recipes, create_recipe, delete_recipe, generate_grocery_list, parse_ingredients_input
from src.models import RecipeCreate

def recipe_form_component(on_saved_callback):
    """Form component for creating new recipes with ingredients per person."""
    with ui.card().classes('w-full max-w-md p-4 shadow-md'):
        ui.label('➕ Add Recipe').classes('text-xl font-bold text-slate-800 mb-2')

        name_input = ui.input('Recipe Name', placeholder='e.g., Spaghetti Bolognese').classes('w-full')
        prep_input = ui.number('Prep Time (mins)', value=15, min=0).classes('w-full')
        cook_input = ui.number('Cook Time (mins)', value=20, min=0).classes('w-full')
        
        ui.label('Ingredients per person (Format: Name, Amount, Unit)').classes('text-xs text-gray-500 font-semibold mt-2')
        ingredients_input = ui.textarea(
            placeholder="Pasta, 100, g\nMinced Meat, 125, g\nTomato Sauce, 150, ml\nOnion, 0.5, pcs"
        ).classes('w-full font-mono text-sm')

        def submit():
            if not name_input.value or not name_input.value.strip():
                ui.notify('Recipe name is required', type='warning')
                return
            
            parsed_ingredients = parse_ingredients_input(ingredients_input.value or "")
            if not parsed_ingredients:
                ui.notify('Please add at least one ingredient', type='warning')
                return

            recipe_data = RecipeCreate(
                name=name_input.value.strip(),
                prep_time=int(prep_input.value or 0),
                cook_time=int(cook_input.value or 0),
                ingredients=parsed_ingredients
            )
            
            create_recipe(recipe_data)
            
            # Reset form inputs
            name_input.value = ''
            prep_input.value = 15
            cook_input.value = 20
            ingredients_input.value = ''
            
            ui.notify('Recipe saved to database!', type='positive')
            if on_saved_callback:
                on_saved_callback()

        ui.button('Save Recipe', on_click=submit).classes('mt-4 w-full bg-blue-600 text-white font-semibold')


def recipe_list_component(selected_ids: Set[int], on_selection_change):
    """Display recipe cards with checkboxes for grocery list selection."""
    container = ui.column().classes('w-full max-w-md m-2')

    def refresh():
        container.clear()
        recipes = get_all_recipes()
        with container:
            ui.label('📖 Recipes').classes('text-xl font-bold text-slate-800 mb-2')
            if not recipes:
                ui.label('No recipes stored yet. Add one!').classes('text-gray-500 italic p-2')
                return

            for recipe in recipes:
                with ui.card().classes('w-full mb-3 p-4 border border-gray-200 shadow-sm'):
                    with ui.row().classes('justify-between items-center w-full'):
                        is_selected = recipe.id in selected_ids
                        
                        def toggle_select(e, rid=recipe.id):
                            if e.value:
                                selected_ids.add(rid)
                            else:
                                selected_ids.discard(rid)
                            on_selection_change()

                        ui.checkbox(recipe.name, value=is_selected, on_change=toggle_select).classes('text-lg font-bold text-slate-900')
                        
                        def handle_delete(rid=recipe.id):
                            delete_recipe(rid)
                            selected_ids.discard(rid)
                            ui.notify('Recipe deleted', type='info')
                            refresh()
                            on_selection_change()

                        ui.button(icon='delete', on_click=handle_delete).props('flat color=red').classes('text-xs')

                    ui.label(f'⏱️ Prep: {recipe.prep_time}m | Cook: {recipe.cook_time}m').classes('text-xs text-gray-500')
                    ui.separator().classes('my-2')

                    with ui.row().classes('gap-1 wrap'):
                        for ing in recipe.ingredients:
                            unit_str = f" {ing.unit}" if ing.unit else ""
                            ui.chip(f"{ing.name}: {ing.amount_per_person:g}{unit_str}/p", icon='restaurant').classes('text-xs bg-slate-100 text-slate-700')

    refresh()
    return refresh


def grocery_list_component(selected_ids: Set[int]):
    """Display aggregated grocery list for 5 people with interactive checkboxes."""
    container = ui.column().classes('w-full max-w-md m-2')
    bought_items: Set[str] = set()

    def refresh():
        container.clear()
        aggregated = generate_grocery_list(list(selected_ids), people_count=5)
        
        with container:
            ui.label('🛒 Grocery List (5 People)').classes('text-xl font-bold text-slate-800 mb-2')
            
            if not selected_ids:
                ui.label('Select recipes above to generate your grocery list.').classes('text-gray-500 italic p-2')
                return

            if not aggregated:
                ui.label('No ingredients found for selected recipes.').classes('text-gray-500 italic p-2')
                return

            with ui.card().classes('w-full p-4 border border-blue-200 bg-blue-50/40 shadow-md'):
                for item in aggregated:
                    unit_str = f" {item.unit}" if item.unit else ""
                    item_key = f"{item.name}_{item.unit}"
                    label_text = f"{item.name} — {item.total_amount:g}{unit_str}"
                    
                    is_bought = item_key in bought_items
                    
                    def on_check_toggle(e, ik=item_key):
                        if e.value:
                            bought_items.add(ik)
                        else:
                            bought_items.discard(ik)
                        refresh()

                    cb = ui.checkbox(label_text, value=is_bought, on_change=on_check_toggle)
                    if is_bought:
                        cb.classes('line-through text-gray-400')

    refresh()
    return refresh
