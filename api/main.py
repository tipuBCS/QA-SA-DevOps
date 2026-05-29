from aws_lambda_powertools import Logger, Tracer, Metrics
from aws_lambda_powertools.event_handler import APIGatewayRestResolver
from aws_lambda_powertools.event_handler.api_gateway import CORSConfig
from aws_lambda_powertools.utilities.typing import LambdaContext

from routes.users import router as users_router

# Initialize core utilities
logger = Logger()
tracer = Tracer()
metrics = Metrics()

cors_config = CORSConfig(
    allow_origin="*",
    allow_headers=["Content-Type"],
    max_age=300,
)
app = APIGatewayRestResolver(cors=cors_config)

# Register route modules
app.include_router(users_router, prefix="/users")


# Main Lambda handler
@logger.inject_lambda_context
@tracer.capture_lambda_handler
@metrics.log_metrics
def lambda_handler(event: dict, context: LambdaContext):
    return app.resolve(event, context)
