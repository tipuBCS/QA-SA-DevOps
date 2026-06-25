from aws_lambda_powertools.event_handler.api_gateway import Router, Response
from aws_lambda_powertools import Logger, Tracer

from models.booking import BookRoomRequest
from models.room import CreateRoomRequest
from routes import to_json, get_current_user
from services.booking_service import BookingService
from services.room_service import RoomService

logger = Logger()
tracer = Tracer()
router = Router()

room_service = RoomService()
booking_service = BookingService()


@router.post("/<building_id>/rooms")
@tracer.capture_method
def create_room(building_id: str):
    current_user = get_current_user(router)
    if not current_user["is_admin"]:
        return Response(
            status_code=403,
            content_type="application/json",
            body=to_json({"error": "Admin access required"}),
        )

    body = router.current_event.json_body

    try:
        request = CreateRoomRequest(
            building_id=building_id,
            floor=body["floor"],
            name=body["name"],
            capacity=body["capacity"],
            min_access_level=body["min_access_level"],
            amenities=body.get("amenities", []),
        )
    except (TypeError, KeyError) as e:
        return Response(
            status_code=400,
            content_type="application/json",
            body=to_json({"error": f"Missing required fields: {e}"}),
        )

    try:
        room = room_service.create_room(request)
    except ValueError as e:
        return Response(
            status_code=400,
            content_type="application/json",
            body=to_json({"error": str(e)}),
        )

    return Response(
        status_code=201,
        content_type="application/json",
        body=to_json({"message": "Room created successfully", "room": room}),
    )


@router.get("/<building_id>/rooms")
@tracer.capture_method
def list_rooms(building_id: str):
    rooms = room_service.list_rooms(building_id=building_id)
    return Response(
        status_code=200,
        content_type="application/json",
        body=to_json({"rooms": rooms}),
    )


@router.get("/<building_id>/rooms/<room_id>")
@tracer.capture_method
def get_room(building_id: str, room_id: str):
    try:
        room = room_service.get_room(building_id, room_id)
    except ValueError as e:
        return Response(
            status_code=404,
            content_type="application/json",
            body=to_json({"error": str(e)}),
        )

    return Response(
        status_code=200,
        content_type="application/json",
        body=to_json({"room": room}),
    )


@router.delete("/<building_id>/rooms/<room_id>")
@tracer.capture_method
def delete_room(building_id: str, room_id: str):
    current_user = get_current_user(router)
    if not current_user["is_admin"]:
        return Response(
            status_code=403,
            content_type="application/json",
            body=to_json({"error": "Admin access required"}),
        )

    try:
        room_service.delete_room(building_id, room_id)
    except ValueError as e:
        return Response(
            status_code=404,
            content_type="application/json",
            body=to_json({"error": str(e)}),
        )

    return Response(
        status_code=200,
        content_type="application/json",
        body=to_json({"message": "Room deleted successfully"}),
    )


@router.post("/<building_id>/rooms/<room_id>/book")
@tracer.capture_method
def book_room(building_id: str, room_id: str):
    current_user = get_current_user(router)

    body = router.current_event.json_body

    try:
        request = BookRoomRequest(
            room_id=room_id,
            building_id=building_id,
            user_id=current_user["user_id"],
            date=body["date"],
            start_time=body["start_time"],
            end_time=body["end_time"],
            purpose=body.get("purpose", ""),
        )
    except (TypeError, KeyError) as e:
        return Response(
            status_code=400,
            content_type="application/json",
            body=to_json({"error": f"Missing required fields: {e}"}),
        )

    try:
        booking = booking_service.book_room(request, current_user["access_level"])
    except ValueError as e:
        return Response(
            status_code=403,
            content_type="application/json",
            body=to_json({"error": str(e)}),
        )

    return Response(
        status_code=201,
        content_type="application/json",
        body=to_json({"message": "Room booked successfully", "booking": booking}),
    )


@router.get("/<building_id>/bookings")
@tracer.capture_method
def list_building_bookings(building_id: str):
    date = router.current_event.get_query_string_value("date")

    if not date:
        return Response(
            status_code=400,
            content_type="application/json",
            body=to_json({"error": "date query parameter is required"}),
        )

    bookings = booking_service.list_building_bookings(building_id, date)
    return Response(
        status_code=200,
        content_type="application/json",
        body=to_json({"bookings": bookings}),
    )
