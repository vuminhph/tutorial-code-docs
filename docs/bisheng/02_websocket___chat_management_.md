---
layout: default
title: "WebSocket & Chat Management"
parent: "Bisheng"
nav_order: 2
---

# Chapter 2: WebSocket & Chat Management

Welcome back! In [Chapter 1: Backend API & Services](01_backend_api___services_.md), we learned how the Bisheng backend acts like a restaurant kitchen, handling requests from the frontend using APIs. But what about conversations that need to happen _right now_, like a live chat? Sending a new request for every single message back and forth would be like sending a separate letter for each sentence in a conversation – very slow!

Imagine you're talking to the restaurant manager through an intercom system instead of waiting for the waiter to relay messages. This intercom allows instant, continuous, two-way communication. That's what **WebSocket & Chat Management** provides for Bisheng.

**What Problem Does This Solve?**

When you chat with an AI assistant in Bisheng, you expect the conversation to feel real-time. You type a message, hit send, and ideally, the response starts appearing almost immediately, maybe even word by word (streaming). The standard request-response cycle we saw in Chapter 1 isn't great for this.

The **WebSocket & Chat Management** component solves this by:

1.  Establishing a **persistent connection** between your browser (frontend) and the Bisheng backend.
2.  Allowing **instant, two-way communication** over this connection.
3.  Handling multiple chat sessions simultaneously.
4.  Receiving your chat messages and sending them to the right place for processing (like a specific AI assistant or workflow).
5.  Managing chat history for ongoing conversations.
6.  **Streaming** responses back to you, so you see the AI typing in real-time.

Think of it as the restaurant's dedicated intercom system connected to every table (frontend client). It manages all the ongoing calls, making sure messages get to the right person (backend logic) and replies come back instantly.

**Key Concepts**

1.  **WebSocket:** This is the technology that enables the "intercom". Unlike standard HTTP requests which are like sending a letter (request) and waiting for a reply letter (response), a WebSocket connection is like opening a phone line or intercom channel. Once opened, both the frontend and backend can send messages to each other at any time without needing to establish a new connection for each message. This is perfect for real-time applications like chat.

2.  **Chat Management:** This is the "operator" managing the intercom system. It's not just about the connection itself. It involves:
    - **Connection Handling:** Accepting new WebSocket connections when a user starts a chat and cleaning up when they leave.
    - **Message Routing:** Receiving messages from the frontend via WebSocket and figuring out which backend logic (e.g., which specific AI Assistant or [Workflow Engine](04_workflow_engine_.md) run) should handle it.
    - **Session Management:** Keeping track of different ongoing chat sessions (e.g., you might be chatting with two different assistants in two different browser tabs).
    - **History Management:** Often works with [Database Models](09_database_models_.md) to save and retrieve conversation history.
    - **Response Streaming:** Receiving responses (often generated piece by piece by an AI) and sending them back over the WebSocket in chunks, creating that "typing" effect.

**How It Works: A Chat Message Journey**

Let's trace what happens when you send a message in a Bisheng chat:

1.  **Connection:** When you open a chat interface, the frontend establishes a WebSocket connection with the backend endpoint (e.g., `/api/v1/chat/{flow_id}`). Think of this as opening the intercom channel.
2.  **User Input:** You type "Hello, Bisheng!" and press Enter.
3.  **Frontend Sends:** The frontend instantly sends your message ("Hello, Bisheng!") over the established WebSocket connection.
4.  **Backend Receives:** The `ChatManager` on the backend receives the message through the specific WebSocket connection tied to your chat session.
5.  **Routing & Processing:** The `ChatManager` identifies which `ChatClient` object represents your connection. This client object then determines the appropriate logic to handle the message. For an AI assistant chat, it might involve:
    - Retrieving chat history ([Database Models](09_database_models_.md)).
    - Calling the specific [GPTS / Assistant Abstraction](03_gpts___assistant_abstraction_.md).
    - The Assistant might use an [LLM & Embedding Wrappers](08_llm___embedding_wrappers_.md) to generate a response.
6.  **Streaming Response:** The AI starts generating a response, perhaps "Hello there! How can I help you today?". Instead of waiting for the full response, the backend `ChatClient` receives it in pieces (e.g., "Hello", " there!", " How", " can", ...).
7.  **Backend Sends:** As each piece arrives, the `ChatClient` immediately sends it back to the frontend over the _same_ WebSocket connection.
8.  **Frontend Displays:** The frontend receives these pieces and displays them progressively, making it look like the AI is typing.

