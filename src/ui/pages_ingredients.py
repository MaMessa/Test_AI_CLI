from nicegui import ui
from src.ui.layout import header_nav
from src.services import get_all_master_ingredients, add_master_ingredient

def render_ingredients_page():
    """Page layout for managing Master Ingredients pool."""
    header_nav(active_page='ingredients')

    with ui.column().classes('w-full max-w-4xl mx-auto p-4'):
        ui.label('📦 Master Ingredients Management').classes('text-2xl font-bold text-slate-800 mb-4')

        # Form to add new master ingredient
        with ui.card().classes('w-full p-4 mb-6 shadow-sm border border-gray-200'):
            ui.label('Add New Master Ingredient').classes('text-lg font-semibold text-slate-800 mb-2')
            with ui.row().classes('w-full gap-4 items-center'):
                name_input = ui.input('Ingredient Name', placeholder='e.g., Avocado').classes('flex-1')
                unit_input = ui.input('Default Unit', value='g', placeholder='e.g., g, ml, pcs, cloves').classes('w-32')
                
                def handle_add():
                    if not name_input.value or not name_input.value.strip():
                        ui.notify('Ingredient name is required', type='warning')
                        return
                    
                    add_master_ingredient(name_input.value, unit_input.value)
                    name_input.value = ''
                    unit_input.value = 'g'
                    ui.notify('Master ingredient added!', type='positive')
                    refresh_list()

                ui.button('Add Ingredient', on_click=handle_add).classes('bg-blue-600 text-white font-medium self-end')

        # List of existing master ingredients
        list_container = ui.column().classes('w-full')

        def refresh_list():
            list_container.clear()
            ingredients = get_all_master_ingredients()
            with list_container:
                ui.label(f'Total Ingredients in Pool ({len(ingredients)})').classes('text-lg font-bold text-slate-800 mb-2')
                
                with ui.grid(columns=3).classes('w-full gap-3'):
                    for ing in ingredients:
                        with ui.card().classes('p-3 border border-gray-100 shadow-xs flex justify-between items-center'):
                            ui.label(ing.name).classes('font-bold text-slate-800')
                            ui.chip(ing.default_unit, icon='straighten').classes('text-xs bg-slate-100')

        refresh_list()
