import { Container, Paper, Typography, Box, Avatar } from '@mui/material';
import { Person } from '@mui/icons-material';

export default function ProfilePage() {
  const user = JSON.parse(localStorage.getItem('user') || '{}');

  return (
    <Container maxWidth="sm" sx={{ py: 4 }}>
      <Paper sx={{ p: 4 }}>
        <Box sx={{ display: 'flex', flexDirection: 'column', alignItems: 'center', mb: 3 }}>
          <Avatar sx={{ width: 64, height: 64, mb: 2, bgcolor: 'primary.main' }}>
            <Person fontSize="large" />
          </Avatar>
          <Typography variant="h5">{user.name}</Typography>
        </Box>
        <Box sx={{ display: 'flex', flexDirection: 'column', gap: 1 }}>
          <Typography variant="body1">
            <strong>Name:</strong> {user.name}
          </Typography>
          <Typography variant="body1">
            <strong>Email:</strong> {user.email}
          </Typography>
          <Typography variant="body2" color="text.secondary">
            <strong>User ID:</strong> {user.user_id}
          </Typography>
        </Box>
      </Paper>
    </Container>
  );
}
