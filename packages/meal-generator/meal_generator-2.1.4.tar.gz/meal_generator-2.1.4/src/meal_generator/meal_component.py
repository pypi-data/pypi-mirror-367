from typing import Optional
import uuid

from .mappable import _PydanticMappable
from .nutrient_profile import NutrientProfile
from .models import _Component, ComponentType


class MealComponent(_PydanticMappable):
    """
    Represents a single component of a meal.
    """

    def __init__(
        self,
        name: str,
        quantity: float,
        total_weight: float,
        component_type: ComponentType,
        nutrient_profile: NutrientProfile,
        brand: Optional[str] = None,
        metric: Optional[str] = None,
        source_url: Optional[str] = None,
        id: Optional[str] = None,
    ):
        if id:
            try:
                self.id: uuid.UUID = uuid.UUID(id)
            except ValueError:
                raise ValueError("Provided ID must be a valid UUID string.")
        else:
            self.id: uuid.UUID = uuid.uuid4()
        self.name = name
        self.brand = brand
        self.quantity = quantity
        self.metric = metric
        self.total_weight = total_weight
        self.type = component_type
        self.nutrient_profile = nutrient_profile
        self.source_url = source_url

    def as_dict(self) -> dict:
        return {
            "id": str(self.id),
            "name": self.name,
            "brand": self.brand,
            "quantity": self.quantity,
            "metric": self.metric,
            "total_weight": self.total_weight,
            "type": self.type.value,
            "source_url": self.source_url,
            "nutrient_profile": self.nutrient_profile.as_dict(),
        }

    @classmethod
    def from_pydantic(cls, pydantic_component: _Component) -> "MealComponent":
        """
        Factory method to create a MealComponent business object
        from its Pydantic data model representation.
        """
        nutrient_profile_object = NutrientProfile.from_pydantic(
            pydantic_component.nutrient_profile
        )

        return cls(
            name=pydantic_component.name,
            brand=pydantic_component.brand,
            quantity=pydantic_component.quantity,
            metric=pydantic_component.metric,
            total_weight=pydantic_component.total_weight,
            component_type=pydantic_component.type,
            nutrient_profile=nutrient_profile_object,
            source_url=pydantic_component.source_url,
        )

    def __repr__(self) -> str:
        quantity_str = (
            f"{self.quantity} {self.metric}" if self.metric else str(self.quantity)
        )
        return f"<MealComponent(id={self.id}, name='{self.name}', quantity='{quantity_str}')>"
