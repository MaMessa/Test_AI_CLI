from typing import List, Dict, Tuple
from sqlalchemy.orm import Session
from src.database import get_db_session, init_db
from src.seed import seed_database_if_empty
from src.models import (
    Recipe, Ingredient, MasterIngredient, 
    RecipeCreate, IngredientCreate, AggregatedIngredient
)

def initialize_database():
    """Ensure database schema exists and populate initial seed data if empty."""
    init_db()
    seed_database_if_empty()

# --- Master Ingredients Services ---

def get_all_master_ingredients() -> List[MasterIngredient]:
    """Fetch all master ingredients sorted alphabetically."""
    db: Session = get_db_session()
    try:
        return db.query(MasterIngredient).order_by(MasterIngredient.name).all()
    finally:
        db.close()


def add_master_ingredient(name: str, default_unit: str = "g") -> MasterIngredient:
    """Add a new ingredient to the master pool."""
    db: Session = get_db_session()
    try:
        name_clean = name.strip()
        existing = db.query(MasterIngredient).filter(MasterIngredient.name.ilike(name_clean)).first()
        if existing:
            return existing
        master = MasterIngredient(name=name_clean, default_unit=default_unit.strip() or "g")
        db.add(master)
        db.commit()
        db.refresh(master)
        return master
    finally:
        db.close()


# --- Recipe Services ---

def create_recipe(recipe_data: RecipeCreate) -> Recipe:
    """Create and persist a new recipe with base servings (default 4)."""
    db: Session = get_db_session()
    try:
        recipe = Recipe(
            name=recipe_data.name,
            prep_time=recipe_data.prep_time,
            cook_time=recipe_data.cook_time,
            base_servings=recipe_data.base_servings or 4
        )
        db.add(recipe)
        db.flush()

        for ing in recipe_data.ingredients:
            db.add(Ingredient(
                recipe_id=recipe.id,
                name=ing.name,
                amount=ing.amount,
                unit=ing.unit
            ))

        db.commit()
        db.refresh(recipe)
        return recipe
    finally:
        db.close()


def get_all_recipes() -> List[Recipe]:
    """Retrieve all recipes with associated ingredients."""
    db: Session = get_db_session()
    try:
        return db.query(Recipe).all()
    finally:
        db.close()


def delete_recipe(recipe_id: int) -> bool:
    """Delete a recipe by ID."""
    db: Session = get_db_session()
    try:
        recipe = db.query(Recipe).filter(Recipe.id == recipe_id).first()
        if recipe:
            db.delete(recipe)
            db.commit()
            return True
        return False
    finally:
        db.close()


# --- Grocery List Aggregation with Portion Scaling ---

def generate_scaled_grocery_list(
    recipe_ids: List[int], 
    target_people: int = 5
) -> List[AggregatedIngredient]:
    """
    Generate aggregated grocery list scaled for target_people.
    Formula: (ingredient_amount / recipe_base_servings) * target_people
    """
    if not recipe_ids:
        return []

    db: Session = get_db_session()
    try:
        recipes = db.query(Recipe).filter(Recipe.id.in_(recipe_ids)).all()
        aggregated_map: Dict[Tuple[str, str], float] = {}
        display_names: Dict[Tuple[str, str], Tuple[str, str]] = {}

        for recipe in recipes:
            base_servings = recipe.base_servings if recipe.base_servings > 0 else 4
            scale_factor = target_people / base_servings

            for ing in recipe.ingredients:
                key = (ing.name.strip().lower(), ing.unit.strip().lower())
                scaled_amount = ing.amount * scale_factor
                aggregated_map[key] = aggregated_map.get(key, 0.0) + scaled_amount
                
                if key not in display_names:
                    display_names[key] = (ing.name.strip(), ing.unit.strip())

        result: List[AggregatedIngredient] = []
        for key, total_amount in aggregated_map.items():
            name, unit = display_names[key]
            result.append(AggregatedIngredient(
                name=name,
                total_amount=round(total_amount, 2),
                unit=unit
            ))
        return result
    finally:
        db.close()