**Looking at the Code (Simplified)**

Let's see some simplified code snippets to understand the core ideas.

**1. Establishing the Connection (`chat.py`)**

The backend needs an endpoint to accept WebSocket connections. FastAPI makes this straightforward.

```python
# src/backend/bisheng/api/v1/chat.py (Simplified)
from fastapi import APIRouter, WebSocket, Depends
from bisheng.chat.manager import ChatManager # Our chat manager
# ... other imports ...

router = APIRouter(tags=['Chat'])
chat_manager = ChatManager() # Create an instance of the manager

@router.websocket('/chat/{flow_id}') # Define the WebSocket route
async def chat(
        *,
        flow_id: UUID,
        websocket: WebSocket,
        chat_id: Optional[str] = None,
        # ... other parameters like user authentication ...
):
    """Websocket endpoint for chat."""
    # ... authentication and validation logic ...

    # Hand over the connection management to the ChatManager
    # This function will handle receiving/sending messages for this specific connection
    await chat_manager.handle_websocket(flow_id.hex,
                                        chat_id,
                                        websocket,
                                        user_id # Extracted from authentication
                                        # ... potentially pass initial graph data ...
                                        )

```

- `@router.websocket('/chat/{flow_id}')`: This decorator tells FastAPI that this function handles WebSocket connections at the specified URL path.
- `websocket: WebSocket`: FastAPI provides the connected WebSocket object.
- `chat_manager.handle_websocket(...)`: This is where we pass the connection details to our central `ChatManager` to handle the rest of the communication lifecycle for this specific chat.

**2. Managing Connections (`manager.py`)**

The `ChatManager` keeps track of all active connections.

```python
# src/backend/bisheng/chat/manager.py (Simplified)
from fastapi import WebSocket
from typing import Dict
from bisheng.chat.client import ChatClient # Represents one connection
# ... other imports ...

class ChatManager:
    def __init__(self):
        # A dictionary to store active connections, mapping a unique key to the WebSocket object
        self.active_connections: Dict[str, WebSocket] = {}
        # A dictionary mapping a unique client key to the ChatClient handler instance
        self.active_clients: Dict[str, ChatClient] = {} # Or other client types
        # ... other initializations like chat history ...

    async def accept_client(self, client_key: str, chat_client: ChatClient, websocket: WebSocket):
        """Accepts and stores a new client connection."""
        await websocket.accept() # Perform the WebSocket handshake
        self.active_clients[client_key] = chat_client
        self.active_connections[client_key] = websocket # Store the raw connection too (or manage within client)
        logger.info(f"Client connected: {client_key}")

    def clear_client(self, client_key: str):
        """Removes a client connection when they disconnect."""
        self.active_clients.pop(client_key, None)
        self.active_connections.pop(client_key, None)
        logger.info(f"Client disconnected: {client_key}")

    async dispatch_client(self, request, client_id, chat_id, login_user, work_type, websocket, **kwargs):
        """Creates a client handler and manages its lifecycle."""
        client_key = generate_uuid() # Unique key for this connection instance

        # Decide which type of client handler to use (e.g., for GPTS or Workflow)
        if work_type == WorkType.GPTS:
             chat_client = ChatClient(request, client_key, client_id, chat_id, login_user.user_id, login_user, work_type, websocket, **kwargs)
        elif work_type == WorkType.WORKFLOW:
             chat_client = WorkflowClient(request, client_key, client_id, chat_id, login_user.user_id, login_user, work_type, websocket, **kwargs)
        else:
             # Handle other types or error
             pass

        await self.accept_client(client_key, chat_client, websocket)

        try:
            while True: # Loop to continuously listen for messages
                message = await websocket.receive_json() # Wait for a message from the frontend
                await chat_client.handle_message(message) # Pass the message to the client handler
        except WebSocketDisconnect:
            logger.info(f"WebSocket disconnected for client: {client_key}")
        # ... other exception handling ...
        finally:
            self.clear_client(client_key) # Clean up on disconnect

    # ... methods to send messages, handle history etc. ...
```

