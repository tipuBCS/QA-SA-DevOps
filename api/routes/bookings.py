from aws_lambda_powertools.event_handler.api_gateway import Router, Response
from aws_lambda_powertools import Logger, Tracer

from routes import to_json
from services.booking_service import BookingService

logger = Logger()
tracer = Tracer()
router = Router()

booking_service = BookingService()


@router.delete("/<booking_id>")
@tracer.capture_method
def cancel_booking(booking_id: str):
    body = router.current_event.json_body

    
    # TODO: Auth
    # Check if logged in and check if admin user
    
    # user = body.get("_user", {})
    # if not user.get("user_id"):
    #     return Response(
    #         status_code=401,
    #         content_type="application/json",
    #         body=to_json({"error": "Authentication required"}),
    #     )

    # Check if user owns booking (or is admin)
    # TODO Auth Checking
    # userIsAdmin = user.get("isAdmin")
    # userOwnsBooking = booking["user_id"] == user.get("user_id")
    # if not userIsAdmin or not userOwnsBooking:
    #     return Response(
    #         status_code=400,
    #         content_type="application/json",
    #         body=to_json(
    #             {"error": "You are not authorised to cancel this booking"}
    #         ),
    #     )

    # Get booking
    try:
        booking = booking_service.get_booking(booking_id)
    except ValueError as e:
        return Response(
            status_code=400,
            content_type="application/json",
            body=to_json({"error": f"Invalid booking id: {booking_id}"}),
        )

    

    try:
        booking_service.cancel_booking(booking_id)
    except (TypeError, KeyError) as e:
        return Response(
            status_code=400,
            content_type="application/json",
            body=to_json({"error": f"Missing required fields: {e}"}),
        )

    return Response(
        status_code=200,
        content_type="application/json",
        body=to_json({"message": "Booking cancelled successfully"}),
    )


@router.get("/user/<user_id>")
@tracer.capture_method
def list_user_bookings(user_id: str):
    body = router.current_event.json_body or {}
    user = body.get("_user", {})
    if not user.get("user_id"):
        return Response(
            status_code=401,
            content_type="application/json",
            body=to_json({"error": "Authentication required"}),
        )

    bookings = booking_service.list_user_bookings(user_id)
    return Response(
        status_code=200,
        content_type="application/json",
        body=to_json({"bookings": bookings}),
    )
