import dotenv
import logging

from examples.prompts import AGENT_BACKSTORY_TMPL
from composio_swe.agents.utils import get_llama_llm
from llama_index.core.agent import FunctionCallingAgentWorker, StructuredPlannerAgent
from llama_index.core.llms import ChatMessage, MessageRole
from llama_index.llms.openai import OpenAI
from llama_agents import (
    LocalLauncher,
    AgentService,
    ControlPlaneServer,
    SimpleMessageQueue,
    AgentOrchestrator,
)
from composio_llamaindex import ComposioToolSet, Action, App


# Load environment variables
dotenv.load_dotenv()

# Initialize logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("llama_agents")

# Initialize LLM and message queue
llm = get_llama_llm()
message_queue = SimpleMessageQueue()

# Initialize control plane
control_plane = ControlPlaneServer(
    message_queue=message_queue,
    orchestrator=AgentOrchestrator(llm=OpenAI()),
)


def generate_launcher_service():
    # Initialize toolset and tools
    toolset = ComposioToolSet()
    tools = [
        *toolset.get_tools(apps=[App.CMDMANAGERTOOL, App.HISTORYKEEPER]),
    ]

    # Generate backstory with instructions
    backstory_added_instruction = AGENT_BACKSTORY_TMPL

    # Create prefix messages
    prefix_messages = [
        ChatMessage(
            role=MessageRole.SYSTEM,
            content=backstory_added_instruction,
        )
    ]

    # Initialize agent
    agent_worker = FunctionCallingAgentWorker(
        tools=tools,
        llm=llm,
        prefix_messages=prefix_messages,
        max_function_calls=10,
        allow_parallel_tool_calls=False,
        verbose=True,
    )
    agent = StructuredPlannerAgent(agent_worker=agent_worker, tools=tools, llm=llm)
    # Create agent service
    # agent_service = AgentService(
    #     agent=agent,
    #     message_queue=message_queue,
    #     description="General purpose assistant",
    #     service_name="assistant",
    # )

    # # Initialize local launcher
    # launcher = LocalLauncher(
    #     services=[agent_service],
    #     control_plane=control_plane,
    #     message_queue=message_queue,
    # )

    return agent
