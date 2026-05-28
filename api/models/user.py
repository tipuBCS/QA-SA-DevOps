from dataclasses import dataclass


@dataclass
class CreateUserRequest:
    email: str
    password: str
    name: str


@dataclass
class LoginRequest:
    email: str
    password: str
