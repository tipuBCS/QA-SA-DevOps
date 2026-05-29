from dataclasses import dataclass


@dataclass
class CreateBuildingRequest:
    name: str
    address: str
    num_floors: int
