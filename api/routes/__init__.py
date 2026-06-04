import json
from decimal import Decimal
from typing import cast

from aws_lambda_powertools.event_handler.api_gateway import Router
from aws_lambda_powertools.utilities.data_classes import APIGatewayProxyEvent

from typings.auth import CurrentUser


class DecimalEncoder(json.JSONEncoder):
    """Custom JSON encoder that handles DynamoDB Decimal types."""

    def default(self, o):
        if isinstance(o, Decimal):
            # Convert to int if it's a whole number, otherwise float
            if o % 1 == 0:
                return int(o)
            return float(o)
        return super().default(o)


def to_json(data) -> str:
    """Serialize data to JSON, handling DynamoDB Decimal types."""
    return json.dumps(data, cls=DecimalEncoder)


def get_current_user(router: Router) -> CurrentUser:
    """Get the authenticated user from the request context."""
    event = cast(APIGatewayProxyEvent, router.current_event)
    return cast(CurrentUser, event.request_context.authorizer)
