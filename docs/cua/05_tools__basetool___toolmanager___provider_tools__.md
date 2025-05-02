# Chapter 5: Tools (BaseTool / ToolManager / Provider Tools)

In [Chapter 4: Agent Loop (BaseLoop / Provider Loops)](04_agent_loop__baseloop___provider_loops__.md), we saw how the `AgentLoop` acts like the engine for our `ComputerAgent`, driving the Observe-Reason-Act cycle. The loop determines *when* the agent should observe, think, and act. But what specific actions can the agent perform beyond the basic mouse clicks and key presses offered by the [Computer Interface](02_computer_interface__basecomputerinterface___macoscomputerinterface__.md)?

Imagine you ask the agent: "List the files in the current directory and then tell me the content of `config.txt`." How does the agent run a command like `ls` or read a file? The basic interface doesn't have `run_command()` or `read_file()` methods. For these more specialized actions, the agent needs **Tools**.

## What are Tools?

Think of tools like the items in a plumber's toolbox. They have a basic wrench (`Computer Interface` for clicks/types), but they also need specialized tools for specific jobs: a pipe cutter (`BashTool` for running commands), a soldering iron (`EditTool` for changing files), maybe a voltage meter (`ComputerTool` for specific UI checks).

In `cua`, **Tools** represent these specific, well-defined actions an agent can request beyond the fundamental mouse and keyboard interactions. They are the agent's specialized capabilities.

Key examples include:
*   `BashTool`: Allows the agent to execute shell commands (like `ls`, `cd`, `pwd`) in the computer's terminal.
*   `EditTool`: Enables the agent to read the contents of files or write new content to files.
*   `ComputerTool`: While the low-level interface handles basic actions, this tool often wraps those actions (like `screenshot`, specific clicks, typing) in a way that the AI model can request them as a "tool call".

Each tool knows:
1.  What action it performs.
2.  What information (parameters) it needs to perform the action (e.g., `BashTool` needs the `command` string).
3.  How to actually perform the action (its execution logic).

## The Blueprint: `BaseTool`

Just like any good toolbox has tools with handles and specific functions, `cua` needs a standard way to define these agent tools. This standard structure is defined by the `BaseTool` blueprint (an abstract class).

`BaseTool` specifies that every tool must have certain characteristics:
*   A `name`: How the tool is identified (e.g., "bash", "edit").
*   An `__call__` method: The actual Python code that runs when the tool is used. This is where the tool performs its specific action.
*   A `to_params` method: A way to describe the tool (its name, purpose, and required parameters) in a format that the AI model (like GPT-4 or Claude) can understand. This allows the AI to know which tools are available and how to ask for them.

Let's look at the basic structure defined in `libs/agent/agent/core/tools/base.py`:

```python
# Simplified from libs/agent/agent/core/tools/base.py
from abc import ABCMeta, abstractmethod
from typing import Any, Dict

# A standard way to represent the result of a tool's execution
@dataclass(kw_only=True, frozen=True)
class ToolResult:
    output: str | None = None # Text output from the tool
    error: str | None = None  # Error message if something went wrong
    # ... other potential fields like base64_image ...

class BaseTool(metaclass=ABCMeta):
    """Abstract base class for tools."""
    name: str # Every tool must have a name

    @abstractmethod
    async def __call__(self, **kwargs) -> ToolResult:
        """Executes the tool's action."""
        # Specific tools implement this logic
        raise NotImplementedError

    @abstractmethod
    def to_params(self) -> Dict[str, Any]:
        """Describes the tool for the AI model."""
        # Specific tools implement this based on provider needs
        raise NotImplementedError
```
This blueprint ensures all tools follow a consistent pattern, making them manageable.

Now, let's see a simplified version of a specific tool, like `BaseBashTool`, which builds upon `BaseTool`:

