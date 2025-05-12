---
layout: default
title: "VectorDb & Embedder"
parent: "Agno"
nav_order: 9
---

# Chapter 9: VectorDb & Embedder

Welcome to Chapter 9! In [Chapter 8: KnowledgeBase & Reader](08_knowledgebase___reader_.md), we learned how to give our [Agent](02_agent_.md) access to specific information from documents using a `KnowledgeBase`. We saw that an agent can "search" this knowledge. But how does an agent efficiently sift through potentially thousands of document pieces to find the *exact* snippet that answers your question, especially when your question might use different words than the document?

This is where the magic of `VectorDb` and `Embedder` comes in! They enable your agent to search by *meaning*, not just keywords.

## The Problem: Finding a Needle in a Haystack by Meaning

Imagine your `KnowledgeBase` contains hundreds of pages from a complex technical manual. If a user asks, "How do I fix the blinking red light?", a simple keyword search for "blinking red light" might miss a relevant section titled "Troubleshooting Indicator LEDs" which explains that a "flashing crimson LED" means a specific error.

We need a way to understand that "blinking red light" and "flashing crimson LED" are semantically similar, even if the words are different. This is what `VectorDb`s and `Embedder`s help us achieve.

**The Core Idea:**

*   An **`Embedder`** is like a universal translator that converts any piece of text (a word, a sentence, a paragraph) into a list of numbers called an "embedding" or a "vector". Think of this vector as a numerical fingerprint representing the *meaning* of the text. Texts with similar meanings will have similar numerical fingerprints.
*   A **`VectorDb`** (Vector Database) is a special kind of database designed to store these numerical fingerprints (embeddings) along with the original text. Its superpower is that it can very quickly find fingerprints that are "close" to a given fingerprint, even in a huge collection.

So, to find information about a "blinking red light":
1.  The `Embedder` translates "blinking red light" into its numerical fingerprint.
2.  The `VectorDb` looks for stored document fingerprints that are most similar to this query fingerprint.
3.  The documents associated with those similar fingerprints are retrieved – these are likely to be the most relevant pieces of information, even if they don't use the exact same words.

This is like a super-powered library catalog where books (documents) are organized not by title, but by the *meaning* of their content, making it easy to find similar information.

## Key Concepts Explained

### 1. Embeddings: The Numerical Fingerprints of Meaning

An embedding is a list of numbers (a vector) that represents a piece of text in a high-dimensional space. It sounds complex, but the key idea is:
*   **Text in, Numbers out**: An `Embedder` takes text as input and produces a vector as output.
*   **Meaning Captured**: This vector aims to capture the semantic meaning of the text.
*   **Similarity is Proximity**: Texts with similar meanings will have embeddings that are "close" to each other in this numerical space. Texts with different meanings will be "far apart".

For example:
*   The embedding for "happy dog" might be numerically close to the embedding for "joyful puppy".
*   But it would be far from the embedding for "sad cat" or "quantum physics".

### 2. `Embedder`: The Meaning Translator

The `Embedder` is the component responsible for creating these embeddings. `agno` provides access to various embedding models, often from the same providers as the main AI [Model](05_model_.md)s.
*   Example: `OpenAIEmbedder` (from `agno.embedder.openai`) uses OpenAI's embedding models (like `text-embedding-3-small`).

Let's see a conceptual example of using an `Embedder`:

```python
# embedder_example.py
from agno.embedder.openai import OpenAIEmbedder # Using OpenAI's embedder

# Initialize the embedder
# You'd typically need an API key set as an environment variable (e.g., OPENAI_API_KEY)
try:
    embedder = OpenAIEmbedder(id="text-embedding-3-small")
    print("OpenAIEmbedder initialized.")

    # Get an embedding for a piece of text
    text_to_embed = "A happy dog plays in the park."
    embedding_vector = embedder.get_embedding(text_to_embed)

    print(f"\nText: '{text_to_embed}'")
    # Embeddings can be long, so we'll just show the first few numbers and its length
    print(f"Embedding (first 5 numbers): {embedding_vector[:5]}...")
    print(f"Length of embedding vector: {len(embedding_vector)}")

except ImportError:
    print("OpenAI library not installed, skipping embedder example.")
except Exception as e:
    print(f"Could not run embedder example (API key might be missing or other issue): {e}")

```
**What's happening?**
1.  We create an `OpenAIEmbedder` instance, specifying which model to use (e.g., "text-embedding-3-small").
2.  We call `embedder.get_embedding()` with our text.
3.  It returns a list of numbers (the embedding vector). The `OpenAIEmbedder` class (from `agno/embedder/openai.py`) handles the communication with the OpenAI API to get this vector.

