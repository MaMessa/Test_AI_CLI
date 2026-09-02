from typing import List, Optional
from sqlalchemy import String, Integer, Float, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
from pydantic import BaseModel, ConfigDict
from src.database import Base

# --- SQLAlchemy ORM Models ---

class MasterIngredient(Base):
    """Master pool of available ingredients for autocomplete."""
    __tablename__ = "master_ingredients"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    name: Mapped[str] = mapped_column(String, unique=True, nullable=False, index=True)
    default_unit: Mapped[str] = mapped_column(String, default="g")


class Recipe(Base):
    """Recipe model with base servings (default 4 people)."""
    __tablename__ = "recipes"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    name: Mapped[str] = mapped_column(String, nullable=False)
    prep_time: Mapped[int] = mapped_column(Integer, default=0)
    cook_time: Mapped[int] = mapped_column(Integer, default=0)
    base_servings: Mapped[int] = mapped_column(Integer, default=4)

    ingredients: Mapped[List["Ingredient"]] = relationship(
        "Ingredient", back_populates="recipe", cascade="all, delete-orphan", lazy="selectin"
    )


class Ingredient(Base):
    """Ingredient line item belonging to a recipe (quantity is for recipe base_servings)."""
    __tablename__ = "ingredients"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    recipe_id: Mapped[int] = mapped_column(ForeignKey("recipes.id"), nullable=False)
    name: Mapped[str] = mapped_column(String, nullable=False)
    amount: Mapped[float] = mapped_column(Float, default=1.0)
    unit: Mapped[str] = mapped_column(String, default="")

    recipe: Mapped["Recipe"] = relationship("Recipe", back_populates="ingredients")


# --- Pydantic Schemas ---

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
    base_servings: int = 4
    ingredients: List[IngredientCreate] = []


class AggregatedIngredient(BaseModel):
    name: str
    total_amount: float
    unit: str
    bought: bool = False

    model_config = ConfigDict(from_attributes=True)
