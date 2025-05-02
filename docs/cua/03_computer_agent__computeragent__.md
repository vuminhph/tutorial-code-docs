---
layout: default
title: "Computer Agent (ComputerAgent)"
parent: "Computer Use Agent (CUA)"
nav_order: 3
---

# Chapter 3: Computer Agent (ComputerAgent)

In [Chapter 2: Computer Interface](02_computer_interface__basecomputerinterface___macoscomputerinterface__.md), we learned how to use the `Computer Interface` to perform low-level actions like clicking the mouse, typing text, and taking screenshots within our virtual computer. It's like having the steering wheel, pedals, and gearstick for our virtual car.

But just having the controls isn't enough to get anywhere! We need a driver – someone (or something!) that can look at the road (the screen), decide where to go (the goal), and use the controls (the interface) to drive the car.

This "driver" in the `cua` world is the **Computer Agent**.

## What is a `ComputerAgent`?

Think of the `ComputerAgent` as the **AI brain** or the **virtual user** sitting in front of the [Computer](01_computer_.md). Its job is to take a high-level task you give it, like "Find the latest sales report file and email it to my boss," and figure out _how_ to accomplish that task step-by-step using the computer.

To do this, the `ComputerAgent` combines three key abilities:

1.  **Perception (Seeing):** It needs to "see" what's on the virtual computer's screen. It does this primarily by using the `screenshot()` function from the [Computer Interface](02_computer_interface__basecomputerinterface___macoscomputerinterface__.md). Sometimes, it gets help from a more advanced vision system called [SOM (OmniParser)](08_som__omniparser__.md), which can identify specific elements on the screen like buttons, text fields, and icons.
2.  **Reasoning (Thinking):** Based on what it "sees" on the screen and the overall task it's trying to achieve, the agent needs to _think_ about the very next small step. Should it click a button? Type something? Scroll down? This reasoning is usually powered by a large language model (LLM) like GPT-4, Claude, or a local model via Ollama.
3.  **Action (Doing):** Once the agent decides on the next step, it needs to _execute_ that action. It uses the methods provided by the [Computer Interface](02_computer_interface__basecomputerinterface___macoscomputerinterface__.md) (like `left_click()`, `type_text()`, `press_key()`) to actually perform the mouse clicks and keyboard inputs.

## The Agent Loop: Observe, Reason, Act

The `ComputerAgent` doesn't do everything at once. It works in a cycle, often called the **Agent Loop**:

1.  **Observe:** Look at the current state of the screen.
2.  **Reason:** Think about the task and the current screen to decide the next best action.
3.  **Act:** Perform the chosen action using the Computer Interface.
4.  **Repeat:** Go back to step 1 with the updated screen, and continue the cycle until the task is complete.

This continuous loop allows the agent to react to changes on the screen and break down complex tasks into manageable steps. The mechanics of this loop are handled by different strategies, which we'll explore more in [Chapter 4: Agent Loop (BaseLoop / Provider Loops)](04_agent_loop__baseloop___provider_loops__.md).

## Creating and Running Your First Agent

Let's see how to create a `ComputerAgent` and give it a simple task. We'll need our `Computer` from Chapter 1, and we'll need to tell the agent which AI model (LLM) and which reasoning strategy ([Agent Loop](04_agent_loop__baseloop___provider_loops__.md)) to use.

For this example, we'll assume you have set up an OpenAI API key as an environment variable (`export OPENAI_API_KEY=your_key_here`).