The output would show the first few numbers of the long vector and its total dimension (e.g., 1536 for "text-embedding-3-small"). This vector is the "fingerprint" for our sentence.

### 3. `VectorDb`: The Smart Library for Embeddings

A `VectorDb` is a database optimized for storing and searching these embedding vectors. When you give it a query embedding, it can efficiently find the stored embeddings that are most similar to it (e.g., using "cosine similarity" or "Euclidean distance" as measures of closeness).

`agno` supports several `VectorDb` backends, such as:
*   `ChromaDb` (from `agno.vectordb.chroma`): Good for local development, stores data on your disk.
*   `LanceDb` (from `agno.vectordb.lancedb`): Another local/embeddable option.
*   `PineconeDb` (from `agno.vectordb.pineconedb`): A popular managed cloud vector database.

Let's see a conceptual setup with `ChromaDb`. (This example assumes you have `chromadb` installed: `pip install chromadb`)

```python
# vectordb_example.py
from agno.document import Document
from agno.vectordb.chroma import ChromaDb
from agno.embedder.openai import OpenAIEmbedder # We need an embedder for the DB

# Assume 'embedder' is initialized as in the previous example, or use a mock
try:
    embedder = OpenAIEmbedder(id="text-embedding-3-small")
except Exception: # Fallback to a mock if OpenAIEmbedder fails
    class MockEmbedder:
        def get_embedding(self, text): return [0.1] * 1536 # Consistent dimension
    embedder = MockEmbedder()
    print("Using MockEmbedder for VectorDB example.")

# 1. Initialize ChromaDb
# It needs a name for its "collection" (like a table) and an embedder.
# 'path' specifies where to store data locally.
db_path = "tmp/my_chroma_db"
vector_db = ChromaDb(
    collection="my_document_store",
    path=db_path,
    embedder=embedder # The DB uses this to create embeddings for new docs
)
vector_db.create() # Creates the collection if it doesn't exist
print(f"ChromaDb collection 'my_document_store' ready at {db_path}.")

# 2. Create some Document objects
doc1 = Document(id="doc1", content="The cat sat on the mat.")
doc2 = Document(id="doc2", content="A dog played in the yard.")
doc3 = Document(id="doc3", content="The feline rested on the rug.") # Similar to doc1

# 3. Add documents to the VectorDb
# The VectorDb will use its 'embedder' to get embeddings for doc.content
# and then store the doc (or its ID/metadata) along with the embedding.
vector_db.insert([doc1, doc2, doc3])
print(f"Inserted {vector_db.get_count()} documents into ChromaDb.")

# 4. Search the VectorDb
query_text = "Where did the kitty sit?"
print(f"\nSearching for: '{query_text}'")
# The VectorDb will:
# a. Use its 'embedder' to get an embedding for query_text.
# b. Search for stored document embeddings similar to the query_text's embedding.
# c. Return the original Document objects.
search_results = vector_db.search(query_text, limit=2)

print("\nSearch Results:")
for result_doc in search_results:
    print(f"  ID: {result_doc.id}, Content: '{result_doc.content}'")

# Clean up (optional, good for temporary test DBs)
# vector_db.drop()
# print("\nChromaDb collection dropped.")
```
**What's happening?**
1.  We initialize `ChromaDb`, giving it a name, a path to store data, and our `embedder`.
2.  We create some `Document` objects.
3.  We call `vector_db.insert()`. `ChromaDb` internally uses the provided `embedder` to convert each `Document`'s content into an embedding and then stores these embeddings along with references to the documents.
4.  We call `vector_db.search()` with a query string. `ChromaDb` again uses the `embedder` for the query, then finds and returns the `Document`s whose stored embeddings are most similar.

