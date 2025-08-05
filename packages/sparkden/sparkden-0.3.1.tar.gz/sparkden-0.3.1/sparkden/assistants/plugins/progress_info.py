from google.adk.agents.base_agent import BaseAgent
from google.adk.agents.callback_context import CallbackContext
from google.adk.models.llm_response import LlmResponse
from google.adk.plugins.base_plugin import BasePlugin

from ..helpers import (
    reset_progress_info,
    update_progress_info,
)


class ProgressInfoPlugin(BasePlugin):
    def __init__(self):
        super().__init__(name="progress_info")

    async def before_agent_callback(
        self, *, agent: BaseAgent, callback_context: CallbackContext
    ) -> None:
        update_progress_info(callback_context, callback_context.agent_name)

    async def after_model_callback(
        self, *, callback_context: CallbackContext, llm_response: LlmResponse
    ) -> LlmResponse | None:
        reset_progress_info(callback_context)
