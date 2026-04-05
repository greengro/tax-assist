import { Bot, Mail, FolderOpen, FileSignature, ClipboardCheck, AlertCircle } from "lucide-react";
import { ActivityFeedItem } from "../lib/types";

interface ActivityFeedProps {
  activities: ActivityFeedItem[];
}

function getIcon(action: string) {
  if (action.toLowerCase().includes("devin") || action.toLowerCase().includes("session"))
    return <Bot size={14} className="text-purple-500" />;
  if (action.toLowerCase().includes("email"))
    return <Mail size={14} className="text-blue-500" />;
  if (action.toLowerCase().includes("folder"))
    return <FolderOpen size={14} className="text-yellow-600" />;
  if (action.toLowerCase().includes("signature") || action.toLowerCase().includes("engagement"))
    return <FileSignature size={14} className="text-emerald-600" />;
  if (action.toLowerCase().includes("document") || action.toLowerCase().includes("checklist"))
    return <ClipboardCheck size={14} className="text-orange-500" />;
  return <AlertCircle size={14} className="text-gray-400" />;
}

function timeAgo(dateStr: string) {
  const now = new Date();
  const d = new Date(dateStr);
  const diff = Math.floor((now.getTime() - d.getTime()) / 1000);
  if (diff < 60) return `${diff}s ago`;
  if (diff < 3600) return `${Math.floor(diff / 60)}m ago`;
  if (diff < 86400) return `${Math.floor(diff / 3600)}h ago`;
  return d.toLocaleDateString();
}

export default function ActivityFeed({ activities }: ActivityFeedProps) {
  return (
    <div className="bg-white rounded-xl shadow-sm p-4">
      <h2 className="text-sm font-bold uppercase tracking-wide text-gray-500 mb-3">
        Activity Feed
      </h2>
      <div className="space-y-2 max-h-96 overflow-y-auto">
        {activities.length === 0 && (
          <p className="text-sm text-gray-400 text-center py-6">No activity yet</p>
        )}
        {activities.map((a) => (
          <div key={a.id} className="flex gap-2 items-start py-2 border-b border-gray-50 last:border-0">
            <div className="mt-0.5">{getIcon(a.action)}</div>
            <div className="flex-1 min-w-0">
              <p className="text-sm text-gray-800">
                <span className="font-semibold">{a.client_name}</span>{" "}
                <span className="text-gray-500">&mdash; {a.action}</span>
              </p>
              {a.details && (
                <p className="text-xs text-gray-400 truncate">{a.details}</p>
              )}
              {a.devin_session_id && (
                <p className="text-xs text-purple-500 font-mono">
                  Devin: {a.devin_session_id}
                </p>
              )}
            </div>
            <span className="text-xs text-gray-400 whitespace-nowrap">{timeAgo(a.created_at)}</span>
          </div>
        ))}
      </div>
    </div>
  );
}
