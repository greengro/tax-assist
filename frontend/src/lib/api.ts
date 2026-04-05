const API_URL = import.meta.env.VITE_API_URL || "http://localhost:8000";

async function request(path: string, options?: RequestInit) {
  const resp = await fetch(`${API_URL}${path}`, {
    ...options,
    headers: { "Content-Type": "application/json", ...options?.headers },
  });
  if (!resp.ok) {
    const err = await resp.json().catch(() => ({ detail: resp.statusText }));
    throw new Error(err.detail || resp.statusText);
  }
  return resp.json();
}

// Pipeline
export const getPipelineSummary = () => request("/api/pipeline/summary");
export const getPipelineStats = () => request("/api/pipeline/stats");
export const getActivityFeed = (limit = 50) =>
  request(`/api/pipeline/activity-feed?limit=${limit}`);
export const getEmailLog = () => request("/api/pipeline/emails");
export const getSignatureLog = () => request("/api/pipeline/signatures");

// Clients
export const getClients = () => request("/api/clients");
export const getClient = (id: number) => request(`/api/clients/${id}`);
export const createClient = (data: {
  name: string;
  email: string;
  phone?: string;
  company?: string;
  state?: string;
  referral_source?: string;
}) => request("/api/clients", { method: "POST", body: JSON.stringify(data) });

export const updateClient = (
  id: number,
  data: Record<string, unknown>
) => request(`/api/clients/${id}`, { method: "PATCH", body: JSON.stringify(data) });

export const deleteClient = (id: number) =>
  request(`/api/clients/${id}`, { method: "DELETE" });

// Webhooks
export const simulateCalendlyWebhook = (data: {
  name: string;
  email: string;
  scheduled_time?: string;
}) =>
  request("/api/webhooks/calendly", {
    method: "POST",
    body: JSON.stringify({
      event: "invitee.created",
      payload: data,
    }),
  });

export const submitMeetingNotes = (data: {
  client_email: string;
  transcript: string;
  action_items?: string[];
  scope_of_services?: string;
  fee_estimate?: number;
}) => request("/api/webhooks/meeting-notes", { method: "POST", body: JSON.stringify(data) });

export const triggerEngagementLetter = (
  clientId: number,
  services = "Individual Tax Return Preparation"
) =>
  request(`/api/webhooks/trigger-engagement-letter/${clientId}?services=${encodeURIComponent(services)}`, {
    method: "POST",
  });

export const checkDocuments = (clientId: number) =>
  request(`/api/webhooks/check-documents/${clientId}`, { method: "POST" });

export const triggerAnalysis = (clientId: number) =>
  request(`/api/webhooks/trigger-analysis/${clientId}`, { method: "POST" });

// Documents
export const getDocuments = (clientId: number) =>
  request(`/api/documents/${clientId}`);

export const getChecklist = (clientId: number) =>
  request(`/api/documents/checklist/${clientId}`);

export const updateChecklistItem = (itemId: number, received: boolean) =>
  request(`/api/documents/checklist/${itemId}?received=${received}`, {
    method: "PATCH",
  });

export const uploadDocument = async (
  clientId: number,
  file: File,
  docType: string
) => {
  const formData = new FormData();
  formData.append("file", file);
  const resp = await fetch(
    `${API_URL}/api/documents/upload/${clientId}?doc_type=${docType}`,
    { method: "POST", body: formData }
  );
  if (!resp.ok) throw new Error("Upload failed");
  return resp.json();
};
