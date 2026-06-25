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
import type { Building } from '../../types';

export default function BuildingsTab() {
  const [buildings, setBuildings] = useState<Building[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [success, setSuccess] = useState('');
  const [form, setForm] = useState({ name: '', address: '', num_floors: '' });

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
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchBuildings();
  }, []);

  const handleCreate = async (e: React.FormEvent) => {
    e.preventDefault();
    setError('');

    if (!form.name || !form.address || !form.num_floors) {
      setError('All fields are required');
      return;
    }

    try {
      const res = await apiRequest('/buildings/', {
        method: 'POST',
        body: JSON.stringify({
          name: form.name,
          address: form.address,
          num_floors: parseInt(form.num_floors),
        }),
      });

      if (res.ok) {
        setSuccess('Building created successfully');
        setForm({ name: '', address: '', num_floors: '' });
        fetchBuildings();
      } else {
        const data = await res.json();
        setError(data.error || 'Failed to create building');
      }
    } catch {
      setError('Failed to connect to server');
    }
  };

  const handleDelete = async (buildingId: string) => {
    if (!confirm('Are you sure you want to delete this building?')) return;

    try {
      const res = await apiRequest(`/buildings/${buildingId}`, { method: 'DELETE' });
      if (res.ok) {
        setSuccess('Building deleted successfully');
        fetchBuildings();
      } else {
        const data = await res.json();
        setError(data.error || 'Failed to delete building');
      }
    } catch {
      setError('Failed to connect to server');
    }
  };

  return (
    <>
      <Paper sx={{ p: 3, mb: 4 }}>
        <Typography variant="h6" gutterBottom>
          Add New Building
        </Typography>
        <Box component="form" onSubmit={handleCreate} sx={{ display: 'flex', flexDirection: 'column', gap: 2, maxWidth: 500 }}>
          <TextField
            label="Building Name"
            value={form.name}
            onChange={(e) => setForm({ ...form, name: e.target.value })}
            required
          />
          <TextField
            label="Address"
            value={form.address}
            onChange={(e) => setForm({ ...form, address: e.target.value })}
            required
          />
          <TextField
            label="Number of Floors"
            type="number"
            value={form.num_floors}
            onChange={(e) => setForm({ ...form, num_floors: e.target.value })}
            required
            slotProps={{ htmlInput: { min: 1 } }}
          />
          <Button type="submit" variant="contained" sx={{ alignSelf: 'flex-start' }}>
            Add Building
          </Button>
        </Box>
      </Paper>

      {error && (
        <Alert severity="error" sx={{ mb: 2 }} onClose={() => setError('')}>
          {error}
        </Alert>
      )}

      <Typography variant="h6" gutterBottom>
        Existing Buildings
      </Typography>

      {loading ? (
        <Typography color="text.secondary">Loading...</Typography>
      ) : buildings.length === 0 ? (
        <Typography color="text.secondary">No buildings yet. Create one above.</Typography>
      ) : (
        <TableContainer component={Paper}>
          <Table>
            <TableHead>
              <TableRow>
                <TableCell>Name</TableCell>
                <TableCell>Address</TableCell>
                <TableCell>Floors</TableCell>
                <TableCell>Actions</TableCell>
              </TableRow>
            </TableHead>
            <TableBody>
              {buildings.map((building) => (
                <TableRow key={building.building_id}>
                  <TableCell>{building.name}</TableCell>
                  <TableCell>{building.address}</TableCell>
                  <TableCell>{building.num_floors}</TableCell>
                  <TableCell>
                    <IconButton
                      size="small"
                      color="error"
                      onClick={() => handleDelete(building.building_id)}
                      aria-label="Delete building"
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
