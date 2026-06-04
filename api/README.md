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
│   ├── room_type.py     # CreateRoomTypeRequest
│   └── booking.py       # BookRoomRequest
├── typings/
│   ├── user.py          # UserItem, User TypedDicts
│   ├── building.py      # BuildingItem, Building TypedDicts
│   ├── room.py          # RoomItem, Room TypedDicts
│   ├── room_type.py     # RoomTypeItem, RoomType TypedDicts
│   └── booking.py       # BookingItem, Booking TypedDicts
├── services/
│   ├── user_service.py      # User CRUD + auth
│   ├── building_service.py  # Building CRUD
│   ├── room_service.py      # Room CRUD (validates building/floor)
│   ├── room_type_service.py # Room type CRUD
│   └── booking_service.py   # Booking operations (checks access level)
├── routes/
│   ├── users.py         # /users/*
│   ├── buildings.py     # /buildings/, /buildings/<id>
│   ├── rooms.py         # /buildings/<id>/rooms/*, booking creation
│   ├── room_types.py    # /room-types/*
│   └── bookings.py      # /bookings/* (cancel, list)
├── tests/
│   ├── test_user_service.py
│   ├── test_building_service.py
│   ├── test_room_service.py
│   ├── test_room_type_service.py
│   ├── test_booking_service.py
│   └── integration/
│       ├── test_users_api.py
│       ├── test_buildings_api.py
│       ├── test_rooms_api.py
│       ├── test_room_types_api.py
│       └── test_bookings_api.py
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
- `POST /buildings/<id>/rooms/<room_id>/book` — Book a room

### Room Types (admin only for create/delete)
- `POST /room-types/` — Create a room type
- `GET /room-types/` — List all room types
- `GET /room-types/<id>` — Get a room type
- `DELETE /room-types/<id>` — Delete a room type

### Bookings (authenticated)
- `DELETE /bookings/<booking_id>` — Cancel a booking
- `GET /bookings/user/<user_id>` — List bookings for a user

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

## Deployment

To deploy the service, run the following from the `infra/` directory:

```bash
npm run deploy
```

Or target specific stacks:
```bash
./deploy.sh api        # Deploy only the API stack
./deploy.sh frontend   # Deploy only the Frontend stack
./deploy.sh all        # Deploy everything (default)
```

Prerequisite: bootstrap the environment first if not already done:
```bash
npx cdk bootstrap --profile {AWS_PROFILE}
```
