---
layout: default
title: "Playground"
parent: "Agno"
nav_order: 1
---

# Chapter 1: Playground

Welcome to the `agno` tutorial! We're excited to help you get started building powerful AI applications. In this first chapter, we'll explore a crucial tool for development and testing: the **Playground**.

## What's the Big Deal with a Playground?

Imagine you've just created your first AI assistant using `agno`. Let's say it's a simple [Agent](02_agent_.md) designed to answer basic questions. How do you quickly try it out? How can you send it a message and see its response without writing a complex testing script or building a full user interface from scratch every time?

This is where the `Playground` comes in! It acts like a ready-made workshop or sandbox.

The `Playground` provides a user interface (typically web-based, powered by a framework called FastAPI) for interacting with and testing your AI creations like [Agent](02_agent_.md)s, [Team](03_team_.md)s, and Workflows. You can send messages, upload files (like images or documents for your AI to process), and observe how your AI components behave and respond in real-time.

Think of it like a real playground for children. They can try out different swings, slides, and climbing frames to see how they work and have fun. Similarly, the `agno` Playground lets you "play" with your AI components, experiment with different inputs, and see the results instantly.

## Key Ideas

The `Playground` essentially does two main things:
1.  **Hosts your AI components:** It takes the [Agent](02_agent_.md)s, [Team](03_team_.md)s, or Workflows you've built and makes them accessible.
2.  **Exposes them via a web server:** It creates web addresses (API endpoints) that you (or another application) can send requests to. This means you can interact with your AI using a web browser or simple command-line tools.

## Let's Set Up a Simple Playground!

The best way to understand the Playground is to see it in action. Let's set up a very basic one with a single, friendly [Agent](02_agent_.md).

First, you'll need an [Agent](02_agent_.md). We'll create a very simple one for now. Don't worry too much about the `Agent` details yet; we'll cover that in [Chapter 2: Agent](02_agent_.md).

```python
# main.py
from agno.agent import Agent
from agno.models.openai import OpenAIChat # We'll use a placeholder for a real AI model
from agno.playground import Playground
from agno.run.response import RunResponse, Message # To define how our agent responds

# 1. Define a simple Agent
# For this example, we'll make our agent echo back what we say.
# In a real application, this agent would use an AI model to generate responses.
def simple_echo_agent_logic(message: str, **kwargs) -> RunResponse:
    """A mock function for our agent's brain."""
    response_content = f"You told me: '{message}'"
    # Agents respond with a 'RunResponse' object, containing 'Messages'.
    # We'll learn more about these in Chapter 4.
    return RunResponse(
        content=response_content,
        messages=[Message(role="assistant", content=response_content)]
    )

my_friendly_agent = Agent(
    name="EchoBot",
    agent_id="echo-bot-001",
    # In a real scenario, you'd configure an actual AI model.
    # For now, we'll just assign our simple logic directly.
    # model=OpenAIChat(id="gpt-3.5-turbo"), # This would be a real model
    instructions="You are an echo bot. Repeat what the user says."
)
# Override the agent's run method with our simple logic for this example
my_friendly_agent.run = simple_echo_agent_logic
# If we wanted to use asynchronous operations, we'd also set 'arun'
# my_friendly_agent.arun = async_simple_echo_agent_logic

# 2. Create the Playground and add our agent
# You can pass a list of agents, teams, or workflows.
playground_instance = Playground(agents=[my_friendly_agent])

# 3. Get the FastAPI web application
# 'use_async=False' means we're using standard synchronous functions for this example.
# 'True' is often used for applications that need to handle many requests efficiently.
app = playground_instance.get_app(use_async=False)

# To run this server (you'd typically put this in your script's main execution block):
# if __name__ == "__main__":
#     import uvicorn
#     # This command starts a web server.
#     uvicorn.run(app, host="0.0.0.0", port=8000)
```

**What's happening in this code?**

1.  We define a very basic `my_friendly_agent`. Instead of connecting to a real AI model, we've given it a simple Python function (`simple_echo_agent_logic`) that just echoes back the input message. This keeps things simple for our first example.
2.  We create an instance of `Playground`, telling it about `my_friendly_agent`.
3.  We call `playground_instance.get_app()` to get a FastAPI application. FastAPI is the web framework `agno` uses to create the web server and API endpoints.
4.  The commented-out `uvicorn.run(...)` line shows how you would typically start this web server. Uvicorn is a server that can run FastAPI applications.

**Running and Interacting with the Playground:**

