import { useState, useEffect } from 'react';
import {
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
  Alert,
  Snackbar,
  MenuItem,
  Chip,
  Divider,
} from '@mui/material';
import { Delete } from '@mui/icons-material';
import { apiRequest } from '../../api';
import type { Building, RoomType } from '../../types';

interface RoomData {
  room_id: string;
  building_id: string;
  building_name: string;
  floor: number;
  name: string;
  capacity: number;
  min_access_level: number;
  min_access_level_name: string;
  room_type_id: string;
  room_type_name: string;
  amenities: string[];
}

const ACCESS_LEVELS = [
  { value: 1, label: 'Employee' },
  { value: 2, label: 'Manager' },
  { value: 3, label: 'Director' },
  { value: 4, label: 'Executive' },
];

export default function RoomsTab() {
  const [rooms, setRooms] = useState<RoomData[]>([]);
  const [buildings, setBuildings] = useState<Building[]>([]);
  const [roomTypes, setRoomTypes] = useState<RoomType[]>([]);
  const [selectedBuildingId, setSelectedBuildingId] = useState('');
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [success, setSuccess] = useState('');
  const [form, setForm] = useState({
    floor: '',
    name: '',
    capacity: '',
    min_access_level: '1',
    room_type_id: '',
    amenities: '',
  });

  const fetchBuildings = async () => {
    try {
      const res = await apiRequest('/buildings/');
      if (res.ok) {
        const data = await res.json();
        setBuildings(data.buildings || []);
      } else {
        setError('Failed to load buildings');
      }
    } catch {
      setError('Failed to connect to server');
    }
  };

  const fetchRooms = async () => {
    if (!selectedBuildingId) {
      setRooms([]);
      setLoading(false);
      return;
    }
    setLoading(true);
    try {
      const res = await apiRequest(`/buildings/${selectedBuildingId}/rooms`);
      if (res.ok) {
        const data = await res.json();
        setRooms(data.rooms || []);
      } else {
        setError('Failed to load rooms');
      }
    } catch {
      setError('Failed to connect to server');
    } finally {
      setLoading(false);
    }
  };

  const fetchRoomTypes = async () => {
    try {
      const res = await apiRequest('/room-types/');
      if (res.ok) {
        const data = await res.json();
        setRoomTypes(data.room_types || []);
      }
    } catch {
      // Non-critical
    }
  };

  useEffect(() => {
    fetchBuildings();
    fetchRoomTypes();
  }, []);

  useEffect(() => {
    fetchRooms();
  }, [selectedBuildingId]);

  const selectedBuilding = buildings.find((b) => b.building_id === selectedBuildingId);
  const maxFloors = selectedBuilding?.num_floors || 1;

  // Group rooms by floor
  const roomsByFloor = rooms.reduce<Record<number, RoomData[]>>((acc, room) => {
    if (!acc[room.floor]) acc[room.floor] = [];
    acc[room.floor].push(room);
    return acc;
  }, {});
  const sortedFloors = Object.keys(roomsByFloor).map(Number).sort((a, b) => a - b);

  const handleCreate = async (e: React.FormEvent) => {
    e.preventDefault();
    setError('');

    if (!selectedBuildingId || !form.floor || !form.name || !form.capacity) {
      setError('Building, floor, name, and capacity are required');
      return;
    }

    try {
      const res = await apiRequest(`/buildings/${selectedBuildingId}/rooms`, {
        method: 'POST',
        body: JSON.stringify({
          floor: parseInt(form.floor),
          name: form.name,
          capacity: parseInt(form.capacity),
          min_access_level: parseInt(form.min_access_level),
          room_type_id: form.room_type_id || '',
          amenities: form.amenities.split(',').map((a) => a.trim()).filter(Boolean),
        }),
      });

      if (res.ok) {
        setSuccess('Room created successfully');
        setForm({ floor: '', name: '', capacity: '', min_access_level: '1', room_type_id: '', amenities: '' });
        fetchRooms();
      } else {
        const data = await res.json();
        setError(data.error || 'Failed to create room');
      }
    } catch {
      setError('Failed to connect to server');
    }
  };

  const handleDelete = async (roomId: string) => {
    if (!confirm('Are you sure you want to delete this room?')) return;

    try {
      const res = await apiRequest(`/buildings/${selectedBuildingId}/rooms/${roomId}`, { method: 'DELETE' });
      if (res.ok) {
        setSuccess('Room deleted successfully');
        fetchRooms();
      } else {
        const data = await res.json();
        setError(data.error || 'Failed to delete room');
      }
    } catch {
      setError('Failed to connect to server');
    }
  };

  return (
    <>
      {/* Building selector */}
      <Paper sx={{ p: 3, mb: 4 }}>
        <Typography variant="h6" gutterBottom>
          Select a Building
        </Typography>
        <TextField
          select
          fullWidth
          label="Building"
          value={selectedBuildingId}
          onChange={(e) => setSelectedBuildingId(e.target.value)}
          sx={{ maxWidth: 400 }}
        >
          {buildings.map((b) => (
            <MenuItem key={b.building_id} value={b.building_id}>
              {b.name} ({b.num_floors} floors)
            </MenuItem>
          ))}
        </TextField>
      </Paper>

      {!selectedBuildingId ? (
        <Typography color="text.secondary" sx={{ textAlign: 'center', mt: 4 }}>
          Please select a building above to manage its rooms.
        </Typography>
      ) : (
        <>
          {error && (
            <Alert severity="error" sx={{ mb: 2 }} onClose={() => setError('')}>
              {error}
            </Alert>
          )}

          {/* Add room form */}
          <Paper sx={{ p: 3, mb: 4 }}>
            <Typography variant="h6" gutterBottom>
              Add Room to {selectedBuilding?.name}
            </Typography>
            <Box component="form" onSubmit={handleCreate} sx={{ display: 'flex', flexDirection: 'column', gap: 2, maxWidth: 500 }}>
              <TextField
                label="Floor"
                type="number"
                value={form.floor}
                onChange={(e) => setForm({ ...form, floor: e.target.value })}
                required
                slotProps={{ htmlInput: { min: 1, max: maxFloors } }}
                helperText={`Building has ${maxFloors} floor(s)`}
              />
              <TextField
                label="Room Name"
                value={form.name}
                onChange={(e) => setForm({ ...form, name: e.target.value })}
                required
              />
              <TextField
                label="Capacity"
                type="number"
                value={form.capacity}
                onChange={(e) => setForm({ ...form, capacity: e.target.value })}
                required
                slotProps={{ htmlInput: { min: 1 } }}
              />
              <TextField
                select
                label="Minimum Access Level"
                value={form.min_access_level}
                onChange={(e) => setForm({ ...form, min_access_level: e.target.value })}
              >
                {ACCESS_LEVELS.map((level) => (
                  <MenuItem key={level.value} value={level.value.toString()}>{level.label}</MenuItem>
                ))}
              </TextField>
              <TextField
                select
                label="Room Type (optional)"
                value={form.room_type_id}
                onChange={(e) => setForm({ ...form, room_type_id: e.target.value })}
              >
                <MenuItem value="">None</MenuItem>
                {roomTypes.map((rt) => (
                  <MenuItem key={rt.room_type_id} value={rt.room_type_id}>{rt.name}</MenuItem>
                ))}
              </TextField>
              <TextField
                label="Amenities (comma-separated)"
                value={form.amenities}
                onChange={(e) => setForm({ ...form, amenities: e.target.value })}
                placeholder="Projector, Whiteboard, TV Screen"
              />
              <Button type="submit" variant="contained" sx={{ alignSelf: 'flex-start' }}>
                Add Room
              </Button>
            </Box>
          </Paper>

          {/* Rooms list grouped by floor */}
          <Typography variant="h6" gutterBottom>
            Rooms in {selectedBuilding?.name}
          </Typography>

          {loading ? (
            <Typography color="text.secondary">Loading...</Typography>
          ) : rooms.length === 0 ? (
            <Typography color="text.secondary">No rooms in this building yet.</Typography>
          ) : (
            sortedFloors.map((floor) => (
              <Box key={floor} sx={{ mb: 3 }}>
                <Typography variant="subtitle1" sx={{ fontWeight: 500, mb: 1 }}>
                  Floor {floor}
                </Typography>
                <TableContainer component={Paper} variant="outlined">
                  <Table size="small">
                    <TableHead>
                      <TableRow>
                        <TableCell>Name</TableCell>
                        <TableCell>Capacity</TableCell>
                        <TableCell>Access Level</TableCell>
                        <TableCell>Type</TableCell>
                        <TableCell>Amenities</TableCell>
                        <TableCell>Actions</TableCell>
                      </TableRow>
                    </TableHead>
                    <TableBody>
                      {roomsByFloor[floor].map((room) => (
                        <TableRow key={room.room_id}>
                          <TableCell>{room.name}</TableCell>
                          <TableCell>{room.capacity}</TableCell>
                          <TableCell>{room.min_access_level_name}</TableCell>
                          <TableCell>{room.room_type_name || '—'}</TableCell>
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
                              onClick={() => handleDelete(room.room_id)}
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
                <Divider sx={{ mt: 2 }} />
              </Box>
            ))
          )}
        </>
      )}

      <Snackbar
        open={!!success}
        autoHideDuration={3000}
        onClose={() => setSuccess('')}
        message={success}
      />
    </>
  );
}
