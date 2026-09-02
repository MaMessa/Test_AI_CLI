from nicegui import ui

def header_nav(active_page: str = ""):
    """Shared header navigation component across all pages."""
    with ui.header().classes('bg-blue-700 text-white p-4 flex justify-between items-center shadow-md w-full'):
        with ui.row().classes('items-center gap-2'):
            ui.label('🥗 RecipeApp').classes('text-xl font-bold tracking-wide')
            ui.label('v0.4').classes('text-xs bg-blue-800 px-2 py-0.5 rounded text-blue-100')

        with ui.row().classes('gap-4'):
            recipes_btn = ui.link('📖 Recipes', '/recipes').classes('text-white font-medium hover:underline')
            grocery_btn = ui.link('🛒 Grocery List', '/grocery').classes('text-white font-medium hover:underline')
            ingredients_btn = ui.link('📦 Master Ingredients', '/ingredients').classes('text-white font-medium hover:underline')

            if active_page == 'recipes':
                recipes_btn.classes('font-bold underline')
            elif active_page == 'grocery':
                grocery_btn.classes('font-bold underline')
            elif active_page == 'ingredients':
                ingredients_btn.classes('font-bold underline')
