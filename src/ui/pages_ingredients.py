from nicegui import ui
from src.ui.layout import header_nav
from src.services import get_all_master_ingredients, add_master_ingredient, update_master_ingredient, delete_master_ingredient

# Liste complète des unités de mesure culinaires usuelles
UNIT_OPTIONS = [
    'g',            # Grammes
    'kg',           # Kilogrammes
    'ml',           # Millilitres
    'cl',           # Centilitres
    'l',            # Litres
    'gousses',      # Gousses (ex: d'ail)
    'c. à café',    # Cuillères à café
    'c. à soupe',   # Cuillères à soupe
    'pièces',       # Pièces / Unités
    'tranches',     # Tranches
    'pots',         # Pots
    'sachets',      # Sachets
    'pincée',       # Pincée (ex: de sel)
    'clous',        # Clous (ex: de girofle)
    'verres',       # Verres
    'tasses',       # Tasses
    'feuilles',     # Feuilles (ex: de basilic)
    'bottes',       # Bottes (ex: de persil)
    'brins',        # Brins (ex: de thym)
    'poignées'      # Poignées
]

def render_ingredients_page():
    """Mise en page pour la gestion du pool d'ingrédients principaux avec sélection des unités en liste déroulante."""
    header_nav(active_page='ingredients')

    with ui.column().classes('w-full max-w-4xl mx-auto p-4'):
        ui.label('📦 Gestion des Ingrédients Principaux').classes('text-2xl font-bold text-slate-800 mb-4')

        # Formulaire d'ajout d'ingrédient principal
        with ui.card().classes('w-full p-4 mb-6 shadow-sm border border-gray-200'):
            ui.label('Ajouter un nouvel ingrédient principal').classes('text-lg font-semibold text-slate-800 mb-2')
            with ui.row().classes('w-full gap-4 items-center'):
                name_input = ui.input('Nom de l\'ingrédient', placeholder='ex: Avocat').classes('flex-1')
                
                # Liste déroulante des unités avec possibilité de saisir une unité personnalisée
                unit_select = ui.select(
                    options=UNIT_OPTIONS,
                    value='g',
                    with_input=True,
                    new_value_mode='add',
                    label='Unité par défaut'
                ).classes('w-44')
                
                def handle_add():
                    if not name_input.value or not name_input.value.strip():
                        ui.notify('Le nom de l\'ingrédient est obligatoire', type='warning')
                        return
                    
                    unit_val = str(unit_select.value or 'g').strip()
                    add_master_ingredient(name_input.value, unit_val)
                    name_input.value = ''
                    unit_select.value = 'g'
                    ui.notify('Ingrédient principal ajouté !', type='positive')
                    refresh_list()

                ui.button('Ajouter l\'ingrédient', on_click=handle_add).classes('bg-blue-600 text-white font-medium self-end')

        list_container = ui.column().classes('w-full')

        def open_edit_dialog(ing):
            with ui.dialog() as dialog, ui.card().classes('w-full max-w-sm p-4'):
                ui.label(f'Éditer l\'ingrédient : {ing.name}').classes('text-lg font-bold text-slate-800 mb-2')
                edit_name = ui.input('Nom de l\'ingrédient', value=ing.name).classes('w-full')
                
                # Liste déroulante des unités dans la modale d'édition
                edit_unit_select = ui.select(
                    options=UNIT_OPTIONS,
                    value=ing.default_unit if ing.default_unit in UNIT_OPTIONS else ing.default_unit,
                    with_input=True,
                    new_value_mode='add',
                    label='Unité par défaut'
                ).classes('w-full')

                with ui.row().classes('w-full justify-end gap-2 mt-4'):
                    ui.button('Annuler', on_click=dialog.close).props('flat')
                    
                    def save_edit():
                        if not edit_name.value or not edit_name.value.strip():
                            ui.notify('Nom obligatoire', type='warning')
                            return
                        unit_val = str(edit_unit_select.value or 'g').strip()
                        update_master_ingredient(ing.id, edit_name.value, unit_val)
                        dialog.close()
                        ui.notify('Ingrédient mis à jour !', type='positive')
                        refresh_list()

                    ui.button('Enregistrer', on_click=save_edit).classes('bg-blue-600 text-white')
            dialog.open()

        def refresh_list():
            list_container.clear()
            ingredients = get_all_master_ingredients()
            with list_container:
                ui.label(f'Total d\'ingrédients disponibles ({len(ingredients)})').classes('text-lg font-bold text-slate-800 mb-2')
                
                with ui.grid(columns=3).classes('w-full gap-3'):
                    for ing in ingredients:
                        with ui.card().classes('p-3 border border-gray-100 shadow-xs flex justify-between items-center'):
                            with ui.column().classes('gap-0'):
                                ui.label(ing.name).classes('font-bold text-slate-800')
                                ui.label(f"Unité : {ing.default_unit}").classes('text-xs text-gray-500')
                            
                            with ui.row().classes('gap-1'):
                                ui.button(icon='edit', on_click=lambda _, item=ing: open_edit_dialog(item)).props('flat round color=blue size=xs')
                                
                                def confirm_delete(item=ing):
                                    delete_master_ingredient(item.id)
                                    ui.notify(f"Ingrédient {item.name} supprimé", type='info')
                                    refresh_list()

                                ui.button(icon='delete', on_click=confirm_delete).props('flat round color=red size=xs')

        refresh_list()
