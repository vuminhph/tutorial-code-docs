---
layout: default
title: "RunResponse & Message"
parent: "Agno"
nav_order: 4
---

# Chapter 4: RunResponse & Message

Welcome to Chapter 4! In [Chapter 3: Team](03_team_.md), we saw how multiple [Agent](02_agent_.md)s can collaborate as a `Team` to tackle complex tasks. Whether it's a single [Agent](02_agent_.md) or a `Team` doing the work, they need a standard way to tell us what happened: What was said? What actions were taken? What's the final answer? This is where `RunResponse` and `Message` come into play.

Imagine you've asked your AI [Agent](02_agent_.md) to write a short poem. After it's done, how do you get the poem? What if the agent had to ask a clarifying question first, or use a tool to find rhyming words? You'd want a record of that entire interaction, not just the final poem. `RunResponse` and `Message` provide exactly this structured information.

## What's the Big Idea?

*   **`Message`**: Think of a `Message` object as a single entry in a chat log or a single line in a script. It records *who* said *what*, and *when*. It can also record if any [Toolkit & Tools](06_toolkit___tools_.md) were involved.
*   **`RunResponse`**: This is the complete package you get back after an [Agent](02_agent_.md) (or a [Team](03_team_.md)) finishes processing an input. It contains the final, primary output (like the poem), and a list of all the `Message` objects that make up the entire interaction. It's like getting the final report *and* the detailed minutes of the meeting.

Let's say our [Agent](02_agent_.md) is a "Story Bot".
1.  You (User): "Tell me a story about a dragon." (This is one `Message`)
2.  Story Bot (Assistant): "Okay! Once upon a time, in a land far away, there lived a friendly dragon named Sparky." (This is another `Message`)

The `RunResponse` would contain the final story ("Okay! Once upon a time...") as its main `content`, and a list containing both of these `Message` objects.

## Meet `Message`: The Building Block of Conversation

A `Message` object captures a single turn in an interaction. It's defined in `agno/models/message.py`. Here are its most important parts for a beginner:

*   `role`: Who is this message from?
    *   `"user"`: The message is from you (the human or the system making the request).
    *   `"assistant"`: The message is from the AI [Agent](02_agent_.md) or [Model](05_model_.md). This could be a textual reply or a request to use a tool.
    *   `"tool"`: The message contains the result from a [Tool](06_toolkit___tools_.md) that the assistant decided to use.
    *   `"system"`: Special instructions given to the AI, usually at the beginning.
*   `content`: What was said or the data for the message. For `user` and `assistant` (text replies), this is usually a string of text. For `tool` messages, it's the output from the tool.
*   `tool_calls` (Optional): If the `assistant` decides to use a [Tool](06_toolkit___tools_.md), this field will contain details about which tool to call and with what arguments.
*   `tool_call_id` (Optional): If a `Message` is a `tool` role, this ID links it back to the specific `tool_calls` request from the `assistant`.
*   `name` (Optional): Sometimes used to identify the specific tool that was called or the participant.

Let's see what some `Message` objects might look like in Python. We're creating them manually here just for illustration:

```python
# message_examples.py
from agno.models.message import Message

# 1. A user's message
user_message = Message(
    role="user",
    content="What's the weather like in Paris?"
)
print(f"User Message: role='{user_message.role}', content='{user_message.content}'")

# 2. An assistant's message deciding to use a tool
assistant_tool_call_message = Message(
    role="assistant",
    content=None, # No direct text reply yet, it wants to use a tool
    tool_calls=[
        {
            "id": "call_abc123", # A unique ID for this tool call
            "type": "function",
            "function": {
                "name": "get_weather",
                "arguments": '{"city": "Paris"}' # Arguments for the tool
            }
        }
    ]
)
print(f"\nAssistant Tool Call: role='{assistant_tool_call_message.role}', tool_calls='{assistant_tool_call_message.tool_calls}'")

# 3. A tool's response message
tool_response_message = Message(
    role="tool",
    tool_call_id="call_abc123", # Links back to the assistant's request
    name="get_weather",        # The name of the tool that ran
    content='{"temperature": "15°C", "condition": "Cloudy"}' # Output from the tool
)
print(f"\nTool Response: role='{tool_response_message.role}', tool_call_id='{tool_response_message.tool_call_id}', content='{tool_response_message.content}'")

# 4. An assistant's final text message after getting tool results
assistant_final_reply = Message(
    role="assistant",
    content="The weather in Paris is 15°C and Cloudy."
)
print(f"\nAssistant Final Reply: role='{assistant_final_reply.role}', content='{assistant_final_reply.content}'")
```

