const BASE = '/api';

export async function uploadFile(file: File) {
  const form = new FormData();
  form.append('file', file);
  const res = await fetch(`${BASE}/upload`, { method: 'POST', body: form });
  return res.json();
}

export async function indexDocuments() {
  const res = await fetch(`${BASE}/documents/index`, { method: 'POST' });
  return res.json();
}

export async function listDocuments() {
  const res = await fetch(`${BASE}/documents`);
  return res.json();
}

export async function healthCheck() {
  const res = await fetch(`${BASE}/health`);
  return res.json();
}

export async function chat(query: string): Promise<{ answer: string; sources: Source[] }> {
  const res = await fetch(`${BASE}/chat`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ query }),
  });
  return res.json();
}

export function chatStream(
  query: string,
  onToken: (token: string) => void,
  onSources: (sources: Source[]) => void,
  onDone: () => void,
  onError: (err: Error) => void,
) {
  fetch(`${BASE}/chat/stream`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ query }),
  }).then(async (res) => {
    const reader = res.body?.getReader();
    if (!reader) return onError(new Error('No reader'));
    const decoder = new TextDecoder();
    let buffer = '';
    while (true) {
      const { done, value } = await reader.read();
      if (done) return onDone();
      buffer += decoder.decode(value, { stream: true });
      const lines = buffer.split('\n');
      buffer = lines.pop() || '';
      for (const line of lines) {
        if (line.startsWith('event: sources')) continue;
        if (line.startsWith('data: ')) {
          const data = line.slice(6);
          if (data === '[DONE]') return onDone();
          onToken(data);
        }
      }
    }
  }).catch(onError);
}

export interface Source {
  content: string;
  score: number;
  source: string;
}
