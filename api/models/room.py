from dataclasses import dataclass


@dataclass
class CreateRoomRequest:
    building_id: str
    floor: int
    name: str
    capacity: int
    min_access_level: int
    amenities: list = None

    def __post_init__(self):
        if self.amenities is None:
            self.amenities = []
