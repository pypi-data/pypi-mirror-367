from agent_zero_lite.python.helpers.extension import Extension
from agent_zero_lite.agent import LoopData
from agent_zero_lite.python.helpers import persist_chat


class SaveChat(Extension):
    async def execute(self, loop_data: LoopData = LoopData(), **kwargs):
        persist_chat.save_tmp_chat(self.agent.context)