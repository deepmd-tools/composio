import os
import dotenv
from crewai import Agent, Task, Crew
from langchain_openai import ChatOpenAI
from composio_crewai import ComposioToolSet
from composio import App

# Load environment variables
dotenv.load_dotenv()

# Initialize OpenAI client
llm = ChatOpenAI(model="gpt-4-turbo")

# Initialize Composio tools
composio_toolset = ComposioToolSet()
productivity_tools = composio_toolset.get_tools([App.SYSTEMTOOLS, App.IMAGEANALYSERTOOL])

# Define the Productivity Assistant Agent
productivity_assistant = Agent(
    role="Productivity Assistant",
    goal="Monitor user activity and provide timely, helpful interventions to enhance productivity",
    backstory="""You are an intelligent and proactive personal productivity assistant. 
    Your job is to analyze screenshots, monitor user activity, and provide helpful interventions.""",
    verbose=True,
    allow_delegation=False,
    tools=productivity_tools,
    llm=llm
)

# Define the Productivity Monitoring Task
productivity_task = Task(
    description="""
    1. Take a screenshot using the screenshot tool.
    2. Analyze the screenshot using the image analyzer tool.
    3. Check if the user is facing a technical or workflow problem, based on previous history.
    4. If they are, notify them with concise, actionable solutions. You don't need to notify them if you don't have something meaningful to say.
    5. Maintain a history of the user's activity and notify them if they are doing something that is not productive.

    Repeat this process every few seconds.
    """,
    agent=productivity_assistant,
    expected_output="A summary of the user's activity and any issues they are facing, or suggestions for improvement."
)

# Create the Crew
productivity_crew = Crew(
    agents=[productivity_assistant],
    tasks=[productivity_task],
    verbose=10,
    cache=False
)

# Main loop
while True:
    result = productivity_crew.kickoff()
    print(result)
