import { X, ExternalLink, Upload, Check, Circle } from "lucide-react";
import { useState, useRef } from "react";
import { Client, STAGE_LABELS, STAGE_DOT_COLORS } from "../lib/types";
import {
  updateClient,
  triggerEngagementLetter,
  checkDocuments,
  triggerAnalysis,
  uploadDocument,
  updateChecklistItem,
} from "../lib/api";

interface ClientDetailModalProps {
  client: Client;
  onClose: () => void;
  onRefresh: () => void;
}

export default function ClientDetailModal({ client, onClose, onRefresh }: ClientDetailModalProps) {
  const [uploading, setUploading] = useState(false);
  const [actionLoading, setActionLoading] = useState("");
  const [docType, setDocType] = useState("W-2 Forms");
  const fileRef = useRef<HTMLInputElement>(null);

  const handleUpload = async (e: React.FormEvent) => {
    e.preventDefault();
    const file = fileRef.current?.files?.[0];
    if (!file) return;
    setUploading(true);
    try {
      await uploadDocument(client.id, file, docType);
      onRefresh();
    } catch (err) {
      console.error(err);
    }
    setUploading(false);
  };

  const handleAction = async (action: string) => {
    setActionLoading(action);
    try {
      if (action === "engagement_letter") {
        await triggerEngagementLetter(client.id, client.scope_of_services || "Individual Tax Return");
      } else if (action === "check_documents") {
        await checkDocuments(client.id);
      } else if (action === "analysis") {
        await triggerAnalysis(client.id);
      }
      onRefresh();
    } catch (err) {
      console.error(err);
    }
    setActionLoading("");
  };

  const handleChecklistToggle = async (itemId: number, received: boolean) => {
    await updateChecklistItem(itemId, !received);
    onRefresh();
  };

  const handleAdvanceStage = async (stage: string) => {
    await updateClient(client.id, { stage });
    onRefresh();
  };

  return (
    <div
      className="fixed inset-0 z-50 flex items-center justify-center p-4"
      style={{ background: "rgba(var(--ink), 0.35)", backdropFilter: "blur(4px)" }}
      onClick={onClose}
    >
      <div
        className="glass rounded-2xl w-full max-w-2xl max-h-[90vh] overflow-y-auto custom-scroll fade-up shadow-2xl"
        onClick={(e) => e.stopPropagation()}
      >
        {/* Header */}
        <div
          className="flex items-center justify-between px-6 py-4"
          style={{ borderBottom: "1px solid rgba(var(--mist), 0.5)" }}
        >
          <div>
            <h2 className="font-display text-xl" style={{ color: "rgb(var(--ink))" }}>{client.name}</h2>
            <p className="text-sm mt-0.5" style={{ color: "rgba(var(--ink), 0.4)" }}>{client.email}</p>
          </div>
          <div className="flex items-center gap-3">
            <span className="pill flex items-center gap-1.5" style={{ background: "rgba(var(--grove), 0.08)", color: "rgb(var(--grove))" }}>
              <span className={`w-1.5 h-1.5 rounded-full ${STAGE_DOT_COLORS[client.stage]}`} />
              {STAGE_LABELS[client.stage]}
            </span>
            <button onClick={onClose} style={{ color: "rgba(var(--ink), 0.3)" }} className="hover:opacity-70 transition-opacity">
              <X size={20} />
            </button>
          </div>
        </div>

        <div className="px-6 py-5 space-y-6">
          {/* Client Info */}
          <div className="grid grid-cols-2 gap-3 text-sm">
            {client.phone && <InfoRow label="Phone" value={client.phone} />}
            {client.company && <InfoRow label="Company" value={client.company} />}
            {client.state && <InfoRow label="State" value={client.state} />}
            {client.referral_source && <InfoRow label="Referral" value={client.referral_source} />}
            {client.scope_of_services && <InfoRow label="Services" value={client.scope_of_services} />}
            {client.fee_estimate && <InfoRow label="Fee Estimate" value={`$${client.fee_estimate}`} />}
            {client.folder_url && (
              <div className="col-span-2">
                <span style={{ color: "rgba(var(--ink), 0.4)" }}>Folder:</span>{" "}
                <a
                  href={client.folder_url}
                  target="_blank"
                  className="inline-flex items-center gap-1 hover:underline"
                  style={{ color: "rgb(var(--grove))" }}
                >
                  Google Drive <ExternalLink size={12} />
                </a>
              </div>
            )}
            {client.meeting_summary && (
              <div className="col-span-2">
                <span style={{ color: "rgba(var(--ink), 0.4)" }}>Meeting Summary:</span>
                <p
                  className="mt-1 text-sm p-3 rounded-lg"
                  style={{ background: "rgba(var(--mist), 0.3)", color: "rgb(var(--ink))" }}
                >
                  {client.meeting_summary}
                </p>
              </div>
            )}
          </div>

          {/* Actions */}
          <div>
            <h3 className="text-xs font-semibold uppercase tracking-wider mb-2" style={{ color: "rgba(var(--ink), 0.4)" }}>
              Actions
            </h3>
            <div className="flex flex-wrap gap-2">
              <button
                onClick={() => handleAction("engagement_letter")}
                disabled={actionLoading === "engagement_letter"}
                className="btn-primary text-xs py-1.5"
              >
                {actionLoading === "engagement_letter" ? "Sending..." : "Send Engagement Letter"}
              </button>
              <button
                onClick={() => handleAction("check_documents")}
                disabled={actionLoading === "check_documents"}
                className="btn-ghost text-xs py-1.5"
                style={{ color: "rgb(var(--accent))", borderColor: "rgba(var(--accent), 0.3)" }}
              >
                {actionLoading === "check_documents" ? "Checking..." : "Check Documents"}
              </button>
              <button
                onClick={() => handleAction("analysis")}
                disabled={actionLoading === "analysis"}
                className="btn-ghost text-xs py-1.5"
              >
                {actionLoading === "analysis" ? "Analyzing..." : "Run Analysis"}
              </button>
              <select
                onChange={(e) => handleAdvanceStage(e.target.value)}
                value=""
                className="input-refined text-xs py-1.5 w-auto"
              >
                <option value="" disabled>Advance Stage...</option>
                {Object.entries(STAGE_LABELS).map(([key, label]) => (
                  <option key={key} value={key}>{label}</option>
                ))}
              </select>
            </div>
          </div>

          {/* Document Checklist */}
          <div>
            <h3 className="text-xs font-semibold uppercase tracking-wider mb-2" style={{ color: "rgba(var(--ink), 0.4)" }}>
              Document Checklist
            </h3>
            <div className="space-y-0.5">
              {client.checklist_items.map((item) => (
                <div
                  key={item.id}
                  className="flex items-center gap-2.5 py-2 px-2 rounded-lg cursor-pointer transition-colors"
                  style={{ background: "transparent" }}
                  onMouseEnter={(e) => e.currentTarget.style.background = "rgba(var(--mist), 0.3)"}
                  onMouseLeave={(e) => e.currentTarget.style.background = "transparent"}
                  onClick={() => handleChecklistToggle(item.id, item.received)}
                >
                  {item.received ? (
                    <Check size={15} style={{ color: "rgb(var(--grove))" }} />
                  ) : (
                    <Circle size={15} style={{ color: "rgba(var(--ink), 0.15)" }} />
                  )}
                  <span
                    className={`text-sm ${item.received ? "line-through" : ""}`}
                    style={{ color: item.received ? "rgba(var(--ink), 0.35)" : "rgb(var(--ink))" }}
                  >
                    {item.doc_name}
                  </span>
                  {item.required && !item.received && (
                    <span className="ml-auto pill" style={{ background: "rgba(var(--rose), 0.1)", color: "rgb(var(--rose))" }}>
                      Required
                    </span>
                  )}
                </div>
              ))}
            </div>
          </div>

          {/* Upload Document */}
          <div>
            <h3 className="text-xs font-semibold uppercase tracking-wider mb-2" style={{ color: "rgba(var(--ink), 0.4)" }}>
              Upload Document
            </h3>
            <form onSubmit={handleUpload} className="flex items-center gap-2">
              <select value={docType} onChange={(e) => setDocType(e.target.value)} className="input-refined text-sm py-1.5 w-auto">
                <option>W-2 Forms</option>
                <option>1099 Forms</option>
                <option>Prior Year Tax Return</option>
                <option>Property Tax Statements</option>
                <option>Mortgage Interest</option>
                <option>Charitable Donations</option>
                <option>Business Expenses</option>
                <option>Health Insurance</option>
                <option>Other</option>
              </select>
              <input ref={fileRef} type="file" className="text-sm flex-1" style={{ color: "rgba(var(--ink), 0.6)" }} />
              <button type="submit" disabled={uploading} className="btn-primary text-xs py-1.5">
                <Upload size={13} /> {uploading ? "Uploading..." : "Upload"}
              </button>
            </form>
          </div>

          {/* Documents */}
          {client.documents.length > 0 && (
            <div>
              <h3 className="text-xs font-semibold uppercase tracking-wider mb-2" style={{ color: "rgba(var(--ink), 0.4)" }}>
                Uploaded Documents
              </h3>
              <div className="space-y-1">
                {client.documents.map((doc) => (
                  <div key={doc.id} className="flex items-center justify-between text-sm py-1.5">
                    <span style={{ color: "rgb(var(--ink))" }}>{doc.filename}</span>
                    <span className="pill" style={{ background: "rgba(var(--ink), 0.05)", color: "rgba(var(--ink), 0.4)" }}>
                      {doc.doc_type}
                    </span>
                  </div>
                ))}
              </div>
            </div>
          )}

          {/* Activities */}
          <div>
            <h3 className="text-xs font-semibold uppercase tracking-wider mb-2" style={{ color: "rgba(var(--ink), 0.4)" }}>
              Activity Log
            </h3>
            <div className="space-y-0 max-h-48 overflow-y-auto custom-scroll">
              {client.activities.map((a) => (
                <div
                  key={a.id}
                  className="text-sm py-2"
                  style={{ borderBottom: "1px solid rgba(var(--mist), 0.3)" }}
                >
                  <span style={{ color: "rgb(var(--ink))" }}>{a.action}</span>
                  {a.devin_session_id && (
                    <span className="ml-2 text-xs font-mono" style={{ color: "rgb(var(--accent))" }}>
                      [{a.devin_session_id}]
                    </span>
                  )}
                  <span className="ml-2 text-xs" style={{ color: "rgba(var(--ink), 0.25)" }}>
                    {new Date(a.created_at).toLocaleString()}
                  </span>
                </div>
              ))}
              {client.activities.length === 0 && (
                <p className="text-xs text-center py-4" style={{ color: "rgba(var(--ink), 0.25)" }}>No activity yet</p>
              )}
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}

function InfoRow({ label, value }: { label: string; value: string }) {
  return (
    <div>
      <span style={{ color: "rgba(var(--ink), 0.4)" }}>{label}:</span>{" "}
      <span style={{ color: "rgb(var(--ink))" }}>{value}</span>
    </div>
  );
}
