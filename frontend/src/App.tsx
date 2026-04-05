import { useEffect, useState, useCallback } from "react";
import Header from "./components/Header";
import PipelineBoard from "./components/PipelineBoard";
import ActivityFeed from "./components/ActivityFeed";
import EmailLog from "./components/EmailLog";
import ClientDetailModal from "./components/ClientDetailModal";
import WebhookSimulatorModal from "./components/WebhookSimulatorModal";
import AddClientModal from "./components/AddClientModal";
import {
  getPipelineSummary,
  getPipelineStats,
  getActivityFeed,
  getClient,
} from "./lib/api";
import {
  PipelineStageSummary,
  PipelineStats,
  ActivityFeedItem,
  Client,
} from "./lib/types";

function App() {
  const [stages, setStages] = useState<PipelineStageSummary[]>([]);
  const [stats, setStats] = useState<PipelineStats | null>(null);
  const [activities, setActivities] = useState<ActivityFeedItem[]>([]);
  const [selectedClient, setSelectedClient] = useState<Client | null>(null);
  const [showWebhook, setShowWebhook] = useState(false);
  const [showAddClient, setShowAddClient] = useState(false);
  const [prefillEmail, setPrefillEmail] = useState<string | undefined>();

  const refresh = useCallback(async () => {
    try {
      const [pipelineData, statsData, activityData] = await Promise.all([
        getPipelineSummary(),
        getPipelineStats(),
        getActivityFeed(30),
      ]);
      setStages(pipelineData);
      setStats(statsData);
      setActivities(activityData);
    } catch (err) {
      console.error("Failed to fetch data:", err);
    }
  }, []);

  useEffect(() => {
    refresh();
    const interval = setInterval(refresh, 5000);
    return () => clearInterval(interval);
  }, [refresh]);

  const handleClientClick = async (clientId: number) => {
    try {
      const client = await getClient(clientId);
      setSelectedClient(client);
    } catch (err) {
      console.error(err);
    }
  };

  const handleProcessMeeting = (email: string) => {
    setPrefillEmail(email);
    setShowWebhook(true);
  };

  const handleRefreshClient = async () => {
    if (selectedClient) {
      const updated = await getClient(selectedClient.id);
      setSelectedClient(updated);
    }
    refresh();
  };

  return (
    <div className="min-h-screen">
      <Header
        stats={stats}
        onAddClient={() => setShowAddClient(true)}
        onSimulateWebhook={() => {
          setPrefillEmail(undefined);
          setShowWebhook(true);
        }}
      />

      <main className="max-w-screen-2xl mx-auto px-6 py-8 space-y-8">
        {/* Pipeline Board */}
        <section>
          <h2
            className="font-display text-lg mb-4 fade-up"
            style={{ animationDelay: "250ms", color: "rgb(var(--ink))" }}
          >
            Pipeline
          </h2>
          <PipelineBoard
            stages={stages}
            onClientClick={handleClientClick}
            onProcessMeeting={handleProcessMeeting}
            onSendLetter={(id) => {
              handleClientClick(id);
            }}
          />
        </section>

        {/* Activity + Communications */}
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          <ActivityFeed activities={activities} />
          <EmailLog />
        </div>
      </main>

      {/* Modals */}
      {selectedClient && (
        <ClientDetailModal
          client={selectedClient}
          onClose={() => setSelectedClient(null)}
          onRefresh={handleRefreshClient}
        />
      )}
      {showWebhook && (
        <WebhookSimulatorModal
          prefillEmail={prefillEmail}
          onClose={() => setShowWebhook(false)}
          onDone={() => {
            refresh();
          }}
        />
      )}
      {showAddClient && (
        <AddClientModal
          onClose={() => setShowAddClient(false)}
          onDone={() => {
            refresh();
          }}
        />
      )}
    </div>
  );
}

export default App
