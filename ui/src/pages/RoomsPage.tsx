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

function timeToMinutes(time: string): number {
  const [h, m] = time.split(':').map(Number);
  return h * 60 + m;
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
  const [selectedFloor, setSelectedFloor] = useState('all');
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
  const [availableWindow, setAvailableWindow] = useState<{ start: string; end: string }>({ start: '07:00', end: '20:00' });

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
  const filteredRooms = selectedFloor !== 'all'
    ? rooms.filter((r) => r.floor === parseInt(selectedFloor))
    : rooms;

  // Get available floors for selected building
  const selectedBuildingData = buildings.find((b) => b.building_id === selectedBuilding);
  const floors = selectedBuildingData
    ? Array.from({ length: selectedBuildingData.num_floors }, (_, i) => i + 1)
    : [];

  // Check if a specific 15-minute quarter is booked
  const isQuarterBooked = (roomId: string, slotTime: string, quarter: number): BookingData | null => {
    // quarter: 0 = :00, 1 = :15, 2 = :30, 3 = :45
    const [h] = slotTime.split(':').map(Number);
    const quarterMinutes = quarter * 15;
    const quarterTime = `${h.toString().padStart(2, '0')}:${quarterMinutes.toString().padStart(2, '0')}`;
    const quarterEndMinutes = quarterMinutes + 15;
    const quarterEnd = quarterEndMinutes >= 60
      ? `${(h + 1).toString().padStart(2, '0')}:00`
      : `${h.toString().padStart(2, '0')}:${quarterEndMinutes.toString().padStart(2, '0')}`;

    return bookings.find((b) => {
      if (b.room_id !== roomId || b.date !== selectedDate) return false;
      // Booking overlaps this quarter if it starts before quarter ends AND ends after quarter starts
      return b.start_time < quarterEnd && b.end_time > quarterTime;
    }) || null;
  };

  const canBook = (room: RoomData): boolean => {
    if (!user) return false;
    return user.access_level >= room.min_access_level;
  };

  const handleSlotClick = (room: RoomData, slotTime: string) => {
    if (!canBook(room)) return;

    // Find the contiguous free window around the clicked time
    const roomBookings = bookings
      .filter((b) => b.room_id === room.room_id && b.date === selectedDate)
      .sort((a, b) => a.start_time.localeCompare(b.start_time));

    // Find the earliest start (walk backwards until we hit a booking or 07:00)
    let windowStart = '07:00';
    for (const b of roomBookings) {
      if (b.end_time <= slotTime) {
        // This booking ends before our slot — our window starts after it
        windowStart = b.end_time;
      }
    }

    // Find the latest end (walk forwards until we hit a booking or 20:00)
    let windowEnd = '20:00';
    for (const b of roomBookings) {
      if (b.start_time > slotTime) {
        // This booking starts after our slot — our window ends at its start
        windowEnd = b.start_time;
        break;
      }
    }

    setAvailableWindow({ start: windowStart, end: windowEnd });
    setSelectedRoom(room);
    // Default end time is 1 hour after start (capped to window end)
    const [h, m] = slotTime.split(':').map(Number);
    const endMinutes = Math.min(h * 60 + m + 60, timeToMinutes(windowEnd));
    const endH = Math.floor(endMinutes / 60);
    const endM = endMinutes % 60;
    const endTime = `${endH.toString().padStart(2, '0')}:${endM.toString().padStart(2, '0')}`;
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
          onChange={(e) => { setSelectedBuilding(e.target.value); setSelectedFloor('all'); }}
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
          <MenuItem value="all">All</MenuItem>
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
                  const isAccessible = canBook(room);

                  // Determine state of each quarter
                  const quarters = [0, 1, 2, 3].map((q) => ({
                    quarter: q,
                    booking: isQuarterBooked(room.room_id, slot, q),
                  }));

                  const allFree = quarters.every((q) => !q.booking);
                  const allSameBooking = quarters.every((q) => q.booking && quarters[0].booking && q.booking.booking_id === quarters[0].booking.booking_id);
                  const firstBooking = quarters.find((q) => q.booking)?.booking;

                  // Check if this slot is in the past
                  const now = new Date();
                  const todayStr = `${now.getFullYear()}-${(now.getMonth() + 1).toString().padStart(2, '0')}-${now.getDate().toString().padStart(2, '0')}`;
                  const currentTime = `${now.getHours().toString().padStart(2, '0')}:${now.getMinutes().toString().padStart(2, '0')}`;
                  const [slotH] = slot.split(':').map(Number);
                  const slotEndTime = `${(slotH + 1).toString().padStart(2, '0')}:00`;
                  const isPast = selectedDate < todayStr || (selectedDate === todayStr && slotEndTime <= currentTime);
                  const canInteract = isAccessible && !isPast;

                  // Determine label
                  let label = '';
                  let labelColor = 'text.secondary';
                  if (isPast && allFree) {
                    label = 'Past';
                  } else if (allFree && canInteract) {
                    label = 'Available';
                  } else if (allFree && !canInteract) {
                    label = '🔒';
                  } else if (allSameBooking && firstBooking) {
                    label = firstBooking.user_id === user?.user_id ? 'You' : 'Booked';
                    labelColor = firstBooking.user_id === user?.user_id ? '#2e7d32' : '#c62828';
                  } else if (!allFree && !allSameBooking) {
                    label = 'Partially\nBooked';
                    labelColor = '#c62828';
                  }

                  // For click, use the first free quarter's time
                  const firstFreeQuarter = quarters.find((q) => !q.booking);
                  const clickTime = firstFreeQuarter
                    ? `${slot.split(':')[0].padStart(2, '0')}:${(firstFreeQuarter.quarter * 15).toString().padStart(2, '0')}`
                    : slot;

                  const tooltipTitle = isPast
                    ? 'This time slot is in the past'
                    : allFree
                      ? (canInteract ? 'Click to book' : `Requires ${room.min_access_level_name} access`)
                      : allSameBooking && firstBooking
                        ? `Booked: ${firstBooking.purpose || 'No purpose'} (${firstBooking.start_time} – ${firstBooking.end_time})`
                        : 'Partially booked — click an available slot';

                  return (
                    <Tooltip key={`${room.room_id}-${slot}`} title={tooltipTitle}>
                      <Box
                        sx={{
                          borderBottom: 1,
                          borderLeft: 1,
                          borderColor: 'divider',
                          display: 'flex',
                          minHeight: 48,
                          position: 'relative',
                          cursor: canInteract && firstFreeQuarter ? 'pointer' : 'default',
                          opacity: isPast ? 0.4 : 1,
                          background: isPast ? 'repeating-linear-gradient(45deg, #f5f5f5, #f5f5f5 4px, #e0e0e0 4px, #e0e0e0 5px)' : undefined,
                        }}
                        onClick={() => {
                          if (canInteract && firstFreeQuarter) {
                            handleSlotClick(room, clickTime);
                          }
                        }}
                      >
                        {/* Quarter segments for coloring */}
                        {quarters.map(({ quarter, booking: qBooking }) => {
                          const isOurs = qBooking && qBooking.user_id === user?.user_id;
                          return (
                            <Box
                              key={quarter}
                              sx={{
                                flex: 1,
                                backgroundColor: qBooking
                                  ? isOurs
                                    ? '#c8e6c9'
                                    : '#ffcdd2'
                                  : !isAccessible
                                    ? '#f5f5f5'
                                    : 'transparent',
                                borderRight: quarter < 3 ? '1px dashed #e0e0e0' : 'none',
                              }}
                            />
                          );
                        })}

                        {/* Centered label */}
                        <Box
                          sx={{
                            position: 'absolute',
                            top: 0,
                            left: 0,
                            right: 0,
                            bottom: 0,
                            display: 'flex',
                            alignItems: 'center',
                            justifyContent: 'center',
                            pointerEvents: 'none',
                          }}
                        >
                          <Typography
                            variant="caption"
                            sx={{
                              color: labelColor,
                              fontWeight: label === 'Available' ? 400 : 500,
                              fontSize: '0.65rem',
                              textAlign: 'center',
                              whiteSpace: 'pre-line',
                            }}
                          >
                            {label}
                          </Typography>
                        </Box>
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
              {TIME_OPTIONS.filter((t) => t >= availableWindow.start && t < availableWindow.end).map((t) => (
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
              {TIME_OPTIONS.filter((t) => t > bookingForm.start_time && t <= availableWindow.end).map((t) => (
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
