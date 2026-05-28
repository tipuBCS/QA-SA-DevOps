import type { Room, Booking } from '../types';

export const mockRooms: Room[] = [
  {
    id: '1',
    name: 'Conference Room A',
    capacity: 10,
    location: 'Floor 1',
    amenities: ['Projector', 'Whiteboard', 'Video Conferencing'],
  },
  {
    id: '2',
    name: 'Meeting Room B',
    capacity: 6,
    location: 'Floor 2',
    amenities: ['TV Screen', 'Whiteboard'],
  },
  {
    id: '3',
    name: 'Board Room',
    capacity: 20,
    location: 'Floor 3',
    amenities: ['Projector', 'Video Conferencing', 'Phone', 'Whiteboard'],
  },
  {
    id: '4',
    name: 'Huddle Space',
    capacity: 4,
    location: 'Floor 1',
    amenities: ['TV Screen'],
  },
  {
    id: '5',
    name: 'Training Room',
    capacity: 30,
    location: 'Floor 2',
    amenities: ['Projector', 'Microphone', 'Whiteboard', 'Video Conferencing'],
  },
];

export const mockBookings: Booking[] = [
  {
    id: '1',
    roomId: '1',
    roomName: 'Conference Room A',
    date: '2026-05-29',
    startTime: '09:00',
    endTime: '10:00',
    bookedBy: 'Alice',
    purpose: 'Sprint Planning',
  },
  {
    id: '2',
    roomId: '2',
    roomName: 'Meeting Room B',
    date: '2026-05-29',
    startTime: '14:00',
    endTime: '15:00',
    bookedBy: 'Bob',
    purpose: '1:1 Meeting',
  },
  {
    id: '3',
    roomId: '3',
    roomName: 'Board Room',
    date: '2026-05-30',
    startTime: '10:00',
    endTime: '12:00',
    bookedBy: 'Charlie',
    purpose: 'Quarterly Review',
  },
];
