from typing import List, Dict, Tuple, Optional, Any
from sqlalchemy.orm import Session
from src.database import get_db_session, init_db
from src.seed import seed_database_if_empty
from src.marmiton import fetch_marmiton_recipe_data
from src.models import (
    Recipe, Ingredient, MasterIngredient, 
    RecipeCreate, IngredientCreate, AggregatedIngredient
)

def initialize_database():
    """Ensure database schema exists and populate initial seed data if empty."""
    init_db()
    seed_database_if_empty()

# --- Auto-creation Helper ---

def ensure_master_ingredient_exists(db: Session, name: str, unit: str):
    """Auto-create unknown ingredient in master pool if it does not exist yet."""
    name_clean = name.strip()
    if not name_clean:
        return
    existing = db.query(MasterIngredient).filter(MasterIngredient.name.ilike(name_clean)).first()
    if not existing:
        db.add(MasterIngredient(name=name_clean, default_unit=unit.strip() or "g"))


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


def update_master_ingredient(ingredient_id: int, name: str, default_unit: str) -> Optional[MasterIngredient]:
    """Update a master ingredient name and default unit."""
    db: Session = get_db_session()
    try:
        master = db.query(MasterIngredient).filter(MasterIngredient.id == ingredient_id).first()
        if master:
            master.name = name.strip()
            master.default_unit = default_unit.strip()
            db.commit()
            db.refresh(master)
            return master
        return None
    finally:
        db.close()


def delete_master_ingredient(ingredient_id: int) -> bool:
    """Delete a master ingredient from the pool."""
    db: Session = get_db_session()
    try:
        master = db.query(MasterIngredient).filter(MasterIngredient.id == ingredient_id).first()
        if master:
            db.delete(master)
            db.commit()
            return True
        return False
    finally:
        db.close()


# --- Recipe CRUD & Filter Services ---

def create_recipe(recipe_data: RecipeCreate) -> Recipe:
    """Create a new recipe with metadata (default 5-person base) & auto-add missing ingredients."""
    db: Session = get_db_session()
    try:
        recipe = Recipe(
            name=recipe_data.name,
            prep_time=recipe_data.prep_time,
            cook_time=recipe_data.cook_time,
            base_servings=recipe_data.base_servings or 5,
            difficulty=recipe_data.difficulty,
            price=recipe_data.price,
            uses_oven=recipe_data.uses_oven,
            season=recipe_data.season,
            is_vegetarian=recipe_data.is_vegetarian
        )
        db.add(recipe)
        db.flush()

        for ing in recipe_data.ingredients:
            ensure_master_ingredient_exists(db, ing.name, ing.unit)
            db.add(Ingredient(
                recipe_id=recipe.id,
                name=ing.name.strip(),
                amount=ing.amount,
                unit=ing.unit.strip()
            ))

        db.commit()
        db.refresh(recipe)
        return recipe
    finally:
        db.close()


def update_recipe(recipe_id: int, recipe_data: RecipeCreate) -> Optional[Recipe]:
    """Update an existing recipe and its ingredients."""
    db: Session = get_db_session()
    try:
        recipe = db.query(Recipe).filter(Recipe.id == recipe_id).first()
        if not recipe:
            return None

        recipe.name = recipe_data.name
        recipe.prep_time = recipe_data.prep_time
        recipe.cook_time = recipe_data.cook_time
        recipe.base_servings = recipe_data.base_servings or 5
        recipe.difficulty = recipe_data.difficulty
        recipe.price = recipe_data.price
        recipe.uses_oven = recipe_data.uses_oven
        recipe.season = recipe_data.season
        recipe.is_vegetarian = recipe_data.is_vegetarian

        db.query(Ingredient).filter(Ingredient.recipe_id == recipe_id).delete()

        for ing in recipe_data.ingredients:
            ensure_master_ingredient_exists(db, ing.name, ing.unit)
            db.add(Ingredient(
                recipe_id=recipe.id,
                name=ing.name.strip(),
                amount=ing.amount,
                unit=ing.unit.strip()
            ))

        db.commit()
        db.refresh(recipe)
        return recipe
    finally:
        db.close()


