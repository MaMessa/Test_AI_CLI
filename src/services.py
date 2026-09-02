from typing import List, Dict, Tuple
from sqlalchemy.orm import Session
from src.database import get_db_session, init_db
from src.models import Recipe, Ingredient, RecipeCreate, IngredientCreate, AggregatedIngredient

def initialize_database():
    """Ensure database schema is created on application startup."""
    init_db()

def parse_ingredients_input(raw_text: str) -> List[IngredientCreate]:
    """
    Parse line-by-line ingredients string.
    Expected line format: 'Name, AmountPerPerson, Unit'
    Examples:
      - 'Pasta, 100, g'
      - 'Eggs, 2, pcs'
      - 'Salt' (defaults to 1.0, '')
    """
    parsed: List[IngredientCreate] = []
    for line in raw_text.splitlines():
        line = line.strip()
        if not line:
            continue
        parts = [p.strip() for p in line.split(',')]
        name = parts[0]
        amount = 1.0
        unit = ""
        
        if len(parts) >= 2:
            try:
                amount = float(parts[1])
            except ValueError:
                amount = 1.0
        if len(parts) >= 3:
            unit = parts[2]
            
        parsed.append(IngredientCreate(name=name, amount_per_person=amount, unit=unit))
    return parsed


def create_recipe(recipe_data: RecipeCreate) -> Recipe:
    """Create and persist a new recipe with its ingredients."""
    db: Session = get_db_session()
    try:
        recipe = Recipe(
            name=recipe_data.name,
            prep_time=recipe_data.prep_time,
            cook_time=recipe_data.cook_time
        )
        db.add(recipe)
        db.flush()  # Obtain generated recipe ID

        for ing in recipe_data.ingredients:
            ingredient = Ingredient(
                recipe_id=recipe.id,
                name=ing.name,
                amount_per_person=ing.amount_per_person,
                unit=ing.unit
            )
            db.add(ingredient)

        db.commit()
        db.refresh(recipe)
        return recipe
    finally:
        db.close()


def get_all_recipes() -> List[Recipe]:
    """Retrieve all stored recipes with ingredients."""
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


def generate_grocery_list(recipe_ids: List[int], people_count: int = 5) -> List[AggregatedIngredient]:
    """
    Aggregate ingredients across selected recipes for N people.
    Combines amounts for ingredients matching (name, unit) case-insensitively.
    """
    if not recipe_ids:
        return []

    db: Session = get_db_session()
    try:
        recipes = db.query(Recipe).filter(Recipe.id.in_(recipe_ids)).all()
        aggregated_map: Dict[Tuple[str, str], float] = {}
        display_names: Dict[Tuple[str, str], Tuple[str, str]] = {}

        for recipe in recipes:
            for ing in recipe.ingredients:
                key = (ing.name.strip().lower(), ing.unit.strip().lower())
                total_for_recipe = ing.amount_per_person * people_count
                aggregated_map[key] = aggregated_map.get(key, 0.0) + total_for_recipe
                
                # Keep first seen formatted display name & unit
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
