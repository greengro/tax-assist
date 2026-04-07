import { Users, Mail, FileSignature, Plus, Zap } from "lucide-react";
import { PipelineStats } from "../lib/types";

interface HeaderProps {
  stats: PipelineStats | null;
  onAddClient: () => void;
  onSimulateWebhook: () => void;
}

export default function Header({ stats, onAddClient, onSimulateWebhook }: HeaderProps) {
  return (
    <header className="relative noise overflow-hidden">
      <div
        className="absolute inset-0"
        style={{
          background: "linear-gradient(135deg, rgb(var(--grove)) 0%, rgb(18 50 36) 100%)",
        }}
      />
      <div className="relative z-10 max-w-screen-2xl mx-auto px-6 py-5 flex items-center justify-between flex-wrap gap-4">
        <div className="flex items-center gap-4 fade-up" style={{ animationDelay: "0ms" }}>
          <div
            className="w-10 h-10 rounded-lg flex items-center justify-center font-display text-lg tracking-tight"
            style={{ background: "rgba(var(--accent), 0.9)", color: "rgb(var(--ink))" }}
          >
            GG
          </div>
          <div>
            <h1 className="font-display text-xl tracking-tight" style={{ color: "rgb(var(--parchment))" }}>
              Green Grove
            </h1>
            <p className="text-xs tracking-widest uppercase" style={{ color: "rgba(var(--accent-light), 0.7)" }}>
              Engagement Management
            </p>
          </div>
        </div>

        <div className="flex items-center gap-8 fade-up" style={{ animationDelay: "100ms" }}>
          {stats && (
            <div className="flex gap-6">
              <Stat icon={<Users size={14} />} value={stats.total_clients} label="Clients" />
              <Stat icon={<Mail size={14} />} value={stats.emails_sent} label="Emails" />
              <Stat icon={<FileSignature size={14} />} value={stats.signature_requests} label="Signed" />
            </div>
          )}
        </div>

        <div className="flex gap-2.5 fade-up" style={{ animationDelay: "200ms" }}>
          <button onClick={onAddClient} className="btn-primary">
            <Plus size={15} /> New Client
          </button>
          <button
            onClick={onSimulateWebhook}
            className="btn-ghost"
            style={{ color: "rgb(var(--parchment))", borderColor: "rgba(var(--parchment), 0.25)" }}
          >
            <Zap size={15} /> Simulate
          </button>
        </div>
      </div>
    </header>
  );
}

function Stat({ icon, value, label }: { icon: React.ReactNode; value: number; label: string }) {
  return (
    <div className="text-center">
      <div className="flex items-center gap-1.5 justify-center" style={{ color: "rgb(var(--accent))" }}>
        {icon}
        <span className="text-xl font-semibold tabular-nums" style={{ color: "rgb(var(--parchment))" }}>
          {value}
        </span>
      </div>
      <span className="text-xs uppercase tracking-widest" style={{ color: "rgba(var(--parchment), 0.4)" }}>
        {label}
      </span>
    </div>
  );
}
