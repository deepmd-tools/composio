"""CrewAI SWE Agent"""

import os
import typing as t

import dotenv
from composio_crewai import Action, App, ComposioToolSet, ExecEnv
from crewai import Agent, Crew, Process, Task
from langchain_anthropic import ChatAnthropic
from langchain_openai import AzureChatOpenAI, ChatOpenAI
from prompts import (
    BACKSTORY,
    CODE_AND_TEST_TMPL,
    DESIGN_TEST_TMPL,
    EXPECTED_FINAL_OUTPUT,
    GOAL,
    REPO_UNDERSTANDING_AND_HYPOTHESIS_TMPL,
    ROLE,
)


# Load environment variables from .env
dotenv.load_dotenv()


# Initialize tool.
def get_langchain_llm() -> t.Union[ChatOpenAI, AzureChatOpenAI, ChatAnthropic]:
    helicone_api_key = os.environ.get("HELICONE_API_KEY")
    if os.environ.get("ANTHROPIC_API_KEY"):
        if helicone_api_key:
            print("Using Anthropic with Helicone")
            return ChatAnthropic(
                model_name="claude-3-5-sonnet-20240620",
                anthropic_api_url="https://anthropic.helicone.ai/",
                default_headers={
                    "Helicone-Auth": f"Bearer {helicone_api_key}",
                },
            )  # type: ignore
        print("Using Anthropic without Helicone")
        return ChatAnthropic(model_name="claude-3-5-sonnet-20240620")  # type: ignore
    if os.environ.get("OPENAI_API_KEY"):
        if helicone_api_key:
            print("Using OpenAI with Helicone")
            return ChatOpenAI(
                model="gpt-4-turbo",
                base_url="https://oai.helicone.ai/v1",
                default_headers={
                    "Helicone-Auth": f"Bearer {helicone_api_key}",
                },
            )
        print("Using OpenAI without Helicone")
        return ChatOpenAI(model="gpt-4-turbo")
    if os.environ.get("AZURE_OPENAI_API_KEY"):
        print("Using Azure OpenAI")
        return AzureChatOpenAI(model="test")

    raise RuntimeError(
        "Could not find API key for any supported LLM models, "
        "please export either `ANTHROPIC_API_KEY`, `OPENAI_API_KEY` "
        "or `AZURE_OPENAI_API_KEY`"
    )


composio_toolset = ComposioToolSet(workspace_env=ExecEnv.DOCKER)

# Get required tools

repo_read_tool = [
    *composio_toolset.get_actions(
        actions=[
            Action.GITCMDTOOL_GIT_REPO_TREE,
            Action.FILEEDITTOOL_OPEN_FILE,
            Action.FILEEDITTOOL_SCROLL,
        ]
    ),
    *composio_toolset.get_tools(
        apps=[
            App.SEARCHTOOL,
        ]
    ),
]

repo_understanding_tool = [
    *repo_read_tool,
    *composio_toolset.get_actions(
        actions=[
            Action.GITCMDTOOL_GITHUB_CLONE_CMD,
        ]
    ),
]

test_design_tool = [
    *repo_read_tool,
    *composio_toolset.get_actions(
        actions=[
            Action.FILEEDITTOOL_CREATE_FILE_CMD,
            Action.FILEEDITTOOL_EDIT_FILE,
        ]
    ),
]

code_and_test_tool = [
    *test_design_tool,
    *composio_toolset.get_actions(
        actions=[
            Action.GITCMDTOOL_GET_PATCH_CMD,
        ]
    ),
]

# Define agent
try:
    agent = Agent(
        role=ROLE,
        goal=GOAL,
        backstory=BACKSTORY,
        llm=get_langchain_llm(),
        verbose=True,
    )
except Exception as e:
    print(e)
    raise e


repo_understanding_task = Task(
    description=REPO_UNDERSTANDING_AND_HYPOTHESIS_TMPL,
    expected_output="""Understanding of the repository structure. Hypothesis around the solution.
    Files that are relevant to the issue. Test plan.
    """,
    agent=agent,
    tools=repo_understanding_tool,
    # output_pydantic=RepUnderstandingOutput,
)

test_design_task = Task(
    description=DESIGN_TEST_TMPL,
    expected_output="A test/script to check if the issue has been fixed.",
    agent=agent,
    tools=test_design_tool,
    context=[repo_understanding_task],
)

code_and_test_task = Task(
    description=CODE_AND_TEST_TMPL,
    expected_output=EXPECTED_FINAL_OUTPUT,
    agent=agent,
    tools=code_and_test_tool,
    context=[repo_understanding_task, test_design_task],
)

crew = Crew(
    agents=[agent],
    tasks=[repo_understanding_task, test_design_task, code_and_test_task],
    process=Process.sequential,
    full_output=True,
    verbose=True,
    cache=False,
    memory=True,
)
