from typing import Dict, Set
from nicegui import ui
from src.ui.layout import header_nav
from src.services import get_filtered_recipes, generate_scaled_grocery_list

def render_grocery_page():
    """Mise en page du Générateur de Liste de Courses avec ajustement individuel des personnes par plat."""
    header_nav(active_page='grocery')

    # Dictionnaire de stockage : recipe_id -> nb_personnes_cible (ex: {1: 4, 2: 2})
    recipe_servings: Dict[int, int] = {}
    bought_items: Set[str] = set()

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
        ui.label('🛒 Générateur de Liste de Courses Sur-Mesure').classes('text-2xl font-bold text-slate-800 mb-2')

        # --- Panneau de Filtres ---
        with ui.card().classes('w-full p-4 mb-4 border border-slate-200 bg-slate-50/50 shadow-sm'):
            ui.label('🔎 Filtrer les recettes disponibles').classes('text-sm font-bold text-slate-700 mb-2')
            
            with ui.row().classes('w-full gap-4 items-center wrap'):
                search_input = ui.input('Rechercher par nom', placeholder='ex: Pâtes...').classes('flex-1 min-w-[180px]')
                
                max_prep_input = ui.number('Prép max (min)', value=None, min=0, placeholder='Tous').classes('w-32')
                max_total_input = ui.number('Total max (min)', value=None, min=0, placeholder='Tous').classes('w-32')

                difficulty_select = ui.select(
                    options=['Toutes', 'Facile', 'Moyen', 'Difficile'], value='Toutes', label='Difficulté'
                ).classes('w-32')

                price_select = ui.select(
                    options=['Tous', 'Économique', 'Modéré', 'Élevé'], value='Tous', label='Budget'
                ).classes('w-36')

                season_select = ui.select(
                    options=['Toutes', 'Été', 'Hiver', 'Aucune'], value='Toutes', label='Saison'
                ).classes('w-32')

                oven_filter = ui.select(
                    options=['Tous', 'Four requis', 'Sans four'], value='Tous', label='Utilisation du four'
                ).classes('w-40')

                veg_switch = ui.checkbox('Végétarien')

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
                refresh_recipes()

            search_input.on('update:model-value', lambda _: apply_filters())
            max_prep_input.on('update:model-value', lambda _: apply_filters())
            max_total_input.on('update:model-value', lambda _: apply_filters())
            difficulty_select.on('update:model-value', lambda _: apply_filters())
            price_select.on('update:model-value', lambda _: apply_filters())
            season_select.on('update:model-value', lambda _: apply_filters())
            oven_filter.on('update:model-value', lambda _: apply_filters())
            veg_switch.on('update:model-value', lambda _: apply_filters())

        with ui.row().classes('w-full gap-6 items-start wrap'):
            
            # Colonne Gauche : Sélection des Plats & Ajustement des Personnes par Plat
            with ui.card().classes('w-full max-w-lg p-4 shadow-md'):
                ui.label('1. Sélectionner les plats & ajuster les personnes').classes('text-lg font-bold text-slate-800 mb-1')
                ui.label('Chaque plat peut avoir son propre nombre de convives indépendamment des autres !').classes('text-xs text-gray-500 mb-3')

                recipe_container = ui.column().classes('w-full gap-2')

                def refresh_recipes():
                    recipe_container.clear()
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
                    with recipe_container:
                        if not recipes:
                            ui.label('Aucune recette correspondante.').classes('text-gray-500 italic p-2')
                            return

                        for recipe in recipes:
                            is_checked = recipe.id in recipe_servings
                            
                            with ui.card().classes('w-full p-3 border border-slate-200 bg-white shadow-xs'):
                                with ui.row().classes('items-center justify-between w-full'):
                                    
                                    def toggle_recipe(e, rid=recipe.id, base_p=recipe.base_servings):
                                        if e.value:
                                            recipe_servings[rid] = base_p
                                        else:
                                            recipe_servings.pop(rid, None)
                                        refresh_recipes()
                                        refresh_grocery()

                                    cb = ui.checkbox(
                                        f"{recipe.name}",
                                        value=is_checked,
                                        on_change=toggle_recipe
                                    ).classes('text-sm font-bold text-slate-900 flex-1')

                                    if recipe.is_vegetarian:
                                        ui.chip('Végé', icon='eco').classes('text-[10px] bg-emerald-50 text-emerald-800 p-1')

                                # Si la recette est cochée, afficher le contrôle individuel du nombre de personnes
                                if is_checked:
                                    ui.separator().classes('my-2')
                                    with ui.row().classes('items-center justify-between w-full bg-slate-50 p-2 rounded border border-slate-100'):
                                        ui.label('👥 Nombre de personnes pour ce plat :').classes('text-xs font-semibold text-slate-700')
                                        
                                        current_p = recipe_servings.get(recipe.id, recipe.base_servings)
                                        
                                        def update_servings(val, rid=recipe.id):
                                            if val is not None and val > 0:
                                                recipe_servings[rid] = int(val)
                                                refresh_grocery()

                                        p_input = ui.number(
                                            value=current_p,
                                            min=1,
                                            step=1,
                                            on_change=lambda e, rid=recipe.id: update_servings(e.value, rid)
                                        ).classes('w-24 text-center font-bold').props('dense outline')

                refresh_recipes()

            # Colonne Droite : Liste de Courses Agrégée
            grocery_container = ui.column().classes('flex-1 max-w-xl')

            def refresh_grocery():
                grocery_container.clear()
                aggregated = generate_scaled_grocery_list(recipe_servings)

                with grocery_container:
                    ui.label('2. Liste de courses agrégée').classes('text-lg font-bold text-slate-800 mb-2')

                    if not recipe_servings:
                        ui.label('Cochez des plats à gauche et définissez le nombre de personnes pour chaque plat.').classes('text-gray-500 italic p-4 card')
                        return

                    # En-tête récapitulatif des plats sélectionnés et des convives
                    with ui.card().classes('w-full p-3 mb-3 border border-blue-200 bg-blue-50/60 shadow-xs'):
                        ui.label('📍 Récapitulatif des plats au menu :').classes('text-xs font-bold text-blue-900 uppercase tracking-wider mb-1')
                        
                        all_recipes_dict = {r.id: r.name for r in get_filtered_recipes()}
                        summary_items = []
                        for rid, p_count in recipe_servings.items():
                            r_name = all_recipes_dict.get(rid, f"Recette #{rid}")
                            summary_items.append(f"• {r_name} ({p_count} pers.)")
                        
                        for item_text in summary_items:
                            ui.label(item_text).classes('text-xs font-medium text-blue-800')

                    if not aggregated:
                        ui.label('Aucun ingrédient trouvé pour les recettes sélectionnées.').classes('text-gray-500 italic p-4')
                        return

                    with ui.card().classes('w-full p-4 border border-blue-200 bg-white shadow-md'):
                        ui.label('Ingrédients à acheter / dans le panier :').classes('text-xs font-bold text-slate-500 uppercase tracking-wider mb-2')
                        
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
