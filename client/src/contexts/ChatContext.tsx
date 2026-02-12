/**
 * Chat Sessions Context
 * Manages AI chat sessions across components
 * All sessions are stored in the database and tied to user accounts
 */

import { createContext, useContext, useState, useEffect, useCallback, useRef, type ReactNode } from 'react';
import { useAuth } from './AuthContext';

// Types
interface ChatSession {
  id: number;
  session_id: string;
  title: string;
  model: string;
  mode: string;
  message_count: number;
  created_at: string;
  updated_at: string;
  last_message?: string;
}

interface ChatMessage {
  id: string;
  role: 'user' | 'assistant';
  content: string;
  timestamp: string;
}

interface CreditsInfo {
  remaining: number;
  cost: number;
  monthly_limit: number;
  tier: string;
  model_costs?: Record<string, number>;
}

interface ChatContextType {
  sessions: ChatSession[];
  currentSessionId: string | null;
  messages: ChatMessage[];
  isLoading: boolean;
  isStreaming: boolean;
  credits: CreditsInfo | null;
  loadSessions: () => Promise<void>;
  createSession: (title?: string, model?: string) => Promise<string | null>;
  selectSession: (sessionId: string) => Promise<void>;
  deleteSession: (sessionId: string) => Promise<void>;
  sendMessage: (message: string, mode?: string, model?: string) => Promise<void>;
  loadCredits: () => Promise<void>;
  setCurrentSessionId: (id: string | null) => void;
  clearMessages: () => void;
}

const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

const ChatContext = createContext<ChatContextType | undefined>(undefined);

