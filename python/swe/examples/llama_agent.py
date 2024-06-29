from examples.prompts import ISSUE_DESC_TMPL
from composio_swe.agents.base import BaseSWEAgent, SWEArgs
from examples.my_agent import generate_launcher_service
from composio_swe.config.store import IssueConfig
import os
from composio_llamaindex import ComposioToolSet, Action

tool_set = ComposioToolSet()


class LlamaIndexAgent(BaseSWEAgent):

    def __init__(self, args: SWEArgs):
        super().__init__(args)

    def solve(self, workspace_id: str, issue_config: IssueConfig):
        # store workspace_id in env
        os.environ["COMPOSIO_WORKSPACE_ID"] = workspace_id

        repo_name = issue_config.repo_name
        if not repo_name:
            raise ValueError("no repo-name configuration is found")
        if not issue_config.issue_id:
            raise ValueError("no git-issue configuration is found")

        repo_name_dir = "/" + repo_name.split("/")[-1].strip()

        issue_added_instruction = ISSUE_DESC_TMPL.format(
            issue=issue_config.issue_desc, issue_id=issue_config.issue_id
        )

        agent = generate_launcher_service()

        prefix_task = f"""The git repo is cloned in the dir,
        '{repo_name_dir}', you need to work in this directory."""
        task = f"{prefix_task}, {issue_added_instruction}, Expected outcome: The files should be modified to solve for the issue."
        print("Tasks: ", task)

        response = agent.chat(task)

        self.logger.info("Agent response: %s", response)

        # tool_set.execute_action(
        #     action=Action.SUBMITPATCHTOOL_SUBMITPATCH,
        #     params={},
        #     entity_id="melissa",
        # )
        self.current_logs.append(
            {"agent_action": "agent_finish", "agent_output": str(response)}
        )