```python
# Simplified from libs/agent/agent/core/tools/bash.py
import asyncio
import logging
from .base import BaseTool, ToolResult # Import the base classes

class BaseBashTool(BaseTool):
    """Base class for bash/shell command execution tools."""
    name = "bash" # The tool's name
    logger = logging.getLogger(__name__)

    # (Initialization omitted)

    async def run_command(self, command: str) -> tuple[int, str, str]:
        """Helper to run a shell command."""
        # ... (Code to execute the command using asyncio.create_subprocess_shell) ...
        # Returns exit_code, stdout, stderr
        # Example implementation detail - not crucial for understanding the concept
        try:
            process = await asyncio.create_subprocess_shell(
                command, stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.PIPE
            )
            stdout, stderr = await process.communicate()
            return process.returncode or 0, stdout.decode(), stderr.decode()
        except Exception as e:
            self.logger.error(f"Error running command: {str(e)}")
            return 1, "", str(e)


    # __call__ is required by BaseTool - here's a conceptual implementation
    # The actual implementation might be in provider-specific subclasses
    async def __call__(self, command: str, **kwargs) -> ToolResult:
        """Execute the bash command."""
        exit_code, stdout, stderr = await self.run_command(command)
        if exit_code == 0:
            return ToolResult(output=stdout)
        else:
            return ToolResult(output=stdout, error=stderr or f"Command failed with exit code {exit_code}")

    # to_params is required by BaseTool
    # It would be implemented in provider-specific subclasses
    @abstractmethod
    def to_params(self) -> Dict[str, Any]:
        raise NotImplementedError
```
Here, `BaseBashTool` defines its `name` as "bash" and implements the core logic for running a command in `run_command`. The `__call__` method uses this logic and returns a `ToolResult`. Notice that `to_params` is still abstract – we'll see why soon.

## The Organizer: `ToolManager`

Okay, so we have individual tools defined. But how does the agent know which tools are available? And when the AI asks to use a tool (e.g., "run the `ls` command using the `bash` tool"), who actually finds the `BashTool` and executes its `__call__` method?

This is the job of the **ToolManager**. Think of it as the agent's toolbelt or toolbox organizer.

