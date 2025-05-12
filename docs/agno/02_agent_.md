---
layout: default
title: "Agent"
parent: "Agno"
nav_order: 2
---

# Chapter 2: Agent

Welcome to the second chapter of our `agno` journey! In [Chapter 1: Playground](01_playground_.md), we got a sneak peek at how to set up a testing environment for an `Agent` using the `Playground`. We even made a simple "EchoBot" agent! Now, it's time to pull back the curtain and understand what an `Agent` truly is and how it works.

## What is an Agent, and Why Do We Need One?

Imagine you want to build a chatbot that can answer questions about your company's products, or a virtual assistant that can schedule meetings, or even an AI that can help you write a story. How would you create such an intelligent entity?

This is where the `Agent` comes in!

In `agno`, the **`Agent`** is like the main actor or the "brain" of your AI application. It's the core component responsible for:
1.  Receiving an input (like a user's question or a command).
2.  Thinking about it – this might involve using its underlying AI [Model](05_model_.md) (its "brainpower"), accessing [Memory](07_memory_.md) of past conversations, consulting a [KnowledgeBase & Reader](08_knowledgebase___reader_.md) for specific information, or using [Toolkit & Tools](06_toolkit___tools_.md) to perform actions.
3.  Generating a response or taking an action.

Think of an `Agent` as a smart, digital assistant. You give it a task, and it figures out how to do it and communicates back to you. Different agents can be designed for different purposes, each with its own unique personality (defined by instructions), "brain" ([Model](05_model_.md)), and set of skills ([Toolkit & Tools](06_toolkit___tools_.md)).

## Creating Your First "Real" Agent

In Chapter 1, our EchoBot was very simple – it just repeated what we said. Let's create a slightly more intelligent agent, one that can actually understand and respond, even if it's just a simple greeting for now.

To create an `Agent`, you'll typically need a few things:
*   A `name`: A friendly name for your agent (e.g., "HelpfulBot").
*   An `agent_id`: A unique identifier for your agent (e.g., "helpful-bot-v1").
*   A [Model](05_model_.md): This is the AI model that acts as the agent's primary brain. We'll learn more about Models in [Chapter 5: Model](05_model_.md). For now, think of it as the engine that powers the agent's understanding and language generation.
*   `instructions`: These are guidelines or a "persona" you give to your agent to tell it how to behave (e.g., "You are a polite and helpful assistant.").

Let's try it out!

```python
# agent_creation.py
from agno.agent import Agent
from agno.models.openai import OpenAIChat # We'll use a placeholder for a real AI model
from agno.run.response import RunResponse, Message # To understand the agent's output

# 1. A mock function to simulate a real AI model's response
# In a real app, the OpenAIChat model would call an actual AI service.
def mock_model_response(messages, tools=None, **kwargs) -> Message:
    # Let's pretend the model crafts a friendly greeting
    user_message_content = ""
    if messages:
        # Get the last user message
        user_message_content = messages[-1].content
    
    response_text = f"Hello there! You said: '{user_message_content}'. How can I help you today?"
    if "story" in user_message_content.lower():
        response_text = "Once upon a time, in a land of code, there was a brave little agent..."

    return Message(role="assistant", content=response_text)

# 2. Set up a mock "brain" (Model) for our agent
# We're using a mock here to keep things simple and avoid needing API keys for this example.
# In Chapter 5, we'll see how to use real models.
mock_llm = OpenAIChat(id="mock-gpt-3.5")
# We override the model's core processing method with our mock function
mock_llm.invoke = mock_model_response
# For asynchronous operations, we'd also set 'ainvoke'
# mock_llm.ainvoke = async_mock_model_response 

# 3. Create our first Agent
friendly_assistant = Agent(
    name="FriendlyBot",
    agent_id="friendly-bot-001",
    model=mock_llm, # Assign our mock brain
    instructions="You are a very friendly and slightly curious assistant."
)

# 4. Interact with the Agent
user_input = "Hi, can you tell me a story?"
print(f"You: {user_input}")

# The .run() method sends the input to the agent and gets a response.
response = friendly_assistant.run(message=user_input)

# 5. See what the Agent said
# The response object contains the agent's reply.
# We'll explore RunResponse and Message in detail in Chapter 4.
if response:
    print(f"{friendly_assistant.name}: {response.content}")
```

**What's happening here?**

1.  **Mock Model Response:** We created a `mock_model_response` function. This function pretends to be a powerful AI model. Real AI models (like those from OpenAI, Anthropic, etc.) are complex, but for now, our mock helps us understand the Agent's structure without needing external services or API keys.
2.  **Mock Model Setup:** We created an `OpenAIChat` instance (which would normally represent a real OpenAI model) and then replaced its `invoke` method (the part that does the thinking) with our simple `mock_model_response` function.
3.  **Agent Creation:** We instantiated an `Agent` by giving it a `name`, `agent_id`, our `mock_llm` as its `model`, and some `instructions`. These instructions help guide the model's responses, giving the agent a personality.
4.  **Interacting:** We called `friendly_assistant.run(message="...")`. This is how you "talk" to your agent.
5.  **Response:** The `agent.run()` method returns a [RunResponse & Message](04_runresponse___message_.md) object. The `response.content` attribute holds the main textual reply from the agent.

If you run this code, you should see an output like:

```
You: Hi, can you tell me a story?
FriendlyBot: Once upon a time, in a land of code, there was a brave little agent...
```

Our `FriendlyBot` didn't just echo us; it "understood" (based on our mock logic) that we asked for a story and gave a story-like response!

## Key Components an Agent Can Have

An `Agent` is more than just a [Model](05_model_.md) and instructions. It can be equipped with several other components to make it more powerful and versatile:

*   **[Model](05_model_.md) (The Brain):** As we've seen, this is the core AI engine. It's responsible for understanding input, making decisions, and generating responses. `agno` supports various models, which we'll explore in [Chapter 5: Model](05_model_.md).

*   **Instructions (The Persona):** These are text guidelines that tell the agent how it should behave, what its role is, and what tone it should use. For example: "You are a sarcastic pirate assistant."

*   **[Toolkit & Tools](06_toolkit___tools_.md) (The Abilities):** What if your agent needs to do something more than just talk? Like search the web, calculate something, or access a database? [Toolkit & Tools](06_toolkit___tools_.md) give your agent special abilities. Think of them as plugins. We'll cover these in detail in [Chapter 6: Toolkit & Tools](06_toolkit___tools_.md).

*   **[Memory](07_memory_.md) (The Short-Term Recall):** For an agent to have a coherent conversation, it needs to remember what was said earlier. [Memory](07_memory_.md) allows an agent to keep track of the current conversation history. Dive deeper in [Chapter 7: Memory](07_memory_.md).

*   **[KnowledgeBase & Reader](08_knowledgebase___reader_.md) (The Long-Term Knowledge):** Sometimes, an agent needs access to specific information not present in its training data or conversation history – like company documents, product manuals, or a set of FAQs. A [KnowledgeBase & Reader](08_knowledgebase___reader_.md) allows the agent to search and retrieve information from external documents. This is often called Retrieval Augmented Generation (RAG). We'll explore this in [Chapter 8: KnowledgeBase & Reader](08_knowledgebase___reader_.md).

Let's see a quick example of an agent with a very simple tool.

```python
# agent_with_a_tool.py
from agno.agent import Agent
from agno.tools.toolkit import Tool # The base for creating tools
from agno.run.response import Message # To help our mock model

# --- Mock Model Setup (to simulate tool usage) ---
class MockToolDecidingModel:
    _last_user_message = ""

    def invoke(self, messages, tools=None, **kwargs) -> Message:
        # Store the user message to "know" what the user asked
        if messages and messages[-1].role == "user":
            MockToolDecidingModel._last_user_message = messages[-1].content

        # If the model thinks it needs a tool based on user's message:
        if "weather" in MockToolDecidingModel._last_user_message.lower() and tools:
            print("MockModel: Decided to use the 'get_current_weather' tool.")
            # This is a simplified representation of a tool call request from an LLM
            tool_call_request = {
                "id": "toolcall_123", "type": "function",
                "function": {"name": "get_current_weather", "arguments": '{"city": "London"}'}
            }
            return Message(role="assistant", content=None, tool_calls=[tool_call_request])
        
        # If a tool was used, the agent will call the model again with tool results.
        # Let's check if the messages include a tool result.
        for msg in reversed(messages): # Check recent messages
            if msg.role == "tool":
                # Pretend the model now forms a final answer using the tool's output
                return Message(role="assistant", content=f"Okay, based on the tool, the weather is: {msg.content}")
        
        # Default response if no tool is used
        return Message(role="assistant", content="I can only tell you the weather right now.")

mock_llm_for_tools = OpenAIChat(id="mock-tool-user-gpt")
mock_llm_for_tools.invoke = MockToolDecidingModel().invoke
# --- End Mock Model Setup ---


# 1. Define a simple tool function
def get_current_weather_tool_func(city: str) -> str:
    """A mock tool to get the current weather for a city."""
    print(f"TOOL: Fetching weather for {city}...")
    # In a real tool, this would call a weather API
    return f"Sunny with a chance of code in {city}."

# 2. Create a Tool instance
weather_tool = Tool(
    name="get_current_weather",
    description="Gets the current weather for a specified city.",
    func=get_current_weather_tool_func # The actual Python function to call
)

# 3. Create an Agent with the tool
weather_reporter_agent = Agent(
    name="WeatherBot",
    agent_id="weather-bot-001",
    model=mock_llm_for_tools, # Our mock model that "knows" to use tools
    instructions="You are a weather bot. Use your tools to find weather information.",
    tools=[weather_tool] # Add our tool to the agent's toolkit!
)

# 4. Interact with the Agent
user_input = "What's the weather like in London?"
print(f"You: {user_input}")
response = weather_reporter_agent.run(message=user_input)

# 5. See the response
if response:
    print(f"{weather_reporter_agent.name}: {response.content}")

```

**What's happening in this "tool-enabled" agent example?**
1.  **Mock Model for Tools:** Our `MockToolDecidingModel` is a bit more clever. It "pretends" that if the user asks about "weather", it should try to use a tool named `get_current_weather`. Real LLMs can be instructed to do this.
2.  **Tool Function:** We defined a Python function `get_current_weather_tool_func` that simulates fetching weather.
3.  **Tool Instance:** We wrapped this function in `agno`'s `Tool` class, giving it a `name` (which the LLM uses to identify it) and a `description` (which helps the LLM understand what the tool does).
4.  **Agent with Tool:** When creating `weather_reporter_agent`, we passed a list containing our `weather_tool` to the `tools` parameter.
5.  **Interaction:**
    *   When we ask, "What's the weather like in London?", our mock model "decides" to use the `get_current_weather` tool.
    *   The `Agent` then executes our `get_current_weather_tool_func` Python function.
    *   The result from the tool ("Sunny with a chance of code in London.") is then (conceptually) sent back to the model.
    *   Our mock model then forms a final answer using this tool result.

If you run this, the output will show the print statements indicating the model's decision and the tool's execution, followed by the agent's final answer:
```
You: What's the weather like in London?
MockModel: Decided to use the 'get_current_weather' tool.
TOOL: Fetching weather for London...
WeatherBot: Okay, based on the tool, the weather is: Sunny with a chance of code in London.
```
This demonstrates how an `Agent` can go beyond just generating text and actually perform actions using tools!

## What Happens Inside an Agent? A Peek Under the Hood

When you call `agent.run("your message")`, a sequence of events unfolds:

1.  **Message Ingestion:** The `Agent` receives your message.
2.  **Context Gathering (Optional):**
    *   If the `Agent` has [Memory](07_memory_.md), it might retrieve relevant parts of the past conversation to provide context.
    *   If the `Agent` has a [KnowledgeBase & Reader](08_knowledgebase___reader_.md) and `search_knowledge=True` (or `add_references=True`), it might search its knowledge for information relevant to your query. This retrieved information is added to the context.
3.  **Prompt Preparation:** The `Agent` combines your current message, its `instructions`, any retrieved memory, and any retrieved knowledge into a comprehensive prompt for its [Model](05_model_.md). If it has [Toolkit & Tools](06_toolkit___tools_.md), information about these tools is also made available to the model.
4.  **Model Invocation:** The `Agent` sends this prepared prompt to its [Model](05_model_.md).
5.  **Model Processing & Decision:** The [Model](05_model_.md) processes the prompt. It might:
    *   Generate a direct textual answer.
    *   Decide to use one or more of the available [Toolkit & Tools](06_toolkit___tools_.md). If so, it specifies which tool(s) to use and with what arguments (e.g., "use `get_current_weather` tool with `city='London'`").
6.  **Tool Execution (If a tool was chosen):**
    *   The `Agent` receives the tool usage request from the [Model](05_model_.md).
    *   It executes the specified tool(s) with the provided arguments.
    *   The results from the tool(s) are collected.
7.  **Iterative Refinement (If a tool was used):**
    *   The tool results are sent back to the [Model](05_model_.md), often along with the original query or a follow-up instruction like "Here are the tool results, now generate the final answer."
    *   The [Model](05_model_.md) then generates a response based on this new information. This loop can happen multiple times if needed.
8.  **Response Generation:** The `Agent` takes the final output from the [Model](05_model_.md).
9.  **Output Formatting:** This output is packaged into a [RunResponse & Message](04_runresponse___message_.md) object, which includes the main content, all intermediate messages (user, assistant, tool calls, tool results), and potentially other metadata.
10. **Memory Update (Optional):** The interaction (your message and the agent's final response) is typically added to the agent's [Memory](07_memory_.md) for future reference.

Here's a simplified diagram showing this flow when a tool is involved:

```mermaid
sequenceDiagram
    participant User
    participant MyAgent as Agent
    participant MyMemory as Memory
    participant MyKnowledge as KnowledgeBase
    participant MyTool as Tool
    participant MyModel as Model

    User->>MyAgent: run("What's the weather in Paris according to our docs?")
    MyAgent->>MyMemory: Get conversation history
    MyMemory-->>MyAgent: Past messages
    MyAgent->>MyKnowledge: Search docs for "weather in Paris"
    MyKnowledge-->>MyAgent: Relevant document snippets
    MyAgent->>MyModel: Prompt (user_msg, history, docs_info, instructions, available_tools)
    MyModel-->>MyAgent: Decision: Use 'get_weather(city="Paris")' tool
    MyAgent->>MyTool: Execute get_weather(city="Paris")
    MyTool-->>MyAgent: Tool Result: "Sunny in Paris"
    MyAgent->>MyModel: Prompt (tool_result="Sunny in Paris", original_prompt_elements)
    MyModel-->>MyAgent: Final Answer: "According to our docs and the current weather, it's sunny in Paris."
    MyAgent->>MyMemory: Store current interaction
    MyMemory-->>MyAgent: Confirmed
    MyAgent-->>User: RunResponse (containing final answer and messages)
end
```

The core logic for this process resides within the `Agent` class, particularly in methods like `run()` (and its asynchronous counterpart `arun()`), which often delegate to internal methods like `_run_llm_with_tools()` (or `_arun_llm_with_tools()`).

Let's look at a conceptual, highly simplified Python-like representation of what `Agent._run_llm_with_tools` might do:

```python
# Conceptual snippet from within the Agent class (agno/agent/agent.py)

# def _run_llm_with_tools(self, messages_for_model: list, stream: bool):
#     # 'self' refers to the Agent instance
#     # 'messages_for_model' includes user input, history, instructions etc.
#     current_messages = list(messages_for_model)
#     final_response_content = ""

#     for _ in range(self.max_tool_iterations): # Limit how many times tools can be called
#         # 1. Call the LLM (Model)
#         # model_response is a Message object from the LLM
#         model_response = self.model.invoke(current_messages, tools=self.tools)
        
#         # Add assistant's raw response (or tool call request) to messages
#         current_messages.append(model_response)

#         # 2. Check if the LLM wants to use any tools
#         if model_response.tool_calls:
#             tool_results_messages = []
#             for tool_call in model_response.tool_calls:
#                 # 3. Execute the tool
#                 tool_name = tool_call.function.name
#                 tool_args = json.loads(tool_call.function.arguments)
#                 # Find and run the actual tool function (e.g., get_current_weather_tool_func)
#                 # result = self._execute_tool(tool_name, tool_args) 
#                 # tool_results_messages.append(Message(role="tool", tool_call_id=tool_call.id, name=tool_name, content=result))
#                 pass # Simplified: In reality, execute tool and create a tool Message

#             # Add tool results to the conversation history for the LLM
#             current_messages.extend(tool_results_messages)
#             # Loop back to call the LLM again with the tool results
#             continue 
#         else:
#             # 4. No tool calls, LLM gave a direct answer
#             final_response_content = model_response.content
#             break # Exit the loop

#     # 5. Construct and return the final RunResponse
#     # return RunResponse(content=final_response_content, messages=current_messages, ...)
#     pass
```
This simplified pseudo-code illustrates the loop:
1.  Call the [Model](05_model_.md).
2.  Check if the model wants to use a tool.
3.  If yes, execute the tool, add its result to the conversation, and go back to step 1.
4.  If no, the model's output is the final answer.
5.  Package everything up.

This iterative process allows agents to perform complex tasks that might require multiple steps or information retrieval via tools. The `test_tool_parsing.py` file in `agno` shows how agents can handle tools with various types of parameters. Similarly, files like `test_rag.py` demonstrate agents using [KnowledgeBase & Reader](08_knowledgebase___reader_.md) to answer questions (Retrieval Augmented Generation).

Agents can also be configured for more advanced behaviors like "reasoning" (as seen in `test_reasoning_content_*.py`), where they might "think step-by-step" before providing an answer, often using specialized reasoning tools. For multi-turn conversations and remembering users across sessions, agents can leverage [Storage](10_storage_.md) and [Memory](07_memory_.md) as shown in `test_agent_with_storage_and_memory.py`.

## Conclusion

The `Agent` is the heart of your `agno` application – it's the entity that thinks, acts, and communicates. You've learned how to create a basic agent, give it a "brain" ([Model](05_model_.md)) and "instructions", and even equip it with simple [Toolkit & Tools](06_toolkit___tools_.md). We also took a high-level look at the internal flow of how an agent processes information and interacts with its components like [Memory](07_memory_.md) and [KnowledgeBase & Reader](08_knowledgebase___reader_.md).

But what if a task is too complex for a single agent? Or what if you need different specialized agents to collaborate? That's where a [Team](03_team_.md) of agents comes in handy!

Next up: [Chapter 3: Team](03_team_.md)

---

Generated by [AI Codebase Knowledge Builder](https://github.com/The-Pocket/Tutorial-Codebase-Knowledge)