**Expected Output (will depend on the actual embeddings if not mocked):**
```
OpenAIEmbedder initialized. # or "Using MockEmbedder..."
ChromaDb collection 'my_document_store' ready at tmp/my_chroma_db.
Inserted 3 documents into ChromaDb.

Searching for: 'Where did the kitty sit?'

Search Results:
  ID: doc1, Content: 'The cat sat on the mat.'
  ID: doc3, Content: 'The feline rested on the rug.'
```
Notice how "Where did the kitty sit?" (which is about a cat) correctly found documents "doc1" (The cat...) and "doc3" (The feline...) because their meanings are similar, even though the exact words are different! `doc2` (about a dog) was not a top result.

You can see more detailed examples of `ChromaDb` in `test_chromadb.py` and `PineconeDb` in `test_pineconedb.py`.

## How `KnowledgeBase` Uses `Embedder` and `VectorDb`

Now, let's connect this back to the [KnowledgeBase & Reader](08_knowledgebase___reader_.md) from Chapter 8. A `KnowledgeBase` uses an `Embedder` and a `VectorDb` behind the scenes:

1.  **Initialization**: When you create a `KnowledgeBase`, you usually provide it with an `Embedder` and a `VectorDb` instance.
    ```python
    # Conceptual KnowledgeBase setup
    # from agno.knowledge.base import AgentKnowledge # A base for KBs
    # from agno.document.reader.base import Reader # A base for Readers
    # pdf_kb = AgentKnowledge(
    #     reader=SomeReader(), # To read source files
    #     vector_db=vector_db, # Our ChromaDb instance from above
    #     embedder=embedder    # Our OpenAIEmbedder instance
    # )
    ```

2.  **Loading Data (`kb.load()`)**:
    *   The `KnowledgeBase` uses its `Reader` to read source files and get `Document` objects.
    *   For each `Document`, it uses its `Embedder` to generate an embedding for the document's content.
    *   It then stores these `Document`s (often just their content or key metadata) and their corresponding embeddings into its `VectorDb`.

3.  **Searching Data (`kb.search(query)`)**:
    *   When you ask the `KnowledgeBase` to search for a `query`, it first uses its `Embedder` to get an embedding for your `query` text.
    *   Then, it passes this query embedding to its `VectorDb`.
    *   The `VectorDb` performs a similarity search and returns the `Document` objects whose stored embeddings are closest to the query embedding.
    *   These retrieved `Document`s are then used by the [Agent](02_agent_.md) as context to answer your question (this is Retrieval Augmented Generation - RAG).

## Under the Hood: The RAG Search Flow

Let's visualize the search process when an [Agent](02_agent_.md) uses a `KnowledgeBase` (which internally uses an `Embedder` and `VectorDb`):

```mermaid
sequenceDiagram
    participant User
    participant MyAgent as Agent
    participant MyKB as KnowledgeBase
    participant MyEmbedder as Embedder
    participant MyVecDB as VectorDb

    User->>MyAgent: "How to descale Model X?"
    MyAgent->>MyKB: search("How to descale Model X?")
    
    MyKB->>MyEmbedder: Get embedding for "How to descale Model X?"
    MyEmbedder-->>MyKB: Returns query_embedding
    
    MyKB->>MyVecDB: Find documents similar to query_embedding
    MyVecDB-->>MyKB: Returns [SimilarDoc1, SimilarDoc2]
    
    MyKB-->>MyAgent: Returns [SimilarDoc1, SimilarDoc2]
    MyAgent->>MyAgent: Use SimilarDocs as context for LLM prompt
    MyAgent-->>User: Answer based on SimilarDocs
end
```

