export interface UploadedDocument {
  docId: string;
  docName: string;
  fileName: string;
  totalChunks: number;
  createdAt?: string;
}

export interface Source {
  docId: string;
  docName: string;
  chunkIndex: number;
  snippet: string;
  score?: number;
}

export interface ChatMessage {
  id: string;
  role: 'user' | 'assistant';
  content: string;
  sources?: Source[];
  timestamp: Date;
}

export interface SummarizeSource {
  docId: string;
  docName: string;
}

export interface SummarizeResult {
  summary: string;
  sources: SummarizeSource[];
}

export type SummaryStyle = 'short' | 'detailed' | 'bullet';
