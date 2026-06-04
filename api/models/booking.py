from dataclasses import dataclass


@dataclass
class BookRoomRequest:
    room_id: str
    building_id: str
    user_id: str
    date: str
    start_time: str
    end_time: str
    purpose: str
