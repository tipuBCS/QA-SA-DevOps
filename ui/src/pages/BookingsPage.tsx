import { useState, useEffect } from 'react';
import {
  Container,
  Typography,
  Box,
  IconButton,
  Alert,
  Snackbar,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  Button,
  Paper,
  Chip,
} from '@mui/material';
import { ChevronLeft, ChevronRight, Delete } from '@mui/icons-material';
import { apiRequest } from '../api';
import { getCurrentUser } from '../types';

interface BookingData {
  booking_id: string;
  room_id: string;
  room_name: string;
  building_id: string;
  building_name: string;
  floor: number;
  user_id: string;
  date: string;
  start_time: string;
  end_time: string;
  purpose: string;
}

function getWeekDates(baseDate: Date): Date[] {
  const day = baseDate.getDay();
  const monday = new Date(baseDate);
  monday.setDate(baseDate.getDate() - ((day + 6) % 7)); // Monday
  const dates: Date[] = [];
  for (let i = 0; i < 7; i++) {
    const d = new Date(monday);
    d.setDate(monday.getDate() + i);
    dates.push(d);
  }
  return dates;
}

function formatDateKey(date: Date): string {
  return `${date.getFullYear()}-${(date.getMonth() + 1).toString().padStart(2, '0')}-${date.getDate().toString().padStart(2, '0')}`;
}

function formatDayLabel(date: Date): string {
  return date.toLocaleDateString('en-GB', { weekday: 'short', day: 'numeric', month: 'short' });
}

function formatWeekRange(dates: Date[]): string {
  const start = dates[0].toLocaleDateString('en-GB', { day: 'numeric', month: 'short' });
  const end = dates[6].toLocaleDateString('en-GB', { day: 'numeric', month: 'short', year: 'numeric' });
  return `${start} – ${end}`;
}

function formatTime(time: string): string {
  const [h, m] = time.split(':');
  const hour = parseInt(h);
  const ampm = hour >= 12 ? 'PM' : 'AM';
  const displayHour = hour > 12 ? hour - 12 : hour === 0 ? 12 : hour;
  return `${displayHour}:${m} ${ampm}`;
}

