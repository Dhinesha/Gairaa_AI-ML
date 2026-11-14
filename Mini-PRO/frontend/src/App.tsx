import React, { useEffect, useState } from 'react';
import { Navbar } from './components/Navbar';
import { DashboardPage } from './pages/DashboardPage';
import { CreateWorkflowPage } from './pages/CreateWorkflowPage';
import { WorkflowDetailsPage } from './pages/WorkflowDetailsPage';
import { WorkflowsListPage } from './pages/WorkflowsListPage';
import { SafetyEventsPage } from './pages/SafetyEventsPage';
import { ApprovalCenterPage } from './pages/ApprovalCenterPage';
import { AnalyticsPage } from './pages/AnalyticsPage';
import { ConfigurationPage } from './pages/ConfigurationPage';
import { LoginPage } from './pages/LoginPage';
import { ProfileModal } from './components/ProfileModal';
import { UserProfile } from './types';
import { api } from './services/api';
import { useTheme } from './context/ThemeContext';

export function App() {
  const { theme } = useTheme();
  const [user, setUser] = useState<UserProfile | null>(() => {
    const saved = localStorage.getItem('loopguard_user');
    if (saved) {
      try {
        return JSON.parse(saved);
      } catch {
        return null;
      }
    }
    return null;
  });

  const [isProfileOpen, setIsProfileOpen] = useState<boolean>(false);
  const [activeTab, setActiveTab] = useState<string>('dashboard');
  const [selectedWorkflowId, setSelectedWorkflowId] = useState<string | null>(null);
  const [pendingApprovalsCount, setPendingApprovalsCount] = useState<number>(0);

  const fetchApprovalsCount = async () => {
    if (!user) return;
    try {
      const approvals = await api.listApprovals('PENDING');
      setPendingApprovalsCount(approvals.length);
    } catch {
      // ignore
    }
  };

  useEffect(() => {
    if (user) {
      fetchApprovalsCount();
      const interval = setInterval(fetchApprovalsCount, 5000);
      return () => clearInterval(interval);
    }
  }, [user]);

  const handleSelectWorkflow = (id: string) => {
    setSelectedWorkflowId(id);
    setActiveTab('workflow-details');
  };

  // If not logged in, show the unique cyber login & persona selector
  if (!user) {
    return <LoginPage onLogin={(loggedUser) => setUser(loggedUser)} />;
  }

  return (
    <div className={`min-h-screen flex flex-col font-sans transition-colors duration-200 ${theme === 'light' ? 'bg-[#F8FAFC] text-slate-800' : 'bg-[#0B0F19] text-slate-100'}`}>
      <Navbar
        activeTab={activeTab}
        setActiveTab={(tab) => {
          setActiveTab(tab);
          if (tab !== 'workflow-details') {
            setSelectedWorkflowId(null);
          }
        }}
        pendingApprovalsCount={pendingApprovalsCount}
        user={user}
        onOpenProfile={() => setIsProfileOpen(true)}
      />

      <ProfileModal
        user={user}
        isOpen={isProfileOpen}
        onClose={() => setIsProfileOpen(false)}
        onUpdateUser={(updated) => {
          setUser(updated);
          localStorage.setItem('loopguard_user', JSON.stringify(updated));
        }}
        onSignOut={() => {
          localStorage.removeItem('loopguard_user');
          setUser(null);
          setIsProfileOpen(false);
        }}
      />

      <main className="flex-1 max-w-7xl w-full mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {activeTab === 'dashboard' && (
          <DashboardPage
            onSelectWorkflow={handleSelectWorkflow}
            onNavigateTab={(tab) => setActiveTab(tab)}
          />
        )}

        {activeTab === 'create' && (
          <CreateWorkflowPage
            onWorkflowCreated={(id) => {
              setSelectedWorkflowId(id);
              setActiveTab('workflow-details');
            }}
          />
        )}

        {activeTab === 'workflows' && (
          <WorkflowsListPage
            onSelectWorkflow={handleSelectWorkflow}
            onNavigateCreate={() => setActiveTab('create')}
          />
        )}

        {activeTab === 'workflow-details' && selectedWorkflowId && (
          <WorkflowDetailsPage
            workflowId={selectedWorkflowId}
            onBack={() => setActiveTab('workflows')}
            onGoToApprovals={() => setActiveTab('approvals')}
          />
        )}

        {activeTab === 'safety-events' && (
          <SafetyEventsPage onSelectWorkflow={handleSelectWorkflow} />
        )}

        {activeTab === 'approvals' && (
          <ApprovalCenterPage
            onSelectWorkflow={handleSelectWorkflow}
            onRefreshApprovalsCount={fetchApprovalsCount}
          />
        )}

        {activeTab === 'analytics' && <AnalyticsPage />}

        {activeTab === 'configuration' && <ConfigurationPage />}
      </main>

      <footer className={`border-t py-6 text-center text-xs font-mono transition-colors ${theme === 'light' ? 'border-slate-200 text-slate-500 bg-white' : 'border-slate-800/80 text-slate-500 bg-[#0B0F19]'}`}>
        Agent Workflow Safety & Loop Prevention Engine &bull; Antigravity Systems &bull; Safe Agent Execution Architecture
      </footer>
    </div>
  );
}

export default App;
