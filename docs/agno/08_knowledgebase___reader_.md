---
layout: default
title: "KnowledgeBase & Reader"
parent: "Agno"
nav_order: 8
---

# Chapter 8: KnowledgeBase & Reader

In [Chapter 7: Memory](07_memory_.md), we learned how to give our [Agent](02_agent_.md)s the ability to remember past conversations and facts about users. This is great for personalized and ongoing chats. But what if your agent needs to access information from a large, specific collection of documents, like your company's product manuals, a set of internal policies, or research papers? This is where a `KnowledgeBase` comes into play!

Imagine you want to build an AI assistant that can answer very specific questions about a new coffee machine your company just launched. You have a detailed PDF user manual. How can you make your [Agent](02_agent_.md) "read" and "understand" this manual to answer customer queries like "How do I descale the Model X coffee machine?"

This is the problem `KnowledgeBase` and `Reader`s are designed to solve.

## What's the Big Idea? The Agent's Library

*   **`KnowledgeBase`**: Think of a `KnowledgeBase` as a specialized library you give to your [Agent](02_agent_.md). Instead of general world knowledge, this library contains a specific collection of documents or data sources that you provide. It's the agent's go-to place for information related to a particular topic or domain.

*   **`Reader`**: Inside this library, you need librarians who know how to read different kinds of books. `Reader`s are specialized components within a `KnowledgeBase` that know how to read different file types (like PDFs, DOCX Word files, CSVs, text from URLs, etc.). They extract the content from these files and convert it into a format the `KnowledgeBase` can understand and use.

*   **`Document`**: When a `Reader` reads a file, it typically converts its content into one or more `Document` objects. A `Document` (from `agno.document.base.Document`) is a simple container that holds the text content and some metadata (like the original file name or page number).

So, the `Reader` "reads" a physical file (e.g., `manual.pdf`), extracts its text, and turns it into `Document` objects. The `KnowledgeBase` then organizes these `Document`s so the [Agent](02_agent_.md) can quickly find relevant information when asked a question. This process is often called Retrieval Augmented Generation (RAG).

## Giving Your Agent a User Manual to Read

Let's continue with our coffee machine example. We have a PDF manual and we want our [Agent](02_agent_.md) to answer questions based on it.

**Step 1: Understanding the `Document` Format**

First, let's see what a `Document` object looks like. It's a basic data structure.

```python
# document_example.py
from agno.document.base import Document

# Imagine this content was extracted from page 5 of "coffee_manual.pdf"
doc_content = "To descale your Model X coffee machine, first ensure it's unplugged. Then, mix one part descaling solution with two parts water..."

# Create a Document object
manual_page_5 = Document(
    id="manual_page_5_chunk_1", # A unique identifier for this piece of text
    name="coffee_manual.pdf",    # Original source name
    content=doc_content,
    meta_data={"source_page": 5} # Extra info, like the page number
)

print(f"Document Name: {manual_page_5.name}")
print(f"Content (excerpt): {manual_page_5.content[:50]}...")
print(f"Metadata: {manual_page_5.meta_data}")
```
This `Document` object simply holds a piece of text (`content`) and some helpful information about where it came from. Large files are often broken down into many smaller `Document` "chunks" by the `Reader` or `KnowledgeBase`.

**Step 2: Using a `Reader` to Extract Content**

`agno` provides different `Reader`s for different file types. For example, `PDFReader` (from `agno.document.reader.pdf_reader.PDFReader`) knows how to read PDF files.

Let's see conceptually how a `PDFReader` might work (we won't run this as it requires a real PDF and `pypdf` installed).

