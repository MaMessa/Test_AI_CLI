from sqlalchemy.orm import Session
from src.database import get_db_session
from src.models import MasterIngredient, Recipe, Ingredient

# 50+ Ingrédients principaux en français
DEFAULT_MASTER_INGREDIENTS = [
    # Fruits & Légumes
    ("Tomates", "g"), ("Ail", "gousses"), ("Oignon", "pièces"), ("Oignon rouge", "pièces"), ("Échalotes", "pièces"),
    ("Pommes de terre", "g"), ("Patates douces", "g"), ("Carottes", "g"), ("Céleri", "g"), ("Épinards", "g"),
    ("Chou kale", "g"), ("Laitue", "g"), ("Concombre", "pièces"), ("Poivron", "pièces"), ("Courgette", "g"),
    ("Aubergine", "g"), ("Champignons", "g"), ("Brocoli", "g"), ("Chou-fleur", "g"), ("Avocat", "pièces"),
    ("Citron", "pièces"), ("Citron vert", "pièces"), ("Basilic frais", "g"), ("Persil", "g"), ("Coriandre", "g"),
    ("Thym", "g"), ("Romarin", "g"),
    
    # Produits laitiers & Œufs
    ("Œufs", "pièces"), ("Beurre", "g"), ("Lait", "ml"), ("Crème fraîche", "ml"), ("Crème liquide", "ml"),
    ("Mozzarella", "g"), ("Parmesan", "g"), ("Cheddar", "g"), ("Feta", "g"), ("Ricotta", "g"), ("Yaourt grec", "g"),

    # Viandes & Poissons
    ("Blanc de poulet", "g"), ("Cuisses de poulet", "g"), ("Bœuf haché", "g"), ("Bœuf pour bourguignon", "g"),
    ("Lardons", "g"), ("Côtes de porc", "g"), ("Saucisses", "g"), ("Pavé de saumon", "g"), ("Thon", "g"), ("Crevettes", "g"),

    # Féculents & Épicerie
    ("Pâtes", "g"), ("Spaghetti", "g"), ("Penne", "g"), ("Riz", "g"), ("Riz à risotto", "g"),
    ("Quinoa", "g"), ("Farine", "g"), ("Pain", "tranches"), ("Pâte à pizza", "g"), ("Feuilles de lasagne", "g"),
    ("Couscous", "g"), ("Flocons d'avoine", "g"),

    # Huiles, Sauces & Condiments
    ("Huile d'olive", "ml"), ("Huile végétale", "ml"), ("Huile de sésame", "ml"), ("Sauce soja", "ml"),
    ("Concentré de tomate", "g"), ("Sauce tomate", "g"), ("Moutarde", "g"), ("Mayonnaise", "g"),
    ("Miel", "g"), ("Vinaigre balsamique", "ml"), ("Vinaigre blanc", "ml"),

    # Épices & Bouillons
    ("Sel", "g"), ("Poivre noir", "g"), ("Origan", "g"), ("Paprika", "g"), ("Cumin", "g"),
    ("Piment en poudre", "g"), ("Ail en poudre", "g"), ("Cannelle", "g"), ("Bouillon de bœuf", "ml"),
    ("Bouillon de volaille", "ml"), ("Bouillon de légumes", "ml"), ("Graines de sésame", "g")
]

