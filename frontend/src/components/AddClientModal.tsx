import { X, UserPlus } from "lucide-react";
import { useState } from "react";
import { createClient } from "../lib/api";

interface AddClientModalProps {
  onClose: () => void;
  onDone: () => void;
}

export default function AddClientModal({ onClose, onDone }: AddClientModalProps) {
  const [loading, setLoading] = useState(false);
  const [name, setName] = useState("");
  const [email, setEmail] = useState("");
  const [phone, setPhone] = useState("");
  const [company, setCompany] = useState("");
  const [state, setState] = useState("");
  const [referral, setReferral] = useState("");

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    try {
      await createClient({
        name,
        email,
        phone: phone || undefined,
        company: company || undefined,
        state: state || undefined,
        referral_source: referral || undefined,
      });
      onDone();
      onClose();
    } catch (err) {
      console.error(err);
    }
    setLoading(false);
  };

  return (
    <div
      className="fixed inset-0 z-50 flex items-center justify-center p-4"
      style={{ background: "rgba(var(--ink), 0.35)", backdropFilter: "blur(4px)" }}
      onClick={onClose}
    >
      <div className="glass rounded-2xl w-full max-w-md shadow-2xl fade-up" onClick={(e) => e.stopPropagation()}>
        <div
          className="flex items-center justify-between px-6 py-4"
          style={{ borderBottom: "1px solid rgba(var(--mist), 0.5)" }}
        >
          <div className="flex items-center gap-2.5">
            <UserPlus size={16} style={{ color: "rgb(var(--grove))" }} />
            <h2 className="font-display text-lg" style={{ color: "rgb(var(--ink))" }}>New Client</h2>
          </div>
          <button onClick={onClose} style={{ color: "rgba(var(--ink), 0.3)" }} className="hover:opacity-70 transition-opacity">
            <X size={20} />
          </button>
        </div>

        <form onSubmit={handleSubmit} className="px-6 py-5 space-y-3">
          <Field label="Full Name" value={name} onChange={setName} required />
          <Field label="Email" value={email} onChange={setEmail} type="email" required />
          <Field label="Phone" value={phone} onChange={setPhone} type="tel" />
          <Field label="Company" value={company} onChange={setCompany} />
          <Field label="State" value={state} onChange={setState} placeholder="CA" />
          <Field label="Referral Source" value={referral} onChange={setReferral} placeholder="Website, Referral, etc." />
          <button type="submit" disabled={loading} className="btn-primary w-full justify-center py-2.5 mt-1">
            {loading ? "Adding..." : "Add Client"}
          </button>
        </form>
      </div>
    </div>
  );
}

function Field({
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
