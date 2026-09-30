from typing import List, Dict, Any
from openai import AsyncOpenAI
from opentelemetry import trace

tracer = trace.get_tracer(__name__)

SOCRATIC_SYSTEM_PROMPT = """
You are CogniLearn's Socratic Tutor. Your goal is to help the student learn by asking guiding questions and giving subtle hints.

Rules:
1. DO NOT give the direct final answer immediately.
2. Use the provided textbook context to understand the concept yourself.
3. Break down complex topics into small, digestible steps.
4. Ask 1 focused question at a time to check or prompt the student's understanding.
"""


class SocraticAgent:
    def __init__(self, openai_client: AsyncOpenAI):
        self.client = openai_client

    async def run(self, query: str, contexts: List[Dict[str, Any]]) -> Dict[str, Any]:
        with tracer.start_as_current_span("SocraticAgent.run") as span:
            span.set_attribute("agent.name", "socratic_agent")

            formatted_context = "\n\n".join([
                f"--- Reference Concept [Chapter: {doc.get('chapter', 'N/A')}] ---\n{doc.get('content', '')}"
                for doc in contexts
            ])

            messages = [
                {"role": "system", "content": SOCRATIC_SYSTEM_PROMPT},
                {"role": "user", "content": f"Textbook Context:\n{formatted_context}\n\nStudent Question: {query}"}
            ]

            response = await self.client.chat.completions.create(
                model="gpt-4o-mini",
                messages=messages,
                temperature=0.7
            )

            reply = response.choices[0].message.content

            return {
                "agent": "socratic",
                "answer": reply,
                "sources": []  # Hints don't show explicit document citations to keep focus on discussion
            }
