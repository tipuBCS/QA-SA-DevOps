from middleware.public_routes import PUBLIC_ROUTES
from services.auth_service import AuthService

auth_service = AuthService()


def authenticate(event: dict) -> dict:
    """
    Validate the JWT token and return the event with user attached.

    For public routes, returns the event unchanged.
    For protected routes, validates the token and attaches the user
    to event["requestContext"]["authorizer"].

    If auth fails, returns a 401 API Gateway response instead of the event.
    Check the return for "statusCode" to determine if it's an error response.
    """
    method = event.get("httpMethod", "")
    path = event.get("path", "")

    # Public routes — return event as-is
    for public_method, public_path in PUBLIC_ROUTES:
        if method == public_method and path == public_path:
            return event

    # Extract and validate token
    headers = event.get("headers") or {}
    auth_header = headers.get("Authorization") or headers.get("authorization")

    try:
        token = auth_service.extract_token_from_header(auth_header)
        user = auth_service.get_user_from_token(token)
    except ValueError as e:
        return {
            "statusCode": 401,
            "headers": {"Content-Type": "application/json"},
            "body": f'{{"error": "Unauthorized", "message": "{e}"}}',
        }

    # Attach user to request context and return modified event
    event.setdefault("requestContext", {})["authorizer"] = user # Put the user info into requestContext for use by our routes
    return event
