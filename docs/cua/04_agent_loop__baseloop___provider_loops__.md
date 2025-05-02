---
layout: default
title: "Agent Loop (BaseLoop / Provider Loops)"
parent: "Computer Use Agent (CUA)"
nav_order: 4
---

# Chapter 4: Agent Loop (BaseLoop / Provider Loops)

In [Chapter 3: Computer Agent (ComputerAgent)](03_computer_agent__computeragent__.md), we met the AI brain, the `ComputerAgent`, which takes our high-level tasks and figures out how to perform them on the [Computer](01_computer_.md). We learned that the agent works in a cycle: **Observe** (see the screen), **Reason** (think about the next step), and **Act** (perform the step using the [Computer Interface](02_computer_interface__basecomputerinterface___macoscomputerinterface__.md)).

But how does the agent _actually keep doing_ this cycle over and over again until the task is finished? It needs a structured routine, a main program that orchestrates this loop. That's the job of the **Agent Loop**.

## What is an Agent Loop?

Think of the Agent Loop as the **operating system** or the **main engine** for our `ComputerAgent`. It's the core process that continuously runs the Observe-Reason-Act cycle. It manages the flow of information: getting observations, sending them to the AI model, receiving instructions, executing actions, and repeating the whole process.

Without a loop, the agent would just perform one step and stop. The loop provides the structure for the agent to work persistently towards its goal.

Imagine our task from Chapter 3: "Open the Calculator app." The Agent Loop is responsible for:

1.  Taking the _first_ screenshot.
2.  Asking the AI: "Based on this screen, what's the first step to open the Calculator?"
3.  Getting the AI's answer (e.g., "Press Command+Space").
4.  Telling the [Computer Interface](02_computer_interface__basecomputerinterface___macoscomputerinterface__.md) to press Command+Space.
5.  Taking a _new_ screenshot (showing Spotlight search).
6.  Asking the AI: "Okay, Spotlight is open. What now?"
7.  Getting the AI's answer (e.g., "Type 'Calculator'").
8.  Telling the Interface to type 'Calculator'.
9.  ...and so on, until the Calculator is open and the AI says the task is complete.

This repetitive execution is managed by the Agent Loop.

## The Blueprint: `BaseLoop`

Just like we have different AI models (GPT-4, Claude, Llama, etc.), each might need slightly different handling. They have different ways of being called (their APIs) and different ways of suggesting actions (sometimes called "tool calls").

However, the _basic_ Observe-Reason-Act cycle is the same for all of them. `BaseLoop` acts as the **master blueprint** for all agent loops in `cua`. It defines the _essential structure_ and _required methods_ that any specific loop implementation must have.

Think of it like a standard car engine blueprint. It specifies that there must be pistons, a crankshaft, etc. (the core components and their relationships), but it doesn't specify the exact materials or dimensions for a specific car model.

`BaseLoop` is an "abstract" class, meaning it defines _what_ needs to be done (like having a `run` method to start the loop) but leaves the _how_ to the specific implementations.

```python
# Simplified from libs/agent/agent/core/base.py
from abc import ABC, abstractmethod
from typing import Any, AsyncGenerator, Dict, List

class BaseLoop(ABC):
    """Base class for agent loops."""

    def __init__(self, computer: Computer, model: str, api_key: str, **kwargs):
        """Basic initialization."""
        self.computer = computer
        self.model = model
        self.api_key = api_key
        # ... other common setup ...
        # Manages the history of messages between user and AI
        self.message_manager = StandardMessageManager(...)
        # Manages saving experiment data (screenshots, logs) if enabled
        self.experiment_manager = ExperimentManager(...)

    @abstractmethod
    async def initialize_client(self) -> None:
        """Sets up the connection to the specific AI provider (e.g., OpenAI, Anthropic)."""
        # Must be implemented by subclasses!
        raise NotImplementedError

    @abstractmethod
    def run(self, messages: List[Dict[str, Any]]) -> AsyncGenerator[AgentResponse, None]:
        """Starts and manages the observe-reason-act cycle.

        Args:
            messages: The initial list of messages (e.g., the user's task).

        Yields:
            AgentResponse: Step-by-step results from the agent's work.
        """
        # Must be implemented by subclasses!
        raise NotImplementedError

    # ... other helper methods like _save_screenshot, _log_api_call ...
```

This blueprint ensures that every loop has a standard way to be initialized (`initialize_client`) and executed (`run`).

