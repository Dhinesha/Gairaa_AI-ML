import React, { useEffect, useState } from 'react';
import { Sliders, Save, CheckCircle2, Shield, Info, AlertTriangle } from 'lucide-react';
import { SafetyPolicyConfig } from '../types';
import { api } from '../services/api';

export const ConfigurationPage: React.FC = () => {
  const [config, setConfig] = useState<SafetyPolicyConfig | null>(null);
  const [loading, setLoading] = useState<boolean>(true);
  const [saving, setSaving] = useState<boolean>(false);
  const [saveSuccess, setSaveSuccess] = useState<boolean>(false);
  const [sensitiveToolsText, setSensitiveToolsText] = useState<string>('');
  const [sensitiveArgsText, setSensitiveArgsText] = useState<string>('');
  const [rules, setRules] = useState<any[]>([]);

  useEffect(() => {
    const load = async () => {
      try {
        setLoading(true);
        const [cfg, ruleList] = await Promise.all([
          api.getSafetyConfig(),
          api.listSafetyRules(),
        ]);
        setConfig(cfg);
        setRules(ruleList);
        setSensitiveToolsText(cfg.sensitive_tools?.join('\n') || '');
        setSensitiveArgsText(cfg.sensitive_argument_patterns?.join(', ') || '');
      } catch (err) {
        console.error('Error loading config:', err);
      } finally {
        setLoading(false);
      }
    };
    load();
  }, []);

  const handleSave = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!config) return;

    try {
      setSaving(true);
      setSaveSuccess(false);

      const updatedTools = sensitiveToolsText
        .split('\n')
        .map((s) => s.trim())
        .filter((s) => s.length > 0);

      const updatedArgs = sensitiveArgsText
        .split(',')
        .map((s) => s.trim())
        .filter((s) => s.length > 0);

      const payload: SafetyPolicyConfig = {
        ...config,
        sensitive_tools: updatedTools,
        sensitive_argument_patterns: updatedArgs,
      };

      const res = await api.updateSafetyConfig(payload);
      setConfig(res);
      setSaveSuccess(true);
      setTimeout(() => setSaveSuccess(false), 4000);
    } catch (err) {
      console.error('Error updating config:', err);
    } finally {
      setSaving(false);
    }
  };

  if (loading || !config) {
    return (
      <div className="py-20 text-center text-slate-400 text-sm">
        Loading safety configuration and active rules...
      </div>
    );
  }

  return (
    <div className="max-w-5xl mx-auto space-y-8 animate-fadeIn pb-12">
      {/* Header */}
      <div>
        <h1 className="text-2xl font-bold tracking-tight text-white flex items-center gap-2">
          <Sliders className="w-6 h-6 text-indigo-400" />
          Safety Policies & Loop Thresholds
        </h1>
        <p className="text-sm text-slate-400 mt-1">
          Tune algorithmic limits, cycle period thresholds, and sensitive operation policies applied across all agent workflows.
        </p>
      </div>

      {saveSuccess && (
        <div className="p-4 rounded-xl bg-emerald-500/10 border border-emerald-500/30 text-emerald-300 text-xs flex items-center gap-2">
          <CheckCircle2 className="w-4 h-4 text-emerald-400" />
          <span>Safety policy thresholds successfully updated and logged in the immutable audit trail.</span>
        </div>
      )}

      {/* Configuration Form */}
      <form onSubmit={handleSave} className="glass-panel p-6 sm:p-8 rounded-2xl border border-slate-800 space-y-6">
        <h2 className="text-sm font-semibold uppercase tracking-wider text-slate-300 flex items-center gap-2">
          <Shield className="w-4 h-4 text-cyan-400" /> Execution Limits & Guardrails
        </h2>

        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-5">
          <div>
            <label htmlFor="config-max-steps" className="block text-xs font-mono text-slate-300 mb-1.5">
              Maximum Workflow Steps
            </label>
            <input
              id="config-max-steps"
              type="number"
              min={1}
              max={100}
              value={config.max_workflow_steps}
              onChange={(e) => setConfig({ ...config, max_workflow_steps: parseInt(e.target.value) || 20 })}
              className="w-full px-3.5 py-2 rounded-xl bg-slate-900 border border-slate-700 text-white text-xs font-mono"
            />
            <span className="text-[10px] text-slate-500 block mt-1">Halt workflows exceeding step count</span>
          </div>

          <div>
            <label htmlFor="config-max-repeats" className="block text-xs font-mono text-slate-300 mb-1.5">
              Repeated Calls Limit
            </label>
            <input
              id="config-max-repeats"
              type="number"
              min={1}
              max={10}
              value={config.max_repeated_calls}
              onChange={(e) => setConfig({ ...config, max_repeated_calls: parseInt(e.target.value) || 3 })}
              className="w-full px-3.5 py-2 rounded-xl bg-slate-900 border border-slate-700 text-white text-xs font-mono"
            />
            <span className="text-[10px] text-slate-500 block mt-1">Consecutive identical calls before BLOCK</span>
          </div>

          <div>
            <label htmlFor="config-loop-threshold" className="block text-xs font-mono text-slate-300 mb-1.5">
              Loop Cycle Threshold (Period K)
            </label>
            <input
              id="config-loop-threshold"
              type="number"
              min={2}
              max={5}
              value={config.loop_cycle_threshold}
              onChange={(e) => setConfig({ ...config, loop_cycle_threshold: parseInt(e.target.value) || 2 })}
              className="w-full px-3.5 py-2 rounded-xl bg-slate-900 border border-slate-700 text-white text-xs font-mono"
            />
            <span className="text-[10px] text-slate-500 block mt-1">Cycle repetitions before BLOCK (A&rarr;B&rarr;A&rarr;B)</span>
          </div>

          <div>
            <label htmlFor="config-max-duration" className="block text-xs font-mono text-slate-300 mb-1.5">
              Execution Timeout (Seconds)
            </label>
            <input
              id="config-max-duration"
              type="number"
              min={10}
              max={3600}
              value={config.max_execution_duration_seconds}
              onChange={(e) => setConfig({ ...config, max_execution_duration_seconds: parseFloat(e.target.value) || 300 })}
              className="w-full px-3.5 py-2 rounded-xl bg-slate-900 border border-slate-700 text-white text-xs font-mono"
            />
            <span className="text-[10px] text-slate-500 block mt-1">Total allowed workflow runtime</span>
          </div>

          <div>
            <label htmlFor="config-no-progress" className="block text-xs font-mono text-slate-300 mb-1.5">
              Max No-Progress Steps
            </label>
            <input
              id="config-no-progress"
              type="number"
              min={1}
              max={10}
              value={config.max_no_progress_steps}
              onChange={(e) => setConfig({ ...config, max_no_progress_steps: parseInt(e.target.value) || 3 })}
              className="w-full px-3.5 py-2 rounded-xl bg-slate-900 border border-slate-700 text-white text-xs font-mono"
            />
            <span className="text-[10px] text-slate-500 block mt-1">Stagnant outcome repetitions before halt</span>
          </div>

          <div>
            <label htmlFor="config-max-retries" className="block text-xs font-mono text-slate-300 mb-1.5">
              Max Tool Retries
            </label>
            <input
              id="config-max-retries"
              type="number"
              min={1}
              max={10}
              value={config.max_retries}
              onChange={(e) => setConfig({ ...config, max_retries: parseInt(e.target.value) || 3 })}
              className="w-full px-3.5 py-2 rounded-xl bg-slate-900 border border-slate-700 text-white text-xs font-mono"
            />
            <span className="text-[10px] text-slate-500 block mt-1">Maximum bounded retries per failure</span>
          </div>
        </div>

        {/* Sensitive Tools Policy */}
        <div className="pt-4 border-t border-slate-800/80 space-y-4">
          <div>
            <label htmlFor="sensitive-tools-textarea" className="block text-xs font-semibold uppercase tracking-wider text-slate-300 mb-1">
              Sensitive Tools (Routes to Approval Gate)
            </label>
            <p className="text-[11px] text-slate-400 mb-2">
              Any proposed tool matching these names or prefixes will be intercepted with REQUIRE_APPROVAL. (One tool per line)
            </p>
            <textarea
              id="sensitive-tools-textarea"
              rows={4}
              value={sensitiveToolsText}
              onChange={(e) => setSensitiveToolsText(e.target.value)}
              className="w-full p-3 rounded-xl bg-slate-900 border border-slate-700 text-white font-mono text-xs focus:outline-none focus:ring-1 focus:ring-indigo-500"
            />
          </div>

          <div>
            <label htmlFor="sensitive-patterns-input" className="block text-xs font-semibold uppercase tracking-wider text-slate-300 mb-1">
              Sensitive Argument Masking Patterns (Audit Sanitization)
            </label>
            <p className="text-[11px] text-slate-400 mb-2">
              Keys matching these patterns are masked with [REDACTED] in logs and UI. (Comma-separated)
            </p>
            <input
              id="sensitive-patterns-input"
              type="text"
              value={sensitiveArgsText}
              onChange={(e) => setSensitiveArgsText(e.target.value)}
              className="w-full px-3.5 py-2 rounded-xl bg-slate-900 border border-slate-700 text-white font-mono text-xs focus:outline-none focus:ring-1 focus:ring-indigo-500"
            />
          </div>
        </div>

        {/* Submit */}
        <div className="pt-2 flex justify-end">
          <button
            type="submit"
            id="save-policy-config-btn"
            disabled={saving}
            className="flex items-center gap-2 px-6 py-2.5 rounded-xl bg-indigo-600 hover:bg-indigo-500 text-white font-semibold text-xs shadow-lg shadow-indigo-600/30 transition disabled:opacity-50"
          >
            {saving ? (
              <>
                <div className="w-3.5 h-3.5 border-2 border-white/20 border-t-white rounded-full animate-spin" />
                Saving...
              </>
            ) : (
              <>
                <Save className="w-3.5 h-3.5" />
                Save Safety Policy
              </>
            )}
          </button>
        </div>
      </form>

      {/* Built-in Safety Detectors Reference Table */}
      <div className="glass-panel p-6 rounded-2xl border border-slate-800 space-y-4">
        <h2 className="text-sm font-semibold uppercase tracking-wider text-slate-300 flex items-center gap-2">
          <Info className="w-4 h-4 text-indigo-400" /> Active Safety Engine Detectors
        </h2>
        <div className="overflow-x-auto">
          <table className="w-full text-left text-xs">
            <thead className="text-[11px] uppercase tracking-wider text-slate-400 border-b border-slate-800 bg-slate-900/60">
              <tr>
                <th className="py-2.5 px-3">Rule Identifier</th>
                <th className="py-2.5 px-3">Detector Name</th>
                <th className="py-2.5 px-3">Enforcement Action</th>
                <th className="py-2.5 px-3">Behavior & Mechanism</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-800/60 font-mono">
              {rules.map((rule) => (
                <tr key={rule.id}>
                  <td className="py-3 px-3 text-cyan-400 font-bold">{rule.id}</td>
                  <td className="py-3 px-3 text-slate-200 font-sans">{rule.name}</td>
                  <td className="py-3 px-3">
                    <span className={`px-2 py-0.5 rounded text-[10px] font-bold ${
                      rule.action === 'BLOCK' ? 'bg-rose-500/20 text-rose-400' : 'bg-amber-500/20 text-amber-400'
                    }`}>
                      {rule.action}
                    </span>
                  </td>
                  <td className="py-3 px-3 text-slate-400 font-sans text-[11px]">{rule.description}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
};
