import React, { useEffect, useState } from 'react';
import { ShieldAlert, Filter, RefreshCw, AlertTriangle, ShieldX, Clock, ExternalLink } from 'lucide-react';
import { SafetyEvent } from '../types';
import { api } from '../services/api';

interface SafetyEventsPageProps {
  onSelectWorkflow: (id: string) => void;
}

export const SafetyEventsPage: React.FC<SafetyEventsPageProps> = ({
  onSelectWorkflow,
}) => {
  const [events, setEvents] = useState<SafetyEvent[]>([]);
  const [loading, setLoading] = useState<boolean>(true);
  const [severityFilter, setSeverityFilter] = useState<string>('ALL');

  const fetchEvents = async () => {
    try {
      setLoading(true);
      const data = await api.listSafetyEvents(severityFilter === 'ALL' ? undefined : severityFilter);
      setEvents(data);
    } catch (err) {
      console.error('Error fetching safety events:', err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchEvents();
  }, [severityFilter]);

  const getSeverityBadge = (severity: string) => {
    switch (severity) {
      case 'CRITICAL':
        return <span className="px-2.5 py-0.5 rounded text-[10px] font-bold uppercase bg-rose-500/20 text-rose-400 border border-rose-500/30">CRITICAL</span>;
      case 'HIGH':
        return <span className="px-2.5 py-0.5 rounded text-[10px] font-bold uppercase bg-amber-500/20 text-amber-400 border border-amber-500/30">HIGH</span>;
      case 'WARNING':
        return <span className="px-2.5 py-0.5 rounded text-[10px] font-bold uppercase bg-yellow-500/20 text-yellow-400 border border-yellow-500/30">WARNING</span>;
      default:
        return <span className="px-2.5 py-0.5 rounded text-[10px] font-bold uppercase bg-slate-800 text-slate-300">INFO</span>;
    }
  };

  return (
    <div className="space-y-6 animate-fadeIn">
      {/* Header */}
      <div className="flex flex-col sm:flex-row justify-between items-start sm:items-center gap-4">
        <div>
          <h1 className="text-2xl font-bold tracking-tight text-white flex items-center gap-2">
            <ShieldAlert className="w-6 h-6 text-rose-400" />
            Safety Events & Audit Log
          </h1>
          <p className="text-sm text-slate-400 mt-1">
            Real-time feed of all pre-execution gate decisions, repeated call blocks, loop detections, and approval events.
          </p>
        </div>
        <button
          id="refresh-safety-events-btn"
          onClick={fetchEvents}
          className="flex items-center gap-2 px-3 py-1.5 rounded-lg border border-slate-700 bg-slate-800 hover:bg-slate-700 text-slate-200 text-xs font-medium transition"
        >
          <RefreshCw className={`w-3.5 h-3.5 ${loading ? 'animate-spin' : ''}`} />
          Refresh
        </button>
      </div>

      {/* Severity Filter Tabs */}
      <div className="flex items-center gap-2 glass-panel p-2 rounded-xl border border-slate-800 overflow-x-auto">
        <span className="text-xs text-slate-400 px-3 font-semibold uppercase tracking-wider flex items-center gap-1.5">
          <Filter className="w-3.5 h-3.5" /> Severity:
        </span>
        {['ALL', 'CRITICAL', 'HIGH', 'WARNING', 'INFO'].map((sev) => (
          <button
            key={sev}
            id={`filter-severity-${sev.toLowerCase()}`}
            onClick={() => setSeverityFilter(sev)}
            className={`px-3 py-1 rounded-lg text-xs font-medium transition ${
              severityFilter === sev
                ? 'bg-indigo-600 text-white'
                : 'text-slate-400 hover:text-slate-200 hover:bg-slate-800'
            }`}
          >
            {sev}
          </button>
        ))}
      </div>

      {/* Events Feed */}
      <div className="space-y-3">
        {loading && events.length === 0 ? (
          <div className="glass-panel py-16 text-center text-slate-400 text-sm rounded-2xl border border-slate-800">
            Loading safety audit logs...
          </div>
        ) : events.length === 0 ? (
          <div className="glass-panel py-16 text-center text-slate-400 text-sm rounded-2xl border border-slate-800">
            No safety events recorded for severity "{severityFilter}".
          </div>
        ) : (
          events.map((evt) => (
            <div
              key={evt.id}
              id={`safety-event-${evt.id.substring(0, 8)}`}
              className="glass-panel p-5 rounded-2xl border border-slate-800/80 hover:border-slate-700 transition space-y-3"
            >
              <div className="flex flex-col sm:flex-row justify-between items-start sm:items-center gap-2">
                <div className="flex items-center gap-3">
                  {getSeverityBadge(evt.severity)}
                  <span className="font-mono text-sm font-bold text-white">
                    {evt.rule_name}
                  </span>
                  <span className={`text-xs font-mono font-semibold px-2 py-0.5 rounded ${
                    evt.decision === 'BLOCK' ? 'bg-rose-500/10 text-rose-400' :
                    evt.decision === 'REQUIRE_APPROVAL' ? 'bg-amber-500/10 text-amber-400' :
                    'bg-emerald-500/10 text-emerald-400'
                  }`}>
                    Action: {evt.decision}
                  </span>
                </div>
                <div className="flex items-center gap-3 text-xs font-mono text-slate-400">
                  <span className="flex items-center gap-1">
                    <Clock className="w-3.5 h-3.5 text-slate-500" />
                    {new Date(evt.created_at).toLocaleString()}
                  </span>
                  <button
                    id={`inspect-wf-link-${evt.id.substring(0, 8)}`}
                    onClick={() => onSelectWorkflow(evt.workflow_id)}
                    className="flex items-center gap-1 text-indigo-400 hover:text-indigo-300 font-medium"
                  >
                    Inspect Workflow <ExternalLink className="w-3 h-3" />
                  </button>
                </div>
              </div>

              {/* Event Details JSON */}
              {evt.details && (
                <div className="bg-[#080C14] p-3 rounded-xl border border-slate-800/80 font-mono text-[11px] text-slate-300 overflow-x-auto">
                  <pre>{JSON.stringify(evt.details, null, 2)}</pre>
                </div>
              )}
            </div>
          ))
        )}
      </div>
    </div>
  );
};
