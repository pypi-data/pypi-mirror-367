import pytest
from src.meal_generator.nutrient_profile import NutrientProfile
from src.meal_generator.meal_component import MealComponent
from src.meal_generator.models import ComponentType, DataSource


@pytest.fixture
def nutrient_profile_fixt() -> NutrientProfile:
    """Provides a sample NutrientProfile instance."""
    return NutrientProfile(
        energy=150.0,
        fats=10.0,
        saturated_fats=2.5,
        carbohydrates=5.0,
        sugars=1.0,
        fibre=2.0,
        protein=15.0,
        salt=0.5,
        contains_gluten=True,
        is_processed=True,
        data_source=DataSource.RETRIEVED_API,
    )


@pytest.fixture
def meal_component_fixt(nutrient_profile_fixt: NutrientProfile) -> MealComponent:
    """Provides a sample MealComponent instance."""
    return MealComponent(
        name="Grilled Chicken Breast",
        quantity=1.0,
        metric="breast",
        total_weight=120.0,
        component_type=ComponentType.FOOD,
        nutrient_profile=nutrient_profile_fixt,
        brand="Farm Fresh",
        source_url="http://example.com/chicken",
    )