```python
# conceptual_reader_usage.py
from agno.document.reader.pdf_reader import PDFReader
# from agno.document.base import Document # Already imported above

# 1. Initialize a PDFReader
# Readers can also chunk documents into smaller pieces for better processing.
pdf_reader = PDFReader(chunk_size=500) # chunk_size for breaking down large text

# 2. Imagine we have a 'coffee_manual.pdf' file
# In a real scenario, you'd provide the path to your PDF file.
# For this example, we'll simulate its output.
# documents_from_pdf = pdf_reader.read("path/to/your/coffee_manual.pdf")

# Let's simulate the output: a list of Document objects
simulated_doc1 = Document(name="coffee_manual", id="manual_p1", content="Welcome to Model X...")
simulated_doc2 = Document(name="coffee_manual", id="manual_p2", content="Safety Instructions...")
documents_from_pdf = [simulated_doc1, simulated_doc2]


print(f"Reader extracted {len(documents_from_pdf)} documents (or chunks).")
if documents_from_pdf:
    print(f"First document content: {documents_from_pdf[0].content[:30]}...")
```
The `PDFReader` would open the PDF, extract text from each page, potentially break long pages into smaller chunks (if `chunk=True`), and return a list of `Document` objects. `agno` has other readers like `DocxReader` for `.docx` files (`test_docx_reader.py`), `ArxivReader` for scientific papers from arXiv (`test_arxiv_reader.py`), and more.

**Step 3: Setting up a `KnowledgeBase`**

Now we need a `KnowledgeBase` to store and manage these `Document`s. `agno` offers various `KnowledgeBase` implementations. For instance, `PDFKnowledgeBase` (from `agno.knowledge.pdf.PDFKnowledgeBase`) is specifically designed to work with PDFs.

