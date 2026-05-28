from aws_lambda_powertools import Logger, Tracer, Metrics
from aws_lambda_powertools.event_handler import APIGatewayRestResolver
from aws_lambda_powertools.event_handler.api_gateway import Response
from aws_lambda_powertools.utilities.typing import LambdaContext
from aws_lambda_powertools.metrics import MetricUnit

# Initialize core utilities
logger = Logger()
tracer = Tracer()
metrics = Metrics()
app = APIGatewayRestResolver()

# Create an endpoint
@app.get("/users/<user_id>")
@tracer.capture_method
def get_user(user_id: str):
    # Log the request
    logger.info("Fetching user details", extra={"user_id": user_id})
    # Add business metrics
    metrics.add_metric(name="GetUserRequests", unit=MetricUnit.Count, value=1)
    # Your business logic here
    user = {
        "id": user_id,
        "name": "John Doe",
        "email": "john@example.com"
    }
    return Response(
        status_code=200,
        content_type="application/json",
        body=user
    )


# Main Lambda handler
@logger.inject_lambda_context
@tracer.capture_lambda_handler
@metrics.log_metrics
def lambda_handler(event: dict, context: LambdaContext):
    return app.resolve(event, context)