Running this would show:
```
User Message: role='user', content='What's the weather like in Paris?'

Assistant Tool Call: role='assistant', tool_calls='[{'id': 'call_abc123', 'type': 'function', 'function': {'name': 'get_weather', 'arguments': '{"city": "Paris"}'}}]'

Tool Response: role='tool', tool_call_id='call_abc123', content='{"temperature": "15°C", "condition": "Cloudy"}'

Assistant Final Reply: role='assistant', content='The weather in Paris is 15°C and Cloudy.'
```
Each `Message` clearly records one step of the interaction.

## Meet `RunResponse`: The Agent's Full Report

When an [Agent](02_agent_.md) (or [Team](03_team_.md)) finishes its `run`, it returns a `RunResponse` object. This object, defined in `agno/run/response.py`, bundles everything up. Key fields include:

*   `content`: The main, final answer or output from the agent (e.g., the poem, the weather summary).
*   `messages`: A list of all `Message` objects that occurred during the run, forming a complete transcript.
*   `metrics`: Performance data, like how many tokens were used (important for cost and performance tracking with AI [Model](05_model_.md)s). You might have seen this in `test_metrics.py`.
*   `agent_id`: The ID of the agent that produced this response.
*   `run_id`: A unique identifier for this specific execution.
*   `session_id` (Optional): If you're having an ongoing conversation, this ID can link multiple runs together.

Think back to the [Playground](01_playground_.md) example in Chapter 1. The JSON output you saw was a `RunResponse` object converted into a dictionary (using its `.to_dict()` method) and then to JSON!

Here's a conceptual `RunResponse` for our weather example:

```python
# Conceptual RunResponse (not actual code to run, but illustrates structure)
# from agno.run.response import RunResponse (would be imported)
# from agno.models.message import Message (would be imported)

# Assume user_message, assistant_tool_call_message, 
# tool_response_message, assistant_final_reply are defined as above

conceptual_run_response = { # Simplified representation
    "content": "The weather in Paris is 15°C and Cloudy.",
    "messages": [
        {"role": "user", "content": "What's the weather like in Paris?"},
        {"role": "assistant", "tool_calls": [{"function": {"name": "get_weather", "arguments": '{"city": "Paris"}'}}]},
        {"role": "tool", "name": "get_weather", "tool_call_id": "call_abc123", "content": '{"temperature": "15°C", "condition": "Cloudy"}'},
        {"role": "assistant", "content": "The weather in Paris is 15°C and Cloudy."}
    ],
    "agent_id": "weather-bot-001",
    "run_id": "run_xyz789",
    "metrics": {"input_tokens": [50, 20], "output_tokens": [15, 30]} # Example metrics
}
# In Python, this would be an actual RunResponse object, not a dict.
# print(conceptual_run_response["content"])
# for msg in conceptual_run_response["messages"]:
#     print(msg)
```
This `RunResponse` gives you the final answer directly in `content` and the full conversation history in `messages`.

## Seeing Them in Action

Let's use a slightly modified version of our `FriendlyBot` from [Chapter 2: Agent](02_agent_.md) to see how we can access `RunResponse` and `Message` details.

```python
# run_response_in_action.py
from agno.agent import Agent
from agno.models.openai import OpenAIChat
from agno.run.response import RunResponse, Message # We need these!

# --- Mock Model Setup ---
def mock_model_response_for_run_response(messages, **kwargs) -> Message:
    user_message_content = messages[-1].content
    response_text = f"Ah, you said: '{user_message_content}'. That's interesting!"
    return Message(role="assistant", content=response_text)

mock_llm = OpenAIChat(id="mock-gpt-3.5-for-rr")
mock_llm.invoke = mock_model_response_for_run_response
# --- End Mock Model Setup ---

friendly_agent = Agent(
    name="ChattyBot",
    agent_id="chatty-bot-002",
    model=mock_llm,
    instructions="You are a talkative bot."
)

# Let's run the agent
user_input = "Hello there, Agno!"
response_object = friendly_agent.run(message=user_input) # This IS a RunResponse object

# 1. Access the final content
print(f"Agent's Final Answer: {response_object.content}")

# 2. Access the list of Messages (the conversation transcript)
print("\n--- Full Conversation Transcript ---")
if response_object.messages:
    for msg in response_object.messages:
        print(f"  Role: {msg.role}")
        # Message content can be complex, get_content_string() helps
        print(f"  Content: {msg.get_content_string()}") 
        if msg.tool_calls:
            print(f"  Tool Calls: {msg.tool_calls}")
        print("  ---")

# 3. Access metrics (if any)
if response_object.metrics:
    print(f"\nMetrics for this run: {response_object.metrics}")

# 4. Other useful info
print(f"\nRun ID: {response_object.run_id}")
print(f"Agent ID: {response_object.agent_id}")
```

