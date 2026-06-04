import pytest

from services.room_type_service import RoomTypeService
from models.room_type import CreateRoomTypeRequest

pytestmark = pytest.mark.unit

class TestCreateRoomType:
    def test_creates_room_type_successfully(self, dynamodb_table):
        service = RoomTypeService(table_resource=dynamodb_table)

        result = service.create_room_type(
            CreateRoomTypeRequest(name="Huddle Space", description="Small informal meeting area")
        )

        assert result["name"] == "Huddle Space"
        assert result["description"] == "Small informal meeting area"
        assert "room_type_id" in result

    def test_raises_error_for_duplicate_name(self, dynamodb_table):
        service = RoomTypeService(table_resource=dynamodb_table)
        service.create_room_type(CreateRoomTypeRequest(name="Conference Room"))

        with pytest.raises(ValueError, match="already exists"):
            service.create_room_type(CreateRoomTypeRequest(name="Conference Room"))

    def test_duplicate_check_is_case_insensitive(self, dynamodb_table):
        service = RoomTypeService(table_resource=dynamodb_table)
        service.create_room_type(CreateRoomTypeRequest(name="Boardroom"))

        with pytest.raises(ValueError, match="already exists"):
            service.create_room_type(CreateRoomTypeRequest(name="boardroom"))


class TestListRoomTypes:
    def test_lists_all_room_types(self, dynamodb_table):
        service = RoomTypeService(table_resource=dynamodb_table)
        service.create_room_type(CreateRoomTypeRequest(name="Huddle"))
        service.create_room_type(CreateRoomTypeRequest(name="Conference"))
        service.create_room_type(CreateRoomTypeRequest(name="Training"))

        result = service.list_room_types()

        assert len(result) == 3
        names = [rt["name"] for rt in result]
        assert "Huddle" in names
        assert "Conference" in names
        assert "Training" in names


class TestGetRoomType:
    def test_get_room_type(self, dynamodb_table):
        service = RoomTypeService(table_resource=dynamodb_table)
        created = service.create_room_type(
            CreateRoomTypeRequest(name="Phone Booth", description="Single person call room")
        )

        result = service.get_room_type(created["room_type_id"])

        assert result["name"] == "Phone Booth"
        assert result["description"] == "Single person call room"

    def test_raises_for_nonexistent(self, dynamodb_table):
        service = RoomTypeService(table_resource=dynamodb_table)

        with pytest.raises(ValueError, match="Room type not found"):
            service.get_room_type("nonexistent-id")


class TestDeleteRoomType:
    def test_deletes_room_type(self, dynamodb_table):
        service = RoomTypeService(table_resource=dynamodb_table)
        created = service.create_room_type(CreateRoomTypeRequest(name="ToDelete"))

        service.delete_room_type(created["room_type_id"])

        with pytest.raises(ValueError, match="Room type not found"):
            service.get_room_type(created["room_type_id"])

    def test_raises_for_nonexistent(self, dynamodb_table):
        service = RoomTypeService(table_resource=dynamodb_table)

        with pytest.raises(ValueError, match="Room type not found"):
            service.delete_room_type("nonexistent-id")
