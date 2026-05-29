from aws_lambda_powertools.event_handler.api_gateway import Router, Response
from aws_lambda_powertools import Logger, Tracer

import json

from models.building import CreateBuildingRequest
from services.building_service import BuildingService

logger = Logger()
tracer = Tracer()
router = Router()

building_service = BuildingService()


@router.post("/")
@tracer.capture_method
def create_building():
    body = router.current_event.json_body

    # Check admin
    user = body.get("_user", {})
    if not user.get("is_admin"):
        return Response(
            status_code=403,
            content_type="application/json",
            body=json.dumps({"error": "Admin access required"}),
        )

    try:
        request = CreateBuildingRequest(
            name=body["name"],
            address=body["address"],
            num_floors=body["num_floors"],
        )
    except (TypeError, KeyError) as e:
        return Response(
            status_code=400,
            content_type="application/json",
            body=json.dumps({"error": f"Missing required fields: {e}"}),
        )

    try:
        building = building_service.create_building(request)
    except ValueError as e:
        return Response(
            status_code=400,
            content_type="application/json",
            body=json.dumps({"error": str(e)}),
        )

    return Response(
        status_code=201,
        content_type="application/json",
        body=json.dumps({"message": "Building created successfully", "building": building}),
    )


@router.get("/")
@tracer.capture_method
def list_buildings():
    buildings = building_service.list_buildings()
    return Response(
        status_code=200,
        content_type="application/json",
        body=json.dumps({"buildings": buildings}),
    )


@router.get("/<building_id>")
@tracer.capture_method
def get_building(building_id: str):
    try:
        building = building_service.get_building(building_id)
    except ValueError as e:
        return Response(
            status_code=404,
            content_type="application/json",
            body=json.dumps({"error": str(e)}),
        )

    return Response(
        status_code=200,
        content_type="application/json",
        body=json.dumps({"building": building}),
    )


@router.delete("/<building_id>")
@tracer.capture_method
def delete_building(building_id: str):
    body = router.current_event.json_body or {}
    user = body.get("_user", {})
    if not user.get("is_admin"):
        return Response(
            status_code=403,
            content_type="application/json",
            body=json.dumps({"error": "Admin access required"}),
        )

    try:
        building_service.delete_building(building_id)
    except ValueError as e:
        return Response(
            status_code=404,
            content_type="application/json",
            body=json.dumps({"error": str(e)}),
        )

    return Response(
        status_code=200,
        content_type="application/json",
        body=json.dumps({"message": "Building deleted successfully"}),
    )
