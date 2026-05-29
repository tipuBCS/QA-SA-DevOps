from dataclasses import dataclass


@dataclass
class CreateRoomTypeRequest:
    name: str
    description: str = ""
