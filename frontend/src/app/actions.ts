'use server';

export interface Citation {
  chapter: string;
  section: string;
  content_snippet: string;
  relevance_score: number;
}

export interface ChatState {
  answer: string;
  citations: Citation[];
  mode: string;
  error?: string;
}

export async function sendChatMessage(
  prevState: ChatState | null,
  formData: FormData
): Promise<ChatState> {
  const query = formData.get('query') as string;
  const courseCode = (formData.get('course_code') as string) || 'DL-101';
  const language = (formData.get('language') as string) || 'en';
  const mode = (formData.get('mode') as string) || 'citation';

  if (!query || !query.trim()) {
    return {
      answer: '',
      citations: [],
      mode,
      error: 'Query cannot be empty.',
    };
  }

  try {
    const res = await fetch('http://localhost:8000/api/v1/chat', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        query,
        course_code: courseCode,
        language,
        mode,
      }),
      cache: 'no-store',
    });

    if (!res.ok) {
      throw new Error(`Server error: ${res.status}`);
    }

    const data = await res.json();

    return {
      answer: data.answer,
      citations: data.citations || [],
      mode: data.mode,
    };
  } catch (err) {
    return {
      answer: '',
      citations: [],
      mode,
      error: language === 'de' 
        ? 'Fehler beim Verbinden mit dem AI Core Backend.' 
        : 'Failed to connect to AI Core Backend.',
    };
  }
}