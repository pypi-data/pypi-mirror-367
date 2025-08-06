from erad.models.asset import Asset
from erad.runner import HarzardSimulator
from erad.systems.asset_system import AssetSystem
from erad.systems.hazard_system import HazardSystem


def get_asset_system() -> AssetSystem:
    asset = Asset.example()
    asset_system = AssetSystem(auto_add_composed_components=True)
    asset_system.add_component(asset.example())
    return asset_system


def test_earthquake_simulation():
    hazard_scenario = HarzardSimulator(asset_system=get_asset_system())
    hazard_scenario.run(hazard_system=HazardSystem.earthquake_example())


def test_fire_simulation():
    hazard_scenario = HarzardSimulator(asset_system=get_asset_system())
    hazard_scenario.run(hazard_system=HazardSystem.fire_example())


def test_wind_simulation():
    hazard_scenario = HarzardSimulator(asset_system=get_asset_system())
    hazard_scenario.run(hazard_system=HazardSystem.wind_example())


def test_flood_simulation():
    hazard_scenario = HarzardSimulator(asset_system=get_asset_system())
    hazard_scenario.run(hazard_system=HazardSystem.flood_example())
