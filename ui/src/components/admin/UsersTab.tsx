import { useState, useEffect } from 'react';
import {
  Typography,
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
  TextField,
  Chip,
} from '@mui/material';
import { Delete } from '@mui/icons-material';
import { apiRequest } from '../../api';
import { getCurrentUser } from '../../types';

interface UserData {
  user_id: string;
  email: string;
  name: string;
  is_admin: boolean;
  access_level: number;
  access_level_name: string;
}

const ACCESS_LEVELS = [
  { value: 1, label: 'Employee' },
  { value: 2, label: 'Manager' },
  { value: 3, label: 'Director' },
  { value: 4, label: 'Executive' },
];

export default function UsersTab() {
  const [users, setUsers] = useState<UserData[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [success, setSuccess] = useState('');

  const currentUser = getCurrentUser();

  const fetchUsers = async () => {
    try {
      const res = await apiRequest('/users/');
      if (res.ok) {
        const data = await res.json();
        setUsers(data.users || []);
      } else {
        setError('Failed to load users');
      }
    } catch {
      setError('Failed to connect to server');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchUsers();
  }, []);

  const handleAccessLevelChange = async (userId: string, newLevel: number) => {
    setError('');
    try {
      const res = await apiRequest(`/users/${userId}`, {
        method: 'PATCH',
        body: JSON.stringify({ access_level: newLevel }),
      });

      if (res.ok) {
        setSuccess('Access level updated');
        fetchUsers();
      } else {
        const data = await res.json();
        setError(data.error || 'Failed to update user');
      }
    } catch {
      setError('Failed to connect to server');
    }
  };

  const handleDelete = async (userId: string) => {
    if (!confirm('Are you sure you want to delete this user? This cannot be undone.')) return;

    try {
      const res = await apiRequest(`/users/${userId}`, { method: 'DELETE' });
      if (res.ok) {
        setSuccess('User deleted');
        fetchUsers();
      } else {
        const data = await res.json();
        setError(data.error || 'Failed to delete user');
      }
    } catch {
      setError('Failed to connect to server');
    }
  };

  return (
    <>
      {error && (
        <Alert severity="error" sx={{ mb: 2 }} onClose={() => setError('')}>
          {error}
        </Alert>
      )}

      <Typography variant="h6" gutterBottom>
        All Users
      </Typography>

      {loading ? (
        <Typography color="text.secondary">Loading...</Typography>
      ) : users.length === 0 ? (
        <Typography color="text.secondary">No users found.</Typography>
      ) : (
        <TableContainer component={Paper}>
          <Table>
            <TableHead>
              <TableRow>
                <TableCell>Name</TableCell>
                <TableCell>Email</TableCell>
                <TableCell>Role</TableCell>
                <TableCell>Access Level</TableCell>
                <TableCell>Actions</TableCell>
              </TableRow>
            </TableHead>
            <TableBody>
              {users.map((user) => (
                <TableRow key={user.user_id}>
                  <TableCell>{user.name}</TableCell>
                  <TableCell>{user.email}</TableCell>
                  <TableCell>
                    <Chip
                      label={user.is_admin ? 'Admin' : 'User'}
                      color={user.is_admin ? 'primary' : 'default'}
                      size="small"
                    />
                  </TableCell>
                  <TableCell>
                    <TextField
                      select
                      size="small"
                      value={user.access_level}
                      onChange={(e) => handleAccessLevelChange(user.user_id, parseInt(e.target.value))}
                      sx={{ minWidth: 140 }}
                    >
                      {ACCESS_LEVELS.map((level) => (
                        <MenuItem key={level.value} value={level.value}>
                          {level.label}
                        </MenuItem>
                      ))}
                    </TextField>
                  </TableCell>
                  <TableCell>
                    <IconButton
                      size="small"
                      color="error"
                      onClick={() => handleDelete(user.user_id)}
                      disabled={user.user_id === currentUser?.user_id}
                      aria-label="Delete user"
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
