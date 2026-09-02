from typing import Set
from nicegui import ui
from src.ui.layout import header_nav
from src.services import get_all_recipes, generate_scaled_grocery_list

def render_grocery_page():
    """Page layout for Grocery List Generation with portion scaling."""
    header_nav(active_page='grocery')

    selected_recipe_ids: Set[int] = set()
    bought_items: Set[str] = set()

    with ui.column().classes('w-full max-w-5xl mx-auto p-4'):
        ui.label('🛒 Grocery List Generator').classes('text-2xl font-bold text-slate-800 mb-4')

        with ui.row().classes('w-full gap-6 items-start wrap'):
            # Left Column: Recipe Selection & Portion Scaling Control
            with ui.card().classes('w-full max-w-md p-4 shadow-md'):
                ui.label('1. Select Recipes').classes('text-lg font-bold text-slate-800 mb-2')

                target_people_input = ui.number('Target People Count', value=5, min=1).classes('w-full mb-3')

                recipe_container = ui.column().classes('w-full')

                def refresh_recipes():
                    recipe_container.clear()
                    recipes = get_all_recipes()
                    with recipe_container:
                        if not recipes:
                            ui.label('No recipes found in database. Add recipes first!').classes('text-gray-500 italic p-2')
                            return

                        for recipe in recipes:
                            is_checked = recipe.id in selected_recipe_ids

                            def toggle_recipe(e, rid=recipe.id):
                                if e.value:
                                    selected_recipe_ids.add(rid)
                                else:
                                    selected_recipe_ids.discard(rid)
                                refresh_grocery()

                            ui.checkbox(
                                f"{recipe.name} (Base: {recipe.base_servings}p)",
                                value=is_checked,
                                on_change=toggle_recipe
                            ).classes('text-sm font-semibold')

                refresh_recipes()

                target_people_input.on('update:model-value', lambda _: refresh_grocery())

            # Right Column: Generated & Scaled Grocery List
            grocery_container = ui.column().classes('flex-1 max-w-xl')

            def refresh_grocery():
                grocery_container.clear()
                target_people = int(target_people_input.value or 5)
                aggregated = generate_scaled_grocery_list(list(selected_recipe_ids), target_people=target_people)

                with grocery_container:
                    ui.label(f'2. Aggregated Grocery List ({target_people} People)').classes('text-lg font-bold text-slate-800 mb-2')

                    if not selected_recipe_ids:
                        ui.label('Select recipes on the left to calculate required grocery ingredients.').classes('text-gray-500 italic p-4')
                        return

                    if not aggregated:
                        ui.label('No ingredients found for selected recipes.').classes('text-gray-500 italic p-4')
                        return

                    with ui.card().classes('w-full p-4 border border-blue-200 bg-blue-50/40 shadow-md'):
                        ui.label('Ingredients in Cart / To Buy:').classes('text-xs font-bold text-blue-800 uppercase tracking-wider mb-2')
                        
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
                                refresh_grocery()

                            cb = ui.checkbox(label_text, value=is_bought, on_change=on_check_toggle)
                            if is_bought:
                                cb.classes('line-through text-gray-400')

            refresh_grocery()
