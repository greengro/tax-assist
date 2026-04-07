import { X, Zap } from "lucide-react";
import { useState } from "react";
import { simulateCalendlyWebhook, submitMeetingNotes } from "../lib/api";

interface WebhookSimulatorModalProps {
  onClose: () => void;
  onDone: () => void;
  prefillEmail?: string;
}

export default function WebhookSimulatorModal({
  onClose,
  onDone,
  prefillEmail,
}: WebhookSimulatorModalProps) {
  const [tab, setTab] = useState<"calendly" | "meeting">(prefillEmail ? "meeting" : "calendly");
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState<string | null>(null);

  const [name, setName] = useState("");
  const [email, setEmail] = useState("");
  const [meetingTime, setMeetingTime] = useState("");

  const [meetingEmail, setMeetingEmail] = useState(prefillEmail || "");
  const [transcript, setTranscript] = useState(
    "Client discussed individual tax return preparation. They have W-2 income, some 1099-INT, and itemized deductions including mortgage interest and charitable contributions. Estimated refund of $3,200. Agreed on fee of $500 for individual return preparation."
  );
  const [scope, setScope] = useState("Individual Tax Return Preparation");
  const [feeEstimate, setFeeEstimate] = useState("500");

  const handleCalendly = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    setResult(null);
    try {
      const res = await simulateCalendlyWebhook({
        name,
        email,
        scheduled_time: meetingTime || new Date().toISOString(),
      });
      setResult(
        `Client created (ID: ${res.client_id}) in stage "${res.stage}". Devin session: ${res.devin_session_id}. Folder: ${res.folder_url}`
      );
      onDone();
    } catch (err) {
      setResult(`Error: ${err}`);
    }
    setLoading(false);
  };

  const handleMeeting = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    setResult(null);
    try {
      const res = await submitMeetingNotes({
        client_email: meetingEmail,
        transcript,
        scope_of_services: scope,
        fee_estimate: Number(feeEstimate),
      });
      setResult(
        `Meeting processed for client ${res.client_id}. Stage: ${res.stage}. Devin session: ${res.devin_session_id}`
      );
      onDone();
    } catch (err) {
      setResult(`Error: ${err}`);
    }
    setLoading(false);
  };

  return (
    <div
      className="fixed inset-0 z-50 flex items-center justify-center p-4"
      style={{ background: "rgba(var(--ink), 0.35)", backdropFilter: "blur(4px)" }}
      onClick={onClose}
    >
      <div className="glass rounded-2xl w-full max-w-lg shadow-2xl fade-up" onClick={(e) => e.stopPropagation()}>
        {/* Header */}
        <div
          className="flex items-center justify-between px-6 py-4"
          style={{ borderBottom: "1px solid rgba(var(--mist), 0.5)" }}
        >
          <div className="flex items-center gap-2.5">
            <Zap size={16} style={{ color: "rgb(var(--accent))" }} />
            <h2 className="font-display text-lg" style={{ color: "rgb(var(--ink))" }}>Simulate Webhook</h2>
          </div>
          <button onClick={onClose} style={{ color: "rgba(var(--ink), 0.3)" }} className="hover:opacity-70 transition-opacity">
            <X size={20} />
          </button>
        </div>

        {/* Tabs */}
        <div className="flex" style={{ borderBottom: "1px solid rgba(var(--mist), 0.5)" }}>
          <button
            onClick={() => setTab("calendly")}
            className="flex-1 py-2.5 text-sm font-semibold transition-colors"
            style={{
              color: tab === "calendly" ? "rgb(var(--grove))" : "rgba(var(--ink), 0.3)",
              borderBottom: tab === "calendly" ? "2px solid rgb(var(--grove))" : "2px solid transparent",
            }}
          >
            Calendly Booking
          </button>
          <button
            onClick={() => setTab("meeting")}
            className="flex-1 py-2.5 text-sm font-semibold transition-colors"
            style={{
              color: tab === "meeting" ? "rgb(var(--grove))" : "rgba(var(--ink), 0.3)",
              borderBottom: tab === "meeting" ? "2px solid rgb(var(--grove))" : "2px solid transparent",
            }}
          >
            Meeting Notes
          </button>
        </div>

        <div className="px-6 py-5">
          {tab === "calendly" ? (
            <form onSubmit={handleCalendly} className="space-y-3">
              <FormField label="Full Name" value={name} onChange={setName} placeholder="John Smith" required />
              <FormField label="Email" value={email} onChange={setEmail} placeholder="john@example.com" type="email" required />
              <FormField label="Meeting Time" value={meetingTime} onChange={setMeetingTime} type="datetime-local" />
              <button type="submit" disabled={loading} className="btn-primary w-full justify-center py-2.5">
                {loading ? "Processing..." : "Simulate Calendly Booking"}
              </button>
            </form>
          ) : (
            <form onSubmit={handleMeeting} className="space-y-3">
              <FormField label="Client Email" value={meetingEmail} onChange={setMeetingEmail} placeholder="john@example.com" type="email" required />
              <div>
                <label className="block text-xs font-semibold uppercase tracking-wider mb-1.5" style={{ color: "rgba(var(--ink), 0.4)" }}>
                  Transcript
                </label>
                <textarea
                  value={transcript}
                  onChange={(e) => setTranscript(e.target.value)}
                  rows={4}
                  className="input-refined"
                />
              </div>
              <FormField label="Scope of Services" value={scope} onChange={setScope} />
              <FormField label="Fee Estimate ($)" value={feeEstimate} onChange={setFeeEstimate} type="number" />
              <button type="submit" disabled={loading} className="btn-primary w-full justify-center py-2.5">
                {loading ? "Processing..." : "Submit Meeting Notes"}
              </button>
            </form>
          )}

          {result && (
            <div
              className="mt-4 p-3 rounded-lg text-sm"
              style={{
                background: "rgba(var(--grove), 0.06)",
                border: "1px solid rgba(var(--grove), 0.15)",
                color: "rgb(var(--grove))",
              }}
            >
              {result}
            </div>
          )}
        </div>
      </div>
    </div>
  );
}

function FormField({
  label,
  value,
  onChange,
  placeholder,
  type = "text",
  required = false,
}: {
  label: string;
  value: string;
  onChange: (v: string) => void;
  placeholder?: string;
  type?: string;
  required?: boolean;
}) {
  return (
    <div>
      <label className="block text-xs font-semibold uppercase tracking-wider mb-1.5" style={{ color: "rgba(var(--ink), 0.4)" }}>
        {label}
      </label>
      <input
        type={type}
        value={value}
        onChange={(e) => onChange(e.target.value)}
        placeholder={placeholder}
        required={required}
        className="input-refined"
      />
    </div>
  );
}
