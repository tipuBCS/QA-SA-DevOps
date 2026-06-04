from aws_lambda_powertools.event_handler.api_gateway import Router, Response
from aws_lambda_powertools import Logger, Tracer

from routes import to_json, get_current_user
from services.booking_service import BookingService

logger = Logger()
tracer = Tracer()
router = Router()

booking_service = BookingService()


@router.delete("/<booking_id>")
@tracer.capture_method
def cancel_booking(booking_id: str):
    current_user = get_current_user(router)

    # Get booking
    try:
        booking = booking_service.get_booking(booking_id)
    except ValueError:
        return Response(
            status_code=404,
            content_type="application/json",
            body=to_json({"error": f"Booking not found: {booking_id}"}),
        )

    # Only the booking owner or an admin can cancel
    if not current_user["is_admin"] and booking["user_id"] != current_user["user_id"]:
        return Response(
            status_code=403,
            content_type="application/json",
            body=to_json({"error": "You are not authorised to cancel this booking"}),
        )

    try:
        booking_service.cancel_booking(booking_id)
    except ValueError as e:
        return Response(
            status_code=400,
            content_type="application/json",
            body=to_json({"error": str(e)}),
        )

    return Response(
        status_code=200,
        content_type="application/json",
        body=to_json({"message": "Booking cancelled successfully"}),
    )


@router.get("/user/<user_id>")
@tracer.capture_method
def list_user_bookings(user_id: str):
    current_user = get_current_user(router)

    # Users can only list their own bookings unless they're admin
    if not current_user["is_admin"] and current_user["user_id"] != user_id:
        return Response(
            status_code=403,
            content_type="application/json",
            body=to_json({"error": "You can only view your own bookings"}),
        )

    bookings = booking_service.list_user_bookings(user_id)
    return Response(
        status_code=200,
        content_type="application/json",
        body=to_json({"bookings": bookings}),
    )
