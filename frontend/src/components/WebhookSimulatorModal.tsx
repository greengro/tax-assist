import { X, Webhook } from "lucide-react";
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

  // Calendly form
  const [name, setName] = useState("");
  const [email, setEmail] = useState("");
  const [meetingTime, setMeetingTime] = useState("");

  // Meeting notes form
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
    <div className="fixed inset-0 bg-black/40 z-50 flex items-center justify-center p-4" onClick={onClose}>
      <div className="bg-white rounded-2xl w-full max-w-lg shadow-2xl" onClick={(e) => e.stopPropagation()}>
        <div className="flex items-center justify-between px-6 py-4 border-b border-gray-100">
          <div className="flex items-center gap-2">
            <Webhook size={18} className="text-emerald-600" />
            <h2 className="text-lg font-bold text-gray-900">Simulate Webhook</h2>
          </div>
          <button onClick={onClose} className="text-gray-400 hover:text-gray-600">
            <X size={20} />
          </button>
        </div>

        <div className="flex border-b border-gray-100">
          <button
            onClick={() => setTab("calendly")}
            className={`flex-1 py-2.5 text-sm font-semibold transition-colors ${
              tab === "calendly"
                ? "text-emerald-700 border-b-2 border-emerald-600"
                : "text-gray-400 hover:text-gray-600"
            }`}
          >
            Calendly Booking
          </button>
          <button
            onClick={() => setTab("meeting")}
            className={`flex-1 py-2.5 text-sm font-semibold transition-colors ${
              tab === "meeting"
                ? "text-emerald-700 border-b-2 border-emerald-600"
                : "text-gray-400 hover:text-gray-600"
            }`}
          >
            Meeting Notes
          </button>
        </div>

        <div className="px-6 py-4">
          {tab === "calendly" ? (
            <form onSubmit={handleCalendly} className="space-y-3">
              <FormField label="Full Name" value={name} onChange={setName} placeholder="John Smith" required />
              <FormField label="Email" value={email} onChange={setEmail} placeholder="john@example.com" type="email" required />
              <FormField
                label="Meeting Time"
                value={meetingTime}
                onChange={setMeetingTime}
                type="datetime-local"
              />
              <button
                type="submit"
                disabled={loading}
                className="w-full py-2.5 bg-emerald-600 text-white rounded-lg font-semibold hover:bg-emerald-700 disabled:opacity-50 transition-colors"
              >
                {loading ? "Processing..." : "Simulate Calendly Booking"}
              </button>
            </form>
          ) : (
            <form onSubmit={handleMeeting} className="space-y-3">
              <FormField
                label="Client Email"
                value={meetingEmail}
                onChange={setMeetingEmail}
                placeholder="john@example.com"
                type="email"
                required
              />
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">Transcript</label>
                <textarea
                  value={transcript}
                  onChange={(e) => setTranscript(e.target.value)}
                  rows={4}
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg text-sm focus:ring-2 focus:ring-emerald-500 focus:border-emerald-500"
                />
              </div>
              <FormField label="Scope of Services" value={scope} onChange={setScope} />
              <FormField label="Fee Estimate ($)" value={feeEstimate} onChange={setFeeEstimate} type="number" />
              <button
                type="submit"
                disabled={loading}
                className="w-full py-2.5 bg-emerald-600 text-white rounded-lg font-semibold hover:bg-emerald-700 disabled:opacity-50 transition-colors"
              >
                {loading ? "Processing..." : "Submit Meeting Notes"}
              </button>
            </form>
          )}

          {result && (
            <div className="mt-4 p-3 bg-emerald-50 border border-emerald-200 rounded-lg text-sm text-emerald-800">
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
      <label className="block text-sm font-medium text-gray-700 mb-1">{label}</label>
      <input
        type={type}
        value={value}
        onChange={(e) => onChange(e.target.value)}
        placeholder={placeholder}
        required={required}
        className="w-full px-3 py-2 border border-gray-300 rounded-lg text-sm focus:ring-2 focus:ring-emerald-500 focus:border-emerald-500"
      />
    </div>
  );
}
