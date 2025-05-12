---
layout: default
title: "Team"
parent: "Agno"
nav_order: 3
---

# Chapter 3: Team

Welcome to Chapter 3! In [Chapter 2: Agent](02_agent_.md), we learned how to build individual AI "brains" called Agents. An [Agent](02_agent_.md) can understand, think, and respond. But what happens when a task is too complex for a single [Agent](02_agent_.md), or requires different kinds of expertise? Imagine you're building a sophisticated AI assistant that needs to:

1.  Answer general knowledge questions (like "What's the capital of France?").
2.  Tell you the current weather (like "What's the weather like in London?").

You could try to build one super-agent, but it's often better to create specialized [Agent](02_agent_.md)s and have them work together. This is where a `Team` comes in!

## What is a Team? The Project Manager for Your Agents

A `Team` in `agno` is like a project manager for your [Agent](02_agent_.md)s. It's an abstraction that coordinates multiple [Agent](02_agent_.md)s to work together on a task. Think of it: if you have a team of people, each with a specialty, the project manager ensures the right person handles the right part of the project.

A `Team` can operate in different modes. Two common ones are:

1.  **`route` mode**: The `Team` acts like a smart receptionist. It receives a task (a user's message) and decides which [Agent](02_agent_.md) in the team is the most suitable to handle it. It then "routes" or directs the task to that specific [Agent](02_agent_.md).
2.  **`collaborate` mode**: The `Team` might involve multiple [Agent](02_agent_.md)s contributing to a single task, with their outputs potentially being combined. This is like a group of experts brainstorming or working on different pieces of a puzzle.

For this chapter, we'll focus on the `route` mode as it's a great starting point for understanding how teams work.

## Creating Your First Team: The "Router" Team

Let's build a `Team` that can route questions to either a "CapitalCityExpert" or a "WeatherExpert".

**Step 1: Define Your Specialist Agents**

First, we need our [Agent](02_agent_.md)s. We'll create two very simple ones, similar to what we did in [Chapter 2: Agent](02_agent_.md), but with mock logic to simulate their expertise.

```python
# team_example.py
from agno.agent import Agent
from agno.models.openai import OpenAIChat # We'll use this as a base for mocks
from agno.run.response import RunResponse, Message

# --- Mock Model for Agents ---
# Mock logic for an agent that "knows" capital cities
def mock_capital_city_expert_logic(messages, **kwargs) -> Message:
    user_query = messages[-1].content.lower()
    if "france" in user_query:
        return Message(role="assistant", content="The capital of France is Paris!")
    return Message(role="assistant", content="I can only tell you about France's capital.")

# Mock logic for an agent that "knows" weather
def mock_weather_expert_logic(messages, **kwargs) -> Message:
    user_query = messages[-1].content.lower()
    if "london" in user_query:
        return Message(role="assistant", content="It's probably drizzling in London!")
    return Message(role="assistant", content="I can only tell you about London's weather.")

# Create mock models for our agents
capital_model = OpenAIChat(id="mock-capital-llm")
capital_model.invoke = mock_capital_city_expert_logic

weather_model = OpenAIChat(id="mock-weather-llm")
weather_model.invoke = mock_weather_expert_logic
# --- End Mock Model Setup ---

# 1. Define our specialist Agents
capital_city_agent = Agent(
    name="CapitalCityExpert",
    model=capital_model,
    instructions="You are an expert on capital cities."
)

weather_agent = Agent(
    name="WeatherExpert",
    model=weather_model,
    instructions="You are an expert on weather conditions."
)

print("Specialist agents defined!")
```
In this snippet:
*   We've created two functions, `mock_capital_city_expert_logic` and `mock_weather_expert_logic`, to simulate how real AI models might respond for these specialized agents.
*   We then create `capital_city_agent` and `weather_agent`, each with its own mock model and instructions.

**Step 2: Create the Team**

Now, let's assemble these [Agent](02_agent_.md)s into a `Team`. Our `Team` will also need its own "brain" ([Model](05_model_.md)) to decide which agent to route the task to. We'll mock this brain too.

```python
# team_example.py (continued)
from agno.team.team import Team

# --- Mock Model for the Team's Routing Logic ---
def mock_team_router_logic(messages, tools=None, **kwargs) -> Message:
    # The team's model looks at the user's message to decide routing.
    # The 'messages' here will include a system message describing the agents.
    user_query = ""
    # Find the latest user message. The actual prompt is more complex.
    for m in reversed(messages):
        if m.role == "user":
            user_query = m.content.lower()
            break
    
    # This is a simplified routing decision.
    # In reality, the Team's LLM chooses from a list of 'tools'
    # representing each agent.
    if "capital" in user_query or "france" in user_query:
        # "Choose" the capital_city_agent
        # The real LLM would return a tool_call for "transfer_task" to "capitalcityexpert"
        return Message(role="assistant", content="Routing to CapitalCityExpert.",
                       tool_calls=[{"id": "call_1", "type": "function",
                                    "function": {"name": "transfer_task", 
                                                 "arguments": '{"member_id": "capitalcityexpert", "task_description": "'+user_query+'"}'}}])
    elif "weather" in user_query or "london" in user_query:
        # "Choose" the weather_agent
        return Message(role="assistant", content="Routing to WeatherExpert.",
                       tool_calls=[{"id": "call_2", "type": "function",
                                    "function": {"name": "transfer_task",
                                                 "arguments": '{"member_id": "weatherexpert", "task_description": "'+user_query+'"}'}}])
    return Message(role="assistant", content="I'm not sure who can handle that.")

team_model = OpenAIChat(id="mock-team-router-llm")
team_model.invoke = mock_team_router_logic
# --- End Mock Team Model ---

# 2. Create the Team in "route" mode
expert_team = Team(
    name="ExpertRouterTeam",
    mode="route",  # Key setting!
    model=team_model, # The Team's own brain for routing
    members=[capital_city_agent, weather_agent] # Our specialist agents
)

print(f"Team '{expert_team.name}' created with mode '{expert_team.mode}'.")
```
Here:
*   `mock_team_router_logic`: This function simulates the `Team`'s [Model](05_model_.md) deciding which agent is best. It looks for keywords in the user's query. A real LLM would make a more sophisticated choice based on the descriptions of the member agents (their `name`, `instructions`, `tools`, etc.).
*   `Team(...)`:
    *   `name`: "ExpertRouterTeam".
    *   `mode="route"`: Tells the `Team` to act as a router.
    *   `model=team_model`: We assign our mock routing brain to the `Team`.
    *   `members=[...]`: We pass the list of [Agent](02_agent_.md)s that are part of this team. Note that `agno` will automatically generate `agent_id`s like "capitalcityexpert" and "weatherexpert" based on their names if not provided explicitly.

**Step 3: Run the Team and See it in Action!**

Let's ask our `Team` some questions and see how it routes them.

```python
# team_example.py (continued)

# Question for the CapitalCityExpert
query1 = "What is the capital of France?"
print(f"\nUser: {query1}")
response1 = expert_team.run(query1)
if response1 and response1.content:
    print(f"{expert_team.name} (via {response1.member_responses[0].agent_id if response1.member_responses else 'N/A'}): {response1.content}")

# Question for the WeatherExpert
query2 = "What's the weather like in London?"
print(f"\nUser: {query2}")
response2 = expert_team.run(query2)
if response2 and response2.content:
    print(f"{expert_team.name} (via {response2.member_responses[0].agent_id if response2.member_responses else 'N/A'}): {response2.content}")
```

If you run this entire `team_example.py` script, you should see output similar to this:

```
Specialist agents defined!
Team 'ExpertRouterTeam' created with mode 'route'.

User: What is the capital of France?
ExpertRouterTeam (via capitalcityexpert): The capital of France is Paris!

User: What's the weather like in London?
ExpertRouterTeam (via weatherexpert): It's probably drizzling in London!
```
Success!
*   When we asked about the capital of France, the `Team` (using its mock routing logic) decided that `capital_city_agent` was the right [Agent](02_agent_.md) and routed the task there. The response content comes from `capital_city_agent`.
*   When we asked about the weather in London, the task was routed to `weather_agent`.

The `response1` and `response2` objects are instances of `TeamRunResponse`. This object contains the final answer (`response.content`) and also information about which member [Agent](02_agent_.md)s were involved (`response.member_responses`). We'll learn more about [RunResponse & Message](04_runresponse___message_.md) (which `TeamRunResponse` builds upon) in the next chapter.

## How Does "Route" Mode Work Under the Hood?

When you call `expert_team.run("Your question")` in `route` mode, several things happen:

1.  **Receive Task**: The `Team` gets your message.
2.  **Prepare for Routing**: The `Team` needs to tell its own [Model](05_model_.md) (the `team_model` we gave it) about the task and the available specialists. It creates a detailed prompt that includes:
    *   The user's current message/task.
    *   A description of each member [Agent](02_agent_.md) – their name, role/instructions, and any tools they might have. The `Team` has a method, conceptually like `get_members_system_message_content()`, to generate this part of the prompt. You can see this in action in `test_team.py` where `team.get_members_system_message_content()` is tested.
3.  **Routing Decision**: The `Team`'s [Model](05_model_.md) processes this prompt. It analyzes the task and the profiles of the member [Agent](02_agent_.md)s. It then decides which agent (or agents, in more complex scenarios) is best suited. The model typically indicates its choice by asking to use a special "tool" called `transfer_task`, specifying the `member_id` of the chosen agent.
4.  **Task Delegation**: The `Team` receives this decision and "transfers" or delegates the original task to the selected [Agent](02_agent_.md).
5.  **Agent Execution**: The chosen [Agent](02_agent_.md) (e.g., `capital_city_agent`) now processes the task just like we learned in [Chapter 2: Agent](02_agent_.md). It uses its own [Model](05_model_.md), instructions, etc., to generate a response.
6.  **Collect Response**: The `Team` gets the [RunResponse & Message](04_runresponse___message_.md) back from the member [Agent](02_agent_.md).
7.  **Final Output**: The `Team` packages this into a `TeamRunResponse`. The `content` of this `TeamRunResponse` is usually the content from the selected agent's response. It also includes details about which agent(s) ran.

Here's a simplified diagram of this flow:

```mermaid
sequenceDiagram
    participant User
    participant ExpertTeam as Team (Router)
    participant TeamLLM as Model (Team's Brain)
    participant CapitalAgent as Member Agent 1
    participant WeatherAgent as Member Agent 2

    User->>ExpertTeam: run("Capital of France?")
    ExpertTeam->>ExpertTeam: Prepare prompt with agent profiles
    ExpertTeam->>TeamLLM: Analyze task & select agent (Task: "Capital of France?", Agent Profiles)
    TeamLLM-->>ExpertTeam: Decision: Use 'transfer_task' to CapitalAgent
    ExpertTeam->>CapitalAgent: run("Capital of France?")
    CapitalAgent->>CapitalAgent: Processes task (uses its own LLM)
    CapitalAgent-->>ExpertTeam: AgentResponse ("Paris!")
    ExpertTeam-->>User: TeamRunResponse (content="Paris!", member_ran=CapitalAgent)
end
```

The actual implementation within `agno.team.team.Team` involves methods that prepare prompts for the team's LLM, including system messages detailing the capabilities of each member agent. The LLM is then expected to output a call to a predefined tool (like `transfer_task` or `forward_task`, see `test_team.py`) to indicate which member should handle the task.

For example, the `Team` constructs a system message for its LLM that might look conceptually like this (simplified from `get_members_system_message_content` in `test_team.py`):

```
You are a routing assistant. Your job is to route the user's task to the correct agent.
Here are the available agents:

Agent 1:
ID: capitalcityexpert
Name: CapitalCityExpert
Role: You are an expert on capital cities.
Tools: (any tools the agent might have)

Agent 2:
ID: weatherexpert
Name: WeatherExpert
Role: You are an expert on weather conditions.
Tools: (any tools the agent might have)

Based on the user's query, decide which agent is most appropriate by calling the 'transfer_task' function with the chosen agent's ID.
```
The `Team`'s [Model](05_model_.md) uses this information to make an informed routing decision.

## Other Team Modes: A Quick Peek

While we focused on `route` mode, `agno` also supports other modes like `collaborate`. In `collaborate` mode, multiple agents might contribute to a task. For instance, one agent might draft an introduction, another might write the main body, and a third might summarize. The `Team` would then manage this collaborative workflow. This is more advanced and often used for complex problem-solving where diverse expertise needs to be pooled and synthesized.

Tests like `test_structured_output.py` show how teams can even ensure that different agents within a team return responses in specific Pydantic model formats, adding another layer of control. Furthermore, as seen in `test_team_with_storage_and_memory.py`, `Team`s can also have their own [Storage](10_storage_.md) and [Memory](07_memory_.md) to persist session information and remember interactions across turns, just like individual [Agent](02_agent_.md)s.

## When Should You Use a Team?

*   **Specialized Tasks**: When you have distinct tasks that are best handled by specialized [Agent](02_agent_.md)s (like our capital city vs. weather example).
*   **Complex Workflows**: When a problem requires multiple steps or different types of processing that can be broken down and assigned to different [Agent](02_agent_.md)s.
*   **Modularity**: To build more organized and maintainable AI systems. Each [Agent](02_agent_.md) can be developed and tested independently.
*   **Scalability**: As your application grows, you can add more specialized [Agent](02_agent_.md)s to a `Team` without drastically overhauling existing components.

## Conclusion

You've now learned how to create a `Team` of [Agent](02_agent_.md)s in `agno`! You saw how a `Team` in `route` mode can act as an intelligent dispatcher, analyzing a user's request and sending it to the most appropriate specialist [Agent](02_agent_.md). This "project manager" approach allows you to build more powerful and organized AI applications by combining the strengths of multiple [Agent](02_agent_.md)s.

When an [Agent](02_agent_.md) (or a `Team` via an agent) runs and produces a result, it does so using specific data structures. In the next chapter, we'll take a closer look at these structures that carry the conversation and results.

Next up: [Chapter 4: RunResponse & Message](04_runresponse___message_.md)

---

Generated by [AI Codebase Knowledge Builder](https://github.com/The-Pocket/Tutorial-Codebase-Knowledge)