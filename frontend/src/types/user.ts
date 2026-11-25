export type UserRole = "manager" | "student" | "facilities" | "internet";



export interface StudentProfile {
  student_number: string;
  is_dorm_resident: boolean;
  dormitory_name: string;
  building: string;
  room_number: string;
  phone_number: string;
}

export interface ManagerProfile {
  job_title?: string;
}

export interface User {
  id: number;
  username: string;
  first_name: string;
  last_name: string;
  full_name: string;
  email: string;
  phone_number: string;
  role: UserRole;
  role_display: string;
  profile: StudentProfile | ManagerProfile | null;
}

export interface Organization {
  organization_id: number;
  organization_name: string;
  membership_role: UserRole;
  membership_role_display: string;
  room_number?: string;
  is_default: boolean;
}

export interface Capabilities {
  is_system_admin: boolean;
  can_manage_organizations: boolean;
  can_report_faults: boolean;
  fault_panels: UserRole[];
  has_booking_panel: boolean;
}

export interface SpecialAssignment {
  resource_type_id: number;
  resource_name: string;
  organization_id: number;
}

export interface LoginResponse {
  tokens: {
    access: string;
    refresh: string;
  };
  user: User;
  organizations: Organization[];
  special_assignments: SpecialAssignment[];
  capabilities: Capabilities;
}