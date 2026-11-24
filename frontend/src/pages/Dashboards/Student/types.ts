export type DashboardTab =
  | "home"
  | "requests"
  | "bookings"
  | "announcements";

export interface Announcement {
  id: number;
  title: string;
  description: string;
  created_at: string;
  is_important?: boolean;
}

export type ServiceType =
  | "washing_machine"
  | "vacuum_cleaner";

export type BookingStatus =
  | "confirmed"
  | "pending"
  | "completed"
  | "cancelled";

export interface ServiceBooking {
  id: number;
  service_type: ServiceType;
  service_title: string;
  device_label: string;
  date_display: string;
  time_slot: string;
  status: BookingStatus;
  status_display: string;
}