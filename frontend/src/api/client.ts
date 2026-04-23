import type { UploadedDocument, Source, SummarizeResult, SummaryStyle } from '../types';

interface ChatApiResponse {
  answer: string;
  sources: Source[];
}

async function handleResponse<T>(res: Response): Promise<T> {
  if (!res.ok) {
    const body = await res.json().catch(() => ({ detail: res.statusText }));
    throw new Error(body.detail ?? 'Sunucu hatası');
  }
  return res.json() as Promise<T>;
}

export async function apiUpload(files: File[]): Promise<UploadedDocument[]> {
  const formData = new FormData();
  files.forEach((f) => formData.append('files', f));

  const res = await fetch('/upload', { method: 'POST', body: formData });
  return handleResponse<UploadedDocument[]>(res);
}

export async function apiGetDocuments(): Promise<UploadedDocument[]> {
  const res = await fetch('/documents');
  return handleResponse<UploadedDocument[]>(res);
}

export async function apiDeleteDocument(docId: string): Promise<void> {
  const res = await fetch(`/documents/${docId}`, { method: 'DELETE' });
  if (!res.ok) {
    const body = await res.json().catch(() => ({ detail: res.statusText }));
    throw new Error(body.detail ?? 'Silme başarısız');
  }
}

export async function apiChat(
  question: string,
  docIds: string[] | null,
  topK = 5,
): Promise<ChatApiResponse> {
  const res = await fetch('/chat', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ question, docIds: docIds?.length ? docIds : null, topK }),
  });
  return handleResponse<ChatApiResponse>(res);
}

export async function apiSummarize(
  docIds: string[],
  style: SummaryStyle = 'short',
): Promise<SummarizeResult> {
  const res = await fetch('/summarize', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ docIds, style }),
  });
  return handleResponse<SummarizeResult>(res);
}