export function ChatProvider({ children }: { children: ReactNode }) {
  const { tokens, isAuthenticated } = useAuth();
  const token = tokens?.accessToken;

  const [sessions, setSessions] = useState<ChatSession[]>([]);
  const [currentSessionId, setCurrentSessionId] = useState<string | null>(null);
  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  const [isStreaming, setIsStreaming] = useState(false);
  const [credits, setCredits] = useState<CreditsInfo | null>(null);

  // Track previous auth state to detect login/logout
  const prevAuthRef = useRef<boolean>(false);

  // Load all sessions from database
  const loadSessions = useCallback(async () => {
    if (!token) return;

    setIsLoading(true);
    try {
      const response = await fetch(`${API_URL}/api/chat-sessions/`, {
        headers: { 'Authorization': `Bearer ${token}` }
      });

      if (response.ok) {
        const data = await response.json();
        setSessions(data);
        console.log(`Loaded ${data.length} chat sessions from database`);
      } else {
        console.error('Failed to load sessions:', response.status);
      }
    } catch (error) {
      console.error('Failed to load sessions:', error);
    } finally {
      setIsLoading(false);
    }
  }, [token]);

  // Load credit info from backend
  const loadCredits = useCallback(async () => {
    if (!token) return;

    try {
      const response = await fetch(`${API_URL}/api/chat-sessions/credits`, {
        headers: { 'Authorization': `Bearer ${token}` }
      });

      if (response.ok) {
        const data = await response.json();
        setCredits({
          remaining: data.credits,
          cost: 0,
          monthly_limit: data.monthly_limit,
          tier: data.tier,
          model_costs: data.model_costs,
        });
      }
    } catch (error) {
      console.error('Failed to load credits:', error);
    }
  }, [token]);

  // Create new session in database
  const createSession = useCallback(async (title?: string, model?: string): Promise<string | null> => {
    if (!token) {
      console.error('Cannot create session: no auth token');
      return null;
    }

    try {
      const response = await fetch(`${API_URL}/api/chat-sessions/`, {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          title: title || 'New Chat',
          model: model || 'gemini',
          mode: 'script',
        }),
      });

      if (response.ok) {
        const session = await response.json();
        setSessions(prev => [session, ...prev]);
        setCurrentSessionId(session.session_id);
        setMessages([]);
        console.log('Created new session:', session.session_id, 'with model:', model || 'gemini');
        return session.session_id;
      } else {
        console.error('Failed to create session:', response.status);
      }
    } catch (error) {
      console.error('Failed to create session:', error);
    }
    return null;
  }, [token]);

  // Select and load session messages from database
  const selectSession = useCallback(async (sessionId: string) => {
    if (!token) return;

    setCurrentSessionId(sessionId);
    setIsLoading(true);

    try {
      const response = await fetch(`${API_URL}/api/chat-sessions/${sessionId}/messages`, {
        headers: { 'Authorization': `Bearer ${token}` }
      });

      if (response.ok) {
        const data = await response.json();
        setMessages(data.map((msg: any) => ({
          id: msg.id.toString(),
          role: msg.role,
          content: msg.content,
          timestamp: msg.created_at,
        })));
        console.log(`Loaded ${data.length} messages for session ${sessionId}`);
      }
    } catch (error) {
      console.error('Failed to load messages:', error);
    } finally {
      setIsLoading(false);
    }
  }, [token]);

  // Delete session from database
  const deleteSession = useCallback(async (sessionId: string) => {
    if (!token) return;

    try {
      const response = await fetch(`${API_URL}/api/chat-sessions/${sessionId}`, {
        method: 'DELETE',
        headers: { 'Authorization': `Bearer ${token}` }
      });

      if (response.ok) {
        setSessions(prev => prev.filter(s => s.session_id !== sessionId));
        if (currentSessionId === sessionId) {
          setCurrentSessionId(null);
          setMessages([]);
        }
        console.log('Deleted session:', sessionId);
      }
    } catch (error) {
      console.error('Failed to delete session:', error);
    }
  }, [token, currentSessionId]);

  // Send message - auto-creates session if needed
  const sendMessage = useCallback(async (message: string, mode?: string, model?: string) => {
    if (!token || isStreaming) return;

    let sessionId = currentSessionId;

    // Auto-create session if none exists
    if (!sessionId) {
      console.log('No session exists, creating new one with model:', model || 'gemini');
      try {
        const response = await fetch(`${API_URL}/api/chat-sessions/`, {
          method: 'POST',
          headers: {
            'Authorization': `Bearer ${token}`,
            'Content-Type': 'application/json',
          },
          body: JSON.stringify({
            title: message.substring(0, 50) + (message.length > 50 ? '...' : ''),
            model: model || 'gemini',
            mode: mode || 'script',
          }),
        });

        if (response.ok) {
          const session = await response.json();
          setSessions(prev => [session, ...prev]);
          setCurrentSessionId(session.session_id);
          sessionId = session.session_id;
          console.log('Auto-created session:', sessionId);
        } else {
          console.error('Failed to auto-create session');
          return;
        }
      } catch (error) {
        console.error('Failed to auto-create session:', error);
        return;
      }
    }

    // Add user message immediately for UI responsiveness
    const userMessage: ChatMessage = {
      id: Date.now().toString(),
      role: 'user',
      content: message,
      timestamp: new Date().toISOString(),
    };
    setMessages(prev => [...prev, userMessage]);
    setIsStreaming(true);

    try {
      // Send message to backend - this saves to database
      const response = await fetch(`${API_URL}/api/chat-sessions/${sessionId}/messages`, {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ message, mode, model }),
      });

      if (response.ok) {
        const data = await response.json();

        // Update user message with real ID from database
        setMessages(prev => prev.map(m =>
          m.id === userMessage.id
            ? { ...m, id: data.user_message.id.toString() }
            : m
        ));

        // Add AI response
        const aiMessage: ChatMessage = {
          id: data.ai_response.id.toString(),
          role: 'assistant',
          content: data.ai_response.content,
          timestamp: data.ai_response.created_at,
        };
        setMessages(prev => [...prev, aiMessage]);

        // Update credits from response
        if (data.credits) {
          setCredits(prev => ({
            ...prev,
            remaining: data.credits.remaining,
            cost: data.credits.cost,
            monthly_limit: data.credits.monthly_limit,
            tier: data.credits.tier,
            model_costs: prev?.model_costs,
          }));
        }

        // Update session in list with new data from server
        setSessions(prev => prev.map(s =>
          s.session_id === sessionId
            ? {
                ...s,
                message_count: data.session.message_count,
                title: data.session.title,
                updated_at: data.session.updated_at,
                last_message: data.ai_response.content.substring(0, 100)
              }
            : s
        ));
      } else if (response.status === 402) {
        // Insufficient credits
        const errorData = await response.json().catch(() => null);
        const errorMsg = errorData?.detail?.message || 'Недостаточно кредитов. Перейдите на более высокий план.';
        const errorMessage: ChatMessage = {
          id: (Date.now() + 1).toString(),
          role: 'assistant',
          content: errorMsg,
          timestamp: new Date().toISOString(),
        };
        // Remove the optimistic user message
        setMessages(prev => prev.filter(m => m.id !== userMessage.id));
        setMessages(prev => [...prev, errorMessage]);
        return;
      } else {
        throw new Error(`Server error: ${response.status}`);
      }
    } catch (error) {
      console.error('Failed to send message:', error);
      // Add error message
      const errorMessage: ChatMessage = {
        id: (Date.now() + 1).toString(),
        role: 'assistant',
        content: 'Sorry, I encountered an error. Please try again.',
        timestamp: new Date().toISOString(),
      };
      setMessages(prev => [...prev, errorMessage]);
    } finally {
      setIsStreaming(false);
    }
  }, [token, currentSessionId, isStreaming]);

  // Clear messages
  const clearMessages = useCallback(() => {
    setMessages([]);
    setCurrentSessionId(null);
  }, []);

  // Clear all state when user logs out, load sessions when user logs in
  useEffect(() => {
    const wasAuthenticated = prevAuthRef.current;
    const nowAuthenticated = isAuthenticated && !!token;

    // User just logged out
    if (wasAuthenticated && !nowAuthenticated) {
      console.log('User logged out - clearing chat state');
      setSessions([]);
      setMessages([]);
      setCurrentSessionId(null);
      setCredits(null);
    }

    // User just logged in
    if (!wasAuthenticated && nowAuthenticated) {
      console.log('User logged in - loading sessions and credits from database');
      loadSessions();
      loadCredits();
    }

    prevAuthRef.current = nowAuthenticated;
  }, [isAuthenticated, token, loadSessions, loadCredits]);

  // Also load sessions and credits on initial mount if already authenticated
  useEffect(() => {
    if (token && sessions.length === 0) {
      loadSessions();
      loadCredits();
    }
  }, [token, sessions.length, loadSessions, loadCredits]);

  return (
    <ChatContext.Provider
      value={{
        sessions,
        currentSessionId,
        messages,
        isLoading,
        isStreaming,
        credits,
        loadSessions,
        createSession,
        selectSession,
        deleteSession,
        sendMessage,
        loadCredits,
        setCurrentSessionId,
        clearMessages,
      }}
    >
      {children}
    </ChatContext.Provider>
  );
}

export function useChat() {
  const context = useContext(ChatContext);
  if (!context) {
    throw new Error('useChat must be used within a ChatProvider');
  }
  return context;
}
