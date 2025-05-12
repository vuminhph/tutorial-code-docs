---
layout: default
title: "Model"
parent: "Agno"
nav_order: 5
---

# Chapter 5: Model

In [Chapter 4: RunResponse & Message](04_runresponse___message_.md), we learned how an [Agent](02_agent_.md) packages its thoughts and final answers into `RunResponse` and `Message` objects. But what actually does the "thinking"? What's the source of the intelligence? That's where the `Model` comes in!

## The Engine of Intelligence: What is a `Model`?

Imagine an [Agent](02_agent_.md) is like a car. It can perform tasks, carry information, and interact with the world. The `Model` is like the specific engine inside that car.
*   A powerful V8 engine (like GPT-4) might offer high performance and tackle complex tasks.
*   A fuel-efficient hybrid engine (like a smaller, specialized model) might be great for specific, less demanding jobs.
*   Different engine manufacturers (like OpenAI, Anthropic, Google) build their engines differently.

In `agno`, the **`Model`** represents the underlying Large Language Model (LLM) or other AI model that powers an agent's intelligence. It's the core "brain" that understands language, generates responses, and makes decisions based on the input it receives.

Examples of well-known AI models include:
*   GPT-series (e.g., GPT-3.5, GPT-4, GPT-4o) from OpenAI
*   Claude series (e.g., Claude 3 Sonnet, Claude 3 Opus) from Anthropic
*   Gemini series from Google
*   Llama series from Meta

Each of these models has different strengths, weaknesses, costs, and ways of being accessed (their APIs). The `Model` abstraction in `agno` is designed to handle the communication with these various AI services, providing a consistent way for your [Agent](02_agent_.md) to use them.

## Why Do We Need a `Model` Abstraction?

Different AI providers have unique ways to interact with their models. If you wrote code directly for OpenAI's API, and then wanted to try Anthropic's Claude, you'd have to rewrite a lot of your communication logic.

The `Model` classes in `agno` solve this by providing a common interface. Your [Agent](02_agent_.md) talks to an `agno` `Model` object, and that object takes care of the specific details of talking to the actual AI service. This makes it much easier to:
*   **Experiment with different LLMs**: Swap out one model for another with minimal code changes.
*   **Keep your agent code clean**: Your agent logic doesn't need to be cluttered with API-specific details.

## Using a `Model` in Your `agno` Agent

In previous chapters, we often used "mock" models for simplicity. Now, let's see how you'd set up an [Agent](02_agent_.md) with a real `Model`.

First, you'll choose a `Model` class from `agno` that corresponds to the AI provider you want to use (e.g., `OpenAIChat` for OpenAI, `Claude` for Anthropic). You then create an instance of this class, providing details like the specific model ID (e.g., "gpt-4o", "claude-3-sonnet-20240229") and any other necessary configurations.

```python
# model_setup_example.py
from agno.agent import Agent
from agno.models.openai import OpenAIChat       # For OpenAI models
from agno.models.anthropic import Claude        # For Anthropic's Claude models
# from agno.models.google import Gemini         # For Google's Gemini models
# from agno.models.groq import Groq             # For models via Groq

# Important: For this to work with real models, you need API keys.
# These are usually set as environment variables:
# - OPENAI_API_KEY for OpenAI
# - ANTHROPIC_API_KEY for Anthropic
# - GOOGLE_API_KEY for Google Gemini (or GOOGLE_CLOUD_PROJECT for Vertex AI)
# - GROQ_API_KEY for Groq

# 1. Instantiate your chosen Model
# Let's pick OpenAI's GPT-3.5 Turbo as an example
llm_brain_openai = OpenAIChat(
    id="gpt-3.5-turbo",  # Specific model ID
    temperature=0.7      # Controls creativity (0.0 more deterministic, 1.0 more creative)
)

# Or, if you wanted to use Anthropic's Claude 3 Sonnet:
# llm_brain_claude = Claude(
#     id="claude-3-sonnet-20240229",
#     temperature=0.5
# )

# 2. Create an Agent and pass the Model to it
my_ai_assistant = Agent(
    name="MyAssistant",
    model=llm_brain_openai,  # Assigning the "brain"
    instructions="You are a helpful assistant that answers questions clearly."
)

print(f"Agent '{my_ai_assistant.name}' is ready.")
print(f"It's powered by: {my_ai_assistant.model.id} from {my_ai_assistant.model.provider}")

# 3. Interacting with the Agent (this part would make a real API call)
# user_question = "What's the main benefit of using an AI model abstraction?"
# response = my_ai_assistant.run(message=user_question)

# if response:
#     print(f"\n{my_ai_assistant.name} says:")
#     print(response.content)
```

**What's happening in this code?**
1.  We import `Agent` and the desired `Model` class (e.g., `OpenAIChat`).
2.  We create an instance of `OpenAIChat`.
    *   `id="gpt-3.5-turbo"`: This tells `agno` exactly which OpenAI model to use.
    *   `temperature=0.7`: This is a common LLM parameter. Higher values make the output more random and creative, while lower values make it more focused and deterministic. `agno` passes these parameters to the underlying AI service.
