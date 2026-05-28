import { useState } from 'react';
import {
  Container,
  Typography,
  Grid,
  Card,
  CardContent,
  CardActions,
  Button,
  Chip,
  Box,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  TextField,
} from '@mui/material';
import { People, LocationOn } from '@mui/icons-material';
import { mockRooms } from '../data/mockData';
import type { Room } from '../types';

export default function RoomsPage() {
  const [rooms] = useState<Room[]>(mockRooms);
  const [bookingDialog, setBookingDialog] = useState(false);
  const [selectedRoom, setSelectedRoom] = useState<Room | null>(null);
  const [bookingForm, setBookingForm] = useState({
    date: '',
    startTime: '',
    endTime: '',
    purpose: '',
  });

  const handleBookClick = (room: Room) => {
    setSelectedRoom(room);
    setBookingDialog(true);
  };

  const handleBookingSubmit = () => {
    // TODO: Submit booking to API
    alert(`Booked ${selectedRoom?.name} on ${bookingForm.date} from ${bookingForm.startTime} to ${bookingForm.endTime}`);
    setBookingDialog(false);
    setBookingForm({ date: '', startTime: '', endTime: '', purpose: '' });
  };

  return (
    <Container sx={{ py: 4 }}>
      <Typography variant="h4" gutterBottom>
        Available Rooms
      </Typography>
      <Grid container spacing={3}>
        {rooms.map((room) => (
          <Grid size={{ xs: 12, sm: 6, md: 4 }} key={room.id}>
            <Card sx={{ height: '100%', display: 'flex', flexDirection: 'column' }}>
              <CardContent sx={{ flexGrow: 1 }}>
                <Typography variant="h6" gutterBottom>
                  {room.name}
                </Typography>
                <Box sx={{ display: 'flex', alignItems: 'center', mb: 1 }}>
                  <People sx={{ mr: 0.5, fontSize: 20 }} />
                  <Typography variant="body2" color="text.secondary">
                    Capacity: {room.capacity}
                  </Typography>
                </Box>
                <Box sx={{ display: 'flex', alignItems: 'center', mb: 2 }}>
                  <LocationOn sx={{ mr: 0.5, fontSize: 20 }} />
                  <Typography variant="body2" color="text.secondary">
                    {room.location}
                  </Typography>
                </Box>
                <Box sx={{ display: 'flex', flexWrap: 'wrap', gap: 0.5 }}>
                  {room.amenities.map((amenity) => (
                    <Chip key={amenity} label={amenity} size="small" variant="outlined" />
                  ))}
                </Box>
              </CardContent>
              <CardActions>
                <Button size="small" variant="contained" onClick={() => handleBookClick(room)}>
                  Book Room
                </Button>
              </CardActions>
            </Card>
          </Grid>
        ))}
      </Grid>

      <Dialog open={bookingDialog} onClose={() => setBookingDialog(false)} maxWidth="sm" fullWidth>
        <DialogTitle>Book {selectedRoom?.name}</DialogTitle>
        <DialogContent>
          <Box sx={{ display: 'flex', flexDirection: 'column', gap: 2, mt: 1 }}>
            <TextField
              label="Date"
              type="date"
              value={bookingForm.date}
              onChange={(e) => setBookingForm({ ...bookingForm, date: e.target.value })}
              slotProps={{ inputLabel: { shrink: true } }}
            />
            <TextField
              label="Start Time"
              type="time"
              value={bookingForm.startTime}
              onChange={(e) => setBookingForm({ ...bookingForm, startTime: e.target.value })}
              slotProps={{ inputLabel: { shrink: true } }}
            />
            <TextField
              label="End Time"
              type="time"
              value={bookingForm.endTime}
              onChange={(e) => setBookingForm({ ...bookingForm, endTime: e.target.value })}
              slotProps={{ inputLabel: { shrink: true } }}
            />
            <TextField
              label="Purpose"
              value={bookingForm.purpose}
              onChange={(e) => setBookingForm({ ...bookingForm, purpose: e.target.value })}
              multiline
              rows={2}
            />
          </Box>
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setBookingDialog(false)}>Cancel</Button>
          <Button onClick={handleBookingSubmit} variant="contained">
            Confirm Booking
          </Button>
        </DialogActions>
      </Dialog>
    </Container>
  );
}