A `KnowledgeBase` often works with a [VectorDb & Embedder](09_vectordb___embedder_.md) (which we'll cover in the next chapter) to efficiently search for relevant documents. For now, let's focus on the concept of loading documents.

```python
# knowledgebase_setup.py
from agno.knowledge.pdf import PDFKnowledgeBase
# from agno.vectordb.lancedb import LanceDb # A type of VectorDb, more in Chapter 9
# from agno.embedder.openai import OpenAIEmbedder # An Embedder, more in Chapter 9

# For simplicity, we'll mock the VectorDb and Embedder for this example.
class MockVectorDb:
    def __init__(self, table_name, uri): self.docs = []; self.name = table_name
    def create(self): print(f"MockVectorDb '{self.name}': Collection created.")
    def insert(self, documents, filters=None): self.docs.extend(documents); print(f"MockVectorDb: Added {len(documents)} docs.")
    def search(self, query, limit, filters=None): print(f"MockVectorDb: Searching for '{query}'..."); return self.docs[:limit] if self.docs else []
    def exists(self): return True
    def drop(self): print(f"MockVectorDb '{self.name}': Dropped.")

mock_db = MockVectorDb(table_name="coffee_manual_kb", uri="tmp/mock_db")

# 1. Create a KnowledgeBase.
# It needs a path to the PDF(s) and a VectorDb.
# The PDFKnowledgeBase internally uses a PDFReader.
coffee_manual_kb = PDFKnowledgeBase(
    path="path/to/your/coffee_manual.pdf", # Path to your PDF file or directory of PDFs
    vector_db=mock_db
    # embedder=OpenAIEmbedder() # Real KBs need an embedder
)
print("KnowledgeBase for coffee manual created (conceptually).")

# 2. Load the document(s) into the KnowledgeBase.
# This tells the KB to read the PDF(s) using its internal PDFReader,
# process the content (chunk, embed), and store it in the VectorDb.
# coffee_manual_kb.load(recreate=True) # 'recreate=True' clears old data

# For this example, let's simulate loading by directly adding documents
# In a real scenario, .load() would use the reader based on 'path'.
manual_doc_content = "To descale Model X, use solution XYZ. Mix one part solution with two parts water. Run the cycle twice."
simulated_doc_for_kb = Document(name="coffee_manual", id="descale_info", content=manual_doc_content)
coffee_manual_kb.vector_db.insert([simulated_doc_for_kb]) # Directly add to our mock_db

print("Documents loaded into KnowledgeBase (simulated).")
```
Here:
1.  We create a `PDFKnowledgeBase`. We tell it where to find the PDF (`path`) and give it a `vector_db` (here, a mock one) to store the information. Real `KnowledgeBase`s also need an [Embedder](09_vectordb___embedder_.md) to convert text into numerical representations for searching.
2.  Calling `coffee_manual_kb.load(recreate=True)` would typically:
    *   Use its internal `PDFReader` to read the PDF specified in `path`.
    *   Break the content into `Document` chunks.
    *   Use an [Embedder](09_vectordb___embedder_.md) to create "embeddings" (numerical vectors) for each chunk.
    *   Store these chunks and their embeddings in the `vector_db`.
    For our example, we simplified this by directly "inserting" a simulated document into our mock database.

**Step 4: Agent Using the `KnowledgeBase`**

Now, our [Agent](02_agent_.md) can use this `coffee_manual_kb` to answer questions.

```python
# agent_using_kb.py
from agno.agent import Agent
from agno.models.openai import OpenAIChat # For mock model
from agno.run.response import Message
# Assume coffee_manual_kb is defined as in the previous snippet

# --- Mock Model for Agent ---
# This mock model will incorporate context from the KnowledgeBase
def mock_model_with_kb_context(messages, **kwargs) -> Message:
    user_query = ""
    kb_context_str = ""
    for m in messages:
        if m.role == "user":
            user_query = m.content
        if m.role == "system" and "Knowledge Base context:" in m.content: # Simplified check for context
            kb_context_str = m.content.replace("Knowledge Base context:", "").strip()

    if "descale" in user_query.lower():
        if kb_context_str:
            # Model "uses" the KB context to answer
            return Message(role="assistant", content=f"Based on the manual: {kb_context_str} Ensure you follow all safety steps.")
        else:
            return Message(role="assistant", content="I found no specific descaling info in the manual for that.")
    return Message(role="assistant", content="How can I help you with the coffee machine?")

mock_llm_for_kb = OpenAIChat(id="mock-gpt-kb-user")
mock_llm_for_kb.invoke = mock_model_with_kb_context
# --- End Mock Model Setup ---

# 1. Create an Agent and give it the KnowledgeBase
qa_agent = Agent(
    name="CoffeeManualExpert",
    model=mock_llm_for_kb,
    instructions="You are an expert on the Model X coffee machine. Use the provided manual excerpts to answer questions.",
    knowledge=coffee_manual_kb # Assign the KnowledgeBase!
)
print(f"Agent '{qa_agent.name}' is ready with its KnowledgeBase.")

# 2. Ask the Agent a question related to the manual
user_question = "How do I descale the Model X?"
print(f"\nUser: {user_question}")

# When the agent runs, it will (behind the scenes):
# a. See the user_question.
# b. Search its 'knowledge' (coffee_manual_kb) for relevant text chunks.
#    This search happens via `knowledge.search(query=user_question)`.
# c. Prepend these chunks as context to the prompt for its model.
# d. The model generates an answer using the query and the provided context.
response = qa_agent.run(message=user_question, search_knowledge=True) # `search_knowledge=True` is key!

if response:
    print(f"{qa_agent.name}: {response.content}")
```
When you run this (combining the `knowledgebase_setup.py` and `agent_using_kb.py` parts):
```
KnowledgeBase for coffee manual created (conceptually).
MockVectorDb 'coffee_manual_kb': Collection created.
MockVectorDb: Added 1 docs.
Documents loaded into KnowledgeBase (simulated).
Agent 'CoffeeManualExpert' is ready with its KnowledgeBase.

User: How do I descale the Model X?
MockVectorDb: Searching for 'How do I descale the Model X?'...
CoffeeManualExpert: Based on the manual: To descale Model X, use solution XYZ. Mix one part solution with two parts water. Run the cycle twice. Ensure you follow all safety steps.
```
Success!
1.  We created an `Agent` and passed our `coffee_manual_kb` to its `knowledge` parameter.
2.  When we called `qa_agent.run(message=user_question, search_knowledge=True)`, the `Agent` automatically used its `KnowledgeBase`.
3.  The `KnowledgeBase` (via our `MockVectorDb`) "searched" for content relevant to "How do I descale the Model X?" and found our simulated document.
4.  This relevant text was then provided as context to the agent's [Model](05_model_.md) (our `mock_llm_for_kb`).
5.  The `mock_llm_for_kb` used this context to formulate an informed answer.

The `test_pdf_knowledge_base.py` file shows more complete examples of how an agent interacts with a `PDFKnowledgeBase` and its underlying `LanceDb` vector store.

## How Does it Work Under the Hood?

Here's a step-by-step of what generally happens when an [Agent](02_agent_.md) with a `KnowledgeBase` answers a query (this is often called Retrieval Augmented Generation or RAG):

1.  **User Query**: The user asks the [Agent](02_agent_.md) a question (e.g., "How to descale Model X?").
2.  **Search KnowledgeBase**:
    *   If `search_knowledge=True` is specified in the `agent.run()` call (or if the agent is configured to always search), the [Agent](02_agent_.md) asks its `KnowledgeBase` to find information relevant to the user's query.
    *   The `KnowledgeBase` typically uses its [VectorDb & Embedder](09_vectordb___embedder_.md) (more in Chapter 9) to perform this search. The user's query is converted into an embedding (a numerical vector), and this vector is used to find `Document` chunks in the [VectorDb & Embedder](09_vectordb___embedder_.md) that have similar embeddings (meaning they are semantically similar).
    *   The `KnowledgeBase` returns a list of the most relevant `Document` chunks.
3.  **Contextual Prompting**: The [Agent](02_agent_.md) takes these retrieved `Document` chunks and adds their content to the prompt it's preparing for its [Model](05_model_.md). This effectively says to the Model: "Here's the user's question, and here's some relevant information I found in my library. Use this information to answer the question."
4.  **Model Generates Answer**: The [Model](05_model_.md) receives the user's query *and* the contextual snippets from the `KnowledgeBase`. It generates an answer that is "grounded" in the information provided from the documents.
5.  **Agent Returns Response**: The [Agent](02_agent_.md) returns the [Model](05_model_.md)'s answer to the user.

```mermaid
sequenceDiagram
    participant User
    participant MyAgent as Agent
    participant MyKB as KnowledgeBase
    participant MyVecDB as VectorDB (details in Ch9)
    participant MyModel as Model

    User->>MyAgent: run("How to descale Model X?", search_knowledge=True)
    MyAgent->>MyKB: search("How to descale Model X?")
    MyKB->>MyVecDB: Find relevant document_chunks for "How to descale Model X?"
    MyVecDB-->>MyKB: Returns [DocumentChunk1, DocumentChunk2]
    MyKB-->>MyAgent: Returns [DocumentChunk1, DocumentChunk2]
    MyAgent->>MyModel: Prompt (query="How to descale?", context="Content of Chunk1. Content of Chunk2.")
    MyModel-->>MyAgent: Answer ("Based on the manual: Use solution XYZ...")
    MyAgent-->>User: RunResponse (containing the answer)
end
```

### A Peek at the Code Structures

*   **`Document` (`agno/document/base.py`)**:
    As we saw, this is a simple dataclass holding content and metadata.
    ```python
    # Simplified from agno/document/base.py
    from dataclasses import dataclass, field
    from typing import Any, Dict, Optional, List

    @dataclass
    class Document:
        content: str
        id: Optional[str] = None
        name: Optional[str] = None
        meta_data: Dict[str, Any] = field(default_factory=dict)
        # ... other fields like embedding, embedder ...
    ```

*   **`Reader` (`agno/document/reader/base.py`)**:
    This is the base class for all readers. Specific readers like `PDFReader` or `DocxReader` inherit from it.
    ```python
    # Simplified from agno/document/reader/base.py
    from agno.document.base import Document
    from typing import List, Any
    from agno.document.chunking.fixed import FixedSizeChunking
    from agno.document.chunking.strategy import ChunkingStrategy


    class Reader:
        chunk: bool = True # Whether to chunk documents
        chunk_size: int = 5000 # Default size for chunks
        chunking_strategy: Optional[ChunkingStrategy] = None


        def __init__(self, chunk_size: int = 5000, chunking_strategy: Optional[ChunkingStrategy] = None) -> None:
            self.chunk_size = chunk_size
            self.chunking_strategy = chunking_strategy or FixedSizeChunking(chunk_size=self.chunk_size)

        def read(self, source: Any) -> List[Document]:
            # Each specific reader (PDFReader, DocxReader) implements this
            raise NotImplementedError

        def chunk_document(self, document: Document) -> List[Document]:
            # Uses a chunking strategy to split a Document into smaller Document chunks
            return self.chunking_strategy.chunk(document)
    ```
    The `PDFReader` in `agno/document/reader/pdf_reader.py` uses the `pypdf` library to extract text from PDF files. It then uses the `chunk_document` method (if `chunk=True`) to split the text into manageable pieces. There are also specialized PDF readers like `PDFImageReader` that can perform OCR on images within PDFs.

*   **`AgentKnowledge` (`agno/knowledge/agent.py`)**:
    This is the base class for knowledge base implementations like `PDFKnowledgeBase`.
    ```python
    # Simplified from agno/knowledge/agent.py
    from pydantic import BaseModel
    from typing import List, Optional, Dict, Any
    from agno.document.base import Document
    from agno.vectordb import VectorDb # Abstract base class for VectorDBs
    from agno.document.reader.base import Reader

    class AgentKnowledge(BaseModel):
        reader: Optional[Reader] = None
        vector_db: Optional[VectorDb] = None
        num_documents: int = 5 # Default number of docs to retrieve

        def load(self, recreate: bool = False, **kwargs):
            # Logic to read from source using self.reader,
            # embed documents, and store in self.vector_db.
            # Iterates through self.document_lists (provided by subclasses)
            print(f"Base AgentKnowledge: Loading with reader {self.reader} and DB {self.vector_db}")
            # ... (simplified: actual loading happens in subclasses like PDFKnowledgeBase) ...

        def search(self, query: str, num_documents: Optional[int] = None, filters: Optional[Dict[str, Any]] = None) -> List[Document]:
            if self.vector_db:
                return self.vector_db.search(query, limit=num_documents or self.num_documents, filters=filters)
            return []
        
        # ... async versions and other methods ...
    ```
    A `PDFKnowledgeBase` (found in `agno/knowledge/pdf.py`, but not shown here for brevity) would inherit from `AgentKnowledge` and implement specifics for handling PDF file paths, using `PDFReader` to get `Document`s, and then loading them into the `vector_db`.

## Conclusion

A `KnowledgeBase` combined with `Reader`s gives your `agno` [Agent](02_agent_.md) a powerful way to access and use information from your specific documents and data sources.
*   **`Reader`s** (like `PDFReader`, `DocxReader`) extract content from various file types.
*   This content is turned into **`Document`** objects (often in small, manageable chunks).
*   The **`KnowledgeBase`** organizes these `Document`s, making them searchable.
*   When an [Agent](02_agent_.md) needs to answer a question based on this knowledge, it searches the `KnowledgeBase` for relevant `Document` chunks and uses them as context for its [Model](05_model_.md).

This allows your agent to provide answers that are grounded in specific, up-to-date information rather than relying solely on its general pre-trained knowledge.

But how does the `KnowledgeBase` efficiently search through potentially thousands or millions of document chunks to find the most relevant ones? This often involves "embeddings" and "vector databases". Let's explore those next!

Next up: [Chapter 9: VectorDb & Embedder](09_vectordb___embedder_.md)

---

Generated by [AI Codebase Knowledge Builder](https://github.com/The-Pocket/Tutorial-Codebase-Knowledge)