The `ToolManager` is responsible for:
1.  **Initialization:** Creating instances of all the available tools (like `BashTool`, `EditTool`, `ComputerTool`) when the agent starts.
2.  **Description:** Gathering the descriptions of all available tools (by calling each tool's `to_params()` method) and formatting them into a list that the AI model understands. This list is sent to the AI (via the [Agent Loop](04_agent_loop__baseloop___provider_loops__.md)) so it knows what capabilities it has.
3.  **Execution:** Receiving a request from the [Agent Loop](04_agent_loop__baseloop___provider_loops__.md) to run a specific tool with certain arguments (e.g., run `name="bash"` with `command="ls"`).
4.  **Dispatch:** Finding the correct tool object (e.g., the `BashTool` instance) and calling its `__call__` method with the provided arguments.
5.  **Returning Result:** Giving the `ToolResult` back to the [Agent Loop](04_agent_loop__baseloop___provider_loops__.md).

Just like `BaseTool`, there's a `BaseToolManager` blueprint (`libs/agent/agent/core/tools/manager.py`) defining the essential functions a tool manager must provide, like `initialize`, `get_tool_params`, and `execute_tool`.

## Provider Tools and Managers: Adapting to Different AIs

Here's a crucial detail: different AI providers (like OpenAI and Anthropic) have slightly different ways they want tools described and requested.
*   OpenAI might expect a tool description like `{"type": "function", "function": {"name": "bash", "description": "...", "parameters": {...}}}`.
*   Anthropic might expect something like `{"name": "bash", "description": "...", "input_schema": {...}}}`.
*   When the AI responds, OpenAI might include a `tool_calls` list, while Anthropic might use a `tool_use` structure.

Because of these differences, we can't have just *one* universal `BashTool` or `ToolManager`. We need provider-specific versions:

*   **Provider Tools:** Subclasses of `BaseTool` tailored for a specific provider. For example, `AnthropicBashTool` and `OpenAIBashTool` would both inherit the core logic from `BaseBashTool` but would implement the `to_params()` method differently to match what Anthropic or OpenAI expects.
    *   See `libs/agent/agent/providers/anthropic/tools/computer.py` or `libs/agent/agent/providers/openai/tools/computer.py` for examples of provider-specific `ComputerTool` implementations.
*   **Provider ToolManagers:** Subclasses of `BaseToolManager` specific to a provider. For example, `AnthropicToolManager` knows how to initialize `Anthropic`-specific tools and format the *list* of tool parameters correctly for the Anthropic API using `get_tool_params()`. It also knows how to parse Anthropic's `tool_use` requests to call the right tool via `execute_tool()`. Similarly for `OpenAIToolManager`.
    *   See `libs/agent/agent/providers/anthropic/tools/manager.py` and `libs/agent/agent/providers/openai/tools/manager.py`.

This specialization ensures that the agent can correctly communicate its capabilities to, and understand the requests from, whichever AI model provider it's configured to use.

Let's look at a simplified `get_tool_params` concept in a provider-specific manager:

```python
# Conceptual Example - AnthropicToolManager
# from libs/agent/agent/providers/anthropic/tools/manager.py
class AnthropicToolManager(BaseToolManager):
    # ... (initialization creates AnthropicBashTool, AnthropicEditTool, etc.) ...
    
    def get_tool_params(self) -> List[Dict[str, Any]]:
        """Get tool parameters formatted for Anthropic API."""
        if self.tools is None:
             raise RuntimeError("Tools not initialized.")
        
        # Each Anthropic-specific tool implements to_params for Anthropic format
        # self.tools.to_params() gathers these descriptions
        return self.tools.to_params() # Returns a list like [{"name": "bash", ...}, {"name": "edit", ...}]

# Conceptual Example - OpenAIToolManager
# from libs/agent/agent/providers/openai/tools/manager.py
class OpenAIToolManager(BaseToolManager):
    # ... (initialization creates OpenAIBashTool, OpenAIEditTool, etc.) ...

    def get_tool_params(self) -> List[Dict[str, Any]]:
        """Get tool parameters formatted for OpenAI API."""
        if self.tools is None:
             raise RuntimeError("Tools not initialized.")

        # Each OpenAI-specific tool implements to_params for OpenAI format
        # self.tools.to_params() gathers these descriptions
        return self.tools.to_params() # Returns a list like [{"type": "function", "function": {...}}, ...]
```
The key takeaway is that the `ToolManager` adapts how tools are presented based on the AI provider.

## How it Works Together: The Tool Execution Flow

So, how does this all fit into the agent's workflow? Let's trace what happens when the AI decides to use the `bash` tool:

1.  **Loop Prepares:** The [Agent Loop](04_agent_loop__baseloop___provider_loops__.md) (e.g., `OpenAILoop`) is about to ask the AI for the next step. Before sending the request, it asks its `ToolManager` (e.g., `OpenAIToolManager`): "Give me the descriptions of all available tools, formatted for OpenAI."
2.  **Manager Describes:** The `ToolManager` calls `get_tool_params()`, which collects the OpenAI-formatted descriptions from each configured tool (like `OpenAIBashTool`, `OpenAIEditTool`).
3.  **Loop Asks AI:** The Loop sends the current conversation history, the latest screenshot, *and* the list of tool descriptions to the AI model (e.g., GPT-4). The prompt is essentially: "Given the situation and these tools you can use, what should you do next?"
4.  **AI Decides:** The AI analyzes the request and decides the best action is to run a command. It formulates a response indicating it wants to use the `bash` tool with the parameter `command="ls"`. The format of this response depends on the provider (e.g., OpenAI uses `tool_calls`).
5.  **Loop Parses:** The Loop receives the AI's response and parses it. It sees a request to use the `bash` tool.
6.  **Loop Dispatches to Manager:** The Loop tells its `ToolManager`: "Execute the tool named `bash` with input `{'command': 'ls'}`."
7.  **Manager Executes:** The `ToolManager` calls its `execute_tool()` method. It finds the `OpenAIBashTool` instance and calls its `__call__(command="ls")` method.
8.  **Tool Runs:** The `BashTool`'s `__call__` method runs the `ls` command using its internal `run_command` logic.
9.  **Tool Returns Result:** The `BashTool` finishes and returns a `ToolResult` (e.g., `ToolResult(output="file1.txt\nfile2.py\n")`) back to the `ToolManager`.
10. **Manager Returns to Loop:** The `ToolManager` passes the `ToolResult` back to the Loop.
11. **Loop Continues:** The Loop adds this tool result to the conversation history (so the AI knows the command was executed and saw the output) and prepares for the next cycle (Observe-Reason-Act). It also `yield`s the result information back to your `agent.run()` loop.

Here’s a simplified sequence diagram:

```mermaid
sequenceDiagram
    participant Loop as Agent Loop (e.g., OpenAILoop)
    participant Manager as ToolManager (e.g., OpenAIToolManager)
    participant AI as AI Model (e.g., GPT-4)
    participant Tool as Specific Tool (e.g., BashTool)

    Note over Loop, Manager: Before asking AI...
    Loop->>+Manager: get_tool_params()
    Manager-->>-Loop: List of tool descriptions (formatted for AI)

    Note over Loop, AI: Asking AI for next step...
    Loop->>+AI: Send history, screenshot, tool descriptions
    AI-->>-Loop: Response requesting tool use (e.g., use "bash", command="ls")

    Note over Loop, Manager: AI requested a tool...
    Loop->>+Manager: execute_tool(name="bash", input={"command": "ls"})
    Manager->>+Tool: __call__(command="ls")
    Note right of Tool: Tool executes `ls` command
    Tool-->>-Manager: ToolResult(output="file1...")
    Manager-->>-Loop: ToolResult(output="file1...")

    Note over Loop, AI: Loop adds result to history, continues cycle...
```

## Using Tools (Good News: It's Mostly Automatic!)

As a user of the `ComputerAgent`, you generally don't need to worry about manually creating tools or managing the `ToolManager`. When you initialize your `ComputerAgent` and choose an `AgentLoop` (like `AgentLoop.OPENAI`), the correct provider-specific `ToolManager` and its associated tools are automatically created and configured for you by the [Agent Loop](04_agent_loop__baseloop___provider_loops__.md)'s initialization process.

```python
# Example from Chapter 3, highlighting the implicit tool setup

agent = ComputerAgent(
    computer=computer,
    model=LLM(provider=LLMProvider.OPENAI),
    loop=AgentLoop.OPENAI # <--- This choice triggers creation of OpenAILoop
)
# When OpenAILoop initializes, it creates an OpenAIToolManager,
# which in turn creates OpenAIBashTool, OpenAIEditTool, etc.
# These tools are then automatically described to the OpenAI model.

async def run_task():
     async with agent:
        task = "List the files in the current directory."
        async for result in agent.run(task):
            # If the AI uses the 'bash' tool, the result might contain info about it
            # You don't need to manually call the tool.
            print(f"Agent Step Result: {result}") 
            # Example result might show a tool call being processed

asyncio.run(run_task())
```

You just give the agent the task, and the underlying machinery (Loop + ToolManager + Tools) handles making those capabilities available to the AI and executing them when requested.

## Conclusion

You've now explored the world of **Tools** in `cua` – the specialized capabilities that allow your agent to perform actions beyond basic mouse and keyboard control.

*   Tools like `BashTool` and `EditTool` provide specific functionalities (running commands, editing files).
*   `BaseTool` acts as the standard blueprint for defining any tool.
*   The `ToolManager` is the organizer, responsible for describing available tools to the AI and executing them when requested.
*   Provider-specific tools and managers (`AnthropicToolManager`, `OpenAIToolManager`, etc.) adapt the descriptions and execution flow to match the requirements of different AI models (OpenAI, Anthropic).
*   This system allows the agent's capabilities to be clearly communicated to the AI and seamlessly executed based on the AI's decisions, mostly happening automatically behind the scenes.

Many of these tools, especially the `ComputerTool`, rely on communicating with a service running *inside* the virtual machine (or on the host) to actually perform the low-level actions. This service is the [Computer Server](06_computer_server_.md).

Ready to learn about the component that listens for and executes commands inside the computer environment? Let's move on to [Chapter 6: Computer Server](06_computer_server_.md)!

---

Generated by [AI Codebase Knowledge Builder](https://github.com/The-Pocket/Tutorial-Codebase-Knowledge)