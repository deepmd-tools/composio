from composio_langchain import ComposioToolSet,App, Action
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from tool import image,video,convert
from langchain_core.messages import HumanMessage
from langgraph.prebuilt import create_react_agent
import os

load_dotenv()

composio_toolset = ComposioToolSet(api_key=os.environ["COMPOSIO_API_KEY"])
tools = composio_toolset.get_actions(actions=[image,video,convert])
llm = ChatOpenAI(model="gpt-4o")


agent_executor = create_react_agent(llm, tools)

input_task=input("Enter your prompt")
prompt = f"""
create a compelling 60-second advertisement storyboard on {input_task}, use convert tool to convert image from webp to png format
including a script and 1 visual prompt for an image generation tool.
Once the image is generated execute the video tool on it with the script. save the image as a png.
Save the video as mp4
"""
response = agent_executor.invoke({"messages": [HumanMessage(content=prompt)]})
print(response)