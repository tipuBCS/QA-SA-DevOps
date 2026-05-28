import { useState } from 'react';
import {
  Container,
  Typography,
  TextField,
  Button,
  Box,
  Paper,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  IconButton,
  Chip,
} from '@mui/material';
import { Delete } from '@mui/icons-material';
import { mockRooms } from '../data/mockData';
import type { Room } from '../types';

export default function AdminPage() {
  const [rooms, setRooms] = useState<Room[]>(mockRooms);
  const [newRoom, setNewRoom] = useState({
    name: '',
    capacity: '',
    location: '',
    amenities: '',
  });

  const handleAddRoom = () => {
    if (!newRoom.name || !newRoom.capacity || !newRoom.location) return;

    const room: Room = {
      id: Date.now().toString(),
      name: newRoom.name,
      capacity: parseInt(newRoom.capacity),
      location: newRoom.location,
      amenities: newRoom.amenities.split(',').map((a) => a.trim()).filter(Boolean),
    };

    setRooms([...rooms, room]);
    setNewRoom({ name: '', capacity: '', location: '', amenities: '' });
  };

  const handleDeleteRoom = (id: string) => {
    setRooms(rooms.filter((r) => r.id !== id));
  };

  return (
    <Container sx={{ py: 4 }}>
      <Typography variant="h4" gutterBottom>
        Admin - Manage Rooms
      </Typography>

      <Paper sx={{ p: 3, mb: 4 }}>
        <Typography variant="h6" gutterBottom>
          Add New Room
        </Typography>
        <Box sx={{ display: 'flex', flexDirection: 'column', gap: 2, maxWidth: 500 }}>
          <TextField
            label="Room Name"
            value={newRoom.name}
            onChange={(e) => setNewRoom({ ...newRoom, name: e.target.value })}
          />
          <TextField
            label="Capacity"
            type="number"
            value={newRoom.capacity}
            onChange={(e) => setNewRoom({ ...newRoom, capacity: e.target.value })}
          />
          <TextField
            label="Location"
            value={newRoom.location}
            onChange={(e) => setNewRoom({ ...newRoom, location: e.target.value })}
          />
          <TextField
            label="Amenities (comma-separated)"
            value={newRoom.amenities}
            onChange={(e) => setNewRoom({ ...newRoom, amenities: e.target.value })}
            placeholder="Projector, Whiteboard, TV Screen"
          />
          <Button variant="contained" onClick={handleAddRoom} sx={{ alignSelf: 'flex-start' }}>
            Add Room
          </Button>
        </Box>
      </Paper>

      <Typography variant="h6" gutterBottom>
        Existing Rooms
      </Typography>
      <TableContainer component={Paper}>
        <Table>
          <TableHead>
            <TableRow>
              <TableCell>Name</TableCell>
              <TableCell>Capacity</TableCell>
              <TableCell>Location</TableCell>
              <TableCell>Amenities</TableCell>
              <TableCell>Actions</TableCell>
            </TableRow>
          </TableHead>
          <TableBody>
            {rooms.map((room) => (
              <TableRow key={room.id}>
                <TableCell>{room.name}</TableCell>
                <TableCell>{room.capacity}</TableCell>
                <TableCell>{room.location}</TableCell>
                <TableCell>
                  <Box sx={{ display: 'flex', flexWrap: 'wrap', gap: 0.5 }}>
                    {room.amenities.map((a) => (
                      <Chip key={a} label={a} size="small" />
                    ))}
                  </Box>
                </TableCell>
                <TableCell>
                  <IconButton
                    size="small"
                    color="error"
                    onClick={() => handleDeleteRoom(room.id)}
                    aria-label="Delete room"
                  >
                    <Delete />
                  </IconButton>
                </TableCell>
              </TableRow>
            ))}
          </TableBody>
        </Table>
      </TableContainer>
    </Container>
  );
}
