from agent import AgentContext
from agent_zero_lite.python.helpers.defer import DeferredTask
from agent_zero_lite.python.api.message import Message


class MessageAsync(Message):
    async def respond(self, task: DeferredTask, context: AgentContext):
        return {
            "message": "Message received.",
            "context": context.id,
        }
