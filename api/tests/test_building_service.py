import pytest

from services.building_service import BuildingService
from models.building import CreateBuildingRequest

pytestmark = pytest.mark.unit

class TestCreateBuilding:
    def test_creates_building_successfully(self, dynamodb_table):
        service = BuildingService(table_resource=dynamodb_table)
        request = CreateBuildingRequest(name="HQ", address="123 Main St", num_floors=5)

        result = service.create_building(request)

        assert result["name"] == "HQ"
        assert result["address"] == "123 Main St"
        assert result["num_floors"] == 5
        assert "building_id" in result

    def test_raises_error_for_zero_floors(self, dynamodb_table):
        service = BuildingService(table_resource=dynamodb_table)

        with pytest.raises(ValueError, match="at least 1 floor"):
            service.create_building(
                CreateBuildingRequest(name="Bad", address="Nowhere", num_floors=0)
            )


class TestGetBuilding:
    def test_get_building_returns_data(self, dynamodb_table):
        service = BuildingService(table_resource=dynamodb_table)
        created = service.create_building(
            CreateBuildingRequest(name="Office", address="456 Ave", num_floors=3)
        )

        result = service.get_building(created["building_id"])

        assert result["name"] == "Office"
        assert result["num_floors"] == 3

    def test_raises_for_nonexistent_building(self, dynamodb_table):
        service = BuildingService(table_resource=dynamodb_table)

        with pytest.raises(ValueError, match="Building not found"):
            service.get_building("nonexistent-id")


class TestListBuildings:
    def test_lists_all_buildings(self, dynamodb_table):
        service = BuildingService(table_resource=dynamodb_table)
        service.create_building(CreateBuildingRequest(name="A", address="1", num_floors=2))
        service.create_building(CreateBuildingRequest(name="B", address="2", num_floors=4))

        result = service.list_buildings()

        assert len(result) == 2
        names = [b["name"] for b in result]
        assert "A" in names
        assert "B" in names


class TestDeleteBuilding:
    def test_deletes_building(self, dynamodb_table):
        service = BuildingService(table_resource=dynamodb_table)
        created = service.create_building(
            CreateBuildingRequest(name="ToDelete", address="X", num_floors=1)
        )

        service.delete_building(created["building_id"])

        with pytest.raises(ValueError, match="Building not found"):
            service.get_building(created["building_id"])
