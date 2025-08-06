from src.meal_generator.models import ComponentType
from src.meal_generator.meal_component import MealComponent
from src.meal_generator.nutrient_profile import NutrientProfile


def test_meal_component_creation(meal_component_fixt: MealComponent):
    """Tests successful creation of a MealComponent."""
    assert meal_component_fixt.name == "Grilled Chicken Breast"
    assert meal_component_fixt.brand == "Farm Fresh"
    assert meal_component_fixt.quantity == 1.0
    assert meal_component_fixt.metric == "breast"
    assert meal_component_fixt.total_weight == 120.0
    assert meal_component_fixt.type == ComponentType.FOOD
    assert meal_component_fixt.source_url == "http://example.com/chicken"
    assert isinstance(meal_component_fixt.nutrient_profile, NutrientProfile)


def test_meal_component_as_dict(meal_component_fixt: MealComponent):
    """Tests the serialization of a MealComponent to a dictionary."""
    component_dict = meal_component_fixt.as_dict()
    assert component_dict["name"] == "Grilled Chicken Breast"
    assert component_dict["quantity"] == 1.0
    assert component_dict["metric"] == "breast"
    assert component_dict["type"] == "food"
    assert component_dict["source_url"] == "http://example.com/chicken"
    assert "nutrient_profile" in component_dict
    assert component_dict["nutrient_profile"]["energy"] == 150.0