---
layout: default
title: "Toolkit & Tools"
parent: "Agno"
nav_order: 6
---

# Chapter 6: Toolkit & Tools

In [Chapter 5: Model](05_model_.md), we learned about the "brain" or `Model` that powers an [Agent](02_agent_.md)'s intelligence, allowing it to understand and generate text. But what if an [Agent](02_agent_.md) needs to do more than just talk? What if it needs to perform specific actions, like searching the internet for today's news, checking the current stock price, or even controlling a smart home device? This is where `Toolkit` & `Tools` come in!

Imagine your [Agent](02_agent_.md) is a helpful assistant. Just like a human assistant might use a calculator, a web browser, or a phone to get things done, your AI [Agent](02_agent_.md) can use `Tools`.

## The Handyman's Toolbox: `Toolkit` and `Tool`

*   **`Tool`**: A `Tool` is essentially a Python function that your [Agent](02_agent_.md) can use to perform a specific action. This function could do anything – make an API call, perform a calculation, or access a database.
*   **`Toolkit`**: A `Toolkit` is a collection of these `Tools`. Think of it as a handyman's toolbox. A "WebSearchKit" `Toolkit` might contain `Tools` for searching Google, DuckDuckGo, and Bing. A "FinanceKit" `Toolkit` might have `Tools` for fetching stock prices, company news, and financial reports.

The magic that makes a regular Python function usable by an [Agent](02_agent_.md) is often a special Python feature called a **decorator**, specifically `@tool` in `agno`.

## Creating Your First `Tool` with `@tool`

Let's say we want our [Agent](02_agent_.md) to be able to get the current price of a cryptocurrency. We can write a simple Python function for this.

```python
# simple_tool_example.py
from agno.tools import tool # Import the magic decorator

@tool
def get_crypto_price(coin_name: str) -> str:
    """
    Fetches the current price of a specified cryptocurrency.
    For example, 'Bitcoin' or 'Ethereum'.
    """
    # In a real tool, this would call a crypto API
    print(f"TOOL: Pretending to fetch price for {coin_name}...")
    if coin_name.lower() == "bitcoin":
        return "Bitcoin is currently $40,000 USD."
    elif coin_name.lower() == "ethereum":
        return "Ethereum is currently $3,000 USD."
    else:
        return f"Sorry, I don't know the price of {coin_name}."

# The 'get_crypto_price' function is now an agno 'Tool'!
# We can see its name and description (extracted from the docstring)
print(f"Tool Name: {get_crypto_price.name}")
print(f"Tool Description: {get_crypto_price.description}")
print(f"Tool Parameters: {get_crypto_price.parameters}")
```

**What's happening here?**
1.  We import `tool` from `agno.tools`.
2.  We define a normal Python function `get_crypto_price` that takes a `coin_name` (like "Bitcoin") and returns a string.
3.  **`@tool`**: This is the important part! By putting `@tool` right above our function definition, `agno` automatically processes this function. It:
    *   Notes its name (`get_crypto_price`).
    *   Reads its docstring (`"Fetches the current price..."`) to understand what the tool does (this becomes the `description`).
    *   Analyzes its parameters (like `coin_name: str`) to know what inputs it expects (this defines the `parameters` schema).
    *   Wraps it in a `Function` object (from `agno.tools.function.Function`), which is `agno`'s internal representation of a callable tool.

If you run this, you'll see something like:
```
Tool Name: get_crypto_price
Tool Description: Fetches the current price of a specified cryptocurrency.
For example, 'Bitcoin' or 'Ethereum'.
Tool Parameters: {'type': 'object', 'properties': {'coin_name': {'type': 'string', 'description': "('str') "}}, 'required': ['coin_name']}
```
Our simple Python function is now a `Tool` that an [Agent](02_agent_.md) can understand and potentially use!

## Organizing `Tool`s with a `Toolkit`

While you can give individual `Tool`s to an [Agent](02_agent_.md), it's often cleaner to group related tools into a `Toolkit`. `agno` provides some pre-built `Toolkits` like:
*   `DuckDuckGoTools` (from `agno.tools.duckduckgo`) for web searching.
*   `YFinanceTools` (from `agno.tools.yfinance`) for stock prices and financial data.
*   `ExaTools` (from `agno.tools.exa`) for advanced web search and content retrieval.

Let's see how you might create a simple custom `Toolkit`.

