import { AppBar, Toolbar, Typography, Button, Box } from '@mui/material';
import { MeetingRoom } from '@mui/icons-material';
import { useNavigate, useLocation } from 'react-router-dom';

export default function Navbar() {
  const navigate = useNavigate();
  const location = useLocation();

  const isActive = (path: string) => location.pathname === path;

  return (
    <AppBar position="static">
      <Toolbar>
        <MeetingRoom sx={{ mr: 1 }} />
        <Typography variant="h6" sx={{ flexGrow: 1, cursor: 'pointer' }} onClick={() => navigate('/')}>
          Room Booker
        </Typography>
        <Box sx={{ display: 'flex', gap: 1 }}>
          <Button
            color="inherit"
            onClick={() => navigate('/')}
            variant={isActive('/') ? 'outlined' : 'text'}
          >
            Rooms
          </Button>
          <Button
            color="inherit"
            onClick={() => navigate('/bookings')}
            variant={isActive('/bookings') ? 'outlined' : 'text'}
          >
            My Bookings
          </Button>
          <Button
            color="inherit"
            onClick={() => navigate('/admin')}
            variant={isActive('/admin') ? 'outlined' : 'text'}
          >
            Admin
          </Button>
        </Box>
      </Toolbar>
    </AppBar>
  );
}
