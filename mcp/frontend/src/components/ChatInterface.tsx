import React, { useState, useRef, useEffect } from 'react';
import { Send, Bot, User, ShieldAlert } from 'lucide-react';
import type { ChatMessage, ToolCallLog, PendingAction } from '../types';
import { ToolExecutionIndicator } from './ToolExecutionIndicator';

interface ChatInterfaceProps {
  messages: ChatMessage[];
  onSendMessage: (msg: string) => Promise<void>;
  isLoading: boolean;
  currentToolExecutions: ToolCallLog[];
  onOpenConfirmation: (action: PendingAction) => void;
}

const QUICK_PROMPTS = [
  'Analyze my repository.',
  'Show me the latest commits.',
  'Run the tests.',
  'Why are my tests failing?',
  'Find bugs in auth.py',
  'Find TODOs in my project.',
  'Create a GitHub issue for this bug.'
];

export const ChatInterface: React.FC<ChatInterfaceProps> = ({
  messages,
  onSendMessage,
  isLoading,
  currentToolExecutions,
  onOpenConfirmation,
}) => {
  const [input, setInput] = useState('');
  const messagesEndRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages, currentToolExecutions, isLoading]);

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (input.trim() && !isLoading) {
      onSendMessage(input.trim());
      setInput('');
    }
  };

  const handleChipClick = (prompt: string) => {
    if (!isLoading) {
      onSendMessage(prompt);
    }
  };

  // Helper to format text with markdown-like code blocks and lists
  const renderFormattedContent = (content: string) => {
    const lines = content.split('\n');
    let inCodeBlock = false;
    let codeBuffer: string[] = [];
    const elements: React.ReactNode[] = [];

    lines.forEach((line, index) => {
      if (line.startsWith('```')) {
        if (inCodeBlock) {
          elements.push(
            <pre key={`code-${index}`} className="my-2 p-3 rounded-xl bg-slate-950/90 border border-slate-800 text-xs font-mono text-emerald-300 overflow-x-auto">
              <code>{codeBuffer.join('\n')}</code>
            </pre>
          );
          codeBuffer = [];
          inCodeBlock = false;
        } else {
          inCodeBlock = true;
        }
        return;
      }

      if (inCodeBlock) {
        codeBuffer.push(line);
        return;
      }

      if (line.startsWith('### ')) {
        elements.push(
          <h4 key={index} className="text-base font-bold text-slate-100 mt-3 mb-1.5 flex items-center gap-1.5">
            {line.replace('### ', '')}
          </h4>
        );
      } else if (line.startsWith('## ')) {
        elements.push(
          <h3 key={index} className="text-lg font-bold text-slate-100 mt-3.5 mb-2">
            {line.replace('## ', '')}
          </h3>
        );
      } else if (line.startsWith('- ') || line.startsWith('* ')) {
        elements.push(
          <li key={index} className="ml-4 list-disc text-slate-300 text-xs sm:text-sm my-0.5">
            {renderInlineCode(line.substring(2))}
          </li>
        );
      } else if (line.trim() === '') {
        elements.push(<div key={index} className="h-2" />);
      } else {
        elements.push(
          <p key={index} className="text-slate-300 text-xs sm:text-sm my-1 leading-relaxed">
            {renderInlineCode(line)}
          </p>
        );
      }
    });

    if (inCodeBlock && codeBuffer.length > 0) {
      elements.push(
        <pre key="code-final" className="my-2 p-3 rounded-xl bg-slate-950/90 border border-slate-800 text-xs font-mono text-emerald-300 overflow-x-auto">
          <code>{codeBuffer.join('\n')}</code>
        </pre>
      );
    }

    return elements;
  };

  const renderInlineCode = (text: string) => {
    const parts = text.split(/(`[^`]+`|\*\*[^*]+\*\*)/g);
    return parts.map((part, i) => {
      if (part.startsWith('`') && part.endsWith('`')) {
        return (
          <code key={i} className="px-1.5 py-0.5 rounded bg-slate-800 text-indigo-300 text-[13px] font-mono border border-slate-700/60">
            {part.slice(1, -1)}
          </code>
        );
      }
      if (part.startsWith('**') && part.endsWith('**')) {
        return <strong key={i} className="font-semibold text-slate-100">{part.slice(2, -2)}</strong>;
      }
      return part;
    });
  };

  return (
    <div className="glass-panel rounded-2xl border border-slate-800 flex flex-col h-[650px] shadow-2xl shadow-black/50 overflow-hidden">
      {/* Chat Header */}
      <div className="px-5 py-3.5 border-b border-slate-800 bg-slate-950/40 flex items-center justify-between">
        <div className="flex items-center gap-2">
          <div className="w-2 h-2 rounded-full bg-emerald-400 animate-ping"></div>
          <span className="text-xs font-semibold text-slate-200 uppercase tracking-wider">
            Conversational DevOps Copilot
          </span>
        </div>
        <span className="text-xs text-slate-500">Natural Language to MCP Tools</span>
      </div>

      {/* Message Area */}
      <div className="flex-1 overflow-y-auto p-4 sm:p-6 space-y-4">
        {messages.length === 0 && (
          <div className="h-full flex flex-col items-center justify-center text-center p-6 space-y-4">
            <div className="w-14 h-14 rounded-2xl bg-indigo-500/10 border border-indigo-500/30 flex items-center justify-center text-indigo-400">
              <Bot className="w-8 h-8" />
            </div>
            <div className="max-w-md">
              <h3 className="text-base font-bold text-slate-100">Welcome to AI DevOps Assistant</h3>
              <p className="text-xs text-slate-400 mt-1">
                Connected to your repository via Model Context Protocol (MCP). Ask questions in natural language,
                and the assistant will autonomously call developer tools.
              </p>
            </div>
          </div>
        )}

        {messages.map((msg, idx) => (
          <div
            key={idx}
            className={`flex items-start gap-3 ${msg.role === 'user' ? 'flex-row-reverse' : 'flex-row'}`}
          >
            {/* Avatar */}
            <div
              className={`w-8 h-8 rounded-xl flex items-center justify-center shrink-0 ${
                msg.role === 'user'
                  ? 'bg-gradient-to-tr from-purple-600 to-indigo-600 text-white'
                  : 'bg-slate-800 border border-slate-700 text-indigo-400'
              }`}
            >
              {msg.role === 'user' ? <User className="w-4 h-4" /> : <Bot className="w-4 h-4" />}
            </div>

            {/* Bubble */}
            <div className={`max-w-[85%] sm:max-w-[75%] rounded-2xl p-4 text-xs sm:text-sm ${
              msg.role === 'user'
                ? 'bg-indigo-600 text-white shadow-lg shadow-indigo-600/20'
                : 'bg-slate-900/90 border border-slate-800/90 text-slate-200'
            }`}>
              {renderFormattedContent(msg.content)}

              {/* Tool Execution Logs attached to this message */}
              {msg.tool_executions && msg.tool_executions.length > 0 && (
                <ToolExecutionIndicator toolExecutions={msg.tool_executions} isThinking={false} />
              )}

              {/* Confirmation Action Button if message triggered a pending action */}
              {msg.requires_confirmation && msg.pending_action && (
                <div className="mt-3 p-3 rounded-xl bg-amber-500/10 border border-amber-500/30 flex items-center justify-between">
                  <div className="flex items-center gap-2 text-xs text-amber-300">
                    <ShieldAlert className="w-4 h-4 text-amber-400" />
                    <span>Issue creation staged: Authorization required</span>
                  </div>
                  <button
                    onClick={() => onOpenConfirmation(msg.pending_action!)}
                    className="px-3 py-1 rounded-lg bg-amber-500 hover:bg-amber-400 text-slate-950 font-bold text-xs shadow transition-colors cursor-pointer"
                  >
                    Review & Confirm
                  </button>
                </div>
              )}
            </div>
          </div>
        ))}

        {/* Active Tool Execution Indicator while thinking */}
        {isLoading && (
          <div className="flex items-start gap-3">
            <div className="w-8 h-8 rounded-xl bg-slate-800 border border-slate-700 text-indigo-400 flex items-center justify-center shrink-0">
              <Bot className="w-4 h-4 animate-pulse" />
            </div>
            <div className="max-w-[85%] sm:max-w-[75%] rounded-2xl p-4 bg-slate-900/90 border border-slate-800 text-slate-200 w-full">
              <ToolExecutionIndicator toolExecutions={currentToolExecutions} isThinking={true} />
            </div>
          </div>
        )}

        <div ref={messagesEndRef} />
      </div>

      {/* Suggested Quick Prompt Chips */}
      <div className="px-4 py-2 bg-slate-950/60 border-t border-slate-800/80 flex items-center gap-2 overflow-x-auto no-scrollbar">
        <span className="text-[11px] text-slate-500 shrink-0">Suggestions:</span>
        {QUICK_PROMPTS.map((prompt) => (
          <button
            key={prompt}
            type="button"
            onClick={() => handleChipClick(prompt)}
            disabled={isLoading}
            className="px-2.5 py-1 rounded-lg bg-slate-900 hover:bg-slate-800 border border-slate-800 text-xs text-slate-300 hover:text-white transition-colors cursor-pointer shrink-0 disabled:opacity-40"
          >
            {prompt}
          </button>
        ))}
      </div>

      {/* Input Area */}
      <form onSubmit={handleSubmit} className="p-3.5 bg-slate-950/80 border-t border-slate-800 flex items-center gap-2">
        <input
          type="text"
          value={input}
          onChange={(e) => setInput(e.target.value)}
          placeholder="Ask anything about your repository (e.g. 'Why are my tests failing?', 'Find bugs in auth.py')..."
          disabled={isLoading}
          className="flex-1 bg-slate-900 border border-slate-800 rounded-xl px-4 py-2.5 text-sm text-slate-100 placeholder-slate-500 focus:outline-none focus:ring-2 focus:ring-indigo-500/50 focus:border-indigo-500 transition-all font-sans"
        />
        <button
          type="submit"
          disabled={isLoading || !input.trim()}
          className="px-4 py-2.5 rounded-xl bg-indigo-600 hover:bg-indigo-500 text-white text-sm font-semibold shadow-md shadow-indigo-600/25 disabled:opacity-40 flex items-center gap-2 transition-all cursor-pointer"
        >
          <span>Send</span>
          <Send className="w-4 h-4" />
        </button>
      </form>
    </div>
  );
};
