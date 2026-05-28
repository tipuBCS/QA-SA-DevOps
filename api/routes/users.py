from aws_lambda_powertools.event_handler.api_gateway import Router, Response
from aws_lambda_powertools import Logger, Tracer

import json

from models.user import CreateUserRequest, LoginRequest
from services.user_service import UserService

logger = Logger()
tracer = Tracer()
router = Router()

user_service = UserService()


@router.post("/signup")
@tracer.capture_method
def signup():
    body = router.current_event.json_body
    try:
        request = CreateUserRequest(**body)
    except (TypeError, KeyError) as e:
        return Response(
            status_code=400,
            content_type="application/json",
            body=json.dumps({"error": f"Missing required fields: {e}"}),
        )

    logger.info("User signup request", extra={"email": request.email})

    try:
        user = user_service.create_user(request)
    except ValueError as e:
        return Response(
            status_code=409,
            content_type="application/json",
            body=json.dumps({"error": str(e)}),
        )

    return Response(
        status_code=201,
        content_type="application/json",
        body=json.dumps({"message": "User created successfully", "user": user}),
    )


@router.post("/login")
@tracer.capture_method
def login():
    body = router.current_event.json_body
    try:
        request = LoginRequest(**body)
    except (TypeError, KeyError) as e:
        return Response(
            status_code=400,
            content_type="application/json",
            body=json.dumps({"error": f"Missing required fields: {e}"}),
        )

    logger.info("User login request", extra={"email": request.email})

    try:
        result = user_service.login(request)
    except ValueError as e:
        return Response(
            status_code=401,
            content_type="application/json",
            body=json.dumps({"error": str(e)}),
        )

    return Response(
        status_code=200,
        content_type="application/json",
        body=json.dumps(result),
    )


@router.get("/<user_id>")
@tracer.capture_method
def get_user(user_id: str):
    logger.info("Get user request", extra={"user_id": user_id})

    try:
        user = user_service.get_user(user_id)
    except ValueError as e:
        return Response(
            status_code=404,
            content_type="application/json",
            body=json.dumps({"error": str(e)}),
        )

    return Response(
        status_code=200,
        content_type="application/json",
        body=json.dumps({"user": user}),
    )


@router.delete("/<user_id>")
@tracer.capture_method
def delete_user(user_id: str):
    logger.info("Delete user request", extra={"user_id": user_id})

    try:
        user_service.delete_user(user_id)
    except ValueError as e:
        return Response(
            status_code=404,
            content_type="application/json",
            body=json.dumps({"error": str(e)}),
        )

    return Response(
        status_code=200,
        content_type="application/json",
        body=json.dumps({"message": "User deleted successfully"}),
    )