# 7 Recettes complètes populaires (Portions pour 5 personnes)
SAMPLE_RECIPES = [
    {
        "name": "Spaghetti à la Carbonara",
        "prep_time": 15, "cook_time": 20, "base_servings": 5,
        "difficulty": "Facile", "price": "Économique", "uses_oven": False, "season": "Aucune", "is_vegetarian": False,
        "ingredients": [("Spaghetti", 500, "g"), ("Lardons", 200, "g"), ("Œufs", 5, "pièces"), ("Parmesan", 125, "g"), ("Poivre noir", 6, "g")]
    },
    {
        "name": "Lasagnes végétariennes aux épinards",
        "prep_time": 30, "cook_time": 45, "base_servings": 5,
        "difficulty": "Moyen", "price": "Modéré", "uses_oven": True, "season": "Aucune", "is_vegetarian": True,
        "ingredients": [("Feuilles de lasagne", 350, "g"), ("Tomates", 600, "g"), ("Épinards", 250, "g"), ("Mozzarella", 250, "g"), ("Ricotta", 200, "g"), ("Oignon", 2, "pièces"), ("Ail", 4, "gousses"), ("Huile d'olive", 30, "ml")]
    },
    {
        "name": "Salade grecque estivale",
        "prep_time": 15, "cook_time": 0, "base_servings": 5,
        "difficulty": "Facile", "price": "Économique", "uses_oven": False, "season": "Été", "is_vegetarian": True,
        "ingredients": [("Tomates", 500, "g"), ("Concombre", 2, "pièces"), ("Feta", 200, "g"), ("Oignon rouge", 1, "pièces"), ("Huile d'olive", 40, "ml"), ("Origan", 5, "g")]
    },
    {
        "name": "Bœuf Bourguignon réconfortant",
        "prep_time": 25, "cook_time": 90, "base_servings": 5,
        "difficulty": "Moyen", "price": "Élevé", "uses_oven": False, "season": "Hiver", "is_vegetarian": False,
        "ingredients": [("Bœuf pour bourguignon", 800, "g"), ("Pommes de terre", 600, "g"), ("Carottes", 300, "g"), ("Oignon", 2, "pièces"), ("Bouillon de bœuf", 800, "ml"), ("Ail", 3, "gousses")]
    },
    {
        "name": "Pizza Margherita maison",
        "prep_time": 20, "cook_time": 15, "base_servings": 5,
        "difficulty": "Facile", "price": "Économique", "uses_oven": True, "season": "Aucune", "is_vegetarian": True,
        "ingredients": [("Pâte à pizza", 600, "g"), ("Concentré de tomate", 200, "g"), ("Mozzarella", 300, "g"), ("Basilic frais", 20, "g"), ("Huile d'olive", 25, "ml"), ("Origan", 4, "g")]
    },
    {
        "name": "Bowl de saumon teriyaki et quinoa",
        "prep_time": 15, "cook_time": 20, "base_servings": 5,
        "difficulty": "Difficile", "price": "Élevé", "uses_oven": False, "season": "Été", "is_vegetarian": False,
        "ingredients": [("Pavé de saumon", 750, "g"), ("Quinoa", 400, "g"), ("Sauce soja", 60, "ml"), ("Miel", 30, "g"), ("Avocat", 3, "pièces"), ("Graines de sésame", 15, "g")]
    },
    {
        "name": "Poulet crémeux au beurre d'ail",
        "prep_time": 15, "cook_time": 25, "base_servings": 5,
        "difficulty": "Moyen", "price": "Modéré", "uses_oven": False, "season": "Aucune", "is_vegetarian": False,
        "ingredients": [("Blanc de poulet", 800, "g"), ("Beurre", 60, "g"), ("Ail", 6, "gousses"), ("Crème fraîche", 250, "ml"), ("Bouillon de volaille", 150, "ml"), ("Parmesan", 80, "g"), ("Épinards", 150, "g")]
    }
]

def seed_database_if_empty():
    """Remplit la base de données avec des ingrédients principaux et des recettes exemple si manquants."""
    db: Session = get_db_session()
    try:
        # 1. S'assurer que les 50+ ingrédients principaux sont présents
        for name, unit in DEFAULT_MASTER_INGREDIENTS:
            existing = db.query(MasterIngredient).filter(MasterIngredient.name.ilike(name.strip())).first()
            if not existing:
                db.add(MasterIngredient(name=name.strip(), default_unit=unit.strip()))
        db.commit()

        # 2. S'assurer que les recettes exemple sont présentes
        for r_data in SAMPLE_RECIPES:
            existing_recipe = db.query(Recipe).filter(Recipe.name.ilike(r_data["name"].strip())).first()
            if not existing_recipe:
                recipe = Recipe(
                    name=r_data["name"],
                    prep_time=r_data["prep_time"],
                    cook_time=r_data["cook_time"],
                    base_servings=r_data["base_servings"],
                    difficulty=r_data["difficulty"],
                    price=r_data["price"],
                    uses_oven=r_data["uses_oven"],
                    season=r_data["season"],
                    is_vegetarian=r_data["is_vegetarian"]
                )
                db.add(recipe)
                db.flush()

                for name, amount, unit in r_data["ingredients"]:
                    existing_master = db.query(MasterIngredient).filter(MasterIngredient.name.ilike(name.strip())).first()
                    if not existing_master:
                        db.add(MasterIngredient(name=name.strip(), default_unit=unit.strip() or "g"))
                        db.flush()

                    db.add(Ingredient(recipe_id=recipe.id, name=name.strip(), amount=amount, unit=unit.strip()))
        db.commit()
    finally:
        db.close()
