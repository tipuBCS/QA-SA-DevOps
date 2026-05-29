from aws_lambda_powertools.event_handler.api_gateway import Router, Response
from aws_lambda_powertools import Logger, Tracer

import json

from models.booking import BookRoomRequest
from services.booking_service import BookingService

logger = Logger()
tracer = Tracer()
router = Router()

booking_service = BookingService()


@router.post("/<building_id>/rooms/<room_id>/book")
@tracer.capture_method
def book_room(building_id: str, room_id: str):
    body = router.current_event.json_body

    user = body.get("_user", {})
    if not user.get("user_id"):
        return Response(
            status_code=401,
            content_type="application/json",
            body=json.dumps({"error": "Authentication required"}),
        )

    try:
        request = BookRoomRequest(
            room_id=room_id,
            user_id=user["user_id"],
            date=body["date"],
            start_time=body["start_time"],
            end_time=body["end_time"],
            purpose=body.get("purpose", ""),
        )
    except (TypeError, KeyError) as e:
        return Response(
            status_code=400,
            content_type="application/json",
            body=json.dumps({"error": f"Missing required fields: {e}"}),
        )

    try:
        booking = booking_service.book_room(request, user.get("access_level", 1))
    except ValueError as e:
        return Response(
            status_code=403,
            content_type="application/json",
            body=json.dumps({"error": str(e)}),
        )

    return Response(
        status_code=201,
        content_type="application/json",
        body=json.dumps({"message": "Room booked successfully", "booking": booking}),
    )