```python
# simple_toolkit_example.py
from agno.tools import Toolkit, tool

@tool
def get_server_status(server_name: str) -> str:
    """Checks the status of a server."""
    return f"Server '{server_name}' is online."

@tool
def reboot_server(server_name: str) -> str:
    """Reboots a server."""
    return f"Server '{server_name}' is rebooting."

# Create a Toolkit and add our tools
server_admin_kit = Toolkit(
    name="ServerAdminKit",
    tools=[get_server_status, reboot_server] # Pass the tool functions
)

print(f"Toolkit '{server_admin_kit.name}' created.")
print(f"It has these tools: {list(server_admin_kit.functions.keys())}")
```
Here, we created two tools, `get_server_status` and `reboot_server`, and then grouped them into a `Toolkit` called `ServerAdminKit`. The `Toolkit` class (from `agno.tools.toolkit.Toolkit`) takes a list of tool functions and organizes them.

## Equipping an Agent with Tools

Now, let's give our [Agent](02_agent_.md) the ability to use these tools.

```python
# agent_with_tools_example.py
from agno.agent import Agent
from agno.models.openai import OpenAIChat # Using a mock model
from agno.run.response import Message
from agno.tools import tool

# --- Mock Model Setup (to simulate tool usage decision) ---
class MockToolUsingModel:
    _last_user_message = ""
    _tools_available = []

    def invoke(self, messages, tools=None, **kwargs) -> Message:
        if messages and messages[-1].role == "user":
            self._last_user_message = messages[-1].content
        self._tools_available = tools # Agent passes its tools here

        # Mock logic: if user asks for crypto price, and tool exists
        if "price of bitcoin" in self._last_user_message.lower() and any(t.name == "get_crypto_price" for t in self._tools_available):
            print("MockModel: Decided to use 'get_crypto_price' tool.")
            return Message(role="assistant", tool_calls=[{
                "id": "call_123", "type": "function",
                "function": {"name": "get_crypto_price", "arguments": '{"coin_name": "Bitcoin"}'}
            }])
        
        # If a tool was called, the agent will send its result back to the model
        for msg in reversed(messages):
            if msg.role == "tool" and msg.name == "get_crypto_price":
                return Message(role="assistant", content=f"The tool said: {msg.content}")
        
        return Message(role="assistant", content="I can't do that with my current tools.")

mock_llm = OpenAIChat(id="mock-tool-decider")
mock_llm.invoke = MockToolUsingModel().invoke
# --- End Mock Model Setup ---

# 1. Our crypto price tool from before
@tool
def get_crypto_price(coin_name: str) -> str:
    """Fetches the current price of a specified cryptocurrency."""
    print(f"TOOL EXECUTING: Fetching price for {coin_name}...")
    if coin_name.lower() == "bitcoin": return "Bitcoin is $40,000."
    return "Unknown coin."

# 2. Create an Agent and give it the tool
crypto_bot = Agent(
    name="CryptoPriceBot",
    model=mock_llm,
    instructions="You can fetch crypto prices.",
    tools=[get_crypto_price] # Pass a list of tools
)

# 3. Interact with the Agent
user_query = "What's the current price of Bitcoin?"
print(f"User: {user_query}")
response = crypto_bot.run(message=user_query)

print(f"{crypto_bot.name}: {response.content}")
```

**What's happening in this example?**
1.  **Mock Model**: Our `MockToolUsingModel` simulates how a real [Model](05_model_.md) (like GPT-4) would behave. When an [Agent](02_agent_.md) has tools, it tells its [Model](05_model_.md) about them (their names, descriptions, parameters). The [Model](05_model_.md) then decides if a user's query requires a tool. If so, it tells the [Agent](02_agent_.md) which tool to use and with what arguments (e.g., call `get_crypto_price` with `coin_name="Bitcoin"`). This instruction is part of the `tool_calls` field in the [RunResponse & Message](04_runresponse___message_.md) from the model.
2.  **Tool Definition**: We have our `@tool` decorated `get_crypto_price` function.
3.  **Agent with Tool**: When creating `crypto_bot`, we pass `[get_crypto_price]` to the `tools` parameter. The [Agent](02_agent_.md) now knows it has this capability.
4.  **Interaction**:
    *   User asks: "What's the current price of Bitcoin?"
    *   The `Agent` passes this to its `mock_llm`.
    *   Our `mock_llm` "decides" to use the `get_crypto_price` tool.
    *   The `Agent` receives this decision, finds the `get_crypto_price` Python function, and executes it with `coin_name="Bitcoin"`.
    *   The tool function runs (prints "TOOL EXECUTING...") and returns "Bitcoin is $40,000.".
    *   This result is then passed back to the `mock_llm`.
    *   The `mock_llm` uses this result to form the final answer.

