import asyncio
import asyncpg
import numpy as np
from app.core.config import settings
from app.rag.retriever import BilingualHybridRetriever

# Sample course documents in English and German
SAMPLE_DOCS = [
    {
        "course_code": "DL-101",
        "language": "en",
        "chapter": "Chapter 3: Optimization",
        "section": "3.2 Gradient Descent",
        "content": "Gradient descent is a first-order iterative optimization algorithm for finding a local minimum of a differentiable function. In deep learning, backpropagation computes the gradient of the loss function with respect to weights."
    },
    {
        "course_code": "DL-101",
        "language": "de",
        "chapter": "Kapitel 3: Optimierung",
        "section": "3.2 Gradientenabstiegsverfahren",
        "content": "Das Gradientenabstiegsverfahren ist ein iterativer Optimierungsalgorithmus erster Ordnung zur Bestimmung eines lokalen Minimums einer differenzierbaren Funktion. Bei Deep Learning berechnet die Backpropagation den Gradienten der Verlustfunktion."
    },
    {
        "course_code": "DL-101",
        "language": "en",
        "chapter": "Chapter 4: Neural Networks",
        "section": "4.1 Activation Functions",
        "content": "Activation functions like ReLU (Rectified Linear Unit), Sigmoid, and Softmax introduce non-linearity into neural network models, enabling them to learn complex patterns."
    },
    {
        "course_code": "DL-101",
        "language": "de",
        "chapter": "Kapitel 4: Neuronale Netze",
        "section": "4.1 Aktivierungsfunktionen",
        "content": "Aktivierungsfunktionen wie ReLU, Sigmoid und Softmax fuehren Nichtlinearitaet in neuronale Netzmodelle ein, sodass diese komplexe Muster erlernen koennen."
    }
]

def generate_mock_embedding(dim: int = 1536) -> list[float]:
    """Generates a normalized random vector representing embeddings."""
    vec = np.random.randn(dim)
    norm = np.linalg.norm(vec)
    return (vec / norm).tolist()

async def seed_database():
    print("Connecting to PostgreSQL database...")
    pool = await asyncpg.create_pool(dsn=settings.DATABASE_URL)

    async with pool.acquire() as conn:
        print("Clearing previous seed data for course DL-101...")
        await conn.execute("DELETE FROM course_documents WHERE course_code = 'DL-101'")

        print("Inserting bilingual course documents...")
        for doc in SAMPLE_DOCS:
            embedding = generate_mock_embedding()
            await conn.execute(
                """
                INSERT INTO course_documents (course_code, language, chapter, section, content, embedding)
                VALUES ($1, $2, $3, $4, $5, $6::vector)
                """,
                doc["course_code"],
                doc["language"],
                doc["chapter"],
                doc["section"],
                doc["content"],
                str(embedding)
            )

    print("Database successfully seeded.")

    # Execute test hybrid searches in both English and German
    retriever = BilingualHybridRetriever(pool)

    print("\n--- Testing English Hybrid Search ---")
    en_query = "Gradient descent optimization"
    en_results = await retriever.hybrid_search(
        query_text=en_query,
        query_embedding=generate_mock_embedding(),
        course_code="DL-101",
        language="en",
        top_k=2
    )
    for res in en_results:
        print(f"[{res['language'].upper()}] {res['chapter']} - {res['section']} | RRF Score: {res['rrf_score']:.4f}")

    print("\n--- Testing German Hybrid Search ---")
    de_query = "Gradientenabstiegsverfahren Optimierung"
    de_results = await retriever.hybrid_search(
        query_text=de_query,
        query_embedding=generate_mock_embedding(),
        course_code="DL-101",
        language="de",
        top_k=2
    )
    for res in de_results:
        print(f"[{res['language'].upper()}] {res['chapter']} - {res['section']} | RRF Score: {res['rrf_score']:.4f}")

    await pool.close()

if __name__ == "__main__":
    asyncio.run(seed_database())