from sqlalchemy.orm import Session
from src.database import get_db_session
from src.models import MasterIngredient, Recipe, Ingredient

# 15+ Common Master Ingredients
DEFAULT_MASTER_INGREDIENTS = [
    ("Pasta", "g"),
    ("Eggs", "pcs"),
    ("Flour", "g"),
    ("Tomatoes", "g"),
    ("Garlic", "cloves"),
    ("Butter", "g"),
    ("Milk", "ml"),
    ("Sugar", "g"),
    ("Salt", "g"),
    ("Olive Oil", "ml"),
    ("Chicken Breast", "g"),
    ("Cheese", "g"),
    ("Onion", "pcs"),
    ("Black Pepper", "g"),
    ("Rice", "g"),
    ("Bacon", "g"),
]

# 3 Sample Recipes (quantities for base of 4 people)
SAMPLE_RECIPES = [
    {
        "name": "Spaghetti Carbonara",
        "prep_time": 15,
        "cook_time": 20,
        "base_servings": 4,
        "ingredients": [
            ("Pasta", 400, "g"),
            ("Bacon", 150, "g"),
            ("Eggs", 4, "pcs"),
            ("Cheese", 100, "g"),
            ("Black Pepper", 5, "g"),
        ]
    },
    {
        "name": "Garlic Butter Chicken with Rice",
        "prep_time": 20,
        "cook_time": 25,
        "base_servings": 4,
        "ingredients": [
            ("Chicken Breast", 600, "g"),
            ("Butter", 50, "g"),
            ("Garlic", 4, "cloves"),
            ("Rice", 300, "g"),
            ("Olive Oil", 30, "ml"),
            ("Salt", 5, "g"),
        ]
    },
    {
        "name": "Classic Tomato Pasta",
        "prep_time": 10,
        "cook_time": 15,
        "base_servings": 4,
        "ingredients": [
            ("Pasta", 400, "g"),
            ("Tomatoes", 500, "g"),
            ("Garlic", 2, "cloves"),
            ("Onion", 1, "pcs"),
            ("Olive Oil", 20, "ml"),
            ("Salt", 4, "g"),
        ]
    }
]


def seed_database_if_empty():
    """Populate DB with initial master ingredients and sample recipes if empty."""
    db: Session = get_db_session()
    try:
        # Seed Master Ingredients if table is empty
        if db.query(MasterIngredient).count() == 0:
            for name, unit in DEFAULT_MASTER_INGREDIENTS:
                db.add(MasterIngredient(name=name, default_unit=unit))
            db.commit()

        # Seed Sample Recipes if table is empty
        if db.query(Recipe).count() == 0:
            for r_data in SAMPLE_RECIPES:
                recipe = Recipe(
                    name=r_data["name"],
                    prep_time=r_data["prep_time"],
                    cook_time=r_data["cook_time"],
                    base_servings=r_data["base_servings"]
                )
                db.add(recipe)
                db.flush()
                for name, amount, unit in r_data["ingredients"]:
                    db.add(Ingredient(
                        recipe_id=recipe.id,
                        name=name,
                        amount=amount,
                        unit=unit
                    ))
            db.commit()
    finally:
        db.close()
