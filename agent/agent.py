from google.adk.agents import LlmAgent
from .prompts.call_of_agents import prompting
from .tools.brief_creator import create_agents_brief_doc


model = "gemini-2.5-flash"


# root_agent = LlmAgent(
#     model = model,
#     name="call_of_agents",
#     description="MVP agent that finds agent names similar to input.",
#     instruction=prompting,
#     tools=[create_agents_brief_doc],
# )


root_agent = LlmAgent(
    model = model,
    name="call_of_agents",
    description="MVP agent that finds agent names similar to input.",
    instruction=prompting,
    tools=[],
)