## Specific Implementations: Provider Loops (`OpenAILoop`, `AnthropicLoop`, `OmniLoop`, etc.)

Now, we need actual engines built according to the blueprint, tailored for specific AI providers. These are the **Provider Loops**:

- `OpenAILoop`: Knows how to talk to OpenAI's models (like GPT-4) using their specific API format and tool-calling system.
- `AnthropicLoop`: Knows how to interact with Anthropic's Claude models, using their unique API and tool-use mechanisms.
- `OmniLoop`: A more complex loop often used with models like GPT-4o or Claude 3. It integrates with [SOM (OmniParser)](08_som__omniparser_.md) to get a structured understanding of the screen elements, not just a raw image.
- `UITARSLoop`: Designed for models following the UI-TARS approach.
- `OllamaLoop`: For interacting with models running locally via Ollama.

Each of these Provider Loops takes the `BaseLoop` blueprint and fills in the details:

- How to format the prompt for _this specific_ AI.
- How to call _this specific_ AI's API endpoint.
- How to understand the AI's response, especially how it requests actions (tool calls).
- How to coordinate with the [Computer Interface](02_computer_interface__basecomputerinterface___macoscomputerinterface__.md) and the [Tools](05_tools__basetool___toolmanager___provider_tools__.md) system to execute those actions.

Think of these as the specific engine models: a Ford engine, a Toyota engine, a Tesla electric motor. They all follow the basic principles from the blueprint but have unique implementations.

## How Does a Loop Work Internally? (The Cycle in Action)

While the exact details vary between Provider Loops, the general flow inside the `run` method looks like this:

1.  **Start:** The loop receives the initial task and message history.
2.  **Loop Begins:** Enter a cycle that repeats until the task is done.
3.  **Observe:**
    - Take a screenshot using `await self.computer.interface.screenshot()`.
    - (For loops like `OmniLoop`) Optionally, analyze the screenshot using [SOM (OmniParser)](08_som__omniparser_.md) to identify UI elements.
    - Add the observation (screenshot image, maybe SOM data) to the message history.
4.  **Reason:**
    - Format the _entire_ current message history (task, previous steps, latest observation) into the specific format required by the AI provider (e.g., OpenAI API format, Anthropic API format).
    - Send this formatted data to the AI provider's API endpoint (e.g., make an HTTP request to OpenAI). This is usually handled by a dedicated "API Handler" component within the loop.
5.  **Act:**
    - Receive the response from the AI. This typically includes the AI's reasoning and potentially one or more requested actions (tool calls).
    - Parse the response to understand the reasoning and identify any requested actions. This is often handled by a "Response Handler".
    - If an action is requested (e.g., "click button X", "type text Y"):
      - Use the [ToolManager](05_tools__basetool___toolmanager___provider_tools__.md) (which uses the [Computer Interface](02_computer_interface__basecomputerinterface___macoscomputerinterface__.md)) to execute the action.
      - Add the result of the action (e.g., "Successfully clicked", or an error message) back into the message history.
    - If no action is requested, or the AI indicates the task is finished, prepare to exit the loop.
