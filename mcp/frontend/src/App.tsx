import { useState, useEffect } from 'react';
import { Header } from './components/Header';
import { RepoConnectBar } from './components/RepoConnectBar';
import { HealthDashboard } from './components/HealthDashboard';
import { ChatInterface } from './components/ChatInterface';
import { ConfirmationModal } from './components/ConfirmationModal';
import { ToolsModal } from './components/ToolsModal';
import { api } from './services/api';
import type { RepositoryInfo, ChatMessage, ToolCallLog, PendingAction, ProjectHealth, SystemHealth, MCPToolInfo } from './types';

export function App() {
  const [systemHealth, setSystemHealth] = useState<SystemHealth | null>(null);
  const [currentRepo, setCurrentRepo] = useState<RepositoryInfo | null>(null);
  const [projectHealth, setProjectHealth] = useState<ProjectHealth | null>(null);
  const [tools, setTools] = useState<MCPToolInfo[]>([]);
  
  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const [isChatLoading, setIsChatLoading] = useState(false);
  const [isConnecting, setIsConnecting] = useState(false);
  const [isHealthLoading, setIsHealthLoading] = useState(false);
  
  const [activeToolExecutions, setActiveToolExecutions] = useState<ToolCallLog[]>([]);
  const [pendingAction, setPendingAction] = useState<PendingAction | null>(null);
  const [isConfirming, setIsConfirming] = useState(false);
  const [isToolsModalOpen, setIsToolsModalOpen] = useState(false);
  const [connectError, setConnectError] = useState<string | null>(null);

  // Initialize application state
  useEffect(() => {
    async function init() {
      try {
        const sys = await api.getHealthCheck();
        setSystemHealth(sys);

        // Fetch tools catalog
        const toolList = await api.getTools();
        setTools(toolList);

        // Connect default demo repository
        await handleConnect('demo/demo_repo');
      } catch (err) {
        console.error('Initialization error:', err);
      }
    }
    init();
  }, []);

  const handleConnect = async (url: string, token?: string) => {
    setIsConnecting(true);
    setConnectError(null);
    try {
      const res = await api.connectRepo(url, token);
      setCurrentRepo(res.repository);
      
      // Fetch health for newly connected repository
      await refreshHealth();

      // Add a system welcome message
      setMessages((prev) => [
        ...prev,
        {
          role: 'assistant',
          content: `✅ Connected to repository **${res.repository.owner}/${res.repository.repo}** via MCP.\n\n` +
            `Default branch: \`${res.repository.default_branch}\`\n\n` +
            `You can ask me to **"Analyze my repository"**, **"Run the tests"**, or **"Find bugs in auth.py"**.`,
        },
      ]);
    } catch (err: any) {
      setConnectError(err.message || 'Failed to connect to repository');
    } finally {
      setIsConnecting(false);
    }
  };

  const refreshHealth = async () => {
    setIsHealthLoading(true);
    try {
      const h = await api.getRepoHealth();
      setProjectHealth(h);
    } catch (err) {
      console.error('Failed to load project health:', err);
    } finally {
      setIsHealthLoading(false);
    }
  };

  const handleSendMessage = async (userText: string) => {
    const userMsg: ChatMessage = { role: 'user', content: userText };
    setMessages((prev) => [...prev, userMsg]);
    setIsChatLoading(true);

    // Provide initial speculative tool steps in execution indicator
    const lower = userText.toLowerCase();
    const initialTools: ToolCallLog[] = [];
    if (lower.includes('analyze') || lower.includes('health') || lower.includes('status')) {
      initialTools.push({ id: '1', tool_name: 'get_repository_info', arguments: {}, status: 'running' });
      initialTools.push({ id: '2', tool_name: 'list_repository_files', arguments: {}, status: 'pending' });
      initialTools.push({ id: '3', tool_name: 'get_project_health', arguments: {}, status: 'pending' });
    } else if (lower.includes('why') && lower.includes('fail')) {
      initialTools.push({ id: '1', tool_name: 'run_tests', arguments: {}, status: 'running' });
      initialTools.push({ id: '2', tool_name: 'read_repository_file', arguments: { path: 'auth.py' }, status: 'pending' });
      initialTools.push({ id: '3', tool_name: 'analyze_test_failure', arguments: {}, status: 'pending' });
    } else if (lower.includes('test')) {
      initialTools.push({ id: '1', tool_name: 'run_tests', arguments: {}, status: 'running' });
    } else if (lower.includes('commit') || lower.includes('diff')) {
      initialTools.push({ id: '1', tool_name: 'get_recent_commits', arguments: {}, status: 'running' });
      initialTools.push({ id: '2', tool_name: 'get_commit_diff', arguments: {}, status: 'pending' });
    } else if (lower.includes('todo') || lower.includes('fixme')) {
      initialTools.push({ id: '1', tool_name: 'find_todos', arguments: {}, status: 'running' });
    } else if (lower.includes('bug') || lower.includes('code')) {
      initialTools.push({ id: '1', tool_name: 'analyze_code', arguments: { file_path: 'auth.py' }, status: 'running' });
    }
    setActiveToolExecutions(initialTools);

    try {
      const response = await api.sendMessage(
        userText,
        [...messages, userMsg],
        currentRepo ? `${currentRepo.owner}/${currentRepo.repo}` : undefined
      );

      setActiveToolExecutions(response.tool_executions || []);

      const assistantMsg: ChatMessage = {
        role: 'assistant',
        content: response.message,
        tool_executions: response.tool_executions,
        requires_confirmation: response.requires_confirmation,
        pending_action: response.pending_action,
      };

      setMessages((prev) => [...prev, assistantMsg]);

      // If issue creation was staged, display the confirmation modal directly
      if (response.requires_confirmation && response.pending_action) {
        setPendingAction(response.pending_action);
      }
    } catch (err: any) {
      setMessages((prev) => [
        ...prev,
        {
          role: 'assistant',
          content: `❌ Error: ${err.message || 'Failed to complete request.'}`,
        },
      ]);
    } finally {
      setIsChatLoading(false);
    }
  };

  const handleConfirmAction = async (actionId: string) => {
    setIsConfirming(true);
    try {
      const result = await api.confirmAction(actionId, true);
      setPendingAction(null);

      // Add assistant response verifying the creation
      setMessages((prev) => [
        ...prev,
        {
          role: 'assistant',
          content: `🎉 **GitHub Issue Created Successfully!**\n\n` +
            `- **Issue Title:** ${result.result?.title || 'Bug Report'}\n` +
            `- **Issue Number:** #${result.result?.number || 28}\n` +
            `- **Status:** Open\n\n` +
            `*Successfully invoked \`create_github_issue\` through MCP after security authorization.*`,
        },
      ]);
      await refreshHealth();
    } catch (err: any) {
      alert(`Failed to create issue: ${err.message}`);
    } finally {
      setIsConfirming(false);
    }
  };

  const handleCancelAction = async (actionId: string) => {
    setIsConfirming(true);
    try {
      await api.confirmAction(actionId, false);
      setPendingAction(null);
      setMessages((prev) => [
        ...prev,
        {
          role: 'assistant',
          content: `ℹ️ GitHub issue creation was cancelled by the user. No changes were written.`,
        },
      ]);
    } catch (err: any) {
      console.error(err);
    } finally {
      setIsConfirming(false);
    }
  };

  return (
    <div className="min-h-screen bg-[#090d16] text-slate-100 flex flex-col selection:bg-indigo-500/30 selection:text-indigo-200">
      {/* Top Header */}
      <Header
        systemHealth={systemHealth}
        onOpenToolsModal={() => setIsToolsModalOpen(true)}
      />

      {/* Main Container */}
      <main className="flex-1 max-w-7xl w-full mx-auto px-4 sm:px-6 lg:px-8 py-6 space-y-6">
        {/* Repository Connect Bar */}
        <RepoConnectBar
          currentRepo={currentRepo}
          onConnect={handleConnect}
          isLoading={isConnecting}
          errorMessage={connectError}
          onClearError={() => setConnectError(null)}
        />

        {/* Project Health Dashboard Metrics */}
        <HealthDashboard
          health={projectHealth}
          onRefresh={refreshHealth}
          isLoading={isHealthLoading}
        />

        {/* AI Assistant Chat Interface */}
        <ChatInterface
          messages={messages}
          onSendMessage={handleSendMessage}
          isLoading={isChatLoading}
          currentToolExecutions={activeToolExecutions}
          onOpenConfirmation={(action) => setPendingAction(action)}
        />
      </main>

      {/* Footer */}
      <footer className="border-t border-slate-800/80 bg-slate-950/60 py-4 mt-8">
        <div className="max-w-7xl mx-auto px-4 text-center text-xs text-slate-500">
          AI DevOps Assistant • Powered by Model Context Protocol (MCP) & Google Gemini • Full End-to-End Demonstration
        </div>
      </footer>

      {/* Security Confirmation Modal for Issue Creation */}
      <ConfirmationModal
        action={pendingAction}
        onConfirm={handleConfirmAction}
        onCancel={handleCancelAction}
        isLoading={isConfirming}
      />

      {/* MCP Tools Catalog Modal */}
      <ToolsModal
        isOpen={isToolsModalOpen}
        onClose={() => setIsToolsModalOpen(false)}
        tools={tools}
      />
    </div>
  );
}

export default App;
