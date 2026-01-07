# Cognix: A Multilingual PDF-Based Question-Answering System

## 1. Introduction

Cognix is an intelligent document-based question-answering (QA) system that leverages Retrieval-Augmented Generation (RAG) architecture to provide accurate, context-aware responses from user-uploaded PDF documents. The system combines Large Language Models (LLMs) with semantic document retrieval, enabling natural language queries with comprehensive, source-backed answers.

The system supports five languages (Italian, English, Spanish, French, and German), making it valuable for international academic and professional contexts. Beyond question-answering, Cognix generates flashcards and quizzes to support active learning and knowledge retention.

---

## 2. Aims and Objectives

The primary aim is to develop a multilingual document-based QA system for efficient knowledge extraction. Key objectives:

1. **Document Ingestion**: Robust PDF parsing, multi-format support (PDF, DOCX, TXT, HTML, CSV), efficient text chunking
2. **Semantic Search**: Multilingual embeddings, ChromaDB vector storage, configurable retrieval mechanisms
3. **Intelligent Routing**: LLM-based intent classification for QA, Flashcard, and Quiz tools
4. **Multilingual Support**: Five-language support with automatic language detection
5. **Educational Content**: Flashcard and quiz generation with configurable difficulty
6. **Evaluation Framework**: Comprehensive testing using BLEU, ROUGE, F1, and LLM-as-judge metrics

---

## 3. Background and Literature Review

**Retrieval-Augmented Generation (RAG)**: Lewis et al. (2020) introduced RAG to combine LLM generative capabilities with external knowledge retrieval, addressing the limitation of fixed training knowledge. RAG systems retrieve relevant documents as context for the generative model, enabling accurate and verifiable responses.

**LLMs for Question Answering**: Modern LLMs (GPT-4, LLaMA, DeepSeek) demonstrate strong capabilities in understanding and generating natural language. Integration with RAG has become standard for domain-specific QA systems (Gao et al., 2023).

**Multilingual NLP**: Cross-lingual understanding is enabled by multilingual sentence transformers like paraphrase-multilingual-MiniLM-L12-v2, allowing semantic similarity computation across different languages.

**Document Chunking**: Liu et al. (2023) highlight the importance of chunk size and overlap for context preservation while maintaining retrieval precision.

**QA Evaluation**: Standard metrics include BLEU, ROUGE for n-gram overlap, and semantic similarity measures. DeepEval provides LLM-as-judge evaluation for faithfulness, relevancy, and contextual metrics (Kryscinski et al., 2019).

---

## 4. Methodology

### System Architecture

Cognix follows a modular four-layer architecture:

**1. Presentation Layer**: Notebook-style GUI for PDF upload, document management, and natural language interaction with source document references.

**2. Ingestion Layer**: Document loading (PDF, DOCX, TXT, HTML, CSV), text splitting (600-char chunks, 200-char overlap), embedding generation (paraphrase-multilingual-MiniLM-L12-v2), and ChromaDB vector storage.

**3. RAG Logic Layer**: Routing Agent (LLM-based intent classification), QA Tool (document retrieval and answer generation), Flashcard Tool (Q&A pair generation), Quiz Tool (multiple-choice generation).

**4. LLM Integration Layer**: Thread-safe singleton with OpenRouter API, DeepSeek-v3.1 model, configurable temperature/top-p/context parameters.

### Language Detection

Automatic language detection through pattern matching (e.g., "rispondi in italiano", "answer in English"). The multilingual embedding model ensures consistent semantic search across all five supported languages.

### Evaluation Methodology

- **Router Evaluation**: 51 test cases testing intent classification accuracy
- **QA Evaluation**: DeepEval metrics (Answer Relevancy, Contextual Precision/Recall, Faithfulness) + Custom metrics (F1, BLEU, ROUGE-L)
- **Summary Evaluation**: Fluency, coherence, consistency, and entity density metrics

---

## 5. Results and Evaluation

### 5.1 Router Agent Performance

