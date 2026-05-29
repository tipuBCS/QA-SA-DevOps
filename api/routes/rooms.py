from aws_lambda_powertools.event_handler.api_gateway import Router, Response
from aws_lambda_powertools import Logger, Tracer

import json

from models.room import CreateRoomRequest
from services.room_service import RoomService

logger = Logger()
tracer = Tracer()
router = Router()

room_service = RoomService()


@router.post("/<building_id>/rooms")
@tracer.capture_method
def create_room(building_id: str):
    body = router.current_event.json_body

    user = body.get("_user", {})
    if not user.get("is_admin"):
        return Response(
            status_code=403,
            content_type="application/json",
            body=json.dumps({"error": "Admin access required"}),
        )

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
            body=json.dumps({"error": f"Missing required fields: {e}"}),
        )

    try:
        room = room_service.create_room(request)
    except ValueError as e:
        return Response(
            status_code=400,
            content_type="application/json",
            body=json.dumps({"error": str(e)}),
        )

    return Response(
        status_code=201,
        content_type="application/json",
        body=json.dumps({"message": "Room created successfully", "room": room}),
    )


@router.get("/<building_id>/rooms")
@tracer.capture_method
def list_rooms(building_id: str):
    rooms = room_service.list_rooms(building_id=building_id)
    return Response(
        status_code=200,
        content_type="application/json",
        body=json.dumps({"rooms": rooms}),
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
            body=json.dumps({"error": str(e)}),
        )

    return Response(
        status_code=200,
        content_type="application/json",
        body=json.dumps({"room": room}),
    )


@router.delete("/<building_id>/rooms/<room_id>")
@tracer.capture_method
def delete_room(building_id: str, room_id: str):
    body = router.current_event.json_body or {}
    user = body.get("_user", {})
    if not user.get("is_admin"):
        return Response(
            status_code=403,
            content_type="application/json",
            body=json.dumps({"error": "Admin access required"}),
        )

    try:
        room_service.delete_room(building_id, room_id)
    except ValueError as e:
        return Response(
            status_code=404,
            content_type="application/json",
            body=json.dumps({"error": str(e)}),
        )

    return Response(
        status_code=200,
        content_type="application/json",
        body=json.dumps({"message": "Room deleted successfully"}),
    )
