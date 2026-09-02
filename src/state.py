from dataclasses import dataclass, field
from typing import List

@dataclass
class Recipe:
    id: int
    name: str
    prep_time: int  # minutes
    cook_time: int  # minutes
    ingredients: List[str] = field(default_factory=list)

class RecipeState:
    """In-memory state management for recipes."""
    def __init__(self):
        self.recipes: List[Recipe] = []
        self._next_id: int = 1

    def add_recipe(self, name: str, prep_time: int, cook_time: int, ingredients_raw: str) -> Recipe:
        ingredients = [i.strip() for i in ingredients_raw.split(",") if i.strip()]
        recipe = Recipe(
            id=self._next_id,
            name=name,
            prep_time=prep_time,
            cook_time=cook_time,
            ingredients=ingredients
        )
        self.recipes.append(recipe)
        self._next_id += 1
        return recipe

    def get_all(self) -> List[Recipe]:
        return self.recipes

# Global in-memory state instance
state = RecipeState()
