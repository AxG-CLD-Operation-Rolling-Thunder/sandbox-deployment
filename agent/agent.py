from google.adk.agents import LlmAgent
from .prompts.call_of_agents import prompting


model = "gemini-2.5-flash"


root_agent = LlmAgent(
    model = model,
    name="call_of_agents",
    description="MVP agent that finds agent names similar to input.",
    instruction=prompting,
    tools=[],
)



