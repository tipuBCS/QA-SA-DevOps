# API

Room Booker API built with AWS Lambda Powertools.

Package Manager: uv

## Project Structure

```
api/
├── models/
│   ├── user.py          # CreateUserRequest, LoginRequest, AccessLevel
│   ├── building.py      # CreateBuildingRequest
│   ├── room.py          # CreateRoomRequest
│   └── booking.py       # BookRoomRequest
├── services/
│   ├── user_service.py      # User CRUD + auth
│   ├── building_service.py  # Building CRUD
│   ├── room_service.py      # Room CRUD (validates building/floor)
│   └── booking_service.py   # Booking operations (checks access level)
├── routes/
│   ├── users.py         # /users/*
│   ├── buildings.py     # /buildings/, /buildings/<id>
│   ├── rooms.py         # /buildings/<id>/rooms/*
│   └── bookings.py      # /buildings/<id>/rooms/<id>/book
├── tests/
│   ├── test_user_service.py
│   ├── test_building_service.py
│   ├── test_room_service.py
│   ├── test_booking_service.py
│   └── integration/
│       └── test_users_api.py
└── main.py              # Lambda handler + route registration
```

## API Endpoints

### Users
- `POST /users/signup` — Create a new user
- `POST /users/login` — Authenticate a user
- `GET /users/<user_id>` — Get user by ID
- `DELETE /users/<user_id>` — Delete a user

### Buildings (admin only for create/delete)
- `POST /buildings/` — Create a building
- `GET /buildings/` — List all buildings
- `GET /buildings/<id>` — Get a building
- `DELETE /buildings/<id>` — Delete a building

### Rooms (admin only for create/delete)
- `POST /buildings/<id>/rooms` — Create a room
- `GET /buildings/<id>/rooms` — List rooms in a building
- `GET /buildings/<id>/rooms/<room_id>` — Get a room
- `DELETE /buildings/<id>/rooms/<room_id>` — Delete a room

### Bookings (access level checked)
- `POST /buildings/<id>/rooms/<room_id>/book` — Book a room

## Access Levels

| Level | Name | Can book |
|---|---|---|
| 1 | Employee | Small meeting rooms, huddle spaces |
| 2 | Manager | + Medium conference rooms |
| 3 | Director | + Large boardrooms |
| 4 | Executive | All rooms |

## Development

### Install dependencies
```bash
uv sync --extra dev
```

### Unit tests
```bash
uv run pytest -m "not integration"
```

### Integration tests

Integration tests hit the live deployed API. Set `API_URL` in your `.env`:

```
API_URL=https://your-api-id.execute-api.eu-west-2.amazonaws.com/dev
```

Get this value from the CDK output after running `./deploy.sh api` in the `infra` folder.

Then run:
```bash
uv run pytest -m integration -v
```
