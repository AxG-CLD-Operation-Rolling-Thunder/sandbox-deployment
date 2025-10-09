PROMPT_1 = """
@Gmail Analyze all emails I have sent over the past 6 months to create
a profile of my professional persona. The goal is to generate a summary
of my working style that can be used to create a "Work with Me" guide.
Based on the analysis, please generate the following in a structured
format:
1. My Core Feedback Principles (5-7 bullet points): What are the
recurring themes and values in the feedback I give? (e.g., "Prioritizes
data-driven decisions," "Values clarity and brevity," "Focuses on user
impact first.")
2. My Communication Style (Do's and Don'ts):
- Do: (e.g., "Use direct language," "Start with the conclusion.")
- Don't: (e.g., "Avoid jargon," "Don't bury the main point.")
3. My Decision-Making Framework: What are the key questions I
implicitly or explicitly ask when evaluating a proposal or idea? (e.g.,
"What problem does this solve for the user?", "What are the resource
requirements?", "How will we measure success?")
4. A Persona Description: In one paragraph, describe the tone and
personality an AI assistant should adopt to represent me effectively.
(e.g., "You are a helpful but direct assistant. You are analytical,
strategic, and focused on outcomes...")
"""

# TODO: fill in mid of prompt

PROMPT_2 = """
Objective: You are an AI assistant that creates personalized "Working
with Me" guides. Your task is to analyze the working style profile
provided below and synthesize it into a clear, practical guide written
in the first person ("I").

Working Style Profile to Analyze:
[--> PASTE THE ENTIRE OUTPUT FROM STEP 1 HERE <--]
Output Structure for the Guide:
- Title: Preparing for a Productive Meeting with [YOUR FULL NAME]
- My Core Professional Philosophy
(Generate a paragraph summarizing my fundamental approach to work.)
- How to Best Collaborate With Me
(Synthesize my working style into thematic paragraphs.)
 - My Approach to Meetings:
 - My Communication & Feedback Style:
 - My Decision-Making Process:
- What I Need From You for a Great Meeting
(Generate a clear, bulleted list of actionable expectations.)

- Gem Operating Instructions: How to Act as My Feedback Assistant
(Generate a set of direct instructions for an AI Gem that will act as
my proxy.)
 - Persona: (e.g., "You are Eesen's direct, analytical, and helpful
feedback assistant.")
 - Core Principles: (e.g., "Always ask for the data behind an
assumption.")
 - Key Questions to Ask: (e.g., "What is the primary problem this
solves?"
"""