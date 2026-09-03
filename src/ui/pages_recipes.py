from typing import List, Optional
from nicegui import ui
from src.ui.layout import header_nav
from src.services import (
    get_filtered_recipes, create_recipe, update_recipe, delete_recipe, 
    get_all_master_ingredients, add_master_ingredient, import_recipe_from_marmiton
)
from src.models import RecipeCreate, IngredientCreate, Recipe

def render_recipes_page():
    """Mise en page pour le catalogue de recettes, l'importation Marmiton, les filtres et l'édition."""
    header_nav(active_page='recipes')

    # État des filtres
    filter_state = {
        "search": "",
        "uses_oven": None,
        "is_vegetarian": None,
        "season": "Toutes",
        "difficulty": "Toutes",
        "price": "Tous",
        "max_prep": None,
        "max_total": None
    }

    with ui.column().classes('w-full max-w-6xl mx-auto p-4'):
        ui.label('📖 Catalogue & Gestion des Recettes').classes('text-2xl font-bold text-slate-800 mb-2')

        # --- Carte d'Importation Marmiton ---
        with ui.card().classes('w-full p-4 mb-4 border border-amber-200 bg-amber-50/40 shadow-sm'):
            ui.label('🥘 Importer directement une recette depuis Marmiton').classes('text-sm font-bold text-amber-900 mb-1')
            ui.label('Collez le lien d\'une recette Marmiton pour l\'ajouter automatiquement avec ses ingrédients et ses quantités.').classes('text-xs text-amber-700 mb-3')
            
            with ui.row().classes('w-full gap-3 items-center'):
                marmiton_url_input = ui.input(
                    'Lien de recette Marmiton',
                    placeholder='ex: https://www.marmiton.org/recettes/recette_butter-chicken-ou-poulet-makkhani-inde_13490.aspx'
                ).classes('flex-1')

                def show_import_logs_modal(logs: List[str], success: bool):
                    with ui.dialog() as dialog, ui.card().classes('w-full max-w-lg p-5'):
                        ui.label('📋 Rapport d\'importation Marmiton').classes('text-xl font-bold text-slate-800 mb-3')
                        
                        with ui.column().classes('w-full gap-2 my-2 max-h-60 overflow-y-auto'):
                            for log in logs:
                                if log.startswith('✅'):
                                    ui.label(log).classes('text-sm font-bold text-emerald-700 bg-emerald-50 p-2 rounded border border-emerald-200')
                                elif log.startswith('📦'):
                                    ui.label(log).classes('text-sm font-semibold text-blue-700 bg-blue-50 p-2 rounded border border-blue-200')
                                elif log.startswith('⚠️'):
                                    ui.label(log).classes('text-xs text-amber-800 bg-amber-50 p-2 rounded border border-amber-200')
                                else:
                                    ui.label(log).classes('text-sm font-semibold text-red-700 bg-red-50 p-2 rounded border border-red-200')

                        with ui.row().classes('w-full justify-end mt-4'):
                            ui.button('Fermer', on_click=dialog.close).classes('bg-blue-600 text-white font-bold')
                    dialog.open()

                def handle_marmiton_import():
                    url = (marmiton_url_input.value or '').strip()
                    if not url:
                        ui.notify('Veuillez coller un lien de recette Marmiton', type='warning')
                        return

                    ui.notify('Importation de la recette Marmiton en cours...', type='info')
                    result = import_recipe_from_marmiton(url)
                    
                    if result["success"]:
                        ui.notify('Recette importée avec succès !', type='positive')
                        marmiton_url_input.value = ''
                        refresh_recipe_list()
                    else:
                        ui.notify(f"Erreur d'importation : {result['error']}", type='negative')

                    show_import_logs_modal(result["logs"], result["success"])

                ui.button('Importer la recette', icon='cloud_download', on_click=handle_marmiton_import).classes('bg-amber-600 text-white font-bold self-end')

        # --- Barre de Recherche & Filtres ---
        with ui.card().classes('w-full p-4 mb-4 border border-slate-200 bg-slate-50/50 shadow-sm'):
            ui.label('🔎 Rechercher & Filtrer les recettes').classes('text-sm font-bold text-slate-700 mb-2')
            
            with ui.row().classes('w-full gap-4 items-center wrap'):
                search_input = ui.input('Rechercher par nom', placeholder='ex: Carbonara...').classes('flex-1 min-w-[180px]')
                
                max_prep_input = ui.number('Prép max (min)', value=None, min=0, placeholder='Tous').classes('w-32')
                max_total_input = ui.number('Total max (min)', value=None, min=0, placeholder='Tous').classes('w-32')

                difficulty_select = ui.select(
                    options=['Toutes', 'Facile', 'Moyen', 'Difficile'], value='Toutes', label='Difficulté'
                ).classes('w-28')

                price_select = ui.select(
                    options=['Tous', 'Économique', 'Modéré', 'Élevé'], value='Tous', label='Budget'
                ).classes('w-28')

                season_select = ui.select(
                    options=['Toutes', 'Été', 'Hiver', 'Aucune'], value='Toutes', label='Saison'
                ).classes('w-28')

                oven_filter = ui.select(
                    options=['Tous', 'Four requis', 'Sans four'], value='Tous', label='Utilisation du four'
                ).classes('w-40')

                veg_switch = ui.checkbox('Végétarien uniquement')

            def apply_filters():
                filter_state["search"] = search_input.value or ""
                filter_state["difficulty"] = difficulty_select.value
                filter_state["price"] = price_select.value
                filter_state["season"] = season_select.value
                filter_state["max_prep"] = int(max_prep_input.value) if max_prep_input.value is not None else None
                filter_state["max_total"] = int(max_total_input.value) if max_total_input.value is not None else None
                
                if oven_filter.value == 'Four requis':
                    filter_state["uses_oven"] = True
                elif oven_filter.value == 'Sans four':
                    filter_state["uses_oven"] = False
                else:
                    filter_state["uses_oven"] = None

                filter_state["is_vegetarian"] = True if veg_switch.value else None
                refresh_recipe_list()

            search_input.on('update:model-value', lambda _: apply_filters())
            max_prep_input.on('update:model-value', lambda _: apply_filters())
            max_total_input.on('update:model-value', lambda _: apply_filters())
            difficulty_select.on('update:model-value', lambda _: apply_filters())
            price_select.on('update:model-value', lambda _: apply_filters())
            season_select.on('update:model-value', lambda _: apply_filters())
            oven_filter.on('update:model-value', lambda _: apply_filters())
            veg_switch.on('update:model-value', lambda _: apply_filters())

        # Disposition principale : Formulaire (Gauche) & Grille des Recettes (Droite)
        with ui.row().classes('w-full gap-6 items-start wrap'):
            
            # --- Formulaire de Création Manuel de Recette ---
            with ui.card().classes('w-full max-w-md p-4 shadow-md'):
                ui.label('➕ Ajouter une Recette manuellement').classes('text-xl font-bold text-slate-800 mb-2')

                name_input = ui.input('Nom de la recette', placeholder='ex: Lasagnes maison').classes('w-full')
                
                with ui.row().classes('w-full gap-2'):
                    prep_input = ui.number('Prép (min)', value=20, min=0).classes('flex-1')
                    cook_input = ui.number('Cuisson (min)', value=30, min=0).classes('flex-1')
                    servings_input = ui.number('Portions de base', value=5, min=1).classes('flex-1')

                with ui.row().classes('w-full gap-2 mt-2'):
                    diff_input = ui.select(options=['Facile', 'Moyen', 'Difficile'], value='Moyen', label='Difficulté').classes('flex-1')
                    price_input = ui.select(options=['Économique', 'Modéré', 'Élevé'], value='Modéré', label='Budget').classes('flex-1')
                    season_input = ui.select(options=['Aucune', 'Été', 'Hiver'], value='Aucune', label='Saison').classes('flex-1')

                with ui.row().classes('w-full gap-4 mt-2 items-center'):
                    uses_oven_cb = ui.checkbox('Four requis')
                    is_veg_cb = ui.checkbox('Végétarien')

                ui.separator().classes('my-3')
                ui.label('Ingrédients (Sélectionner ou saisir)').classes('text-sm font-bold text-slate-700')

                master_ingredients = get_all_master_ingredients()
                master_options = [m.name for m in master_ingredients]
                master_units = {m.name: m.default_unit for m in master_ingredients}

                ingredient_select = ui.select(
                    options=master_options,
                    with_input=True,
                    new_value_mode='add',
                    label='Sélectionner/Saisir un ingrédient'
                ).classes('w-full')

                with ui.row().classes('w-full gap-2 items-center'):
                    amount_input = ui.number('Quantité (5 pers.)', value=100, min=0.1).classes('flex-1')
                    unit_input = ui.input('Unité', value='g').classes('w-24')

                # Mise à jour automatique de l'unité ET de la quantité par défaut selon l'ingrédient sélectionné
                def on_ingredient_change(e):
                    if e.value and e.value in master_units:
                        unit = master_units[e.value]
                        unit_input.value = unit
                        # Grammes ou Millilitres -> 100 par défaut, sinon 1 (ex: gousses, cuillères, pièces)
                        if unit.lower() in ['g', 'ml']:
                            amount_input.value = 100
                        else:
                            amount_input.value = 1

                ingredient_select.on('update:model-value', on_ingredient_change)

                draft_ingredients: List[IngredientCreate] = []
                draft_container = ui.column().classes('w-full my-2')

                def refresh_draft():
                    draft_container.clear()
                    with draft_container:
                        for idx, ing in enumerate(draft_ingredients):
                            with ui.row().classes('justify-between items-center w-full bg-slate-50 p-2 rounded border'):
                                ui.label(f"{ing.name} — {ing.amount:g} {ing.unit}").classes('text-xs font-semibold')
                                ui.button(icon='close', on_click=lambda _, i=idx: (draft_ingredients.pop(i), refresh_draft())).props('flat round color=red size=xs')

                def add_to_draft():
                    ing_name = ingredient_select.value
                    if not ing_name or not str(ing_name).strip():
                        ui.notify('Veuillez sélectionner ou saisir un nom d\'ingrédient', type='warning')
                        return
                    
                    name_str = str(ing_name).strip()
                    unit_str = (unit_input.value or 'g').strip()

                    add_master_ingredient(name_str, unit_str)

                    draft_ingredients.append(IngredientCreate(
                        name=name_str,
                        amount=float(amount_input.value or 1),
                        unit=unit_str
                    ))
                    refresh_draft()
                    ingredient_select.value = None

                ui.button('Ajouter cet ingrédient', on_click=add_to_draft).classes('w-full bg-slate-200 text-slate-800 text-xs font-semibold mb-2')

                def save_new_recipe():
                    if not name_input.value or not name_input.value.strip():
                        ui.notify('Le nom de la recette est obligatoire', type='warning')
                        return
                    if not draft_ingredients:
                        ui.notify('Ajoutez au moins un ingrédient', type='warning')
                        return

                    create_recipe(RecipeCreate(
                        name=name_input.value.strip(),
                        prep_time=int(prep_input.value or 0),
                        cook_time=int(cook_input.value or 0),
                        base_servings=int(servings_input.value or 5),
                        difficulty=diff_input.value,
                        price=price_input.value,
                        uses_oven=bool(uses_oven_cb.value),
                        season=season_input.value,
                        is_vegetarian=bool(is_veg_cb.value),
                        ingredients=draft_ingredients
                    ))

                    name_input.value = ''
                    prep_input.value = 20
                    cook_input.value = 30
                    servings_input.value = 5
                    uses_oven_cb.value = False
                    is_veg_cb.value = False
                    draft_ingredients.clear()
                    refresh_draft()

                    ui.notify('Recette enregistrée avec succès !', type='positive')
                    refresh_recipe_list()

                ui.button('Enregistrer la recette', on_click=save_new_recipe).classes('mt-2 w-full bg-blue-600 text-white font-bold')

            # --- Liste des Cartes de Recettes ---
            list_container = ui.column().classes('flex-1 max-w-2xl')

            # Modale d'Édition de Recette
            def open_edit_recipe_dialog(recipe: Recipe):
                with ui.dialog() as dialog, ui.card().classes('w-full max-w-lg p-4'):
                    ui.label(f'Éditer la recette : {recipe.name}').classes('text-xl font-bold text-slate-800 mb-2')

                    e_name = ui.input('Nom de la recette', value=recipe.name).classes('w-full')
                    with ui.row().classes('w-full gap-2'):
                        e_prep = ui.number('Prép (min)', value=recipe.prep_time, min=0).classes('flex-1')
                        e_cook = ui.number('Cuisson (min)', value=recipe.cook_time, min=0).classes('flex-1')
                        e_servings = ui.number('Portions', value=recipe.base_servings, min=1).classes('flex-1')

                    with ui.row().classes('w-full gap-2 mt-2'):
                        e_diff = ui.select(options=['Facile', 'Moyen', 'Difficile'], value=recipe.difficulty, label='Difficulté').classes('flex-1')
                        e_price = ui.select(options=['Économique', 'Modéré', 'Élevé'], value=recipe.price, label='Budget').classes('flex-1')
                        e_season = ui.select(options=['Aucune', 'Été', 'Hiver'], value=recipe.season, label='Saison').classes('flex-1')

                    with ui.row().classes('w-full gap-4 mt-2 items-center'):
                        e_oven = ui.checkbox('Four requis', value=recipe.uses_oven)
                        e_veg = ui.checkbox('Végétarien', value=recipe.is_vegetarian)

                    ui.separator().classes('my-2')
                    ui.label('Ingrédients').classes('text-sm font-bold text-slate-700')

                    e_draft: List[IngredientCreate] = [
                        IngredientCreate(name=ing.name, amount=ing.amount, unit=ing.unit)
                        for ing in recipe.ingredients
                    ]
                    e_draft_container = ui.column().classes('w-full my-2')

                    def refresh_edit_draft():
                        e_draft_container.clear()
                        with e_draft_container:
                            for idx, ing in enumerate(e_draft):
                                with ui.row().classes('justify-between items-center w-full bg-slate-50 p-2 rounded border'):
                                    ui.label(f"{ing.name} — {ing.amount:g} {ing.unit}").classes('text-xs font-semibold')
                                    ui.button(icon='close', on_click=lambda _, i=idx: (e_draft.pop(i), refresh_edit_draft())).props('flat round color=red size=xs')

                    refresh_edit_draft()

                    e_ing_select = ui.select(options=master_options, with_input=True, new_value_mode='add', label='Ajouter un ingrédient').classes('w-full')
                    with ui.row().classes('w-full gap-2 items-center'):
                        e_amount = ui.number('Quantité', value=100, min=0.1).classes('flex-1')
                        e_unit = ui.input('Unité', value='g').classes('w-24')

                    # Mise à jour automatique de l'unité et de la quantité dans la modale d'édition
                    def on_edit_ingredient_change(e):
                        if e.value and e.value in master_units:
                            unit = master_units[e.value]
                            e_unit.value = unit
                            if unit.lower() in ['g', 'ml']:
                                e_amount.value = 100
                            else:
                                e_amount.value = 1

                    e_ing_select.on('update:model-value', on_edit_ingredient_change)

                    def add_edit_ing():
                        if not e_ing_select.value:
                            return
                        n_str = str(e_ing_select.value).strip()
                        u_str = (e_unit.value or 'g').strip()
                        add_master_ingredient(n_str, u_str)
                        e_draft.append(IngredientCreate(name=n_str, amount=float(e_amount.value or 1), unit=u_str))
                        refresh_edit_draft()
                        e_ing_select.value = None

                    ui.button('Ajouter l\'élément', on_click=add_edit_ing).classes('w-full bg-slate-100 text-xs font-semibold')

                    with ui.row().classes('w-full justify-end gap-2 mt-4'):
                        ui.button('Annuler', on_click=dialog.close).props('flat')
                        
                        def save_edit_changes():
                            if not e_name.value or not e_name.value.strip():
                                ui.notify('Nom obligatoire', type='warning')
                                return
                            update_recipe(recipe.id, RecipeCreate(
                                name=e_name.value.strip(),
                                prep_time=int(e_prep.value or 0),
                                cook_time=int(e_cook.value or 0),
                                base_servings=int(e_servings.value or 5),
                                difficulty=e_diff.value,
                                price=e_price.value,
                                uses_oven=bool(e_oven.value),
                                season=e_season.value,
                                is_vegetarian=bool(e_veg.value),
                                ingredients=e_draft
                            ))
                            dialog.close()
                            ui.notify('Recette mise à jour !', type='positive')
                            refresh_recipe_list()

                        ui.button('Enregistrer les modifications', on_click=save_edit_changes).classes('bg-blue-600 text-white font-bold')

                dialog.open()

            def refresh_recipe_list():
                list_container.clear()
                recipes = get_filtered_recipes(
                    search_query=filter_state["search"],
                    uses_oven=filter_state["uses_oven"],
                    is_vegetarian=filter_state["is_vegetarian"],
                    season=filter_state["season"],
                    difficulty=filter_state["difficulty"],
                    price=filter_state["price"],
                    max_prep_time=filter_state["max_prep"],
                    max_total_time=filter_state["max_total"]
                )

                with list_container:
                    ui.label(f'Recettes correspondantes ({len(recipes)})').classes('text-xl font-bold text-slate-800 mb-2')
                    if not recipes:
                        ui.label('Aucune recette ne correspond aux filtres actifs.').classes('text-gray-500 italic p-4')
                        return

                    for recipe in recipes:
                        total_time = recipe.prep_time + recipe.cook_time
                        with ui.card().classes('w-full mb-3 p-4 border border-gray-200 shadow-sm'):
                            with ui.row().classes('justify-between items-center w-full'):
                                ui.label(recipe.name).classes('text-lg font-bold text-slate-900')
                                
                                with ui.row().classes('gap-1'):
                                    ui.button(icon='edit', on_click=lambda _, r=recipe: open_edit_recipe_dialog(r)).props('flat round color=blue size=xs')
                                    ui.button(icon='delete', on_click=lambda _, rid=recipe.id: (delete_recipe(rid), ui.notify('Recette supprimée', type='info'), refresh_recipe_list())).props('flat round color=red size=xs')

                            # Badges de métadonnées
                            with ui.row().classes('gap-1 wrap my-1'):
                                ui.chip(f"Prép : {recipe.prep_time}m | Total : {total_time}m", icon='timer').classes('text-xs bg-slate-100 font-medium')
                                ui.chip(f" {recipe.base_servings} pers. base", icon='groups').classes('text-xs bg-indigo-100')
                                ui.chip(recipe.difficulty, icon='equalizer').classes('text-xs bg-white-800 text-blue-100')
                                ui.chip(recipe.price, icon='attach_money').classes('text-xs bg-pink-50 text-red-900')
                                if recipe.uses_oven:
                                    ui.chip('Four requis', icon='microwave').classes('text-xs bg-amber-50 text-amber-800')
                                else:
                                    ui.chip('Sans four', icon='flatware').classes('text-xs bg-slate-100 text-slate-600')
                                if recipe.is_vegetarian:
                                    ui.chip('Végétarien', icon='eco').classes('text-xs bg-emerald-50 text-emerald-800')
                                if recipe.season and recipe.season != 'Aucune':
                                    ui.chip(recipe.season, icon='wb_sunny').classes('text-xs bg-purple-50 text-purple-800')

                            ui.separator().classes('my-2')

                            with ui.row().classes('gap-1 wrap'):
                                for ing in recipe.ingredients:
                                    unit_str = f" {ing.unit}" if ing.unit else ""
                                    ui.chip(f"{ing.name}: {ing.amount:g}{unit_str}", icon='restaurant').classes('text-xs bg-slate-100')

            refresh_recipe_list()
