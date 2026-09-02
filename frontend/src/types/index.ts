// Mirrors backend/app/schemas/*.py and app/models/enums.py.
// Kept as one file for now — split by domain if/when it grows unwieldy.

export type Role = "ADMIN" | "HR" | "IT_SUPPORT" | "EMPLOYEE";

export type AssetStatus =
  | "AVAILABLE"
  | "ASSIGNED"
  | "RESERVED"
  | "UNDER_REPAIR"
  | "DAMAGED"
  | "LOST"
  | "RETIRED"
  | "DISPOSED";

export type AssetCondition = "NEW" | "GOOD" | "FAIR" | "DAMAGED";

export type EmploymentStatus =
  | "ACTIVE"
  | "NOTICE_PERIOD"
  | "RESIGNED"
  | "TERMINATED"
  | "INACTIVE";

export type AssignmentItemStatus = "ACTIVE" | "RETURNED" | "TRANSFERRED";
export type ReturnCondition = "GOOD" | "DAMAGED" | "MISSING";
export type RepairStatus =
  | "OPEN"
  | "ACKNOWLEDGED"
  | "DIAGNOSING"
  | "SENT_TO_VENDOR"
  | "IN_REPAIR"
  | "RESOLVED"
  | "CLOSED"
  | "CANCELLED";
export type RepairPriority = "LOW" | "MEDIUM" | "HIGH" | "CRITICAL";
export type LicenseStatus = "ACTIVE" | "EXPIRING" | "EXPIRED" | "SUSPENDED";

export interface User {
  id: number;
  email: string;
  role: Role;
  status: "ACTIVE" | "DISABLED";
  employee_id: number | null;
  last_login: string | null;
  created_at: string;
}

export interface Group {
  id: number;
  name: string;
  code: string | null;
  status: string;
}

export interface Employee {
  id: number;
  employee_code: string;
  first_name: string;
  last_name: string;
  full_name?: string;
  email: string;
  phone: string | null;
  department_id: number | null;
  designation: string | null;
  manager_id: number | null;
  location_id: number | null;
  group_id: number | null;
  joining_date: string | null;
  employment_status: EmploymentStatus;
  created_at: string;
}

export interface Asset {
  id: number;
  asset_code: string;
  asset_type_id: number;
  manufacturer: string | null;
  model: string | null;
  serial_number: string | null;
  purchase_date: string | null;
  purchase_cost: string | null;
  vendor_id: number | null;
  status: AssetStatus;
  condition: AssetCondition;
  location_id: number | null;
  hostname: string | null;
  description: string | null;
  created_at: string;
}

export interface AssignmentItem {
  id: number;
  assignment_id: number;
  asset_id: number;
  condition_at_assignment: AssetCondition | null;
  status: AssignmentItemStatus;
  returned_at: string | null;
  return_condition: ReturnCondition | null;
  notes: string | null;
}

export interface AssetComponent {
  id: number;
  asset_id: number;
  component_type_id: number;
  description: string;
  serial_number: string | null;
  status: "ACTIVE" | "REMOVED";
  installed_at: string;
  removed_at: string | null;
  replaced_by_component_id: number | null;
}

export interface SoftwareAssignmentRecord {
  id: number;
  employee_id: number;
  license_id: number;
  assigned_at: string;
  revoked_at: string | null;
  status: "ACTIVE" | "REVOKED";
}

export interface AmsDocument {
  id: number;
  entity_type: string;
  entity_id: number;
  doc_type: string;
  file_name: string;
  content_type: string | null;
  uploaded_by: number | null;
  uploaded_at: string;
}

export interface Assignment {
  id: number;
  employee_id: number;
  assigned_by: number;
  assigned_at: string;
  expected_return_date: string | null;
  acknowledged_at: string | null;
  notes: string | null;
  items: AssignmentItem[];
}

export interface RepairTicket {
  id: number;
  ticket_code: string;
  asset_id: number;
  reported_by: number;
  issue: string;
  priority: RepairPriority;
  status: RepairStatus;
  diagnosis: string | null;
  vendor_id: number | null;
  repair_cost: string | null;
  repair_start_date: string | null;
  repair_end_date: string | null;
  resolution: string | null;
  created_at: string;
}

export interface Software {
  id: number;
  name: string;
  publisher: string | null;
  version: string | null;
  category: string | null;
  description: string | null;
}

export interface License {
  id: number;
  software_id: number;
  license_type: string | null;
  seats: number;
  assigned_seats: number;
  purchase_date: string | null;
  expiry_date: string | null;
  vendor_id: number | null;
  status: LicenseStatus;
  masked_key: string | null;
}

export interface Warranty {
  id: number;
  asset_id: number;
  warranty_start: string | null;
  warranty_end: string | null;
  vendor_id: number | null;
  warranty_type: string | null;
  warranty_reference: string | null;
  computed_status: "ACTIVE" | "EXPIRING_SOON" | "EXPIRED" | "UNKNOWN";
}

export interface Department {
  id: number;
  name: string;
  code: string | null;
  manager_id: number | null;
  status: string;
}

export interface Location {
  id: number;
  name: string;
  city: string | null;
  status: string;
}

export interface AssetType {
  id: number;
  name: string;
  code: string | null;
  status: string;
}

export interface Notification {
  id: number;
  type: string;
  title: string;
  message: string;
  related_entity_type: string | null;
  related_entity_id: number | null;
  is_read: boolean;
  created_at: string;
}

export interface AdminDashboard {
  total_employees: number;
  active_employees: number;
  total_assets: number;
  assets_by_status: Record<string, number>;
  warranties_expiring_soon: number;
  licenses_expiring_soon: number;
  recent_activity: {
    action: string;
    entity_type: string;
    entity_id: number | null;
    timestamp: string;
  }[];
}

export interface ItDashboard {
  available_assets: number;
  assigned_assets: number;
  assets_under_repair: number;
  pending_assignment_acknowledgments: number;
  open_repair_tickets: number;
  warranties_expiring_soon: number;
  licenses_expiring_soon: number;
  agent_status: string;
}

export interface HrDashboard {
  total_employees: number;
  new_joiners_last_30_days: number;
  upcoming_joiners: number;
  employees_on_notice_period: number;
}


export interface MyDashboard {
  employee: {
    id: number;
    employee_code: string;
    full_name: string;
    employment_status: string;
  };
  active_assets: { asset_id: number; status: string }[];
  software_count: number;
  open_repair_requests: number;
}

export interface AuditLogEntry {
  id: number;
  actor_user_id: number | null;
  action: string;
  entity_type: string;
  entity_id: number | null;
  old_value: Record<string, unknown> | null;
  new_value: Record<string, unknown> | null;
  timestamp: string;
  ip_address: string | null;
}

export interface ImportRowError {
  row: number;
  message: string;
}

export interface ImportResult {
  created: number;
  skipped: number;
  errors: ImportRowError[];
}
