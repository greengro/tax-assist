import { Bot, Mail, FolderOpen, FileSignature, ClipboardCheck, Circle } from "lucide-react";
import { ActivityFeedItem } from "../lib/types";

interface ActivityFeedProps {
  activities: ActivityFeedItem[];
}

function getIcon(action: string) {
  const base = "flex-shrink-0";
  if (action.toLowerCase().includes("devin") || action.toLowerCase().includes("session"))
    return <Bot size={13} className={base} style={{ color: "rgb(var(--accent))" }} />;
  if (action.toLowerCase().includes("email"))
    return <Mail size={13} className={base} style={{ color: "rgb(var(--grove))" }} />;
  if (action.toLowerCase().includes("folder"))
    return <FolderOpen size={13} className={base} style={{ color: "rgb(var(--accent))" }} />;
  if (action.toLowerCase().includes("signature") || action.toLowerCase().includes("engagement"))
    return <FileSignature size={13} className={base} style={{ color: "rgb(var(--grove))" }} />;
  if (action.toLowerCase().includes("document") || action.toLowerCase().includes("checklist"))
    return <ClipboardCheck size={13} className={base} style={{ color: "rgb(var(--accent))" }} />;
  return <Circle size={13} className={base} style={{ color: "rgba(var(--ink), 0.2)" }} />;
}

function timeAgo(dateStr: string) {
  const now = new Date();
  const d = new Date(dateStr);
  const diff = Math.floor((now.getTime() - d.getTime()) / 1000);
  if (diff < 60) return `${diff}s`;
  if (diff < 3600) return `${Math.floor(diff / 60)}m`;
  if (diff < 86400) return `${Math.floor(diff / 3600)}h`;
  return d.toLocaleDateString();
}

export default function ActivityFeed({ activities }: ActivityFeedProps) {
  return (
    <div className="glass rounded-xl p-5 fade-up" style={{ animationDelay: "500ms" }}>
      <h2 className="font-display text-base mb-4" style={{ color: "rgb(var(--ink))" }}>
        Activity
      </h2>
      <div className="space-y-0 max-h-96 overflow-y-auto custom-scroll">
        {activities.length === 0 && (
          <p className="text-sm text-center py-8" style={{ color: "rgba(var(--ink), 0.25)" }}>
            No activity yet
          </p>
        )}
        {activities.map((a) => (
          <div
            key={a.id}
            className="flex gap-3 items-start py-2.5"
            style={{ borderBottom: "1px solid rgba(var(--mist), 0.4)" }}
          >
            <div className="mt-1">{getIcon(a.action)}</div>
            <div className="flex-1 min-w-0">
              <p className="text-sm">
                <span className="font-semibold" style={{ color: "rgb(var(--ink))" }}>{a.client_name}</span>
                <span style={{ color: "rgba(var(--ink), 0.4)" }}> &mdash; {a.action}</span>
              </p>
              {a.details && (
                <p className="text-xs truncate mt-0.5" style={{ color: "rgba(var(--ink), 0.35)" }}>{a.details}</p>
              )}
              {a.devin_session_id && (
                <p className="text-xs font-mono mt-0.5" style={{ color: "rgb(var(--accent))" }}>
                  {a.devin_session_id}
                </p>
              )}
            </div>
            <span className="text-xs whitespace-nowrap tabular-nums" style={{ color: "rgba(var(--ink), 0.25)" }}>
              {timeAgo(a.created_at)}
            </span>
          </div>
        ))}
      </div>
    </div>
  );
}
