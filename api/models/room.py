from dataclasses import dataclass


@dataclass
class CreateRoomRequest:
    building_id: str
    floor: int
    name: str
    capacity: int
    min_access_level: int
    room_type_id: str = ""
    room_type_name: str = ""
    amenities: list = None

    def __post_init__(self):
        if self.amenities is None:
            self.amenities = []
