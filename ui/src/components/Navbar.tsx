import { useState } from 'react';
import {
  AppBar,
  Toolbar,
  Typography,
  Button,
  Box,
  IconButton,
  Menu,
  MenuItem,
  ListItemIcon,
  ListItemText,
} from '@mui/material';
import { MeetingRoom, AccountCircle, Person, Logout } from '@mui/icons-material';
import { useNavigate, useLocation } from 'react-router-dom';

export default function Navbar() {
  const navigate = useNavigate();
  const location = useLocation();
  const [anchorEl, setAnchorEl] = useState<null | HTMLElement>(null);

  const user = JSON.parse(localStorage.getItem('user') || 'null');
  const isActive = (path: string) => location.pathname === path;

  const handleSignOut = () => {
    localStorage.removeItem('user');
    setAnchorEl(null);
    navigate('/login');
  };

  return (
    <AppBar position="static">
      <Toolbar>
        <MeetingRoom sx={{ mr: 1 }} />
        <Typography variant="h6" sx={{ flexGrow: 1, cursor: 'pointer' }} onClick={() => navigate('/')}>
          Room Booker
        </Typography>
        <Box sx={{ display: 'flex', gap: 1, alignItems: 'center' }}>
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

          {user && (
            <>
              <Typography variant="body2" sx={{ ml: 2 }}>
                {user.name}
              </Typography>
              <IconButton
                color="inherit"
                onClick={(e) => setAnchorEl(e.currentTarget)}
                aria-label="User menu"
              >
                <AccountCircle />
              </IconButton>
              <Menu
                anchorEl={anchorEl}
                open={Boolean(anchorEl)}
                onClose={() => setAnchorEl(null)}
              >
                <MenuItem onClick={() => { setAnchorEl(null); navigate('/profile'); }}>
                  <ListItemIcon><Person fontSize="small" /></ListItemIcon>
                  <ListItemText>Profile</ListItemText>
                </MenuItem>
                <MenuItem onClick={handleSignOut}>
                  <ListItemIcon><Logout fontSize="small" /></ListItemIcon>
                  <ListItemText>Sign Out</ListItemText>
                </MenuItem>
              </Menu>
            </>
          )}
        </Box>
      </Toolbar>
    </AppBar>
  );
}