- `active_connections` / `active_clients`: Dictionaries to keep track of who is currently connected.
- `accept_client`: Handles the initial handshake and stores the connection.
- `clear_client`: Removes the connection when the user closes the chat or navigates away.
- `dispatch_client`: This is called by the endpoint. It creates a specific client handler (`ChatClient`, `WorkflowClient`) based on the type of chat, accepts the connection, and then enters a loop listening for incoming messages using `websocket.receive_json()`. When a message arrives, it calls `chat_client.handle_message()`.

**3. Handling a Single Chat Connection (`client.py`)**

The `ChatClient` (or similar classes in `clients/`) represents one specific user's chat session and handles its messages.

```python
# src/backend/bisheng/chat/client.py (Simplified version focusing on GPTS)
from fastapi import WebSocket
from queue import Queue # Used for streaming responses
# ... other imports like AssistantAgent, ChatResponse ...

class ChatClient: # Simplified example for a GPTS chat
    def __init__(self, ..., websocket: WebSocket, **kwargs):
        self.websocket = websocket
        # ... store client_id, chat_id, user_info, etc. ...
        self.gpts_agent: AssistantAgent | None = None # The AI Assistant logic
        self.stream_queue = Queue() # Queue to handle streaming chunks
        self.task_ids = [] # To manage background processing tasks

    async def send_json(self, message: ChatMessage):
        """Sends a JSON message back to the frontend via WebSocket."""
        await self.websocket.send_json(message.dict())

    async def handle_message(self, message: Dict[any, any]):
        """Handles an incoming message from the frontend."""
        # Submit the actual processing to a background thread to avoid blocking
        # the WebSocket connection handling.
        trace_id = generate_uuid()
        thread_pool.submit(trace_id, self.wrapper_task, trace_id, self._process_gpts_message, message)

    async def _process_gpts_message(self, message: Dict[any, any]):
        """The actual logic to process a message (runs in background)."""
        try:
            await self.send_response('processing', 'begin', '') # Inform frontend processing started
            inputs = message.get('inputs', {})
            input_msg = inputs.get('input')

            # 1. Initialize the assistant agent if not already done
            await self.init_gpts_agent()

            # 2. Save the user's message to history (simplified)
            await self.add_message('human', json.dumps(inputs), 'question')

            # 3. Get chat history (simplified)
            chat_history = await self.get_latest_history()

            # 4. Run the assistant agent to get the response
            # The agent uses a callback (self.gpts_async_callback) to handle streaming
            result = await self.gpts_agent.run(input_msg, chat_history, self.gpts_async_callback)
            answer = result[-1].content # Final complete answer

            # 5. Save the final answer to history (simplified)
            res = await self.add_message('bot', answer, 'answer')

            # 6. Send final answer confirmation (streaming handled by callback)
            await self.send_response('answer', 'end_cover', answer, message_id=res.id)

        except Exception as e:
            logger.exception('Error processing message:')
            await self.send_response('system', 'end', 'Error: ' + str(e))
        finally:
            await self.send_response('processing', 'close', '') # Inform frontend processing finished

    # ... other methods like init_gpts_agent, add_message, get_latest_history ...
    # ... Callback handler (`AsyncGptsDebugCallbackHandler`) would use `send_json` to stream partial responses ...
```

- `__init__`: Stores the WebSocket connection and initializes things like the agent or streaming queue.
- `send_json`: A helper to send structured messages back to the frontend.
- `handle_message`: Receives the raw message dictionary and typically delegates the heavy processing (`_process_gpts_message`) to a background task/thread to keep the WebSocket responsive.
- `_process_gpts_message`: This is where the core chat logic happens: initialize the agent, save messages, get history, run the agent, save the response. Crucially, when `self.gpts_agent.run` is called, it uses a _callback handler_ (`self.gpts_async_callback`, often defined in `api/v1/callback.py`). This callback is responsible for receiving streamed chunks from the AI model and using `send_json` to immediately forward them to the frontend via the WebSocket.

**Internal Implementation: The Intercom System**

Let's visualize the flow when a user sends a chat message:

```mermaid
sequenceDiagram
    participant FE as Frontend (Browser)
    participant WS_EP as WebSocket Endpoint (chat.py)
    participant Mgr as ChatManager (manager.py)
    participant Client as ChatClient (client.py)
    participant Logic as Processing Logic (e.g., AssistantAgent)

    FE->>+WS_EP: Establishes WebSocket Connection
    WS_EP->>+Mgr: handle_websocket(connection_details)
    Mgr->>Mgr: Creates ChatClient instance
    Mgr->>+Client: Initializes Client
    Client-->>-Mgr: Initialization Done
    Mgr-->>-WS_EP: Ready
    WS_EP-->>-FE: Connection Open

    Note over FE, Client: Connection is now open for messages

    FE->>+Client: Sends Message ("Hello!") via WebSocket
    Client->>Client: handle_message(payload)
    Client->>+Logic: process_message("Hello!", history, callback)
    Logic->>Logic: Generates response ("Hi ", "there!")
    Logic->>-Client: Calls callback with "Hi " (stream chunk 1)
    Client->>-FE: Sends "Hi " via WebSocket
    Logic->>-Client: Calls callback with "there!" (stream chunk 2)
    Client->>-FE: Sends "there!" via WebSocket
    Logic-->>-Client: Returns full response ("Hi there!")
    Client->>Client: Saves history, etc.
    Client-->>-FE: Sends end-of-message signal (optional)

```

**Step-by-Step:**

1.  **Connect:** Frontend connects to the WebSocket endpoint (`/api/v1/chat/{flow_id}`).
2.  **Accept:** The endpoint function in `chat.py` runs.
3.  **Manage:** It calls `ChatManager.handle_websocket` (or `dispatch_client` in newer versions).
4.  **Create Client:** `ChatManager` creates a specific `ChatClient` (or `WorkflowClient`, etc.) instance to manage this individual connection and stores it.
5.  **Listen:** The `ChatManager` (via the client handler loop) waits for messages on the WebSocket (`websocket.receive_json()`).
6.  **Receive:** Frontend sends a message.
7.  **Handle:** The loop receives the message and calls `chat_client.handle_message()`.
8.  **Process:** `handle_message` typically starts a background task (`_process_gpts_message` or similar) which:
    - Initializes necessary components (like the `AssistantAgent`).
    - Calls the processing logic (e.g., `gpts_agent.run`).
    - Provides a **callback handler** to the processing logic.
9.  **Stream:** As the processing logic generates response chunks, it calls the callback handler.
10. **Send:** The callback handler immediately uses `chat_client.send_json()` to send the chunk back over the WebSocket to the frontend.
11. **Complete:** Once processing is fully done, the background task might send a final confirmation message.
12. **Disconnect:** When the user closes the chat, the `WebSocketDisconnect` exception is caught, and `ChatManager.clear_client` cleans up the stored connection information.

**Connecting to Other Parts**

WebSocket & Chat Management is the real-time communication backbone, connecting:

- The **Frontend User Interface** (providing the chat window).
- [Backend API & Services](01_backend_api___services_.md): While WebSockets handle the chat stream, initial setup or related actions might still use standard APIs.
- [GPTS / Assistant Abstraction](03_gpts___assistant_abstraction_.md): Routes chat messages to the correct assistant for processing.
- [Workflow Engine](04_workflow_engine_.md): Can interact with workflows that involve chat steps or user input via WebSocket communication (`WorkflowClient`).
- [LLM & Embedding Wrappers](08_llm___embedding_wrappers_.md): Used by the Assistant/Workflow to generate responses that are then streamed back.
- [Database Models](09_database_models_.md): Used by the `ChatClient` or `ChatHistory` to store and retrieve conversation logs.

**Conclusion**

You've now learned how Bisheng handles real-time conversations using the "intercom" system of WebSockets. We saw how the `ChatManager` acts as the central operator, managing connections, while individual `ChatClient` instances handle the message flow for each user, routing messages for processing and streaming responses back instantly. This provides the smooth, interactive chat experience users expect.

But how does the system know _which_ assistant to talk to, and how does that assistant actually work? In the next chapter, we'll explore the abstraction that represents these AI assistants.

Ready to meet the assistants? Let's move on to [Chapter 3: GPTS / Assistant Abstraction](03_gpts___assistant_abstraction_.md).

---

Generated by [AI Codebase Knowledge Builder](https://github.com/The-Pocket/Tutorial-Codebase-Knowledge)
