from aws_lambda_powertools.event_handler.api_gateway import Router, Response
from aws_lambda_powertools import Logger, Tracer

import json

from models.room_type import CreateRoomTypeRequest
from services.room_type_service import RoomTypeService

logger = Logger()
tracer = Tracer()
router = Router()

room_type_service = RoomTypeService()


@router.post("/")
@tracer.capture_method
def create_room_type():
    body = router.current_event.json_body

    user = body.get("_user", {})
    if not user.get("is_admin"):
        return Response(
            status_code=403,
            content_type="application/json",
            body=json.dumps({"error": "Admin access required"}),
        )

    try:
        request = CreateRoomTypeRequest(
            name=body["name"],
            description=body.get("description", ""),
        )
    except (TypeError, KeyError) as e:
        return Response(
            status_code=400,
            content_type="application/json",
            body=json.dumps({"error": f"Missing required fields: {e}"}),
        )

    try:
        room_type = room_type_service.create_room_type(request)
    except ValueError as e:
        return Response(
            status_code=409,
            content_type="application/json",
            body=json.dumps({"error": str(e)}),
        )

    return Response(
        status_code=201,
        content_type="application/json",
        body=json.dumps({"message": "Room type created successfully", "room_type": room_type}),
    )


@router.get("/")
@tracer.capture_method
def list_room_types():
    room_types = room_type_service.list_room_types()
    return Response(
        status_code=200,
        content_type="application/json",
        body=json.dumps({"room_types": room_types}),
    )


@router.delete("/<room_type_id>")
@tracer.capture_method
def delete_room_type(room_type_id: str):
    body = router.current_event.json_body or {}
    user = body.get("_user", {})
    if not user.get("is_admin"):
        return Response(
            status_code=403,
            content_type="application/json",
            body=json.dumps({"error": "Admin access required"}),
        )

    try:
        room_type_service.delete_room_type(room_type_id)
    except ValueError as e:
        return Response(
            status_code=404,
            content_type="application/json",
            body=json.dumps({"error": str(e)}),
        )

    return Response(
        status_code=200,
        content_type="application/json",
        body=json.dumps({"message": "Room type deleted successfully"}),
    )