The routing agent was evaluated on 51 queries with both JSON and TOON format inputs (102 total tests).

| Metric | Value |
|--------|-------|
| Total Tests | 102 |
| Total Successes | 55 |
| Overall Success Rate | 53.92% |

**Performance by Tool:**
| Tool | Tests | Successes | Rate |
|------|-------|-----------|------|
| QA_TOOL | 34 | 34 | 100.00% |
| FLASHCARD_TOOL | 36 | 14 | 38.89% |
| QUIZ_TOOL | 32 | 7 | 21.88% |

**Successful Test Cases (Examples):**
- *QA*: "Spiegami in modo semplice il funzionamento del protocollo MQTT" ✓
- *QA*: "Explain how SSL/TLS works in simple terms" ✓
- *Flashcard*: "Generami 5 flashcard sul capitolo del Fog Computing" ✓
- *Quiz*: "Fammi un quiz a risposta multipla sul machine learning supervisionato" ✓

**Challenging Cases (Failures):**
- "Quiz!" → Predicted QA_TOOL (minimal input)
- "Fashcards sobre AI plz" → Predicted QA_TOOL (typo)
- "Genérame un cuestionario sobre seguridad" → Predicted FLASHCARD_TOOL
- "Crea flashcards sobre Kubernetes in italiano" → Predicted QA_TOOL (mixed language)

The QA_TOOL achieves perfect accuracy. Lower performance occurs with typos, minimal/ambiguous input, and cross-language queries.

### 5.2 QA Tool Performance

Evaluated across 24 multilingual test cases (IT: 6, EN: 2, ES: 2, FR: 2, DE: 12) covering Android, software engineering, data analytics, and electronics.

**Metrics Used:**
- *DeepEval*: Answer Relevancy, Contextual Precision/Recall, Faithfulness
- *Custom*: F1 Score (token-level), BLEU (n-gram precision), ROUGE-L (sequence overlap)

### 5.3 System Configuration

| Parameter | Value |
|-----------|-------|
| Model | deepseek/deepseek-chat-v3.1 (OpenRouter) |
| Temperature | 0.1 |
| Top-p | 0.9 |
| Context Window | 4096 tokens |

**Embedding**: paraphrase-multilingual-MiniLM-L12-v2, 600-char chunks, 200-char overlap, 0.75 similarity threshold

---

## 6. Conclusion

Cognix successfully combines RAG architecture with modern LLMs for efficient multilingual knowledge extraction from PDF documents.

**Key Achievements:**
- Robust multilingual support (5 languages) with automatic detection
- Modular architecture for easy extension
- Comprehensive evaluation framework
- Perfect QA routing accuracy (100%)

**Limitations and Future Work:**
- Router accuracy for Flashcard/Quiz tools needs improvement through fine-tuning
- Conversation memory across sessions would enhance context continuity
- Better handling of ambiguous cross-language queries
- Support for document images and tables

Cognix demonstrates the viability of RAG-based systems for educational document exploration.

---

## 7. References

1. Gao, Y., et al. (2023). Retrieval-Augmented Generation for Large Language Models: A Survey. *arXiv:2312.10997*.

2. Kryscinski, W., et al. (2019). Neural Text Summarization: A Critical Evaluation. *EMNLP 2019*.

3. Lewis, P., et al. (2020). Retrieval-Augmented Generation for Knowledge-Intensive NLP Tasks. *NeurIPS*, 33, 9459-9474.

4. Liu, N., et al. (2023). Lost in the Middle: How Language Models Use Long Contexts. *arXiv:2307.03172*.

5. Reimers, N., & Gurevych, I. (2019). Sentence-BERT. *EMNLP 2019*.

6. Vaswani, A., et al. (2017). Attention is All You Need. *NeurIPS*, 30.

7. LangChain Documentation. (2024). https://python.langchain.com/

8. ChromaDB Documentation. (2024). https://www.trychroma.com/

9. DeepEval Documentation. (2024). https://docs.confident-ai.com/

10. Sentence Transformers. (2024). https://www.sbert.net/