```python
import asyncio
from computer import Computer
from agent import ComputerAgent, AgentLoop, LLM, LLMProvider

# 1. Set up the Computer (as seen in Chapter 1)
computer = Computer(os_type="macos", image="macos-sequoia-cua:latest")

# 2. Configure the AI Model to use
# We specify the provider (OpenAI) and optionally the model name.
# If no name is given, it uses a default for that provider.
llm_config = LLM(provider=LLMProvider.OPENAI)
# Other options:
# llm_config = LLM(provider=LLMProvider.ANTHROPIC)
# llm_config = LLM(provider=LLMProvider.OLLAMA, name="llama3")

async def run_agent_task():
    print("Starting computer...")
    async with computer: # Manages starting and stopping the computer
        print("Computer is running. Creating agent...")

        # 3. Create the ComputerAgent
        agent = ComputerAgent(
            computer=computer,     # The virtual computer to control
            model=llm_config,      # Which AI brain to use
            loop=AgentLoop.OPENAI  # Which strategy/loop to follow
            # Other loop options: AgentLoop.ANTHROPIC, AgentLoop.OMNI, etc.
        )
        print("Agent created.")

        # 4. Define the task for the agent
        task = "Open the Calculator app."
        print(f"Giving agent task: '{task}'")

        # 5. Run the task and stream the results
        async for result in agent.run(task):
            # The agent yields results step-by-step
            # 'result' is a dictionary containing details like
            # the agent's reasoning and actions taken in this step.
            print("--- Agent Step ---")
            # Let's just print the agent's thought process (reasoning) if available
            reasoning = result.get("reasoning", {}).get("rationale", "No reasoning provided.")
            print(f"Reasoning: {reasoning}")
            # And any text output from the agent
            text_output = result.get("text", {}).get("value", "")
            if text_output:
                 print(f"Text: {text_output}")
            # You can inspect 'result' for more details (like tool calls)
            # print(result)
            print("------------------")

        print(f"\n✅ Agent finished task: '{task}'")

# Run the asynchronous function
asyncio.run(run_agent_task())

# Example Output (will vary based on the model and OS state):
# Starting computer...
# Computer is running. Creating agent...
# Agent created.
# Giving agent task: 'Open the Calculator app.'
# --- Agent Step ---
# Reasoning: The user wants to open the Calculator app. I should look for it, perhaps using Spotlight search. I will press Command+Space to open Spotlight.
# ------------------
# --- Agent Step ---
# Reasoning: Spotlight is open. Now I need to type 'Calculator' into the search bar.
# ------------------
# --- Agent Step ---
# Reasoning: I have typed 'Calculator'. The Calculator app should be the top hit. I need to press Enter to launch it.
# ------------------
# --- Agent Step ---
# Reasoning: I have pressed Enter. The Calculator app should now be open. The task is complete.
# Text: Okay, I have opened the Calculator app.
# ------------------
#
# ✅ Agent finished task: 'Open the Calculator app.'
# (You would also see the Calculator app open in the VM window if you were watching it)
```

Let's break down the code:

