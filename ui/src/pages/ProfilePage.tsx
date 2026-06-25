import { Container, Paper, Typography, Box, Avatar, Chip } from '@mui/material';
import { Person, AdminPanelSettings } from '@mui/icons-material';
import { getCurrentUser } from '../types';

export default function ProfilePage() {
  const user = getCurrentUser();

  if (!user) return null;

  return (
    <Container maxWidth="sm" sx={{ py: 4 }}>
      <Paper sx={{ p: 4 }}>
        <Box sx={{ display: 'flex', flexDirection: 'column', alignItems: 'center', mb: 3 }}>
          <Avatar sx={{ width: 64, height: 64, mb: 2, bgcolor: 'primary.main' }}>
            <Person fontSize="large" />
          </Avatar>
          <Typography variant="h5">{user.name}</Typography>
          {user.is_admin && (
            <Chip
              icon={<AdminPanelSettings />}
              label="Administrator"
              color="primary"
              size="small"
              sx={{ mt: 1 }}
            />
          )}
        </Box>
        <Box sx={{ display: 'flex', flexDirection: 'column', gap: 2 }}>
          <Box>
            <Typography variant="caption" color="text.secondary">Name</Typography>
            <Typography variant="body1">{user.name}</Typography>
          </Box>
          <Box>
            <Typography variant="caption" color="text.secondary">Email</Typography>
            <Typography variant="body1">{user.email}</Typography>
          </Box>
          <Box>
            <Typography variant="caption" color="text.secondary">Access Level</Typography>
            <Typography variant="body1">{user.access_level_name} (Level {user.access_level})</Typography>
          </Box>
          <Box>
            <Typography variant="caption" color="text.secondary">Role</Typography>
            <Typography variant="body1">{user.is_admin ? 'Admin' : 'User'}</Typography>
          </Box>
          <Box>
            <Typography variant="caption" color="text.secondary">User ID</Typography>
            <Typography variant="body2" color="text.secondary">{user.user_id}</Typography>
          </Box>
        </Box>
      </Paper>
    </Container>
  );
}
