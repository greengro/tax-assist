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
  intro_completed: "Intro Complete",
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

export const STAGE_DOT_COLORS: Record<PipelineStage, string> = {
  lead: "bg-gray-400",
  intro_booked: "bg-sky-400",
  intro_completed: "bg-blue-500",
  documents_requested: "bg-amber-500",
  documents_received: "bg-orange-500",
  engagement_letter_sent: "bg-violet-500",
  engagement_signed: "bg-emerald-500",
  in_progress: "bg-teal-500",
  review: "bg-pink-500",
  return_completed: "bg-indigo-500",
  return_signed: "bg-cyan-600",
  filed: "bg-lime-600",
  completed: "bg-green-700",
};
