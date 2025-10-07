from google.adk.tools import ToolContext
from brief_creator import create_agent_brief_doc, AgentBrief

INTAKE_FIELDS = [
    "Agent Overview",
    "Vision",
    "Problem Statement",
    "Target Users",
    "Key Features",
    "Success Metrics",
    "Dependencies or Constraints"
]

def agent_brief_tool(tool_context: ToolContext):
    st = tool_context.state

    # Initialize intake state
    if "agent_inputs" not in st:
        st["agent_inputs"] = {}
        st["current_field_index"] = 0
        tool_context.send("Let's build your agent idea into a structured brief. I'll ask you a few questions.")
        tool_context.send(f"{INTAKE_FIELDS[0]}:")
        st["current_field_index"] += 1
        return

    # Store user response
    agent_inputs = st["agent_inputs"]
    current_index = st["current_field_index"]

    if tool_context.last_user_message:
        last_field = INTAKE_FIELDS[current_index - 1]
        agent_inputs[last_field] = tool_context.last_user_message.strip() or "To Be Added"

    # If all fields are collected, generate the brief
    if current_index >= len(INTAKE_FIELDS):
        tool_context.send("Thanks! Generating your agent brief now…")

        agent_data = AgentBrief(
            agent_overview=agent_inputs.get("Agent Overview", "To Be Added"),
            vision=agent_inputs.get("Vision", "To Be Added"),
            problem_statement=agent_inputs.get("Problem Statement", "To Be Added"),
            target_users=agent_inputs.get("Target Users", "To Be Added"),
            key_features=agent_inputs.get("Key Features", "To Be Added"),
            success_metrics=agent_inputs.get("Success Metrics", "To Be Added"),
            dependencies_or_constraints=agent_inputs.get("Dependencies or Constraints", "To Be Added")
        )

        doc_buffer = create_agent_brief_doc(agent_data)
        doc_buffer.seek(0)

        st["agent_brief_doc"] = doc_buffer
        st["agent_brief_filename"] = "Agent_Brief.docx"

        tool_context.send("✅ Your agent brief is ready. You can now download the document below.")
        return

    # Ask next question
    next_field = INTAKE_FIELDS[current_index]
    tool_context.send(f"{next_field}:")
    st["current_field_index"] += 1
