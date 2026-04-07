import { PipelineStageSummary, STAGE_DOT_COLORS } from "../lib/types";

interface PipelineBoardProps {
  stages: PipelineStageSummary[];
  onClientClick: (clientId: number) => void;
  onProcessMeeting: (email: string) => void;
  onSendLetter: (clientId: number) => void;
}

export default function PipelineBoard({
  stages,
  onClientClick,
  onProcessMeeting,
  onSendLetter,
}: PipelineBoardProps) {
  return (
    <div className="flex gap-3 overflow-x-auto pb-4 custom-scroll">
      {stages.map((stage, i) => (
        <div
          key={stage.stage}
          className="min-w-48 max-w-60 flex-1 glass rounded-xl flex flex-col fade-up"
          style={{ animationDelay: `${300 + i * 50}ms` }}
        >
          {/* Column header */}
          <div className="px-3 py-2.5 flex items-center justify-between" style={{ borderBottom: "1px solid rgba(var(--mist), 0.5)" }}>
            <div className="flex items-center gap-2">
              <div className={`w-2 h-2 rounded-full ${STAGE_DOT_COLORS[stage.stage]}`} />
              <h3 className="text-xs font-semibold uppercase tracking-wider" style={{ color: "rgba(var(--ink), 0.45)" }}>
                {stage.label}
              </h3>
            </div>
            {stage.count > 0 && (
              <span
                className="pill"
                style={{ background: "rgba(var(--ink), 0.06)", color: "rgba(var(--ink), 0.5)" }}
              >
                {stage.count}
              </span>
            )}
          </div>

          {/* Cards */}
          <div className="p-2 flex-1 min-h-16 space-y-2">
            {stage.clients.map((client) => (
              <div
                key={client.id}
                onClick={() => onClientClick(client.id)}
                className="rounded-lg p-3 cursor-pointer hover-lift"
                style={{
                  background: "rgba(255,255,255,0.8)",
                  border: "1px solid rgba(var(--mist), 0.4)",
                }}
              >
                <p className="font-semibold text-sm" style={{ color: "rgb(var(--ink))" }}>{client.name}</p>
                <p className="text-xs truncate mt-0.5" style={{ color: "rgba(var(--ink), 0.4)" }}>{client.email}</p>
                <p className="text-xs mt-1.5" style={{ color: "rgba(var(--ink), 0.3)" }}>
                  {client.meeting_time
                    ? new Date(client.meeting_time).toLocaleDateString()
                    : new Date(client.created_at).toLocaleDateString()}
                </p>
                {stage.stage === "intro_booked" && (
                  <button
                    onClick={(e) => { e.stopPropagation(); onProcessMeeting(client.email); }}
                    className="btn-ghost mt-2 text-xs py-1 px-2"
                  >
                    Process Meeting
                  </button>
                )}
                {stage.stage === "documents_received" && (
                  <button
                    onClick={(e) => { e.stopPropagation(); onSendLetter(client.id); }}
                    className="btn-ghost mt-2 text-xs py-1 px-2"
                    style={{ color: "rgb(var(--accent))", borderColor: "rgba(var(--accent), 0.3)" }}
                  >
                    Send Letter
                  </button>
                )}
              </div>
            ))}
            {stage.count === 0 && (
              <p className="text-xs text-center py-6" style={{ color: "rgba(var(--ink), 0.2)" }}>
                &mdash;
              </p>
            )}
          </div>
        </div>
      ))}
    </div>
  );
}