export default function BookingsPage() {
  const [bookings, setBookings] = useState<BookingData[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [success, setSuccess] = useState('');
  const [weekBase, setWeekBase] = useState(new Date());
  const [selectedBooking, setSelectedBooking] = useState<BookingData | null>(null);
  const [detailDialog, setDetailDialog] = useState(false);
  const [cancelDialog, setCancelDialog] = useState(false);

  const user = getCurrentUser();
  const weekDates = getWeekDates(weekBase);

  const fetchBookings = async () => {
    if (!user) return;
    try {
      const res = await apiRequest(`/bookings/user/${user.user_id}`);
      if (res.ok) {
        const data = await res.json();
        setBookings(data.bookings || []);
      } else {
        setError('Failed to load bookings');
      }
    } catch {
      setError('Failed to connect to server');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchBookings();
  }, []);

  const handleWeekChange = (offset: number) => {
    const newDate = new Date(weekBase);
    newDate.setDate(weekBase.getDate() + offset * 7);
    setWeekBase(newDate);
  };

  const getBookingsForDate = (date: Date): BookingData[] => {
    const key = formatDateKey(date);
    return bookings
      .filter((b) => b.date === key)
      .sort((a, b) => a.start_time.localeCompare(b.start_time));
  };

  const handleBookingClick = (booking: BookingData) => {
    setSelectedBooking(booking);
    setDetailDialog(true);
  };

  const handleCancelClick = () => {
    setDetailDialog(false);
    setCancelDialog(true);
  };

  const handleCancelConfirm = async () => {
    if (!selectedBooking) return;

    try {
      const res = await apiRequest(`/bookings/${selectedBooking.booking_id}`, {
        method: 'DELETE',
      });

      if (res.ok) {
        setSuccess('Booking cancelled successfully');
        fetchBookings();
      } else {
        const data = await res.json();
        setError(data.error || 'Failed to cancel booking');
      }
    } catch {
      setError('Failed to connect to server');
    } finally {
      setCancelDialog(false);
      setSelectedBooking(null);
    }
  };

  const today = formatDateKey(new Date());

  return (
    <Container sx={{ py: 4 }}>
      <Typography variant="h4" gutterBottom>
        My Bookings
      </Typography>

      {error && (
        <Alert severity="error" sx={{ mb: 2 }} onClose={() => setError('')}>
          {error}
        </Alert>
      )}

      {/* Week navigation */}
      <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'center', mb: 3 }}>
        <IconButton onClick={() => handleWeekChange(-1)} aria-label="Previous week">
          <ChevronLeft />
        </IconButton>
        <Typography variant="h6" sx={{ mx: 2 }}>
          {formatWeekRange(weekDates)}
        </Typography>
        <IconButton onClick={() => handleWeekChange(1)} aria-label="Next week">
          <ChevronRight />
        </IconButton>
        <Button size="small" variant="outlined" sx={{ ml: 2 }} onClick={() => setWeekBase(new Date())}>
          Today
        </Button>
      </Box>

      {loading ? (
        <Typography color="text.secondary">Loading bookings...</Typography>
      ) : (
        <Box sx={{ display: 'grid', gridTemplateColumns: 'repeat(7, 1fr)', gap: 1 }}>
          {weekDates.map((date) => {
            const dateKey = formatDateKey(date);
            const dayBookings = getBookingsForDate(date);
            const isToday = dateKey === today;

            return (
              <Paper
                key={dateKey}
                variant="outlined"
                sx={{
                  p: 1.5,
                  minHeight: 140,
                  backgroundColor: isToday ? '#e3f2fd' : 'transparent',
                  borderColor: isToday ? 'primary.main' : 'divider',
                }}
              >
                <Typography
                  variant="caption"
                  sx={{ display: 'block', mb: 1, fontWeight: 'bold', color: isToday ? 'primary.main' : 'text.secondary' }}
                >
                  {formatDayLabel(date)}
                </Typography>

                {dayBookings.length === 0 ? (
                  <Typography variant="caption" color="text.disabled">
                    No bookings
                  </Typography>
                ) : (
                  <Box sx={{ display: 'flex', flexDirection: 'column', gap: 0.5 }}>
                    {dayBookings.map((booking) => (
                      <Box
                        key={booking.booking_id}
                        onClick={() => handleBookingClick(booking)}
                        sx={{
                          p: 0.75,
                          borderRadius: 1,
                          backgroundColor: 'primary.main',
                          color: 'white',
                          cursor: 'pointer',
                          '&:hover': { backgroundColor: 'primary.dark' },
                        }}
                      >
                        <Typography variant="caption" sx={{ display: 'block', fontWeight: 'bold' }}>
                          {formatTime(booking.start_time)} – {formatTime(booking.end_time)}
                        </Typography>
                        <Typography variant="caption" sx={{ display: 'block', opacity: 0.9 }}>
                          {booking.room_name}
                        </Typography>
                      </Box>
                    ))}
                  </Box>
                )}
              </Paper>
            );
          })}
        </Box>
      )}

      {bookings.length === 0 && !loading && (
        <Typography color="text.secondary" sx={{ mt: 2, textAlign: 'center' }}>
          No bookings yet. Go to the Rooms page to book a room.
        </Typography>
      )}

      {/* Booking detail dialog */}
      <Dialog open={detailDialog} onClose={() => setDetailDialog(false)} maxWidth="sm" fullWidth>
        <DialogTitle>Booking Details</DialogTitle>
        <DialogContent>
          {selectedBooking && (
            <Box sx={{ display: 'flex', flexDirection: 'column', gap: 1.5, mt: 1 }}>
              <Box>
                <Typography variant="caption" color="text.secondary">Room</Typography>
                <Typography variant="body1" sx={{ fontWeight: 'bold' }}>{selectedBooking.room_name}</Typography>
              </Box>
              <Box>
                <Typography variant="caption" color="text.secondary">Location</Typography>
                <Typography variant="body1">{selectedBooking.building_name} — Floor {selectedBooking.floor}</Typography>
              </Box>
              <Box>
                <Typography variant="caption" color="text.secondary">Date</Typography>
                <Typography variant="body1">{selectedBooking.date}</Typography>
              </Box>
              <Box>
                <Typography variant="caption" color="text.secondary">Time</Typography>
                <Typography variant="body1">{formatTime(selectedBooking.start_time)} – {formatTime(selectedBooking.end_time)}</Typography>
              </Box>
              {selectedBooking.purpose && (
                <Box>
                  <Typography variant="caption" color="text.secondary">Purpose</Typography>
                  <Typography variant="body1">{selectedBooking.purpose}</Typography>
                </Box>
              )}
              <Box>
                <Typography variant="caption" color="text.secondary">Status</Typography>
                <Box sx={{ mt: 0.5 }}>
                  <Chip
                    label={selectedBooking.date >= today ? 'Upcoming' : 'Past'}
                    color={selectedBooking.date >= today ? 'primary' : 'default'}
                    size="small"
                  />
                </Box>
              </Box>
            </Box>
          )}
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setDetailDialog(false)}>Close</Button>
          <Button onClick={handleCancelClick} color="error" startIcon={<Delete />}>
            Cancel Booking
          </Button>
        </DialogActions>
      </Dialog>

      {/* Cancel confirmation dialog */}
      <Dialog open={cancelDialog} onClose={() => setCancelDialog(false)}>
        <DialogTitle>Cancel Booking</DialogTitle>
        <DialogContent>
          <Typography>
            Are you sure you want to cancel your booking for{' '}
            <strong>{selectedBooking?.room_name}</strong> on{' '}
            <strong>{selectedBooking?.date}</strong> ({selectedBooking?.start_time} – {selectedBooking?.end_time})?
          </Typography>
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setCancelDialog(false)}>Keep Booking</Button>
          <Button onClick={handleCancelConfirm} color="error" variant="contained">
            Cancel Booking
          </Button>
        </DialogActions>
      </Dialog>

      {/* Success snackbar */}
      <Snackbar
        open={!!success}
        autoHideDuration={3000}
        onClose={() => setSuccess('')}
        message={success}
      />
    </Container>
  );
}
