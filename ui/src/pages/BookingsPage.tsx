import { useState } from 'react';
import {
  Container,
  Typography,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  Paper,
  IconButton,
  Chip,
} from '@mui/material';
import { Delete } from '@mui/icons-material';
import { mockBookings } from '../data/mockData';
import type { Booking } from '../types';

export default function BookingsPage() {
  const [bookings, setBookings] = useState<Booking[]>(mockBookings);

  const handleDelete = (id: string) => {
    setBookings(bookings.filter((b) => b.id !== id));
  };

  const isUpcoming = (date: string) => new Date(date) >= new Date();

  return (
    <Container sx={{ py: 4 }}>
      <Typography variant="h4" gutterBottom>
        My Bookings
      </Typography>
      {bookings.length === 0 ? (
        <Typography color="text.secondary">No bookings yet.</Typography>
      ) : (
        <TableContainer component={Paper}>
          <Table>
            <TableHead>
              <TableRow>
                <TableCell>Room</TableCell>
                <TableCell>Date</TableCell>
                <TableCell>Time</TableCell>
                <TableCell>Purpose</TableCell>
                <TableCell>Status</TableCell>
                <TableCell>Actions</TableCell>
              </TableRow>
            </TableHead>
            <TableBody>
              {bookings.map((booking) => (
                <TableRow key={booking.id}>
                  <TableCell>{booking.room_id}</TableCell>
                  <TableCell>{booking.date}</TableCell>
                  <TableCell>{booking.start_time} - {booking.end_time}</TableCell>
                  <TableCell>{booking.purpose}</TableCell>
                  <TableCell>
                    <Chip
                      label={isUpcoming(booking.date) ? 'Upcoming' : 'Past'}
                      color={isUpcoming(booking.date) ? 'primary' : 'default'}
                      size="small"
                    />
                  </TableCell>
                  <TableCell>
                    <IconButton
                      size="small"
                      color="error"
                      onClick={() => handleDelete(booking.id)}
                      aria-label="Cancel booking"
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
    </Container>
  );
}
