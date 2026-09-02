from typing import List, Optional
from sqlalchemy import String, Integer, Float, Boolean, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
from pydantic import BaseModel, ConfigDict
from src.database import Base

# --- SQLAlchemy ORM Models ---

class MasterIngredient(Base):
    """Pool d'ingrédients principaux disponibles pour l'autocomplétion."""
    __tablename__ = "master_ingredients"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    name: Mapped[str] = mapped_column(String, unique=True, nullable=False, index=True)
    default_unit: Mapped[str] = mapped_column(String, default="g")


class Recipe(Base):
    """Modèle de recette avec métadonnées et portions de base (par défaut 5 personnes)."""
    __tablename__ = "recipes"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    name: Mapped[str] = mapped_column(String, nullable=False)
    prep_time: Mapped[int] = mapped_column(Integer, default=0)
    cook_time: Mapped[int] = mapped_column(Integer, default=0)
    base_servings: Mapped[int] = mapped_column(Integer, default=5)
    
    # Métadonnées (en français)
    difficulty: Mapped[str] = mapped_column(String, default="Moyen")     # Facile, Moyen, Difficile
    price: Mapped[str] = mapped_column(String, default="Modéré")        # Économique, Modéré, Élevé
    uses_oven: Mapped[bool] = mapped_column(Boolean, default=False)     # True = Four requis
    season: Mapped[str] = mapped_column(String, default="Aucune")       # Été, Hiver, Aucune

    is_vegetarian: Mapped[bool] = mapped_column(Boolean, default=False)

    ingredients: Mapped[List["Ingredient"]] = relationship(
        "Ingredient", back_populates="recipe", cascade="all, delete-orphan", lazy="selectin"
    )


class Ingredient(Base):
    """Ligne d'ingrédient appartenant à une recette."""
    __tablename__ = "ingredients"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    recipe_id: Mapped[int] = mapped_column(ForeignKey("recipes.id"), nullable=False)
    name: Mapped[str] = mapped_column(String, nullable=False)
    amount: Mapped[float] = mapped_column(Float, default=1.0)
    unit: Mapped[str] = mapped_column(String, default="")

    recipe: Mapped["Recipe"] = relationship("Recipe", back_populates="ingredients")


# --- Schémas Pydantic ---

class MasterIngredientCreate(BaseModel):
    name: str
    default_unit: str = "g"


class IngredientCreate(BaseModel):
    name: str
    amount: float = 1.0
    unit: str = ""


class RecipeCreate(BaseModel):
    name: str
    prep_time: int = 0
    cook_time: int = 0
    base_servings: int = 5
    difficulty: str = "Moyen"
    price: str = "Modéré"
    uses_oven: bool = False
    season: str = "Aucune"
    is_vegetarian: bool = False
    ingredients: List[IngredientCreate] = []


class AggregatedIngredient(BaseModel):
    name: str
    total_amount: float
    unit: str
    bought: bool = False

    model_config = ConfigDict(from_attributes=True)
