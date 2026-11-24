
// Maintenance request categories
export type FaultCategory =
  | "repairs"
  | "facilities"
  | "internet"
  | "other";

// Maintenance request statuses
export type FaultStatus =
  | "submitted"
  | "approved"
  | "in_progress"
  | "resolved"
  | "rejected"
  | "irrelevant"
  | "cancelled";

// Maintenance request
export interface FaultRequest {
  id: number;
  title: string;
  description: string;
  category: FaultCategory;
  room_number: string;
  created_at: string;
  status: FaultStatus;
  status_display: string;
}
