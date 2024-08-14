import typing as t

from composio.tools.local.base import Action, Tool

from .actions import CreateEvent


class Calendar(Tool):
    """
    Calendar Tools for LLM
    """

    def actions(self) -> list[t.Type[Action]]:
        return [CreateEvent]

    def triggers(self) -> list:
        return []
