from dataclasses import dataclass


class AccessLevel:
    EMPLOYEE = 1
    MANAGER = 2
    DIRECTOR = 3
    EXECUTIVE = 4

    NAMES = {
        1: "Employee",
        2: "Manager",
        3: "Director",
        4: "Executive",
    }

    @classmethod
    def is_valid(cls, level: int) -> bool:
        return level in cls.NAMES

    @classmethod
    def name_for(cls, level: int) -> str:
        return cls.NAMES.get(level, "Unknown")


@dataclass
class CreateUserRequest:
    email: str
    password: str
    name: str
    is_admin: bool = False
    access_level: int = AccessLevel.EMPLOYEE


@dataclass
class LoginRequest:
    email: str
    password: str
