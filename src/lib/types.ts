/**
 * Shared TypeScript types for StudySense AI.
 */

export interface Document {
  id: number;
  filename: string;
  file_type: string;
  uploaded_at: string;
  chunk_count: number;
}

export interface Topic {
  id: number;
  name: string;
  subject: string;
  importance: number;
  frequency: number;
}

export interface Question {
  id: number;
  text: string;
  topic: string;
  difficulty: "easy" | "medium" | "hard";
  answer?: string;
}

export interface ChatMessage {
  role: "user" | "assistant";
  content: string;
  citations?: Citation[];
  confidence?: number;
}

export interface Citation {
  filename: string;
  page: number;
  snippet: string;
}

export interface QuizResult {
  score: number;
  total: number;
  time_taken_seconds: number;
}

export interface AnalyticsOverview {
  documents: number;
  chunks: number;
  topics: number;
  questions: number;
  formulas: number;
  mock_attempts: number;
  chat_messages: number;
}
