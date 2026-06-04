from aws_lambda_powertools.event_handler.api_gateway import Router, Response
from aws_lambda_powertools import Logger, Tracer

from models.room_type import CreateRoomTypeRequest
from routes import to_json, get_current_user
from services.room_type_service import RoomTypeService

logger = Logger()
tracer = Tracer()
router = Router()

room_type_service = RoomTypeService()


@router.post("/")
@tracer.capture_method
def create_room_type():
    current_user = get_current_user(router)
    if not current_user["is_admin"]:
        return Response(
            status_code=403,
            content_type="application/json",
            body=to_json({"error": "Admin access required"}),
        )

    body = router.current_event.json_body

    try:
        request = CreateRoomTypeRequest(
            name=body["name"],
            description=body.get("description", ""),
        )
    except (TypeError, KeyError) as e:
        return Response(
            status_code=400,
            content_type="application/json",
            body=to_json({"error": f"Missing required fields: {e}"}),
        )

    try:
        room_type = room_type_service.create_room_type(request)
    except ValueError as e:
        return Response(
            status_code=409,
            content_type="application/json",
            body=to_json({"error": str(e)}),
        )

    return Response(
        status_code=201,
        content_type="application/json",
        body=to_json({"message": "Room type created successfully", "room_type": room_type}),
    )


@router.get("/")
@tracer.capture_method
def list_room_types():
    room_types = room_type_service.list_room_types()
    return Response(
        status_code=200,
        content_type="application/json",
        body=to_json({"room_types": room_types}),
    )


@router.delete("/<room_type_id>")
@tracer.capture_method
def delete_room_type(room_type_id: str):
    current_user = get_current_user(router)
    if not current_user["is_admin"]:
        return Response(
            status_code=403,
            content_type="application/json",
            body=to_json({"error": "Admin access required"}),
        )

    try:
        room_type_service.delete_room_type(room_type_id)
    except ValueError as e:
        return Response(
            status_code=404,
            content_type="application/json",
            body=to_json({"error": str(e)}),
        )

    return Response(
        status_code=200,
        content_type="application/json",
        body=to_json({"message": "Room type deleted successfully"}),
    )