If you save the code above as `main.py` and run `uvicorn main:app --reload` in your terminal (you'll need `uvicorn` and `fastapi` installed: `pip install uvicorn fastapi`), a web server will start.

Now, you can interact with your "EchoBot":

1.  **API Documentation (Swagger UI):** Open your web browser and go to `http://localhost:8000/docs`. FastAPI automatically generates interactive API documentation. You'll see your agent's endpoints listed there, and you can even try them out directly from the browser!

2.  **Using `curl` (a command-line tool):**
    You can send a POST request to the agent's "run" endpoint. The endpoint path follows a pattern: `/v1/playground/agents/{agent_id}/runs`. For our `echo-bot-001`:

    ```bash
    curl -X POST "http://localhost:8000/v1/playground/agents/echo-bot-001/runs" \
         -H "Content-Type: application/x-www-form-urlencoded" \
         -d "message=Hello Playground!" \
         -d "stream=false"
    ```

    **Expected Output (JSON):**
    You should get a JSON response back that looks something like this:

    ```json
    {
        "content": "You told me: 'Hello Playground!'",
        "event": "run_end",
        "run_id": "some-unique-run-id",
        "session_id": "some-unique-session-id",
        "messages": [
            {
                "role": "user",
                "content": "Hello Playground!",
                "name": null,
                "tool_calls": null,
                "tool_call_id": null,
                "from_history": false
            },
            {
                "role": "assistant",
                "content": "You told me: 'Hello Playground!'",
                "name": null,
                "tool_calls": null,
                "tool_call_id": null,
                "from_history": false
            }
        ],
        "tools_results": null,
        "error": null,
        "input_tokens": 0,
        "output_tokens": 0,
        "cost": 0.0,
        "agent_id": "echo-bot-001"
    }
    ```
    As you can see, the agent responded as we defined! The Playground handled the web request, passed the message to our agent, and returned its response.

## What's Going On Under the Hood?

When you interact with the Playground, several things happen behind the scenes:

1.  **HTTP Request:** Your browser (or `curl`) sends an HTTP request to the web server started by `Playground`.
2.  **FastAPI Receives:** FastAPI, the web framework, receives this request.
3.  **Routing:** The `Playground` has "routers" (`async_router.py` or `sync_router.py`) that look at the URL (e.g., `/v1/playground/agents/echo-bot-001/runs`) and decide which function should handle it.
4.  **Finding the Component:** The handler function uses the `agent_id` from the URL ("echo-bot-001") to find the correct [Agent](02_agent_.md) instance that you provided when creating the `Playground`.
5.  **Executing the Component:** It then calls the [Agent](02_agent_.md)'s `run()` method (or `arun()` for asynchronous operations), passing along your message and any other data (like uploaded files).
6.  **Getting the Response:** The [Agent](02_agent_.md) does its work (in our example, just echoing) and returns a [RunResponse & Message](04_runresponse___message_.md) object.
7.  **Sending HTTP Response:** The Playground formats this `RunResponse` into JSON and sends it back as an HTTP response to your browser or `curl`.

Here's a simplified diagram of this flow:

```mermaid
sequenceDiagram
    participant User
    participant Client as Browser/curl
    participant PG as Playground (FastAPI)
    participant YourAgent as Agent (e.g., EchoBot)

    User->>Client: Enters "Hello!" & sends
    Client->>PG: POST /v1/playground/agents/echo-bot-001/runs (message="Hello!")
    PG->>PG: Finds 'echo-bot-001'
    PG->>YourAgent: Calls run(message="Hello!")
    YourAgent->>YourAgent: Processes message (echoes it)
    YourAgent-->>PG: Returns RunResponse object
    PG->>PG: Converts RunResponse to JSON
    PG-->>Client: Sends JSON response
    Client-->>User: Displays "You told me: 'Hello!'"
end
```

Let's peek at a bit of the `Playground` class itself:

```python
# Simplified from agno/playground/playground.py

from fastapi import FastAPI, APIRouter
from typing import List, Optional
from agno.agent import Agent # We'll cover Agent in the next chapter

class Playground:
    def __init__(
        self,
        agents: Optional[List[Agent]] = None,
        # ... can also accept teams and workflows
    ):
        # Ensure at least one type of component is provided
        if not agents: # Simplified condition
            raise ValueError("Agents (or teams/workflows) must be provided.")
        self.agents = agents
        # ... (more setup like initializing agents)

    def get_app(self, use_async: bool = True, prefix: str = "/v1") -> FastAPI:
        # If no FastAPI app exists, create one
        if not hasattr(self, 'api_app') or not self.api_app:
            self.api_app = FastAPI(title="Agno Playground") # Basic FastAPI app

        # Create a router if it doesn't exist. Routers help organize endpoints.
        if not hasattr(self, 'router') or not self.router:
            self.router = APIRouter(prefix=prefix) # Endpoints will start with /v1

        # Add the specific routes (API endpoints) for agents, teams, etc.
        if use_async:
            # self.get_async_router() returns an APIRouter with async endpoints
            self.router.include_router(self.get_async_router())
        else:
            # self.get_router() returns an APIRouter with sync endpoints
            self.router.include_router(self.get_router())
        
        # Add all these routes to the main FastAPI application
        self.api_app.include_router(self.router)
        return self.api_app

    # ... (methods like get_router, get_async_router are defined elsewhere)
    # These methods dynamically create the API endpoints based on the provided agents, etc.
    def get_router(self): # Simplified
        from agno.playground.sync_router import get_sync_playground_router
        return get_sync_playground_router(self.agents, None, None) # Pass agents

    def get_async_router(self): # Simplified
        from agno.playground.async_router import get_async_playground_router
        return get_async_playground_router(self.agents, None, None) # Pass agents
```
This `Playground` class is responsible for setting up the FastAPI application and its routes. The `get_router()` and `get_async_router()` methods (which internally call functions like `get_sync_playground_router` from `agno/playground/sync_router.py`) dynamically create the API endpoints based on the [Agent](02_agent_.md)s (or [Team](03_team_.md)s, Workflows) you provide.

For instance, the `create_agent_run` function within `sync_router.py` (or its async counterpart) handles the POST requests to `/v1/playground/agents/{agent_id}/runs`:

```python
# Highly simplified from agno/playground/sync_router.py
# This function is dynamically created and added to the router by get_sync_playground_router

# 'agents_list' would be the list of Agent objects passed to the Playground
def create_agent_run_handler(
    agent_id: str, # Comes from the URL path, e.g., "echo-bot-001"
    message: str,  # Comes from the request body (form data)
    agents_list: List[Agent] # The list of agents available to the playground
    # ... other parameters like stream, session_id, files
):
    # 1. Find the agent instance
    target_agent = None
    for ag in agents_list:
        if ag.agent_id == agent_id:
            target_agent = ag
            break
    
    if target_agent is None:
        # If agent not found, return an error (FastAPI's HTTPException)
        # raise HTTPException(status_code=404, detail="Agent not found")
        return {"error": "Agent not found"} # Simplified error

    # ... (handle file uploads, session management, etc.)

    # 2. Call the agent's run method
    response = target_agent.run(message=message) # Pass the message

    # 3. Return the response (FastAPI will convert this dict to JSON)
    return response.to_dict()
```
This handler function extracts the `agent_id` and `message`, finds the corresponding [Agent](02_agent_.md), and executes its `run` method.

**What About File Uploads?**

The Playground also makes it easy to send files to your [Agent](02_agent_.md)s. For example, an [Agent](02_agent_.md) might need to analyze an image or read a PDF document to answer questions using a [KnowledgeBase & Reader](08_knowledgebase___reader_.md).

The `test_image_support_file_upload.py` file contains tests showing this. When you upload a file through the Playground's API endpoint:

1.  The router function (like `create_agent_run`) receives the uploaded file(s).
2.  It checks the file type (e.g., `image/jpeg`, `application/pdf`).
3.  Helper utilities (like `process_image`, `process_document` from `agno/playground/utils.py`) convert these files into formats that `agno` components can work with (e.g., `Image` objects for pictures, or text content for documents that can be loaded into a [KnowledgeBase & Reader](08_knowledgebase___reader_.md)).
4.  These processed files are then passed to the [Agent](02_agent_.md)'s `run` method.

```python
# Snippet showing conceptual file handling within a router function
# (Simplified from async_router.py or sync_router.py)

# 'files' would be a list of uploaded files from the HTTP request
# 'agent' is the target Agent instance

# if files:
#     for uploaded_file in files:
#         if uploaded_file.content_type.startswith("image/"):
#             image_object = process_image(uploaded_file) # Converts to agno.media.Image
#             # Pass image_object to agent.run(images=[image_object], ...)
#         elif uploaded_file.content_type == "application/pdf":
#             if agent.knowledge: # Check if the agent has a knowledge base
#                 # Simplified: read content from PDF
#                 pdf_file_content_list = PDFReader().read(uploaded_file.file)
#                 agent.knowledge.load_documents(pdf_file_content_list)
#             else:
#                 # Handle error: agent can't process PDF without a knowledge base
#                 pass
#         # ... other file types
```
This allows you to test how your [Agent](02_agent_.md)s handle various types of multimodal input or document-based knowledge.

## Conclusion

The `Playground` is your go-to tool for quickly setting up a testbed for your `agno` creations. It wraps your [Agent](02_agent_.md)s, [Team](03_team_.md)s, and Workflows in a web server, providing API endpoints for interaction. This allows for easy testing, experimentation, and even forms the basis for building more complex UIs. You can send messages, upload files, and see your AI components in action without much boilerplate code.

Now that you understand how to host and test an AI component with the Playground, you're probably wondering what an `Agent` actually is and how to build one. Let's dive into that in the next chapter!

Next up: [Chapter 2: Agent](02_agent_.md)

---

Generated by [AI Codebase Knowledge Builder](https://github.com/The-Pocket/Tutorial-Codebase-Knowledge)