3.  We create our `Agent` and, crucially, pass our `llm_brain_openai` instance to its `model` parameter. This links the agent to its "brain."
4.  The commented-out `run` call shows that when the agent processes a message, it will use the configured `OpenAIChat` model to generate a response. This involves an actual call to the OpenAI API (if API keys are set up).

If you were to run this (with a valid API key for the chosen model), the `Agent` would use the specified `Model` to understand your question and generate an answer.

## What Happens Under the Hood?

When an [Agent](02_agent_.md)'s `run()` method is called, and it needs the `Model` to think:

1.  **Agent Prepares**: The [Agent](02_agent_.md) gathers all necessary information: your current message, any relevant past [RunResponse & Message](04_runresponse___message_.md)s (from [Memory](07_memory_.md)), its instructions, and details about available [Toolkit & Tools](06_toolkit___tools_.md). This forms a "prompt" or a set of messages for the `Model`.
2.  **Agent Delegates to Model**: The [Agent](02_agent_.md) calls a method on its `Model` object (typically `invoke()` for a single response, or `invoke_stream()` for streaming). It passes the prepared messages to this method.
3.  **Model Communicates**: The `Model` object (e.g., `OpenAIChat`, `Claude` instance) takes over.
    *   It formats the messages and parameters into the specific format required by its AI service (e.g., OpenAI API, Anthropic API).
    *   It makes an HTTP request to the AI service's API endpoint.
4.  **AI Service Responds**: The external AI service processes the request and sends back a raw response (usually in JSON format).
5.  **Model Parses**: The `agno` `Model` object receives this raw response. It then parses this provider-specific JSON into a standardized `agno.models.response.ModelResponse` object. This `ModelResponse` contains the AI's reply, any tool usage requests, token usage metrics, etc., in a way `agno` can uniformly understand.
6.  **Model Returns to Agent**: The `ModelResponse` is returned to the [Agent](02_agent_.md).
7.  **Agent Finalizes**: The [Agent](02_agent_.md) uses the `ModelResponse` to construct its final [RunResponse & Message](04_runresponse___message_.md) that you, the user, receive.

Here's a simplified diagram of this interaction:

```mermaid
sequenceDiagram
    participant User
    participant MyAgent as Agent
    participant MyModel as Model (e.g., OpenAIChat)
    participant AIService as AI Service (e.g., OpenAI API)

    User->>MyAgent: run("Tell me about agno Models.")
    MyAgent->>MyAgent: Prepares messages for Model
    MyAgent->>MyModel: invoke(formatted_messages)
    MyModel->>MyModel: Formats request for specific API
    MyModel->>AIService: HTTP API Request (to OpenAI, Anthropic, etc.)
    AIService-->>MyModel: HTTP API Response (raw JSON)
    MyModel->>MyModel: Parses raw JSON into ModelResponse
    MyModel-->>MyAgent: Returns ModelResponse object
    MyAgent->>MyAgent: Creates final RunResponse
    MyAgent-->>User: Returns RunResponse
end
```

**A Peek at the Code Structure (Conceptual)**

`agno` has a base `Model` class (in `agno/models/base.py`) that defines the common interface all specific model implementations should follow. This includes methods like:
*   `invoke(messages: List[Message], **kwargs)`: For getting a single, complete response.
*   `ainvoke(messages: List[Message], **kwargs)`: The asynchronous version of `invoke`.
*   `invoke_stream(messages: List[Message], **kwargs)`: For getting a response as a stream of chunks.
*   `ainvoke_stream(messages: List[Message], **kwargs)`: The asynchronous version for streaming.
*   `parse_provider_response(response_from_api)`: To convert the AI service's raw response into `agno`'s standard `ModelResponse`.
*   `parse_provider_response_delta(chunk_from_api)`: To parse individual chunks from a streaming response.

Specific classes like `OpenAIChat` (in `agno/models/openai/chat.py`), `Claude` (in `agno/models/anthropic/claude.py`), etc., inherit from this base `Model` and implement these methods to handle the unique aspects of their respective AI services.

Let's look at a *highly simplified* conceptual structure of how `OpenAIChat` might work:

```python
# Conceptual and highly simplified from agno/models/openai/chat.py
# from openai import OpenAI as OpenAIClient # The actual OpenAI library
from agno.models.response import ModelResponse
from agno.models.message import Message # Used for type hinting

class OpenAIChatConceptual: # Not the real class name
    def __init__(self, id="gpt-3.5-turbo", api_key=None, temperature=0.7, #...
                 openai_sdk_client=None): # In reality, it might take an SDK client
        self.id = id
        self.api_key = api_key # Typically fetched from environment variables
        self.temperature = temperature
        # self.client = openai_sdk_client or OpenAIClient(api_key=self.api_key)
        print(f"Conceptual OpenAIChat initialized for model {self.id}")

    def _format_messages_for_openai(self, messages: list) -> list:
        # Convert agno's Message objects into OpenAI's expected format
        print("Formatting messages for OpenAI API...")
        # formatted = []
        # for msg in messages:
        #     formatted.append({"role": msg.role, "content": msg.content})
        # return formatted
        return [{"role": m.role, "content": m.get_content_string()} for m in messages] # Simplified

    def invoke(self, messages: list) -> dict: # Real return is an OpenAI ChatCompletion object
        print(f"OpenAIChat: Calling OpenAI API for model {self.id}...")
        formatted_api_messages = self._format_messages_for_openai(messages)
        
        # Actual call to OpenAI SDK would happen here:
        # response = self.client.chat.completions.create(
        #     model=self.id,
        #     messages=formatted_api_messages,
        #     temperature=self.temperature,
        #     # ... other OpenAI specific parameters
        # )
        # return response
        
        # For this tutorial, we'll simulate a raw response from OpenAI
        simulated_raw_response = {
            "id": "chatcmpl-xxxxx",
            "choices": [{
                "index": 0,
                "message": {"role": "assistant", "content": f"Hello from simulated {self.id}!"},
                "finish_reason": "stop"
            }],
            "usage": {"prompt_tokens": 20, "completion_tokens": 10, "total_tokens": 30}
        }
        print("OpenAIChat: Received raw response from (simulated) OpenAI API.")
        return simulated_raw_response

    def parse_provider_response(self, raw_response_from_openai: dict) -> ModelResponse:
        print("OpenAIChat: Parsing raw OpenAI response into Agno ModelResponse...")
        parsed_model_response = ModelResponse()
        
        choice = raw_response_from_openai["choices"][0]
        message_data = choice["message"]
        
        parsed_model_response.role = message_data["role"]
        parsed_model_response.content = message_data["content"]
        
        # In reality, would parse tool_calls, usage, etc.
        # parsed_model_response.response_usage = raw_response_from_openai["usage"]
        
        print("OpenAIChat: Parsing complete.")
        return parsed_model_response

# Example of how an Agent might interact with this (conceptually)
# model_instance = OpenAIChatConceptual(id="gpt-4-mini")
# input_msgs = [Message(role="user", content="Explain Models in Agno.")]

# This is what Agent's `_run_llm_with_tools` or similar method does internally:
# raw_api_response = model_instance.invoke(input_msgs) 
# agno_model_response = model_instance.parse_provider_response(raw_api_response)
# print(f"Final content for Agent: {agno_model_response.content}")
```
This conceptual example illustrates that:
1.  The `OpenAIChatConceptual` class would handle creating an OpenAI client.
2.  Its `invoke` method prepares messages for the OpenAI API and calls it.
3.  Its `parse_provider_response` method takes the raw JSON from OpenAI and transforms it into a standard `ModelResponse` that the [Agent](02_agent_.md) can work with.

Each `Model` implementation (for Claude, Gemini, Groq, etc.) in `agno` follows a similar pattern, tailored to its specific AI service. You can find these in `agno/models/`. For example, `agno/models/anthropic/claude.py` contains the `Claude` model, and `agno/models/google/gemini.py` contains the `Gemini` model.

## Choosing Your Engine

Different `Model`s offer varied capabilities:
*   **Performance & Accuracy**: Some models are better at reasoning, others at creativity, and some at following complex instructions.
*   **Cost**: API calls to different models have different pricing.
*   **Speed**: Some models respond faster than others.
*   **Context Window**: This is the amount of information (text, tokens) the model can consider at once. Larger context windows allow for longer conversations or processing larger documents.
*   **Multimodality**: Some newer models can process not just text, but also images, audio, or even video. `agno` supports this where the underlying models do.
*   **Special Features**: Some models might offer unique features like guaranteed JSON output, specific tool-use capabilities, or grounding with search results.

`agno`'s `Model` abstraction allows you to configure these aspects and makes it easier to switch and test which "engine" is best for your particular AI application.

## Conclusion

The `Model` is the heart of your [Agent](02_agent_.md)'s intelligence, the "engine" that drives its understanding and responses. `agno` provides a clean abstraction that lets you plug in various LLMs from different providers (like OpenAI, Anthropic, Google) without getting bogged down in the specific API details of each one. This empowers you to choose the best brain for your agent's tasks and easily experiment with new advancements in AI.

But what if your [Agent](02_agent_.md) needs to do more than just "think" and "talk"? What if it needs to perform actions in the real world, like searching the web, calling an API, or running a piece of code? For that, it needs special abilities.

Next up: [Chapter 6: Toolkit & Tools](06_toolkit___tools_.md)

---

Generated by [AI Codebase Knowledge Builder](https://github.com/The-Pocket/Tutorial-Codebase-Knowledge)