Running this would produce:
```
User: What's the current price of Bitcoin?
MockModel: Decided to use 'get_crypto_price' tool.
TOOL EXECUTING: Fetching price for Bitcoin...
CryptoPriceBot: The tool said: Bitcoin is $40,000.
```
Our agent successfully used a tool to answer the question!

## What Happens Under the Hood? The Tool-Using Flow

1.  **User Input**: You send a message to the [Agent](02_agent_.md).
2.  **Contextualization**: The [Agent](02_agent_.md) prepares a prompt for its [Model](05_model_.md). This prompt includes your message, the agent's instructions, any relevant conversation history ([Memory](07_memory_.md)), and, crucially, descriptions of all the `Tools` it has available.
3.  **Model Decides**: The [Model](05_model_.md) (e.g., GPT-4, Claude) analyzes the prompt. If it determines that one or more tools could help answer the query, it doesn't generate a direct text reply. Instead, it outputs a special instruction, often in a structured format like JSON, indicating:
    *   Which tool to call (e.g., `get_crypto_price`).
    *   What arguments to use (e.g., `{"coin_name": "Bitcoin"}`).
    This is often found in the `tool_calls` attribute of an assistant's [RunResponse & Message](04_runresponse___message_.md).
4.  **Agent Receives Tool Call**: The `Agent` receives this "tool call" request from the [Model](05_model_.md).
5.  **Tool Dispatch**: The `Agent` looks up the requested tool name (e.g., `get_crypto_price`) in its list of available `Tools`.
6.  **Tool Execution**: The `Agent` executes the actual Python function associated with that `Tool` (our `get_crypto_price` function), passing the arguments provided by the [Model](05_model_.md). The execution of the tool is managed by a `FunctionCall` object (from `agno.tools.function.FunctionCall`).
7.  **Tool Result**: The Python function returns its result (e.g., "Bitcoin is $40,000 USD.").
8.  **Result to Model**: The `Agent` sends this tool result back to the [Model](05_model_.md), usually along with the original context. The message containing the tool's output will have `role="tool"`.
9.  **Model Generates Final Response**: The [Model](05_model_.md) now uses the tool's output to generate a final, human-readable text response (e.g., "The current price of Bitcoin is $40,000 USD.").
10. **Agent Returns Response**: The [Agent](02_agent_.md) sends this final response back to you.

Here's a simplified sequence diagram:
```mermaid
sequenceDiagram
    participant User
    participant MyAgent as Agent
    participant LLM as Model
    participant CryptoTool as Tool (Python Function)

    User->>MyAgent: "Price of Bitcoin?"
    MyAgent->>LLM: Prompt (query, available_tool_descriptions)
    LLM-->>MyAgent: Request: Use CryptoTool(coin_name="Bitcoin")
    MyAgent->>CryptoTool: Execute get_crypto_price(coin_name="Bitcoin")
    CryptoTool-->>MyAgent: Result: "Bitcoin is $40,000."
    MyAgent->>LLM: Send tool_result="Bitcoin is $40,000."
    LLM-->>MyAgent: Final Answer: "The price of Bitcoin is $40,000."
    MyAgent-->>User: RunResponse (containing final answer)
end
```

## A Glimpse into `agno`'s Tool Machinery

*   **`@tool` Decorator (`agno/tools/decorator.py`)**:
    This decorator is the primary way to define a `Tool`. It wraps your Python function in an `agno.tools.function.Function` object.
    ```python
    # Simplified concept from agno/tools/decorator.py
    from agno.tools.function import Function # The class that represents a callable tool
    
    def tool(*decorator_args, **decorator_kwargs): # Can be @tool or @tool(name="...")
        def wrapper(func_to_decorate):
            # 'func_to_decorate' is your Python function (e.g., get_crypto_price)
            # It creates a Function object, extracting name, docstring for description,
            # and type hints for parameters.
            function_instance = Function.from_callable(
                func_to_decorate, 
                **decorator_kwargs # Passes arguments like name, description if provided to @tool()
            )
            return function_instance # Returns the Function object
        
        # This handles both @tool and @tool(with_arguments)
        if len(decorator_args) == 1 and callable(decorator_args[0]) and not decorator_kwargs:
            return wrapper(decorator_args[0]) # Called as @tool
        return wrapper # Called as @tool(name="custom_name")
    ```
    The `Function` object holds the actual callable, its description (usually from the docstring), and a JSON schema of its parameters (derived from type hints). This structured information is what the [Model](05_model_.md) uses to understand how and when to use the tool.

