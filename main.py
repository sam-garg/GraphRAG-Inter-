from pathlib import Path
import networkx as nx
from langchain_ollama import ChatOllama
from langchain_core.prompts import PromptTemplate
from langchain_core.output_parsers import JsonOutputParser

# 1. Load Local LLM
# Temperature=0 is crucial here. We want facts, not creativity.
llm = ChatOllama(model="llama3.1:latest", temperature=0)

# 2. turning text into graph
# This step is the most important. We can’t put raw text straight into a graph; we need triples. A triple is the basic unit of a knowledge graph: (Head) -> [Relation] -> (Tail).

# Prompt for Extracting Graph Triples
extract_prompt = PromptTemplate(
    template="""
You are an expert knowledge graph builder.
Extract entities and relationships from the text.
Return ONLY a JSON list. Each item must contain:
- "head": source entity
- "relation": relationship
- "tail": target entity

Text:
{text}

Output JSON:
""",
    input_variables=["text"],
)

extraction_chain = extract_prompt | llm | JsonOutputParser()

# 3. Document Loading Function change Path to your document
def load_document(source: str | Path = "knowledge_base.txt") -> str:  
    """Load text content from a file path (.txt/.md/.pdf), directory, or raw string."""
    path = Path(source)
    if path.is_file():
        if path.suffix.lower() == ".pdf":
            from pypdf import PdfReader
            return "\n".join(page.extract_text() or "" for page in PdfReader(str(path)).pages)
        return path.read_text(encoding="utf-8")
    if path.is_dir():
        return "\n".join(
            f.read_text(encoding="utf-8", errors="ignore")
            for f in path.glob("*.*")
            if f.is_file() and f.suffix.lower() in {".txt", ".md"}
        )
    return str(source)

# Load document from file
doc_text = load_document("knowledge_base.txt")

print("\n Extracting knowledge graph triples...\n")
triples = extraction_chain.invoke({"text": doc_text})
print(triples)

# 4. Building Graph
kg = nx.DiGraph() # DiGraph means "Directed Graph" (arrows point one way)

def build_knowledge_graph(triples):
    if isinstance(triples, dict):
        triples = triples.get("triples", triples.get("data", []))
    for item in triples:
        if not isinstance(item, dict):
            continue
        head = item.get("head")
        tail = item.get("tail")
        relation = item.get("relation", "")

        if head and tail:
            kg.add_node(head)
            kg.add_node(tail)
            kg.add_edge(head, tail, label=relation)

build_knowledge_graph(triples)

print("\n Nodes in Graph:")
print(list(kg.nodes()))

# 5. MULTI-HOP RETRIEVAL(successors->next, predecessors->previous)

def retrieve_graph_context(entity, max_depth=2):
    context = set() # set() -> stores unique vals to avoid duplications
    visited_nodes = set()

    def dfs(node, depth):
        if depth > max_depth:
            return
        visited_nodes.add(node)

        # 1. Check Outgoing edges (What does this node do?)
        for neighbor in kg.successors(node):
            relation = kg.get_edge_data(node, neighbor)["label"]  #What it does: Looks up the metadata associated with the edge going from node to neighbor and extracts its "label" attribute (e.g., "developed_by").
            context.add(f"{node} {relation} {neighbor}")
            if neighbor not in visited_nodes:
                dfs(neighbor, depth + 1)

        # 2. Check Incoming edges (Who interacts with this node?)
        for predecessor in kg.predecessors(node):
            relation = kg.get_edge_data(predecessor, node)["label"]
            context.add(f"{predecessor} {relation} {node}")
            if predecessor not in visited_nodes:
                dfs(predecessor, depth + 1)

    if entity in kg.nodes:
        dfs(entity, 1) # Start the traversal, entity = starting node, 1 = depth

    return ". ".join(context)

# [ Predecessor ] ──(Incoming)──► [ Current Node ] ──(Outgoing)──► [ Neighbor ]
#        │                                                                │
#    (dfs depth+1)                                                   (dfs depth+1)

# 6. Final RAG Prompt
final_prompt = PromptTemplate(
    template="""
Answer the question using ONLY the context below.

Context:
{context}

Question:
{question}

Answer:
""",
    input_variables=["context", "question"]
)

rag_chain = final_prompt | llm

# 7. Ask a Multi-hop Reasoning Question
entity = "ChatGPT" #main entity

# We ask for a depth of 3 to catch distant connections
graph_context = retrieve_graph_context(entity, max_depth=3) 

print("\n Retrieved Graph Context:\n")
print(graph_context)

question = "Which company invested in the company that built ChatGPT?"

response = rag_chain.invoke({
    "context": graph_context,
    "question": question
})

print("\n Final Answer:\n")
print(response.content)