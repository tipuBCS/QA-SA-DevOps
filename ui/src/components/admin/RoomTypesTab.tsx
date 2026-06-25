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
} from '@mui/material';
import { Delete } from '@mui/icons-material';
import { apiRequest } from '../../api';
import type { RoomType } from '../../types';

export default function RoomTypesTab() {
  const [roomTypes, setRoomTypes] = useState<RoomType[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [success, setSuccess] = useState('');
  const [form, setForm] = useState({ name: '', description: '' });

  const fetchRoomTypes = async () => {
    try {
      const res = await apiRequest('/room-types/');
      if (res.ok) {
        const data = await res.json();
        setRoomTypes(data.room_types || []);
      } else {
        setError('Failed to load room types');
      }
    } catch {
      setError('Failed to connect to server');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchRoomTypes();
  }, []);

  const handleCreate = async (e: React.FormEvent) => {
    e.preventDefault();
    setError('');

    if (!form.name) {
      setError('Name is required');
      return;
    }

    try {
      const res = await apiRequest('/room-types/', {
        method: 'POST',
        body: JSON.stringify({
          name: form.name,
          description: form.description,
        }),
      });

      if (res.ok) {
        setSuccess('Room type created successfully');
        setForm({ name: '', description: '' });
        fetchRoomTypes();
      } else {
        const data = await res.json();
        setError(data.error || 'Failed to create room type');
      }
    } catch {
      setError('Failed to connect to server');
    }
  };

  const handleDelete = async (roomTypeId: string) => {
    if (!confirm('Are you sure you want to delete this room type?')) return;

    try {
      const res = await apiRequest(`/room-types/${roomTypeId}`, { method: 'DELETE' });
      if (res.ok) {
        setSuccess('Room type deleted successfully');
        fetchRoomTypes();
      } else {
        const data = await res.json();
        setError(data.error || 'Failed to delete room type');
      }
    } catch {
      setError('Failed to connect to server');
    }
  };

  return (
    <>
      <Paper sx={{ p: 3, mb: 4 }}>
        <Typography variant="h6" gutterBottom>
          Add New Room Type
        </Typography>
        <Box component="form" onSubmit={handleCreate} sx={{ display: 'flex', flexDirection: 'column', gap: 2, maxWidth: 500 }}>
          <TextField
            label="Room Type Name"
            value={form.name}
            onChange={(e) => setForm({ ...form, name: e.target.value })}
            required
            placeholder="e.g. Conference Room, Huddle Space"
          />
          <TextField
            label="Description"
            value={form.description}
            onChange={(e) => setForm({ ...form, description: e.target.value })}
            multiline
            rows={2}
            placeholder="Optional description"
          />
          <Button type="submit" variant="contained" sx={{ alignSelf: 'flex-start' }}>
            Add Room Type
          </Button>
        </Box>
      </Paper>

      {error && (
        <Alert severity="error" sx={{ mb: 2 }} onClose={() => setError('')}>
          {error}
        </Alert>
      )}

      <Typography variant="h6" gutterBottom>
        Existing Room Types
      </Typography>

      {loading ? (
        <Typography color="text.secondary">Loading...</Typography>
      ) : roomTypes.length === 0 ? (
        <Typography color="text.secondary">No room types yet. Create one above.</Typography>
      ) : (
        <TableContainer component={Paper}>
          <Table>
            <TableHead>
              <TableRow>
                <TableCell>Name</TableCell>
                <TableCell>Description</TableCell>
                <TableCell>Actions</TableCell>
              </TableRow>
            </TableHead>
            <TableBody>
              {roomTypes.map((rt) => (
                <TableRow key={rt.room_type_id}>
                  <TableCell>{rt.name}</TableCell>
                  <TableCell>{rt.description || '—'}</TableCell>
                  <TableCell>
                    <IconButton
                      size="small"
                      color="error"
                      onClick={() => handleDelete(rt.room_type_id)}
                      aria-label="Delete room type"
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
