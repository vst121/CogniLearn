import json
from typing import List, Dict, Any
from openai import AsyncOpenAI
from opentelemetry import trace

tracer = trace.get_tracer(__name__)

CITATION_SYSTEM_PROMPT = """
You are CogniLearn's Citation Agent. Answer the student's question accurately using ONLY the provided course context.
For every main claim or explanation, you MUST provide explicit citations referencing the chapter and section from the context.

Formatting format for citations: [Chapter X, Section Y]
If the context does not contain enough information to answer, state clearly that the provided textbook materials do not cover the topic.
"""


class CitationAgent:
    def __init__(self, openai_client: AsyncOpenAI):
        self.client = openai_client

    async def run(self, query: str, contexts: List[Dict[str, Any]]) -> Dict[str, Any]:
        with tracer.start_as_current_span("CitationAgent.run") as span:
            span.set_attribute("agent.name", "citation_agent")
            span.set_attribute("agent.num_contexts", len(contexts))

            # Format retrieved context snippets into prompt string
            formatted_context = "\n\n".join([
                f"--- Document [Chapter: {doc.get('chapter', 'N/A')}, Section: {doc.get('section', 'N/A')}] ---\n{doc.get('content', '')}"
                for doc in contexts
            ])

            messages = [
                {"role": "system", "content": CITATION_SYSTEM_PROMPT},
                {"role": "user", "content": f"Context:\n{formatted_context}\n\nUser Question: {query}"}
            ]

            response = await self.client.chat.completions.create(
                model="gpt-4o-mini",
                messages=messages,
                temperature=0.2
            )

            answer = response.choices[0].message.content
            span.set_attribute("agent.output_length", len(answer) if answer else 0)

            return {
                "agent": "citation",
                "answer": answer,
                "sources": [
                    {
                        "chapter": doc.get("chapter"),
                        "section": doc.get("section"),
                        "rrf_score": doc.get("rrf_score")
                    }
                    for doc in contexts
                ]
            }
