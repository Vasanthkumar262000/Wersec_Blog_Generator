const API = '/api';

export type GenerateResponse = {
  topic: string;
  summary: string;
  full_content: string;
  sources: string[];
  tools_used: string[];
  linkedin_post: string;
  thumbnail_url: string | null;
};

function getErrorMessage(res: Response, fallback: string): string {
  if (res.status === 502) {
    return 'Backend took too long or is unavailable. Ensure the API is running (uvicorn api:app --port 8000) and try again.';
  }
  if (res.status === 503) {
    return 'Backend is not configured. Check the API logs and set GROQ_API_KEY in .env.';
  }
  if (res.status === 504) {
    return 'Generation timed out. Try a simpler topic or try again.';
  }
  return fallback;
}

export async function generateBlog(
  topic: string,
  tone: string,
  length: string
): Promise<GenerateResponse> {
  let res: Response;
  try {
    res = await fetch(`${API}/generate`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ topic: topic.trim(), tone, length }),
    });
  } catch (e) {
    throw new Error(
      'Cannot reach the API. Start the backend with: uvicorn api:app --reload --port 8000'
    );
  }
  if (!res.ok) {
    const fallback = getErrorMessage(res, 'Generation failed');
    const err = await res.json().catch(() => ({ detail: res.statusText }));
    const detail = typeof err?.detail === 'string' ? err.detail : fallback;
    throw new Error(detail || fallback);
  }
  return res.json();
}

export async function publishLinkedIn(
  topic: string,
  summary: string,
  full_content: string,
  linkedin_post: string,
  thumbnail_filename: string | null
): Promise<void> {
  const res = await fetch(`${API}/linkedin`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      topic,
      summary,
      full_content,
      linkedin_post,
      thumbnail_filename,
    }),
  });
  if (!res.ok) {
    const err = await res.json().catch(() => ({ detail: res.statusText }));
    throw new Error(err.detail || 'LinkedIn post failed');
  }
}

export async function publishWhatsApp(
  topic: string,
  summary: string,
  sources: string[]
): Promise<void> {
  const res = await fetch(`${API}/whatsapp`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ topic, summary, sources }),
  });
  if (!res.ok) {
    const err = await res.json().catch(() => ({ detail: res.statusText }));
    throw new Error(err.detail || 'WhatsApp failed');
  }
}
