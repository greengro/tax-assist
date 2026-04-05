import { PipelineStageSummary, STAGE_BORDER_COLORS } from "../lib/types";

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
    <div className="flex gap-3 overflow-x-auto pb-4 px-1">
      {stages.map((stage) => (
        <div
          key={stage.stage}
          className="min-w-52 max-w-64 flex-1 bg-white rounded-xl shadow-sm flex flex-col"
        >
          <div className="px-3 py-2.5 border-b border-gray-100 flex items-center justify-between">
            <h3 className="text-xs font-semibold uppercase tracking-wide text-gray-500">
              {stage.label}
            </h3>
            <span className="bg-gray-100 text-gray-500 px-2 py-0.5 rounded-full text-xs font-semibold">
              {stage.count}
            </span>
          </div>
          <div className="p-2 flex-1 min-h-20 space-y-2">
            {stage.clients.map((client) => (
              <div
                key={client.id}
                onClick={() => onClientClick(client.id)}
                className={`bg-gray-50 rounded-lg p-3 cursor-pointer hover:shadow-md transition-all border-l-3 ${STAGE_BORDER_COLORS[stage.stage]} hover:-translate-y-0.5`}
              >
                <p className="font-semibold text-sm text-gray-900">{client.name}</p>
                <p className="text-xs text-gray-500 truncate">{client.email}</p>
                <p className="text-xs text-gray-400 mt-1">
                  {client.meeting_time
                    ? new Date(client.meeting_time).toLocaleDateString()
                    : new Date(client.created_at).toLocaleDateString()}
                </p>
                {stage.stage === "intro_booked" && (
                  <button
                    onClick={(e) => { e.stopPropagation(); onProcessMeeting(client.email); }}
                    className="mt-2 text-xs px-2 py-1 border border-emerald-600 text-emerald-700 rounded hover:bg-emerald-50 transition-colors"
                  >
                    Process Meeting
                  </button>
                )}
                {stage.stage === "documents_received" && (
                  <button
                    onClick={(e) => { e.stopPropagation(); onSendLetter(client.id); }}
                    className="mt-2 text-xs px-2 py-1 border border-purple-600 text-purple-700 rounded hover:bg-purple-50 transition-colors"
                  >
                    Send Letter
                  </button>
                )}
              </div>
            ))}
            {stage.count === 0 && (
              <p className="text-xs text-gray-400 text-center py-4">No clients</p>
            )}
          </div>
        </div>
      ))}
    </div>
  );
}
