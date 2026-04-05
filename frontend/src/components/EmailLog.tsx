import { Mail } from "lucide-react";
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
    <div className="bg-white rounded-xl shadow-sm p-4">
      <div className="flex items-center gap-2 mb-3">
        <Mail size={16} className="text-blue-500" />
        <h2 className="text-sm font-bold uppercase tracking-wide text-gray-500">
          Communication Log
        </h2>
      </div>

      <div className="flex gap-2 mb-3">
        <button
          onClick={() => setTab("emails")}
          className={`px-3 py-1 text-xs rounded-full font-semibold ${
            tab === "emails" ? "bg-blue-100 text-blue-700" : "bg-gray-100 text-gray-500"
          }`}
        >
          Emails ({emails.length})
        </button>
        <button
          onClick={() => setTab("signatures")}
          className={`px-3 py-1 text-xs rounded-full font-semibold ${
            tab === "signatures" ? "bg-purple-100 text-purple-700" : "bg-gray-100 text-gray-500"
          }`}
        >
          Signatures ({signatures.length})
        </button>
      </div>

      <div className="space-y-2 max-h-64 overflow-y-auto">
        {tab === "emails" &&
          emails.map((e, i) => (
            <div key={i} className="text-sm p-2 bg-gray-50 rounded">
              <p className="font-semibold text-gray-800">{e.subject}</p>
              <p className="text-xs text-gray-500">To: {e.to}</p>
              <p className="text-xs text-gray-400 mt-1 line-clamp-2">{e.body}</p>
            </div>
          ))}
        {tab === "signatures" &&
          signatures.map((s, i) => (
            <div key={i} className="text-sm p-2 bg-gray-50 rounded">
              <p className="font-semibold text-gray-800">{s.document_name}</p>
              <p className="text-xs text-gray-500">
                {s.client_name} ({s.client_email})
              </p>
            </div>
          ))}
        {tab === "emails" && emails.length === 0 && (
          <p className="text-xs text-gray-400 text-center py-4">No emails sent yet</p>
        )}
        {tab === "signatures" && signatures.length === 0 && (
          <p className="text-xs text-gray-400 text-center py-4">No signature requests yet</p>
        )}
      </div>
    </div>
  );
}
