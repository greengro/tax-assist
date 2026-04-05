import { useEffect, useState } from "react";
import { getEmailLog, getSignatureLog } from "../lib/api";

interface EmailEntry {
  to: string;
  subject: string;
  body: string;
  sent_at: string;
}

interface SignatureEntry {
  client_name: string;
  client_email: string;
  document_name: string;
  sent_at: string;
}

export default function EmailLog() {
  const [emails, setEmails] = useState<EmailEntry[]>([]);
  const [signatures, setSignatures] = useState<SignatureEntry[]>([]);
  const [tab, setTab] = useState<"emails" | "signatures">("emails");

  useEffect(() => {
    getEmailLog().then(setEmails).catch(console.error);
    getSignatureLog().then(setSignatures).catch(console.error);
  }, []);

  return (
    <div className="glass rounded-xl p-5 fade-up" style={{ animationDelay: "600ms" }}>
      <h2 className="font-display text-base mb-4" style={{ color: "rgb(var(--ink))" }}>
        Communications
      </h2>

      <div className="flex gap-2 mb-4">
        <button
          onClick={() => setTab("emails")}
          className="pill transition-colors"
          style={{
            background: tab === "emails" ? "rgba(var(--grove), 0.1)" : "rgba(var(--ink), 0.04)",
            color: tab === "emails" ? "rgb(var(--grove))" : "rgba(var(--ink), 0.4)",
          }}
        >
          Emails ({emails.length})
        </button>
        <button
          onClick={() => setTab("signatures")}
          className="pill transition-colors"
          style={{
            background: tab === "signatures" ? "rgba(var(--accent), 0.12)" : "rgba(var(--ink), 0.04)",
            color: tab === "signatures" ? "rgb(var(--accent))" : "rgba(var(--ink), 0.4)",
          }}
        >
          Signatures ({signatures.length})
        </button>
      </div>

      <div className="space-y-2 max-h-64 overflow-y-auto custom-scroll">
        {tab === "emails" &&
          emails.map((e, i) => (
            <div
              key={i}
              className="text-sm p-3 rounded-lg"
              style={{ background: "rgba(var(--mist), 0.25)" }}
            >
              <p className="font-semibold" style={{ color: "rgb(var(--ink))" }}>{e.subject}</p>
              <p className="text-xs mt-0.5" style={{ color: "rgba(var(--ink), 0.4)" }}>To: {e.to}</p>
              <p className="text-xs mt-1 line-clamp-2" style={{ color: "rgba(var(--ink), 0.35)" }}>{e.body}</p>
            </div>
          ))}
        {tab === "signatures" &&
          signatures.map((s, i) => (
            <div
              key={i}
              className="text-sm p-3 rounded-lg"
              style={{ background: "rgba(var(--mist), 0.25)" }}
            >
              <p className="font-semibold" style={{ color: "rgb(var(--ink))" }}>{s.document_name}</p>
              <p className="text-xs mt-0.5" style={{ color: "rgba(var(--ink), 0.4)" }}>
                {s.client_name} ({s.client_email})
              </p>
            </div>
          ))}
        {tab === "emails" && emails.length === 0 && (
          <p className="text-xs text-center py-6" style={{ color: "rgba(var(--ink), 0.25)" }}>No emails sent yet</p>
        )}
        {tab === "signatures" && signatures.length === 0 && (
          <p className="text-xs text-center py-6" style={{ color: "rgba(var(--ink), 0.25)" }}>No signature requests yet</p>
        )}
      </div>
    </div>
  );
}
