from openai import AzureOpenAI
from typing import List
import logging
from config import settings
from backend.retrieval import RetrievalResult

logger = logging.getLogger(__name__)

class LLMClient:
    """Handles Azure OpenAI interactions for grounded response generation."""
    
    def __init__(self):
        self.client = AzureOpenAI(
            azure_endpoint=settings.azure_openai_endpoint,
            api_key=settings.azure_openai_api_key,
            api_version=settings.azure_openai_api_version
        )
        self.deployment = settings.azure_openai_deployment
    
    def generate_grounded_response(
        self,
        query: str,
        retrieved_chunks: List[RetrievalResult],
        conversation_history: List[Dict] = None
    ) -> Dict[str, any]:
        """
        Generate a response grounded in retrieved documents.
        
        Returns:
            Dict with 'answer', 'citations', and 'diagnostic_info'
        """
        # Build context from retrieved chunks
        context = self._build_context(retrieved_chunks)
        
        # Build system prompt with strict grounding rules
        system_prompt = """You are an enterprise knowledge assistant. Follow these rules strictly:

1. Answer ONLY using the provided context documents
2. If the answer is not in the documents, respond: "I don't have that information in the available documents."
3. Always cite your sources using [1], [2], etc.
4. Be concise and professional
5. Do not make assumptions or use external knowledge"""
        
        # Build messages
        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": f"Context:\n{context}\n\nQuestion: {query}"}
        ]
        
        # Add conversation history if provided
        if conversation_history:
            messages = [messages[0]] + conversation_history[-4:] + [messages[1]]
        
        try:
            response = self.client.chat.completions.create(
                model=self.deployment,
                messages=messages,
                temperature=0.2,  # Low temperature for factual responses
                max_tokens=800,
                top_p=0.95
            )
            
            answer = response.choices[0].message.content
            
            # Build citations
            citations = [
                {
                    "number": idx + 1,
                    "title": chunk.title,
                    "url": chunk.url,
                    "snippet": chunk.content[:200]
                }
                for idx, chunk in enumerate(retrieved_chunks)
            ]
            
            return {
                "answer": answer,
                "citations": citations,
                "usage": {
                    "prompt_tokens": response.usage.prompt_tokens,
                    "completion_tokens": response.usage.completion_tokens,
                    "total_tokens": response.usage.total_tokens
                }
            }
            
        except Exception as e:
            logger.error(f"LLM generation failed: {str(e)}")
            raise
    
    def _build_context(self, chunks: List[RetrievalResult]) -> str:
        """Build formatted context string from retrieval results."""
        context_parts = []
        
        for idx, chunk in enumerate(chunks, 1):
            context_parts.append(
                f"[{idx}] {chunk.title}\n{chunk.content}\nSource: {chunk.url}\n"
            )
        
        return "\n---\n".join(context_parts)
