export interface Client {
  id: number;
  name: string;
  email: string;
  phone: string | null;
  company: string | null;
  state: string | null;
  client_type: "prospect" | "customer";
  stage: PipelineStage;
  scope_of_services: string | null;
  fee_estimate: number | null;
  referral_source: string | null;
  owner: string | null;
  needs_extension: boolean | null;
  meeting_time: string | null;
  meeting_summary: string | null;
  notes: string | null;
  folder_url: string | null;
  created_at: string;
  updated_at: string;
  activities: Activity[];
  documents: Document[];
  checklist_items: ChecklistItem[];
}

export interface Activity {
  id: number;
  action: string;
  details: string | null;
  devin_session_id: string | null;
  created_at: string;
}

export interface Document {
  id: number;
  filename: string;
  doc_type: string;
  uploaded_at: string;
}

export interface ChecklistItem {
  id: number;
  doc_name: string;
  required: boolean;
  received: boolean;
}

export type PipelineStage =
  | "lead"
  | "intro_booked"
  | "intro_completed"
  | "documents_requested"
  | "documents_received"
  | "engagement_letter_sent"
  | "engagement_signed"
  | "in_progress"
  | "review"
  | "return_completed"
  | "return_signed"
  | "filed"
  | "completed";

export interface PipelineStageSummary {
  stage: PipelineStage;
  label: string;
  count: number;
  clients: Client[];
}

export interface ActivityFeedItem {
  id: number;
  client_id: number;
  client_name: string;
  action: string;
  details: string | null;
  devin_session_id: string | null;
  created_at: string;
}

export interface PipelineStats {
  total_clients: number;
  stage_counts: Record<string, number>;
  emails_sent: number;
  signature_requests: number;
}

export const STAGE_LABELS: Record<PipelineStage, string> = {
  lead: "Lead",
  intro_booked: "Intro Booked",
  intro_completed: "Intro Done",
  documents_requested: "Docs Requested",
  documents_received: "Docs Received",
  engagement_letter_sent: "Letter Sent",
  engagement_signed: "Signed",
  in_progress: "In Progress",
  review: "Review",
  return_completed: "Return Done",
  return_signed: "Return Signed",
  filed: "Filed",
  completed: "Completed",
};

export const STAGE_COLORS: Record<PipelineStage, string> = {
  lead: "bg-gray-200 text-gray-700",
  intro_booked: "bg-cyan-100 text-cyan-800",
  intro_completed: "bg-blue-100 text-blue-800",
  documents_requested: "bg-yellow-100 text-yellow-800",
  documents_received: "bg-orange-100 text-orange-800",
  engagement_letter_sent: "bg-purple-100 text-purple-800",
  engagement_signed: "bg-green-100 text-green-800",
  in_progress: "bg-teal-100 text-teal-800",
  review: "bg-pink-100 text-pink-800",
  return_completed: "bg-indigo-100 text-indigo-800",
  return_signed: "bg-emerald-100 text-emerald-800",
  filed: "bg-lime-100 text-lime-800",
  completed: "bg-green-200 text-green-900",
};

export const STAGE_BORDER_COLORS: Record<PipelineStage, string> = {
  lead: "border-l-gray-400",
  intro_booked: "border-l-cyan-500",
  intro_completed: "border-l-blue-500",
  documents_requested: "border-l-yellow-500",
  documents_received: "border-l-orange-500",
  engagement_letter_sent: "border-l-purple-500",
  engagement_signed: "border-l-green-500",
  in_progress: "border-l-teal-500",
  review: "border-l-pink-500",
  return_completed: "border-l-indigo-500",
  return_signed: "border-l-emerald-500",
  filed: "border-l-lime-500",
  completed: "border-l-green-700",
};
