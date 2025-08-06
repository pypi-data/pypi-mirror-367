from agent_zero_lite.python.helpers import persist_chat, tokens
from agent_zero_lite.python.helpers.extension import Extension
from agent_zero_lite.agent import LoopData
import asyncio
from agent_zero_lite.python.helpers.log import LogItem
from agent_zero_lite.python.helpers import log
import math


class LogForStream(Extension):

    async def execute(self, loop_data: LoopData = LoopData(), text: str = "", **kwargs):
        # create log message and store it in loop data temporary params
        if "log_item_generating" not in loop_data.params_temporary:
            loop_data.params_temporary["log_item_generating"] = (
                self.agent.context.log.log(
                    type="agent",
                    heading=build_default_heading(self.agent),
                )
            )

def build_heading(agent, text: str):
    return f"icon://network_intelligence {agent.agent_name}: {text}"

def build_default_heading(agent):
    return build_heading(agent, "Generating...") 