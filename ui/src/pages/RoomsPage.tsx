import { useState, useEffect } from 'react';
import {
  Container,
  Typography,
  Box,
  TextField,
  MenuItem,
  Button,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  Alert,
  Snackbar,
  IconButton,
  Tooltip,
} from '@mui/material';
import { ChevronLeft, ChevronRight } from '@mui/icons-material';
import { apiRequest } from '../api';
import { getCurrentUser } from '../types';
import type { Building } from '../types';

interface RoomData {
  room_id: string;
  building_id: string;
  building_name: string;
  floor: number;
  name: string;
  capacity: number;
  min_access_level: number;
  min_access_level_name: string;
  room_type_id: string;
  room_type_name: string;
  amenities: string[];
}

interface BookingData {
  booking_id: string;
  room_id: string;
  room_name: string;
  building_name: string;
  floor: number;
  user_id: string;
  date: string;
  start_time: string;
  end_time: string;
  purpose: string;
}

// Generate 15-minute interval time options from 07:00 to 20:00
const TIME_OPTIONS = Array.from({ length: 53 }, (_, i) => {
  const totalMinutes = i * 15 + 7 * 60; // Start at 07:00
  const hour = Math.floor(totalMinutes / 60);
  const minute = totalMinutes % 60;
  const value = `${hour.toString().padStart(2, '0')}:${minute.toString().padStart(2, '0')}`;
  return value;
});

// Hourly slots for the grid display
const TIME_SLOTS = Array.from({ length: 11 }, (_, i) => {
  const hour = i + 8;
  return `${hour.toString().padStart(2, '0')}:00`;
});

function formatTime(time: string): string {
  const [h, m] = time.split(':');
  const hour = parseInt(h);
  const ampm = hour >= 12 ? 'PM' : 'AM';
  const displayHour = hour > 12 ? hour - 12 : hour === 0 ? 12 : hour;
  return `${displayHour}:${m} ${ampm}`;
}

function formatDate(dateStr: string): string {
  const date = new Date(dateStr + 'T00:00:00');
  return date.toLocaleDateString('en-GB', { weekday: 'short', day: 'numeric', month: 'short', year: 'numeric' });
}

