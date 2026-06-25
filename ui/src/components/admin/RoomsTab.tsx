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
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [success, setSuccess] = useState('');
  const [form, setForm] = useState({
    building_id: '',
    floor: '',
    name: '',
    capacity: '',
    min_access_level: '1',
    room_type_id: '',
    amenities: '',
  });

  const fetchRooms = async () => {
    try {
      const buildingsRes = await apiRequest('/buildings/');
      if (!buildingsRes.ok) {
        setError('Failed to load buildings');
        return;
      }
      const buildingsData = await buildingsRes.json();
      const allBuildings: Building[] = buildingsData.buildings || [];
      setBuildings(allBuildings);

      const allRooms: RoomData[] = [];
      for (const building of allBuildings) {
        const roomsRes = await apiRequest(`/buildings/${building.building_id}/rooms`);
        if (roomsRes.ok) {
          const roomsData = await roomsRes.json();
          allRooms.push(...(roomsData.rooms || []));
        }
      }
      setRooms(allRooms);
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
      // Non-critical, room type is optional
    }
  };

  useEffect(() => {
    fetchRooms();
    fetchRoomTypes();
  }, []);

  const selectedBuilding = buildings.find((b) => b.building_id === form.building_id);
  const maxFloors = selectedBuilding?.num_floors || 1;

  const handleCreate = async (e: React.FormEvent) => {
    e.preventDefault();
    setError('');

    if (!form.building_id || !form.floor || !form.name || !form.capacity) {
      setError('Building, floor, name, and capacity are required');
      return;
    }

    try {
      const res = await apiRequest(`/buildings/${form.building_id}/rooms`, {
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
        setForm({ building_id: '', floor: '', name: '', capacity: '', min_access_level: '1', room_type_id: '', amenities: '' });
        fetchRooms();
      } else {
        const data = await res.json();
        setError(data.error || 'Failed to create room');
      }
    } catch {
      setError('Failed to connect to server');
    }
  };

  const handleDelete = async (buildingId: string, roomId: string) => {
    if (!confirm('Are you sure you want to delete this room?')) return;

    try {
      const res = await apiRequest(`/buildings/${buildingId}/rooms/${roomId}`, { method: 'DELETE' });
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
      <Paper sx={{ p: 3, mb: 4 }}>
        <Typography variant="h6" gutterBottom>
          Add New Room
        </Typography>
        <Box component="form" onSubmit={handleCreate} sx={{ display: 'flex', flexDirection: 'column', gap: 2, maxWidth: 500 }}>
          <TextField
            select
            label="Building"
            value={form.building_id}
            onChange={(e) => setForm({ ...form, building_id: e.target.value, floor: '' })}
            required
          >
            {buildings.map((b) => (
              <MenuItem key={b.building_id} value={b.building_id}>{b.name}</MenuItem>
            ))}
          </TextField>
          <TextField
            label="Floor"
            type="number"
            value={form.floor}
            onChange={(e) => setForm({ ...form, floor: e.target.value })}
            required
            slotProps={{ htmlInput: { min: 1, max: maxFloors } }}
            helperText={selectedBuilding ? `Building has ${maxFloors} floor(s)` : ''}
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

      {error && (
        <Alert severity="error" sx={{ mb: 2 }} onClose={() => setError('')}>
          {error}
        </Alert>
      )}

      <Typography variant="h6" gutterBottom>
        Existing Rooms
      </Typography>

      {loading ? (
        <Typography color="text.secondary">Loading...</Typography>
      ) : rooms.length === 0 ? (
        <Typography color="text.secondary">No rooms yet. Create one above.</Typography>
      ) : (
        <TableContainer component={Paper}>
          <Table>
            <TableHead>
              <TableRow>
                <TableCell>Name</TableCell>
                <TableCell>Building</TableCell>
                <TableCell>Floor</TableCell>
                <TableCell>Capacity</TableCell>
                <TableCell>Access Level</TableCell>
                <TableCell>Type</TableCell>
                <TableCell>Amenities</TableCell>
                <TableCell>Actions</TableCell>
              </TableRow>
            </TableHead>
            <TableBody>
              {rooms.map((room) => (
                <TableRow key={room.room_id}>
                  <TableCell>{room.name}</TableCell>
                  <TableCell>{room.building_name}</TableCell>
                  <TableCell>{room.floor}</TableCell>
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
                      onClick={() => handleDelete(room.building_id, room.room_id)}
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
