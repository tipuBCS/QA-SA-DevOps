export interface Room {
  id: string;
  name: string;
  capacity: number;
  location: string;
  amenities: string[];
  imageUrl?: string;
}

export interface Booking {
  id: string;
  roomId: string;
  roomName: string;
  date: string;
  startTime: string;
  endTime: string;
  bookedBy: string;
  purpose: string;
}
