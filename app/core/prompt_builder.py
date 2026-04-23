def build_qa_prompt(question: str, context: str) -> str:
    return f"""You are a document QA assistant.
Answer the user's question using only the retrieved context below.
If the context is insufficient, reply exactly with: 根据当前文档无法确定。
Keep the answer concise and grounded.
If you cite evidence, mention the source markers like [1], [2].
Prefer the highest-scoring evidence when multiple chunks overlap.

Question:
{question}

Retrieved context:
{context}
"""
