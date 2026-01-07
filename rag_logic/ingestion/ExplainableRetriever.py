import logging
from langchain_classic.retrievers import ContextualCompressionRetriever
from langchain_cohere import CohereRerank

logger = logging.getLogger(__name__)

class ExplainableRetriever:

    def __init__(self, vectorstore, top_k=20, rerank_top_n=5):

        self.vectorstore = vectorstore

        self.base_retriever = vectorstore.as_retriever(
            search_type="similarity",
            search_kwargs={"k": top_k},
        )

        try:
            self.compressor = CohereRerank(
                model="rerank-multilingual-v3.0",
                top_n=rerank_top_n,
            )

            self.retriever = ContextualCompressionRetriever(
                base_retriever=self.base_retriever,
                base_compressor=self.compressor,
            )
            self.has_reranker = True
        except Exception as e:
            logger.warning(f"Cohere Rerank non disponibile (manca API Key?). Fallback su base retriever. Errore: {e}")
            self.retriever = self.base_retriever
            self.has_reranker = False

    def retrieve_and_explain(self, query):
        """Perform similarity search with detailed explanations"""

        retrieved_docs = self.retriever.invoke(query)

        explained_results = []

        for i, doc in enumerate(retrieved_docs):
            # Gestione dello score: Cohere usa 'relevance_score', Chroma usa distanza
            score = doc.metadata.get("relevance_score")

            if score is None:
                score = 0.0

            explanation = {
                'rank': i + 1,
                'document_content': doc.page_content,
                'metadata': doc.metadata,
                'score': score,
                'confidence_level': self._calculate_confidence(score, is_reranked=self.has_reranker),
                'explanation_text': self._generate_explanation(doc, score, self.has_reranker),
                'key_terms': self._extract_key_terms(doc.page_content, query)
            }
            explained_results.append(explanation)

        return explained_results

    def _calculate_confidence(self, score, is_reranked=True):

        # Cohere score è 0-1 (più alto è meglio).
        # Chroma distance (L2) è 0-inf (più basso è meglio).
        if is_reranked:
            if score > 0.9:
                return "Very High"
            elif score > 0.7:
                return "High"
            elif score > 0.5:
                return "Medium"
            else:
                return "Low"
        else:
            return "N/A (Base Retrieval)"

    def _generate_explanation(self, doc, score, is_reranked):
        page_num = doc.metadata.get('page_number', 'N/A')
        chunk_id = doc.metadata.get('chunk_id', 'N/A')

        if is_reranked:
            return (f"Questo contenuto (Pag {page_num}, Chunk {chunk_id}) è stato riordinato "
                    f"dall'AI con un punteggio di rilevanza del {score:.2%}. "
                    f"È semanticamente molto pertinente alla tua domanda.")
        else:
            return f"Contenuto recuperato per similarità vettoriale (Pag {page_num})."

    def _extract_key_terms(self, content, query):
        query_words = set(query.lower().split())
        content_words = content.lower().split()

        matches = [w for w in content_words if w in query_words and len(w) > 3]
        return list(set(matches))[:5]