**Step-by-step during a search:**
1.  **Query to Agent**: The user sends a query to the [Agent](02_agent_.md).
2.  **Agent to KnowledgeBase**: The [Agent](02_agent_.md) passes the query to its `KnowledgeBase`'s `search` method.
3.  **KnowledgeBase to Embedder (Query Embedding)**: The `KnowledgeBase` uses its configured `Embedder` to convert the user's text query into a numerical query embedding.
4.  **KnowledgeBase to VectorDb (Similarity Search)**: The `KnowledgeBase` sends this query embedding to its `VectorDb`. The `VectorDb` compares this query embedding against all the document embeddings it has stored and identifies the ones that are most similar (closest in the vector space).
5.  **VectorDb to KnowledgeBase (Results)**: The `VectorDb` returns the original `Document`s (or their IDs/content) that correspond to the top N most similar embeddings.
6.  **KnowledgeBase to Agent (Context)**: The `KnowledgeBase` passes these relevant `Document`s back to the [Agent](02_agent_.md).
7.  **Agent uses Context**: The [Agent](02_agent_.md) adds the content of these retrieved `Document`s as context into the prompt it sends to its main AI [Model](05_model_.md), which then generates the final answer.

### A Glimpse into the Code Definitions

*   **`Embedder` (`agno/embedder/base.py`)**: This is the base class all specific embedders inherit from.
    ```python
    # Simplified from agno/embedder/base.py
    from dataclasses import dataclass
    from typing import List, Optional, Tuple, Dict

    @dataclass
    class Embedder:
        dimensions: Optional[int] = 1536 # Example default

        def get_embedding(self, text: str) -> List[float]:
            raise NotImplementedError # Each subclass implements this

        def get_embedding_and_usage(self, text: str) -> Tuple[List[float], Optional[Dict]]:
            # Also returns token usage, etc.
            raise NotImplementedError
    ```
    The `OpenAIEmbedder` class in `agno/embedder/openai.py` implements these methods by calling the OpenAI API.

*   **`VectorDb` (`agno/vectordb/base.py`)**: This is the abstract base class for all vector database implementations.
    ```python
    # Simplified from agno/vectordb/base.py
    from abc import ABC, abstractmethod
    from typing import List, Optional, Dict, Any
    from agno.document import Document

    class VectorDb(ABC):
        @abstractmethod
        def create(self) -> None: # Setup the DB/collection
            raise NotImplementedError

        @abstractmethod
        def insert(self, documents: List[Document], ...) -> None:
            # Takes Document objects, gets their embeddings (often using an
            # embedder associated with the VectorDb instance or the KnowledgeBase),
            # and stores them.
            raise NotImplementedError
        
        def upsert(self, documents: List[Document], ...) -> None:
            # Insert or update documents.
            # Not all DBs might implement this distinct from insert.
            raise NotImplementedError

        @abstractmethod
        def search(self, query: str, limit: int = 5, ...) -> List[Document]:
            # Takes a query string, gets its embedding, searches the DB,
            # and returns relevant Document objects.
            raise NotImplementedError
        
        # ... other methods like exists, drop, async versions ...
    ```
    Implementations like `ChromaDb` (`agno/vectordb/chroma.py`) or `PineconeDb` (`agno/vectordb/pineconedb.py`) provide the concrete logic for interacting with those specific vector database systems. They typically take an `Embedder` instance during their initialization to handle the embedding of documents and queries.

## Conclusion

`Embedder`s and `VectorDb`s are the engines that power modern semantic search and Retrieval Augmented Generation (RAG) in systems like `agno`.
*   **`Embedder`s** turn text into meaningful numerical representations (embeddings).
*   **`VectorDb`s** store these embeddings and allow for fast similarity searches.

Together, they enable your `KnowledgeBase` (and thus your [Agent](02_agent_.md)) to find information based on semantic relevance, leading to much smarter and more accurate answers grounded in your provided documents. This "understanding by meaning" is a huge leap beyond simple keyword matching.

We've seen how agents can remember things with [Memory](07_memory_.md), access specific documents with [KnowledgeBase & Reader](08_knowledgebase___reader_.md), and search that knowledge effectively with `VectorDb` & `Embedder`. But where does all this persistent data (like memory databases, vector database files, or agent configurations) actually live?

Next up: [Chapter 10: Storage](10_storage_.md)

---

Generated by [AI Codebase Knowledge Builder](https://github.com/The-Pocket/Tutorial-Codebase-Knowledge)