*   **`Toolkit` Class (`agno/tools/toolkit.py`)**:
    A `Toolkit` is essentially a named collection of these `Function` objects.
    ```python
    # Simplified concept from agno.tools.toolkit.py
    from typing import List, Callable, Dict
    from agno.tools.function import Function
    
    class Toolkit:
        def __init__(self, name: str, tools: List[Callable] = None, auto_register: bool = True, **kwargs):
            self.name: str = name
            self.raw_tools: List[Callable] = tools or [] # The original Python functions or Function objects
            self.functions: Dict[str, Function] = {} # Stores name -> Function object
            
            if auto_register:
                self._register_tools()
        
        def _register_tools(self) -> None:
            for t_callable in self.raw_tools:
                if isinstance(t_callable, Function): # If it's already a Function (from @tool)
                    self.functions[t_callable.name] = t_callable
                elif callable(t_callable): # If it's a raw Python function
                    # Convert it to a Function object
                    # function_instance = Function.from_callable(t_callable)
                    # self.functions[function_instance.name] = function_instance
                    pass # Simplified: real code converts callable to Function

        def register(self, func_callable: Callable, name: Optional[str] = None):
            # Simplified: Allows adding more tools after initialization
            # tool_func = Function.from_callable(func_callable, name=name)
            # self.functions[tool_func.name] = tool_func
            pass
    ```
    When you provide tools to an [Agent](02_agent_.md), whether as individual `Function` objects or within a `Toolkit`, the agent makes their definitions (name, description, parameters) available to its [Model](05_model_.md).

*   **Pre-built Toolkits**: `agno` comes with handy pre-built toolkits. For instance, `YFinanceTools` (in `agno/tools/yfinance.py`) offers tools for financial data:
    ```python
    # Highly simplified structure of YFinanceTools from agno/tools/yfinance.py
    from agno.tools import Toolkit
    # import yfinance as yf # The actual library it uses

    class YFinanceTools(Toolkit):
        def __init__(self, stock_price: bool = True, **kwargs):
            super().__init__(name="yfinance_tools", **kwargs)
            if stock_price:
                # The 'register' method (or auto-registration if methods are @tool decorated)
                # would turn 'get_current_stock_price' into a 'Function' object.
                self.register(self.get_current_stock_price)
            # ... other financial tools like get_company_info ...

        def get_current_stock_price(self, symbol: str) -> str:
            """Use this function to get the current stock price for a given symbol."""
            # try:
            #     stock = yf.Ticker(symbol)
            #     current_price = stock.info.get("regularMarketPrice")
            #     return f"{current_price:.2f}" if current_price else "Price not found."
            # except Exception as e:
            #     return f"Error: {e}"
            return f"Mock price for {symbol}: {(len(symbol) * 10):.2f}" # Simplified mock
    ```
    You can use these pre-built toolkits by simply instantiating them and passing them to your [Agent](02_agent_.md)'s `tools` list (or by adding their `functions` to the agent's tools).

## Conclusion

`Tool`s and `Toolkit`s are what give your `agno` [Agent](02_agent_.md)s superpowers beyond just text generation.
*   A **`Tool`** is a specific capability, a Python function made available to the agent, often defined easily using the `@tool` decorator.
*   A **`Toolkit`** is a convenient way to group related `Tool`s.

By equipping your [Agent](02_agent_.md)s with the right `Tool`s, they can interact with external systems, fetch real-time data, perform calculations, and take actions in the digital world, making them much more powerful and useful. The [Model](05_model_.md) acts as the brain, deciding *when* to use a tool, and `agno` handles the mechanics of executing it and feeding the results back.

Now that our agents can think ([Model](05_model_.md)) and act ([Toolkit & Tools](06_toolkit___tools_.md)), what about remembering past interactions to have more coherent, multi-turn conversations?

Next up: [Chapter 7: Memory](07_memory_.md)

---

Generated by [AI Codebase Knowledge Builder](https://github.com/The-Pocket/Tutorial-Codebase-Knowledge)