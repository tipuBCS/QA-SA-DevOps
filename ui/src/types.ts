export interface User {
  user_id: string;
  email: string;
  name: string;
  is_admin: boolean;
  access_level: number;
  access_level_name: string;
}

export interface Room {
  id: string;
  name: string;
  capacity: number;
  floor: number;
  building_id: string;
  min_access_level: number;
  amenities: string[];
}

export interface Building {
  id: string;
  name: string;
  address: string;
  num_floors: number;
}

export interface RoomType {
  id: string;
  name: string;
  description: string;
}

export interface Booking {
  id: string;
  room_id: string;
  building_id: string;
  user_id: string;
  date: string;
  start_time: string;
  end_time: string;
  purpose: string;
}

/** Helper to get the current user from localStorage */
export function getCurrentUser(): User | null {
  const raw = localStorage.getItem('user');
  if (!raw) return null;
  try {
    return JSON.parse(raw) as User;
  } catch {
    return null;
  }
}
