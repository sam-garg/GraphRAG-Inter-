# Graph Report - GraphRAG (2026-09-17)

## Corpus Check
- **Code:** 2 files (`main.py`, `pyproject.toml`)
- **Documents:** 1 file (`knowledge_base.txt`)
- **Total:** 3 files · ~350 words

## Summary
- 8 nodes · 11 edges · 2 communities
- Extraction: 100% EXTRACTED · 0% INFERRED · 0% AMBIGUOUS
- Token cost: 0 input · 0 output (AST & deterministic extraction)

## Community Hubs (Navigation)
- **GraphRAG Pipeline** (Community 0): Core execution flow in `main.py`
- **Corpus & Configuration** (Community 1): Knowledge base documents and package configuration

## God Nodes (most connected - your core abstractions)
1. `main.py` - 5 edges (central entry point connecting all pipeline components)
2. `build_knowledge_graph()` - 3 edges (constructs NetworkX directed graph from extracted triples)
3. `retrieve_graph_context()` - 3 edges (multi-hop traversal engine via DFS)
4. `extraction_chain` - 3 edges (Ollama JSON triple extractor)

## Surprising Connections (you probably didn't know these)
- `main_extraction_chain` $\rightarrow$ `doc_knowledge_base`: Direct triple extraction pipeline bridging structured code execution with unstructured text corpus.
- `main_retrieve_graph_context` $\rightarrow$ `main_rag_chain`: Dynamic subgraph retrieval supplying relevant context to local LLM question answering.

## Import Cycles
- None detected.

## Communities (2 total)

### Community 0: GraphRAG Pipeline (6 nodes)
- `main.py`
- `load_document()`
- `extraction_chain`
- `build_knowledge_graph()`
- `retrieve_graph_context()`
- `rag_chain`

### Community 1: Corpus & Configuration (2 nodes)
- `knowledge_base.txt`
- `graphrag package` (`pyproject.toml`)

## Knowledge Gaps
- No isolated nodes detected.
- All core functions in `main.py` are explicitly linked to document input and graph retrieval output.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **How does unstructured text in `knowledge_base.txt` get converted into graph context for `rag_chain`?**
  _Traces the flow from `load_document()` $\rightarrow$ `extraction_chain` $\rightarrow$ `build_knowledge_graph()` $\rightarrow$ `retrieve_graph_context()` $\rightarrow$ `rag_chain`._
- **What is the multi-hop depth traversal path when querying about `ChatGPT`?**
  _Inspects how `retrieve_graph_context()` traverses `successors` and `predecessors` around target nodes._