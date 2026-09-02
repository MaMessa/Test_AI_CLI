from typing import List
from sqlalchemy import String, Integer, Float, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
from pydantic import BaseModel, ConfigDict
from src.database import Base

# --- SQLAlchemy ORM Models ---

class Recipe(Base):
    """Recipe model for storing recipe metadata."""
    __tablename__ = "recipes"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    name: Mapped[str] = mapped_column(String, nullable=False)
    prep_time: Mapped[int] = mapped_column(Integer, default=0)
    cook_time: Mapped[int] = mapped_column(Integer, default=0)

    ingredients: Mapped[List["Ingredient"]] = relationship(
        "Ingredient", back_populates="recipe", cascade="all, delete-orphan", lazy="selectin"
    )


class Ingredient(Base):
    """Ingredient model linked to a specific recipe."""
    __tablename__ = "ingredients"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    recipe_id: Mapped[int] = mapped_column(ForeignKey("recipes.id"), nullable=False)
    name: Mapped[str] = mapped_column(String, nullable=False)
    amount_per_person: Mapped[float] = mapped_column(Float, default=1.0)
    unit: Mapped[str] = mapped_column(String, default="")

    recipe: Mapped["Recipe"] = relationship("Recipe", back_populates="ingredients")


# --- Pydantic Schemas ---

class IngredientCreate(BaseModel):
    name: str
    amount_per_person: float = 1.0
    unit: str = ""


class RecipeCreate(BaseModel):
    name: str
    prep_time: int = 0
    cook_time: int = 0
    ingredients: List[IngredientCreate] = []


class AggregatedIngredient(BaseModel):
    name: str
    total_amount: float
    unit: str
    bought: bool = False

    model_config = ConfigDict(from_attributes=True)
