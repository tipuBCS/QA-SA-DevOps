import pytest

from services.room_service import RoomService
from services.building_service import BuildingService
from models.building import CreateBuildingRequest
from models.room import CreateRoomRequest
from models.user import AccessLevel


class TestCreateRoom:
    def test_creates_room_successfully(self, dynamodb_table):
        building_service = BuildingService(table_resource=dynamodb_table)
        room_service = RoomService(table_resource=dynamodb_table)
        building = building_service.create_building(
            CreateBuildingRequest(name="HQ", address="123", num_floors=5)
        )

        room = room_service.create_room(CreateRoomRequest(
            building_id=building["building_id"],
            floor=3,
            name="Conference A",
            capacity=10,
            min_access_level=AccessLevel.EMPLOYEE,
            amenities=["Projector", "Whiteboard"],
        ))

        assert room["name"] == "Conference A"
        assert room["floor"] == 3
        assert room["capacity"] == 10
        assert room["min_access_level"] == 1
        assert room["amenities"] == ["Projector", "Whiteboard"]

    def test_raises_for_invalid_floor(self, dynamodb_table):
        building_service = BuildingService(table_resource=dynamodb_table)
        room_service = RoomService(table_resource=dynamodb_table)
        building = building_service.create_building(
            CreateBuildingRequest(name="Small", address="1", num_floors=2)
        )

        with pytest.raises(ValueError, match="Floor must be between 1 and 2"):
            room_service.create_room(CreateRoomRequest(
                building_id=building["building_id"],
                floor=5,
                name="Bad Room",
                capacity=4,
                min_access_level=AccessLevel.EMPLOYEE,
            ))

    def test_raises_for_invalid_access_level(self, dynamodb_table):
        building_service = BuildingService(table_resource=dynamodb_table)
        room_service = RoomService(table_resource=dynamodb_table)
        building = building_service.create_building(
            CreateBuildingRequest(name="HQ", address="1", num_floors=3)
        )

        with pytest.raises(ValueError, match="Invalid access level"):
            room_service.create_room(CreateRoomRequest(
                building_id=building["building_id"],
                floor=1,
                name="Bad Level",
                capacity=4,
                min_access_level=99,
            ))


class TestListRooms:
    def test_lists_rooms_for_building(self, dynamodb_table):
        building_service = BuildingService(table_resource=dynamodb_table)
        room_service = RoomService(table_resource=dynamodb_table)
        building = building_service.create_building(
            CreateBuildingRequest(name="HQ", address="1", num_floors=3)
        )
        room_service.create_room(CreateRoomRequest(
            building_id=building["building_id"], floor=1, name="Room A",
            capacity=4, min_access_level=1,
        ))
        room_service.create_room(CreateRoomRequest(
            building_id=building["building_id"], floor=2, name="Room B",
            capacity=8, min_access_level=2,
        ))

        rooms = room_service.list_rooms(building["building_id"])

        assert len(rooms) == 2
        names = [r["name"] for r in rooms]
        assert "Room A" in names
        assert "Room B" in names