When you run this:
```
Agent's Final Answer: Ah, you said: 'Hello there, Agno!'. That's interesting!

--- Full Conversation Transcript ---
  Role: user
  Content: Hello there, Agno!
  ---
  Role: assistant
  Content: Ah, you said: 'Hello there, Agno!'. That's interesting!
  ---

Metrics for this run: {'input_tokens': [0], 'output_tokens': [0], 'total_tokens': [0], 'model': ['mock-gpt-3.5-for-rr']}

Run ID: ...a unique run id will be printed here...
Agent ID: chatty-bot-002
```
*(Note: The `input_tokens`, `output_tokens` are 0 in this mock example because our `mock_model_response_for_run_response` doesn't populate `MessageMetrics`. Real models would provide these.)*

This shows how the `RunResponse` object gives you both the concise final answer and the detailed turn-by-turn `Message` log.

## Under the Hood: How `RunResponse` and `Message`s Are Born

When you call `agent.run("Your input")`:

1.  **User Message Creation**: Your input string is transformed into a `Message` object with `role="user"`.
2.  **Agent Processing**: The [Agent](02_agent_.md) takes this user `Message`, potentially adds system instructions (as another `Message`), and sends them to its [Model](05_model_.md).
3.  **Assistant Message (Attempt 1)**: The [Model](05_model_.md) responds. This response becomes an `assistant` `Message`.
    *   If the Model gives a direct textual answer, this might be the final assistant message.
    *   If the Model decides to use a [Tool](06_toolkit___tools_.md), this `assistant` `Message` will contain `tool_calls`.
4.  **Tool Cycle (If tools are called)**:
    *   The [Agent](02_agent_.md) sees the `tool_calls` in the assistant's message.
    *   It executes the specified tool(s).
    *   The result of each tool execution is wrapped in a `Message` with `role="tool"`.
    *   These `tool` `Message`s, along with the previous conversation, are sent back to the [Model](05_model_.md).
    *   The [Model](05_model_.md) then generates a new `assistant` `Message`, hopefully using the tool's information to form a final answer. This loop can happen multiple times if the agent needs to use several tools in sequence.
5.  **Collection**: All these `Message` objects (user, assistant, tool, system) are collected in a list.
6.  **Packaging `RunResponse`**: The [Agent](02_agent_.md) takes the content of the *final* `assistant` `Message` as the main `content` for the `RunResponse`. It puts the collected list of all `Message`s into the `RunResponse.messages` field. It also gathers any `metrics` (like token counts, timing from `MessageMetrics` on each `Message`), `tool_results`, etc., and packages them into the `RunResponse` object.
7.  **Return**: The fully populated `RunResponse` object is returned.

Here's a simplified sequence diagram illustrating this:

```mermaid
sequenceDiagram
    participant You
    participant MyAgent as Agent
    participant LLM as AI Model
    participant WeatherTool as Tool

    You->>MyAgent: run("Paris weather?")
    MyAgent->>MyAgent: Creates User Message(role="user", content="Paris weather?")
    MyAgent->>LLM: Sends [User Message, System Instructions]
    LLM-->>MyAgent: Returns Assistant Message(tool_calls=[get_weather("Paris")])
    MyAgent->>WeatherTool: Executes get_weather("Paris")
    WeatherTool-->>MyAgent: Returns "Cloudy, 15°C"
    MyAgent->>MyAgent: Creates Tool Message(role="tool", content="Cloudy, 15°C")
    MyAgent->>LLM: Sends [User Msg, Assistant Msg (tool_call), Tool Msg]
    LLM-->>MyAgent: Returns Assistant Message(content="Paris is Cloudy, 15°C.")
    MyAgent->>MyAgent: Assembles RunResponse: content="Paris is...", messages=[all previous messages]
    MyAgent-->>You: Returns RunResponse object
end
```

**A Glimpse into the Code Definitions:**

The structure of `Message` is defined in `agno/models/message.py`. Here's a very simplified idea:

```python
# Simplified from agno/models/message.py

# from pydantic import BaseModel, Field # Uses Pydantic for data validation
# from typing import Optional, List, Any, Dict
# from time import time

# class MessageMetrics: # Simplified
#     input_tokens: int = 0
#     output_tokens: int = 0
#     # ... other metrics like time, etc.

class Message: # Conceptual and simplified
    role: str  # "user", "assistant", "tool", "system"
    content: Optional[Union[List[Any], str]] = None
    tool_calls: Optional[List[Dict[str, Any]]] = None
    tool_call_id: Optional[str] = None
    name: Optional[str] = None
    # metrics: MessageMetrics = MessageMetrics() # Each message can have its own metrics
    # created_at: int = int(time())
    # ... and many other fields for images, audio, references, etc.

    def __init__(self, role, content=None, tool_calls=None, tool_call_id=None, name=None):
        self.role = role
        self.content = content
        self.tool_calls = tool_calls
        self.tool_call_id = tool_call_id
        self.name = name
        # self.metrics = MessageMetrics() # Simplified for example

    def get_content_string(self) -> str:
        # Helper to get content as a simple string
        if isinstance(self.content, str):
            return self.content
        # ... (more logic for complex content types)
        return str(self.content)

    def to_dict(self) -> Dict[str, Any]:
        # Converts the Message object to a Python dictionary
        # (Useful for sending as JSON, like in the Playground)
        # ... (implementation details)
        return {"role": self.role, "content": self.content, ...}
```
Notice the `MessageMetrics` which can track token usage and time for each step, and these are often summed up in the final `RunResponse.metrics`.

And for `RunResponse`, defined in `agno/run/response.py`:

```python
# Simplified from agno/run/response.py

# from dataclasses import dataclass, field # Uses dataclasses
# from typing import Optional, List, Any, Dict
# from agno.models.message import Message # Imports Message

# @dataclass # This decorator auto-generates __init__, __repr__, etc.
class RunResponse: # Conceptual and simplified
    content: Optional[Any] = None # The final, primary output
    messages: Optional[List[Message]] = None # The list of all Message objects
    metrics: Optional[Dict[str, Any]] = None # Summary of metrics
    agent_id: Optional[str] = None
    run_id: Optional[str] = None
    # ... many other fields like session_id, tools (tool definitions),
    # images, audio, video artifacts, citations, extra_data etc.

    def __init__(self, content=None, messages=None, metrics=None, agent_id=None, run_id=None):
        self.content = content
        self.messages = messages or []
        self.metrics = metrics or {}
        self.agent_id = agent_id
        self.run_id = run_id

    def to_dict(self) -> Dict[str, Any]:
        # Converts the RunResponse object to a Python dictionary
        # ... (implementation details, calls .to_dict() on each message)
        return {"content": self.content, "messages": [m.to_dict() for m in self.messages], ...}
```
These classes are the containers for all the rich information an [Agent](02_agent_.md) generates.

### What About Teams? `TeamRunResponse`

When you use a [Team](03_team_.md) as described in Chapter 3, it returns a `TeamRunResponse` object (defined in `agno/run/team.py`). This is very similar to `RunResponse` but has an additional important field:
*   `member_responses`: A list containing the `RunResponse` (or even nested `TeamRunResponse`) objects from each member [Agent](02_agent_.md) or sub-team that participated in the task.

This allows you to see not only the `Team`'s overall result but also the individual contributions of its members.

## Conclusion

`RunResponse` and `Message` are your best friends for understanding what your `agno` [Agent](02_agent_.md)s and [Team](03_team_.md)s are doing.
*   `Message` objects give you a granular, turn-by-turn transcript of the interaction, including user inputs, assistant replies, and tool usage.
*   `RunResponse` bundles up the final output (`content`) along with the complete list of `Message`s and other valuable metadata like `metrics`.

By inspecting these objects, you can debug your agents, understand their decision-making processes, and extract the exact information you need. They provide transparency and control over your AI application's behavior.

Now that we know how agents and teams structure their output and record their interactions, it's time to dive deeper into one of their most critical components: the "brain" itself.

Next up: [Chapter 5: Model](05_model_.md)

---

Generated by [AI Codebase Knowledge Builder](https://github.com/The-Pocket/Tutorial-Codebase-Knowledge)