export default function RoomsPage() {
  const [rooms, setRooms] = useState<RoomData[]>([]);
  const [buildings, setBuildings] = useState<Building[]>([]);
  const [bookings, setBookings] = useState<BookingData[]>([]);
  const [selectedBuilding, setSelectedBuilding] = useState('');
  const [selectedFloor, setSelectedFloor] = useState('');
  const [selectedDate, setSelectedDate] = useState(new Date().toISOString().split('T')[0]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [success, setSuccess] = useState('');

  // Booking dialog state
  const [bookingDialog, setBookingDialog] = useState(false);
  const [selectedRoom, setSelectedRoom] = useState<RoomData | null>(null);
  const [bookingForm, setBookingForm] = useState({
    start_time: '',
    end_time: '',
    purpose: '',
  });
  const [bookingError, setBookingError] = useState('');

  const user = getCurrentUser();

  const fetchBuildings = async () => {
    try {
      const res = await apiRequest('/buildings/');
      if (res.ok) {
        const data = await res.json();
        const allBuildings: Building[] = data.buildings || [];
        setBuildings(allBuildings);
        // Auto-select first building
        if (allBuildings.length > 0 && !selectedBuilding) {
          setSelectedBuilding(allBuildings[0].building_id);
        }
      }
    } catch {
      setError('Failed to load buildings');
    }
  };

  const fetchRooms = async () => {
    if (!selectedBuilding) return;
    setLoading(true);
    try {
      const res = await apiRequest(`/buildings/${selectedBuilding}/rooms`);
      if (res.ok) {
        const data = await res.json();
        setRooms(data.rooms || []);
      } else {
        setError('Failed to load rooms');
      }
    } catch {
      setError('Failed to connect to server');
    } finally {
      setLoading(false);
    }
  };

  // TODO: Replace with a proper API endpoint that fetches all bookings for a building/date
  // Currently fetches only the current user's bookings since there's no room-level booking query
  const fetchBookings = async () => {
    if (!selectedBuilding) return;
    try {
      const res = await apiRequest(`/buildings/${selectedBuilding}/bookings?date=${selectedDate}`);
      if (res.ok) {
        const data = await res.json();
        setBookings(data.bookings || []);
      }
    } catch {
      // Non-critical
    }
  };

  useEffect(() => {
    fetchBuildings();
  }, []);

  useEffect(() => {
    if (selectedBuilding) {
      fetchRooms();
      fetchBookings();
    }
  }, [selectedBuilding, selectedDate]);

  // Filter rooms by floor
  const filteredRooms = selectedFloor
    ? rooms.filter((r) => r.floor === parseInt(selectedFloor))
    : rooms;

  // Get available floors for selected building
  const selectedBuildingData = buildings.find((b) => b.building_id === selectedBuilding);
  const floors = selectedBuildingData
    ? Array.from({ length: selectedBuildingData.num_floors }, (_, i) => i + 1)
    : [];

  // Get booking for a specific room and time slot on the selected date
  const getBookingForSlot = (roomId: string, slotTime: string): BookingData | null => {
    return bookings.find((b) => {
      if (b.room_id !== roomId || b.date !== selectedDate) return false;
      // Check if this booking overlaps with the slot
      return b.start_time <= slotTime && b.end_time > slotTime;
    }) || null;
  };

  const canBook = (room: RoomData): boolean => {
    if (!user) return false;
    return user.access_level >= room.min_access_level;
  };

  const handleSlotClick = (room: RoomData, slotTime: string) => {
    if (!canBook(room)) return;
    const booking = getBookingForSlot(room.room_id, slotTime);
    if (booking) return; // Slot is taken

    setSelectedRoom(room);
    // Default end time is 1 hour after start
    const startHour = parseInt(slotTime.split(':')[0]);
    const endTime = `${(startHour + 1).toString().padStart(2, '0')}:00`;
    setBookingForm({ start_time: slotTime, end_time: endTime, purpose: '' });
    setBookingError('');
    setBookingDialog(true);
  };

  const handleBookingSubmit = async () => {
    setBookingError('');

    if (!bookingForm.start_time || !bookingForm.end_time) {
      setBookingError('Start time and end time are required');
      return;
    }

    if (bookingForm.start_time >= bookingForm.end_time) {
      setBookingError('End time must be after start time');
      return;
    }

    if (!selectedRoom) return;

    try {
      const res = await apiRequest(`/buildings/${selectedRoom.building_id}/rooms/${selectedRoom.room_id}/book`, {
        method: 'POST',
        body: JSON.stringify({
          date: selectedDate,
          start_time: bookingForm.start_time,
          end_time: bookingForm.end_time,
          purpose: bookingForm.purpose,
        }),
      });

      if (res.ok) {
        setSuccess(`Successfully booked ${selectedRoom.name}`);
        setBookingDialog(false);
        fetchBookings(); // Refresh bookings
      } else {
        const data = await res.json();
        setBookingError(data.error || 'Failed to book room');
      }
    } catch {
      setBookingError('Failed to connect to server');
    }
  };

  const handleDateChange = (offset: number) => {
    const [year, month, day] = selectedDate.split('-').map(Number);
    const date = new Date(year, month - 1, day + offset);
    const newDate = `${date.getFullYear()}-${(date.getMonth() + 1).toString().padStart(2, '0')}-${date.getDate().toString().padStart(2, '0')}`;
    setSelectedDate(newDate);
  };

  return (
    <Container maxWidth={false} sx={{ py: 4, px: { xs: 2, md: 4 } }}>
      <Typography variant="h4" gutterBottom>
        Room Booking
      </Typography>

      {/* Filters */}
      <Box sx={{ display: 'flex', gap: 2, mb: 3, flexWrap: 'wrap', alignItems: 'center' }}>
        <TextField
          select
          label="Building"
          value={selectedBuilding}
          onChange={(e) => { setSelectedBuilding(e.target.value); setSelectedFloor(''); }}
          sx={{ minWidth: 200 }}
          size="small"
        >
          {buildings.map((b) => (
            <MenuItem key={b.building_id} value={b.building_id}>{b.name}</MenuItem>
          ))}
        </TextField>
        <TextField
          select
          label="Floor"
          value={selectedFloor}
          onChange={(e) => setSelectedFloor(e.target.value)}
          sx={{ minWidth: 100 }}
          size="small"
        >
          <MenuItem value="">All</MenuItem>
          {floors.map((f) => (
            <MenuItem key={f} value={f.toString()}>{f}</MenuItem>
          ))}
        </TextField>
        <TextField
          label="Date"
          type="date"
          value={selectedDate}
          onChange={(e) => setSelectedDate(e.target.value)}
          size="small"
          slotProps={{ inputLabel: { shrink: true } }}
        />
      </Box>

      {error && (
        <Alert severity="error" sx={{ mb: 2 }} onClose={() => setError('')}>
          {error}
        </Alert>
      )}

      {/* Date navigation */}
      <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'center', mb: 2 }}>
        <IconButton onClick={() => handleDateChange(-1)} aria-label="Previous day">
          <ChevronLeft />
        </IconButton>
        <Typography variant="h6" sx={{ mx: 2 }}>
          {formatDate(selectedDate)}
        </Typography>
        <IconButton onClick={() => handleDateChange(1)} aria-label="Next day">
          <ChevronRight />
        </IconButton>
      </Box>

      {/* Timeline grid */}
      {loading ? (
        <Typography color="text.secondary">Loading rooms...</Typography>
      ) : filteredRooms.length === 0 ? (
        <Typography color="text.secondary">No rooms available for this selection.</Typography>
      ) : (
        <Box sx={{ overflowX: 'auto' }}>
          <Box sx={{ display: 'grid', gridTemplateColumns: `180px repeat(${TIME_SLOTS.length}, 1fr)`, minWidth: 900 }}>
            {/* Header row - time slots */}
            <Box sx={{ p: 1, borderBottom: 1, borderColor: 'divider', fontWeight: 'bold' }} />
            {TIME_SLOTS.map((slot) => (
              <Box
                key={slot}
                sx={{
                  p: 1,
                  borderBottom: 1,
                  borderLeft: 1,
                  borderColor: 'divider',
                  textAlign: 'center',
                  fontSize: '0.75rem',
                  fontWeight: 'bold',
                }}
              >
                {formatTime(slot)}
              </Box>
            ))}

            {/* Room rows */}
            {filteredRooms.map((room) => (
              <>
                {/* Room name cell */}
                <Box
                  key={`label-${room.room_id}`}
                  sx={{
                    p: 1,
                    borderBottom: 1,
                    borderColor: 'divider',
                    display: 'flex',
                    flexDirection: 'column',
                    justifyContent: 'center',
                  }}
                >
                  <Typography variant="body2" sx={{ fontWeight: 'bold' }}>
                    {room.name}
                  </Typography>
                  <Typography variant="caption" color="text.secondary">
                    Cap: {room.capacity} | {room.min_access_level_name}
                  </Typography>
                </Box>

                {/* Time slot cells */}
                {TIME_SLOTS.map((slot) => {
                  const booking = getBookingForSlot(room.room_id, slot);
                  const isBooked = !!booking;
                  const isAccessible = canBook(room);

                  return (
                    <Tooltip
                      key={`${room.room_id}-${slot}`}
                      title={
                        isBooked
                          ? `Booked: ${booking.purpose || 'No purpose'} (${booking.start_time} - ${booking.end_time})`
                          : !isAccessible
                            ? `Requires ${room.min_access_level_name} access`
                            : 'Click to book'
                      }
                    >
                      <Box
                        sx={{
                          p: 0.5,
                          borderBottom: 1,
                          borderLeft: 1,
                          borderColor: 'divider',
                          cursor: !isBooked && isAccessible ? 'pointer' : 'default',
                          backgroundColor: isBooked
                            ? '#ffcdd2'
                            : !isAccessible
                              ? '#f5f5f5'
                              : 'transparent',
                          '&:hover': !isBooked && isAccessible ? { backgroundColor: '#e3f2fd' } : {},
                          display: 'flex',
                          alignItems: 'center',
                          justifyContent: 'center',
                          minHeight: 48,
                        }}
                        onClick={() => handleSlotClick(room, slot)}
                      >
                        {isBooked ? (
                          <Typography variant="caption" sx={{ color: '#c62828', fontWeight: 500 }}>
                            {booking.user_id === user?.user_id ? 'You' : 'Booked'}
                          </Typography>
                        ) : (
                          <Typography variant="caption" color="text.secondary">
                            {isAccessible ? 'Available' : '🔒'}
                          </Typography>
                        )}
                      </Box>
                    </Tooltip>
                  );
                })}
              </>
            ))}
          </Box>
        </Box>
      )}

      {/* Booking dialog */}
      <Dialog open={bookingDialog} onClose={() => setBookingDialog(false)} maxWidth="sm" fullWidth>
        <DialogTitle>Book {selectedRoom?.name}</DialogTitle>
        <DialogContent>
          {selectedRoom && (
            <Box sx={{ mb: 2, p: 2, backgroundColor: '#f5f5f5', borderRadius: 1 }}>
              <Typography variant="subtitle1" sx={{ fontWeight: 'bold' }}>
                {selectedRoom.building_name} — Floor {selectedRoom.floor}
              </Typography>
              <Typography variant="body2" color="text.secondary">
                {formatDate(selectedDate)}
              </Typography>
              <Typography variant="body2" sx={{ mt: 0.5 }}>
                {selectedRoom.room_type_name && `${selectedRoom.room_type_name} · `}Capacity: {selectedRoom.capacity}
              </Typography>
            </Box>
          )}

          {bookingError && (
            <Alert severity="error" sx={{ mb: 2 }}>
              {bookingError}
            </Alert>
          )}

          <Box sx={{ display: 'flex', flexDirection: 'column', gap: 2, mt: 1 }}>
            <TextField
              select
              label="Start Time"
              value={bookingForm.start_time}
              onChange={(e) => setBookingForm({ ...bookingForm, start_time: e.target.value })}
              required
            >
              {TIME_OPTIONS.map((t) => (
                <MenuItem key={t} value={t}>{formatTime(t)}</MenuItem>
              ))}
            </TextField>
            <TextField
              select
              label="End Time"
              value={bookingForm.end_time}
              onChange={(e) => setBookingForm({ ...bookingForm, end_time: e.target.value })}
              required
            >
              {TIME_OPTIONS.filter((t) => t > bookingForm.start_time).map((t) => (
                <MenuItem key={t} value={t}>{formatTime(t)}</MenuItem>
              ))}
            </TextField>
            <TextField
              label="Purpose (optional)"
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
