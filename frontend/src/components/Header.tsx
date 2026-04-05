import { Users, Mail, FileSignature, Plus, Webhook } from "lucide-react";
import { PipelineStats } from "../lib/types";

interface HeaderProps {
  stats: PipelineStats | null;
  onAddClient: () => void;
  onSimulateWebhook: () => void;
}

export default function Header({ stats, onAddClient, onSimulateWebhook }: HeaderProps) {
  return (
    <header className="bg-emerald-900 text-white px-6 py-4 shadow-lg">
      <div className="max-w-screen-2xl mx-auto flex items-center justify-between flex-wrap gap-4">
        <div className="flex items-center gap-3">
          <div className="w-8 h-8 bg-emerald-500 rounded-lg flex items-center justify-center font-bold text-sm">
            GG
          </div>
          <div>
            <h1 className="text-lg font-bold tracking-tight">Green Grove Tax Services</h1>
            <p className="text-emerald-300 text-xs">Engagement Management Dashboard</p>
          </div>
        </div>

        <div className="flex items-center gap-6 flex-wrap">
          {stats && (
            <div className="flex gap-5">
              <StatItem icon={<Users size={16} />} value={stats.total_clients} label="Clients" />
              <StatItem icon={<Mail size={16} />} value={stats.emails_sent} label="Emails" />
              <StatItem icon={<FileSignature size={16} />} value={stats.signature_requests} label="Signatures" />
            </div>
          )}

          <div className="flex gap-2">
            <button
              onClick={onAddClient}
              className="flex items-center gap-1.5 px-3 py-2 bg-emerald-600 hover:bg-emerald-500 rounded-lg text-sm font-semibold transition-colors"
            >
              <Plus size={16} /> Add Client
            </button>
            <button
              onClick={onSimulateWebhook}
              className="flex items-center gap-1.5 px-3 py-2 border border-emerald-500 hover:bg-emerald-800 rounded-lg text-sm font-semibold transition-colors"
            >
              <Webhook size={16} /> Simulate Webhook
            </button>
          </div>
        </div>
      </div>
    </header>
  );
}

function StatItem({ icon, value, label }: { icon: React.ReactNode; value: number; label: string }) {
  return (
    <div className="text-center">
      <div className="flex items-center gap-1 justify-center text-emerald-300">
        {icon}
        <span className="text-xl font-bold text-emerald-300">{value}</span>
      </div>
      <span className="text-xs text-emerald-400 uppercase tracking-wider">{label}</span>
    </div>
  );
}