1.  **Computer Setup:** We create our `Computer` instance as usual.
2.  **LLM Configuration:** We create an `LLM` object, telling the agent _which_ AI provider (like OpenAI, Anthropic, Ollama) and potentially which specific model to use for its reasoning. We used `LLMProvider.OPENAI` here.
3.  **Agent Creation:** We instantiate `ComputerAgent`, passing it the `computer` it will control, the `model` configuration for its brain, and the `loop` type (the strategy it will use, like `AgentLoop.OPENAI`).
4.  **Task Definition:** We define our high-level goal as a simple string.
5.  **Running the Task:** We use `async for result in agent.run(task):`. This starts the agent loop. The agent will take screenshots, think, act, and `yield` a result dictionary after each significant step or thought process. We loop through these results and print some information (like the agent's reasoning) until the agent signals the task is done.

This simple example shows how the `ComputerAgent` acts as the orchestrator, taking a task and using its configured resources (computer interface, AI model, agent loop strategy) to execute it.

## How Does `agent.run()` Work Internally? (A Simplified Look)

When you call `await agent.run(task)`, the specific [Agent Loop](04_agent_loop__baseloop___provider_loops__.md) implementation takes over, but generally follows the Observe-Reason-Act cycle:

1.  **Task Received:** The `run` method gets the task ("Open Calculator app"). It adds this task to the conversation history.
2.  **Observe Phase:** The loop asks the [Computer Interface](02_computer_interface__basecomputerinterface___macoscomputerinterface__.md) for a `screenshot()`. Depending on the loop type (e.g., `AgentLoop.OMNI`), it might also use [SOM (OmniParser)](08_som__omniparser__.md) to analyze the screenshot and identify UI elements.
3.  **Reason Phase:** The loop packages the current task, the conversation history, the latest screenshot (and maybe SOM data) into a prompt for the configured AI model (e.g., GPT-4). The prompt essentially asks: "Given this task, this history, and this screen, what single action should you take next?".
4.  **Act Phase:** The AI model responds with its decision, often including both reasoning ("I need to click the 'File' menu") and a specific action ("Click at coordinates X, Y" or "Type 'hello'"). The loop parses this response. If it's an action, it uses the [Computer Interface](02_computer_interface__basecomputerinterface___macoscomputerinterface__.md) to execute it (e.g., `await interface.left_click(x, y)`).
5.  **Yield Result:** The loop packages the reasoning and action taken (or just the reasoning if no action was needed yet) into a result dictionary (`AgentResponse`) and `yield`s it back to your code.
6.  **Repeat:** The loop checks if the task is complete. If not, it goes back to Step 2 (Observe) and repeats the cycle with the updated screen state.

Here's a simplified diagram of one cycle:

```mermaid
sequenceDiagram
    participant UserCode as Your Script
    participant Agent as ComputerAgent
    participant Loop as AgentLoop (e.g., OpenAILoop)
    participant Interface as ComputerInterface
    participant AIModel as LLM (e.g., GPT-4)

    UserCode->>+Agent: agent.run(task)
    Agent->>+Loop: Start loop with task
    Loop->>+Interface: await screenshot()
    Interface-->>-Loop: Screenshot data
    Loop->>+AIModel: Send prompt (task, history, screenshot)
    Note right of AIModel: "What should I do next?"
    AIModel-->>-Loop: Response (Reasoning + Action)
    alt Action Suggested
        Loop->>+Interface: await interface.action() (e.g., click, type)
        Interface-->>-Loop: Action result
    end
    Loop->>Loop: Package result (reasoning, action)
    Loop-->>-Agent: yield result
    Agent-->>-UserCode: Receive result
    Note over Loop, AIModel: Check if task complete. If not, repeat cycle.
```

## Looking at the Code

The `ComputerAgent` class itself is relatively simple. Its main job during initialization is to set up the configuration and create the correct underlying [Agent Loop](04_agent_loop__baseloop___provider_loops__.md) instance using a factory.

```python
# Simplified from libs/agent/agent/core/agent.py

import logging
from computer import Computer
from .types import LLM, AgentLoop
from .factory import LoopFactory # Used to create the correct loop instance

logger = logging.getLogger(__name__)

class ComputerAgent:
    def __init__(
        self,
        computer: Computer,
        model: LLM,
        loop: AgentLoop,
        # ... other options like api_key, save_trajectory ...
    ):
        self.computer = computer
        self.provider = model.provider
        actual_model_name = model.name # ... logic to get default name if needed ...
        actual_api_key = # ... logic to get API key from args or env vars ...

        logger.info(
            f"Initializing Agent with Loop: {loop}, Provider: {self.provider}, Model: {actual_model_name}"
        )

        # The core logic: Use a Factory to create the specific loop implementation
        # This factory knows whether to create an OpenAILoop, AnthropicLoop, OmniLoop, etc.
        # based on the 'loop' parameter.
        self._loop = LoopFactory.create_loop(
            loop_type=loop,
            provider=self.provider,
            computer=self.computer,
            model_name=actual_model_name,
            api_key=actual_api_key,
            # ... pass other relevant options ...
        )

        # Get the message manager from the created loop
        # (Used to keep track of the conversation history)
        self.message_manager = self._loop.message_manager

        self._initialized = False
        logger.info("ComputerAgent initialized.")

    # ... other methods like __aenter__, __aexit__, initialize ...

    async def run(self, task: str) -> AsyncGenerator[AgentResponse, None]:
        # ... (initialization check omitted for brevity) ...

        logger.info(f"Running task: {task}")

        # Add the user's task to the conversation history
        self.message_manager.add_user_message([{"type": "text", "text": task}])

        # Delegate the actual execution to the specific loop instance (_loop)
        # The loop handles the observe-reason-act cycle.
        async for result in self._loop.run(self.message_manager.messages):
            yield result # Yield results from the loop back to the caller
```

As you can see, the `ComputerAgent` acts as a high-level controller. It takes your configuration (`computer`, `model`, `loop`), sets up the appropriate `_loop` instance using `LoopFactory`, and then when `run()` is called, it passes the task to that `_loop` to handle the complex observe-reason-act cycle.

## Conclusion

You've now met the **Computer Agent** – the AI brain that acts like a virtual user for your `Computer`.

- It bridges the gap between high-level tasks and low-level [Computer Interface](02_computer_interface__basecomputerinterface___macoscomputerinterface__.md) actions.
- It works by repeatedly **Observing** the screen, **Reasoning** about the next step (using an LLM), and **Acting** via the Interface.
- You create an agent by providing a `Computer`, an `LLM` configuration, and choosing an `AgentLoop` strategy.
- You run tasks using `agent.run(task)` and can observe the agent's progress through the yielded results.

The `ComputerAgent` relies heavily on its chosen **Agent Loop** strategy to manage the observe-reason-act cycle, interact with the AI model, and handle errors or retries.

Ready to learn more about these different strategies? Let's dive into [Chapter 4: Agent Loop (BaseLoop / Provider Loops)](04_agent_loop__baseloop___provider_loops__.md)!

---

Generated by [AI Codebase Knowledge Builder](https://github.com/The-Pocket/Tutorial-Codebase-Knowledge)