6.  **Yield:** Package the key information from this cycle (AI's reasoning, action taken, result) into an `AgentResponse` dictionary and `yield` it back to the `ComputerAgent`. This allows the user's code to see the agent's progress step-by-step.
7.  **Repeat or Exit:** If the task isn't finished, go back to Step 3 (Observe). Otherwise, exit the loop.

Here’s a simplified diagram showing one cycle:

```mermaid
sequenceDiagram
    participant Agent as ComputerAgent
    participant Loop as ProviderLoop (e.g., OpenAILoop)
    participant Interface as ComputerInterface
    participant AI_API as AI Provider API (e.g., OpenAI)
    participant Tools as ToolManager

    Agent->>+Loop: loop.run(messages)
    Loop->>+Interface: await screenshot()
    Interface-->>-Loop: Screenshot data
    Loop->>Loop: Add screenshot to messages
    Loop->>+AI_API: Send formatted messages/prompt
    AI_API-->>-Loop: AI Response (Reasoning + Tool Call)
    Loop->>Loop: Parse response, identify tool call
    alt Tool Call Found
        Loop->>+Tools: Execute tool (e.g., click)
        Tools->>+Interface: Perform action (e.g., left_click)
        Interface-->>-Tools: Action result
        Tools-->>-Loop: Tool execution result
        Loop->>Loop: Add tool result to messages
    end
    Loop->>Loop: Package step result (AgentResponse)
    Loop-->>-Agent: yield result
    Note over Loop, AI_API: If task not done, repeat from Observe phase
```

## Using the Loop (via the Agent)

You typically don't call the loop directly. Instead, you choose which loop the `ComputerAgent` should use when you create it, using the `loop` parameter.

```python
import asyncio
from computer import Computer
from agent import ComputerAgent, AgentLoop, LLM, LLMProvider

# 1. Set up the Computer
computer = Computer(os_type="macos", image="macos-sequoia-cua:latest")

# 2. Configure the AI Model
llm_config = LLM(provider=LLMProvider.OPENAI)

# 3. Create the ComputerAgent, specifying the loop
agent = ComputerAgent(
    computer=computer,
    model=llm_config,
    loop=AgentLoop.OPENAI # <--- HERE! We tell the agent to use OpenAILoop
    # Other options: AgentLoop.ANTHROPIC, AgentLoop.OMNI, AgentLoop.OLLAMA etc.
)

# The ComputerAgent will automatically create and manage the chosen loop (OpenAILoop in this case)
# when you call agent.run()

async def run_task():
     async with agent: # Handles agent initialization (which initializes the loop)
        task = "Open the Calculator app."
        async for result in agent.run(task):
            # The agent calls loop.run() internally and yields results
            reasoning = result.get("reasoning", {}).get("rationale", "Thinking...")
            print(f"Agent thought: {reasoning}")
            # Check for specific actions if needed (more in Chapter 5)

asyncio.run(run_task())

# Expected Output (Simplified):
# Agent thought: I need to open the Calculator app. Spotlight search is a good way. I'll press Command+Space.
# Agent thought: Spotlight is open. I should type 'Calculator'.
# Agent thought: I typed 'Calculator'. Now I press Enter.
# Agent thought: Calculator should be open now. Task complete.
```

When you create the `ComputerAgent`, you pass an `AgentLoop` enum value (like `AgentLoop.OPENAI`). Internally, the agent uses a `LoopFactory` to create the correct Provider Loop instance (`OpenAILoop`, `AnthropicLoop`, etc.) based on your choice. Then, when you call `agent.run(task)`, the agent delegates the execution to the `run` method of that specific loop instance.

## A Peek Inside the Code

**1. The Factory (`LoopFactory`)**

The `ComputerAgent` uses this factory to get the right loop instance based on the `AgentLoop` enum provided during initialization.

```python
# Simplified from libs/agent/agent/core/factory.py
import logging
from typing import Dict, Type
from .types import AgentLoop
from .base import BaseLoop
# Import specific loops (often done lazily to avoid unnecessary imports)
# from ..providers.openai.loop import OpenAILoop
# from ..providers.anthropic.loop import AnthropicLoop
# ... etc ...

logger = logging.getLogger(__name__)

class LoopFactory:
    """Factory class for creating agent loops."""

    @classmethod
    def create_loop(
        cls,
        loop_type: AgentLoop,
        # ... other parameters like api_key, model_name, computer ...
        **kwargs
    ) -> BaseLoop:
        """Create and return an appropriate loop instance based on type."""

        logger.info(f"Creating loop of type: {loop_type}")

        if loop_type == AgentLoop.OPENAI:
            # Import the specific loop class when needed
            from ..providers.openai.loop import OpenAILoop
            return OpenAILoop(**kwargs) # Pass relevant arguments

        elif loop_type == AgentLoop.ANTHROPIC:
            from ..providers.anthropic.loop import AnthropicLoop
            return AnthropicLoop(**kwargs)

        elif loop_type == AgentLoop.OMNI:
            from ..providers.omni.loop import OmniLoop
            return OmniLoop(**kwargs)

        # ... add cases for OLLAMA, UITARS, etc. ...

        else:
            raise ValueError(f"Unsupported loop type: {loop_type}")
```

This factory pattern keeps the `ComputerAgent` code clean, letting it simply request the type of loop it needs without knowing the creation details of each one.

**2. A Provider Loop Example (`OpenAILoop` - Highly Simplified)**

Let's look at a drastically simplified structure of the `run` method within a provider loop like `OpenAILoop`. The real code is much more complex to handle API specifics, error handling, retries, and detailed tool call processing.

```python
# Highly Simplified structure inspired by libs/agent/agent/providers/openai/loop.py

import asyncio
import base64
from typing import AsyncGenerator, List, Dict, Any

from ...core.base import BaseLoop
from ...core.types import AgentResponse
# Specific handlers for this provider
from .api_handler import OpenAIAPIHandler
from .response_handler import OpenAIResponseHandler
from .tools.manager import ToolManager

class OpenAILoop(BaseLoop):

    async def initialize_client(self) -> None:
        """Initialize OpenAI specific things."""
        # Setup API client, tool manager, handlers for OpenAI
        self.api_handler = OpenAIAPIHandler(self)
        self.response_handler = OpenAIResponseHandler(self)
        self.tool_manager = ToolManager(self.computer)
        await self.tool_manager.initialize()
        # ... other OpenAI specific setup ...
        print("OpenAI Loop Initialized.") # Placeholder

    async def run(self, messages: List[Dict[str, Any]]) -> AsyncGenerator[AgentResponse, None]:
        """Runs the OpenAI observe-reason-act cycle."""

        self.message_manager.messages = messages # Load initial messages

        # Get screen size once
        screen_size = await self.computer.interface.get_screen_size()

        running = True
        while running:
            # --- Observe ---
            screenshot_bytes = await self.computer.interface.screenshot()
            img_base64 = base64.b64encode(screenshot_bytes).decode("utf-8")
            self._save_screenshot(img_base64, "state") # Save if configured

            # Add observation to messages using self.message_manager
            self.message_manager.add_user_message([
                {"type": "image_url", "image_url": {"url": f"data:image/png;base64,{img_base64}"}}
            ])

            # --- Reason ---
            # Use the API handler to call the OpenAI API
            api_response = await self.api_handler.send_request(
                messages=self.message_manager.get_messages(), # Get formatted history
                display_width=str(screen_size["width"]),
                display_height=str(screen_size["height"]),
                # ... other OpenAI specific parameters ...
            )

            # --- Act ---
            # Use the Response handler to process the API response and execute tools
            should_continue, result_package = await self.response_handler.process_response(
                response=api_response,
                tool_manager=self.tool_manager
            )

            # Add results (like tool execution output) back to message history
            if result_package.get("tool_outputs"):
                 self.message_manager.add_tool_results(result_package["tool_outputs"])

            # Yield the progress back to the ComputerAgent
            yield result_package # Contains reasoning, actions, etc.

            running = should_continue # Decide whether to continue the loop
```

This simplified snippet highlights the core cycle within the `run` method:

1.  **Observe:** Get screenshot (`interface.screenshot()`), add to `message_manager`.
2.  **Reason:** Call the provider-specific `api_handler.send_request()` with current messages.
3.  **Act:** Process the `api_response` using the `response_handler`, which internally uses the `tool_manager` to execute actions if requested by the AI. Add results back to `message_manager`.
4.  **Yield:** Send the step's results back.
5.  **Repeat:** Continue the `while running:` loop based on the `response_handler`'s decision.

The actual loops are more sophisticated, often managing complex state, retries, and the nuances of different AI provider APIs and tool formats.

## Conclusion

You've learned about the **Agent Loop**, the engine that powers the `ComputerAgent`'s continuous Observe-Reason-Act cycle.

- It provides the structure for the agent to work step-by-step towards a goal.
- `BaseLoop` is the abstract blueprint defining the required structure (`run`, `initialize_client`).
- **Provider Loops** (`OpenAILoop`, `AnthropicLoop`, `OmniLoop`, etc.) implement the `BaseLoop` blueprint specifically for different AI models and their APIs.
- You choose the loop when creating the `ComputerAgent`, which then uses a `LoopFactory` to instantiate and manage the correct loop.
- The loop orchestrates taking screenshots, calling the AI, parsing responses, and executing actions.

When the AI model in the "Reason" step decides _what_ specific action to take (like "click this button" or "type this text"), how does the loop actually make that happen? It uses a system of **Tools**. These tools are the specific commands the AI can request.

Ready to learn how the AI tells the agent _exactly_ what to do? Let's move on to [Chapter 5: Tools (BaseTool / ToolManager / Provider Tools)](05_tools__basetool___toolmanager___provider_tools__.md)!

---

Generated by [AI Codebase Knowledge Builder](https://github.com/The-Pocket/Tutorial-Codebase-Knowledge)
