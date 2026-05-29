from aws_lambda_powertools import Logger, Tracer, Metrics
from aws_lambda_powertools.event_handler import APIGatewayRestResolver
from aws_lambda_powertools.event_handler.api_gateway import CORSConfig
from aws_lambda_powertools.utilities.typing import LambdaContext

from routes.users import router as users_router
from routes.buildings import router as buildings_router
from routes.rooms import router as rooms_router
from routes.bookings import router as bookings_router
from routes.room_types import router as room_types_router

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
app.include_router(buildings_router, prefix="/buildings")
app.include_router(rooms_router, prefix="/buildings")
app.include_router(bookings_router, prefix="/buildings")
app.include_router(room_types_router, prefix="/room-types")


# Main Lambda handler
@logger.inject_lambda_context
@tracer.capture_lambda_handler
@metrics.log_metrics
def lambda_handler(event: dict, context: LambdaContext):
    return app.resolve(event, context)