def import_recipe_from_marmiton(url: str) -> Dict[str, Any]:
    """Fetch Marmiton recipe from URL, create recipe & ingredients in DB, and return detail log dict."""
    marmiton_data = fetch_marmiton_recipe_data(url)
    db: Session = get_db_session()
    new_master_count = 0
    new_master_names = []

    try:
        ingredient_creates = []
        for ing in marmiton_data["ingredients"]:
            name = ing["name"].strip()
            unit = ing["unit"].strip()
            amount = ing["amount"]

            existing_master = db.query(MasterIngredient).filter(MasterIngredient.name.ilike(name)).first()
            if not existing_master:
                db.add(MasterIngredient(name=name, default_unit=unit or "g"))
                db.flush()
                new_master_count += 1
                new_master_names.append(name)

            ingredient_creates.append(IngredientCreate(name=name, amount=amount, unit=unit))

        recipe_create = RecipeCreate(
            name=marmiton_data["name"],
            prep_time=marmiton_data["prep_time"],
            cook_time=marmiton_data["cook_time"],
            base_servings=marmiton_data["base_servings"],
            difficulty="Moyen",
            price="Modéré",
            uses_oven=False,
            season="Aucune",
            is_vegetarian=False,
            ingredients=ingredient_creates
        )

        db.close()
        saved_recipe = create_recipe(recipe_create)

        logs = marmiton_data["logs"]
        if new_master_count > 0:
            names_summary = ", ".join(new_master_names[:4]) + ("..." if new_master_count > 4 else "")
            logs.append(f"📦 {new_master_count} nouveaux ingrédients ajoutés au catalogue ({names_summary})")

        return {
            "success": True,
            "recipe": saved_recipe,
            "logs": logs,
            "error": None
        }
    except Exception as e:
        if db:
            db.close()
        return {
            "success": False,
            "recipe": None,
            "logs": [f"❌ Échec de l'importation : {str(e)}"],
            "error": str(e)
        }


def get_filtered_recipes(
    search_query: str = "",
    uses_oven: Optional[bool] = None,
    is_vegetarian: Optional[bool] = None,
    season: Optional[str] = None,
    difficulty: Optional[str] = None,
    price: Optional[str] = None,
    max_prep_time: Optional[int] = None,
    max_total_time: Optional[int] = None
) -> List[Recipe]:
    """Retrieve recipes based on search term, metadata filters (French & English), prep time, and total time."""
    db: Session = get_db_session()
    try:
        query = db.query(Recipe)
        if search_query and search_query.strip():
            query = query.filter(Recipe.name.ilike(f"%{search_query.strip()}%"))
        if uses_oven is True:
            query = query.filter(Recipe.uses_oven == True)
        elif uses_oven is False:
            query = query.filter(Recipe.uses_oven == False)
        if is_vegetarian is True:
            query = query.filter(Recipe.is_vegetarian == True)
        
        # Support both French & English wildcard values for filters
        if season and season not in ["All", "Toutes", "Tous"]:
            query = query.filter(Recipe.season == season)
        if difficulty and difficulty not in ["All", "Toutes", "Tous"]:
            query = query.filter(Recipe.difficulty == difficulty)
        if price and price not in ["All", "Toutes", "Tous"]:
            query = query.filter(Recipe.price == price)

        if max_prep_time is not None and max_prep_time > 0:
            query = query.filter(Recipe.prep_time <= max_prep_time)
        if max_total_time is not None and max_total_time > 0:
            query = query.filter((Recipe.prep_time + Recipe.cook_time) <= max_total_time)

        return query.all()
    finally:
        db.close()


def get_all_recipes() -> List[Recipe]:
    """Retrieve all recipes with associated ingredients."""
    return get_filtered_recipes()


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


# --- Grocery List Aggregation with Individual Per-Recipe Portion Scaling ---

def generate_scaled_grocery_list(
    recipe_servings_map: Dict[int, int]
) -> List[AggregatedIngredient]:
    """
    Generate aggregated grocery list scaled individually per recipe.
    `recipe_servings_map` maps recipe_id -> target_people_count for that specific recipe.
    Formula per recipe: (ingredient_amount / recipe.base_servings) * target_people
    """
    if not recipe_servings_map:
        return []

    db: Session = get_db_session()
    try:
        recipe_ids = list(recipe_servings_map.keys())
        recipes = db.query(Recipe).filter(Recipe.id.in_(recipe_ids)).all()
        
        aggregated_map: Dict[Tuple[str, str], float] = {}
        display_names: Dict[Tuple[str, str], Tuple[str, str]] = {}

        for recipe in recipes:
            target_people = recipe_servings_map.get(recipe.id, recipe.base_servings or 5)
            base_servings = recipe.base_servings if recipe.base_servings > 0 else 5
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
            result.append(AggregatedIngredient(name=name, total_amount=round(total_amount, 2), unit=unit))
        return result
    finally:
        db.close()
