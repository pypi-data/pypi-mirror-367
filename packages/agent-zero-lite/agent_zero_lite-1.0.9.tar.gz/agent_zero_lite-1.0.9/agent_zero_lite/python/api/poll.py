from agent_zero_lite.python.helpers.api import ApiHandler, Request, Response

from agent_zero_lite.agent import AgentContext

from agent_zero_lite.python.helpers.localization import Localization
from agent_zero_lite.python.helpers.dotenv import get_dotenv_value


class Poll(ApiHandler):

    @classmethod
    def requires_auth(cls) -> bool:
        return False

    async def process(self, input: dict, request: Request) -> dict | Response:
        ctxid = input.get("context", "")
        from_no = input.get("log_from", 0)
        notifications_from = input.get("notifications_from", 0)

        # Get timezone from input (default to dotenv default or UTC if not provided)
        timezone = input.get("timezone", get_dotenv_value("DEFAULT_USER_TIMEZONE", "UTC"))
        Localization.get().set_timezone(timezone)

        # context instance - get or create
        context = self.get_context(ctxid)

        logs = context.log.output(start=from_no)

        # Simplified notifications for Lite version
        notifications = []  # No notifications in lite version

        # loop AgentContext._contexts

        # Get a task scheduler instance
        # scheduler = TaskScheduler.get()

        # Always reload the scheduler on each poll to ensure we have the latest task state
        # await scheduler.reload() # does not seem to be needed

        # loop AgentContext._contexts and divide into contexts and tasks

        ctxs = []
        tasks = []
        processed_contexts = set()  # Track processed context IDs

        all_ctxs = list(AgentContext._contexts.values())
        # First, identify all tasks
        for ctx in all_ctxs:
            # Skip if already processed
            if ctx.id in processed_contexts:
                continue

            # Create the base context data that will be returned
            context_data = ctx.serialize()

            context_task = None  # scheduler.get_task_by_uuid(ctx.id)
            # Determine if this is a task-dedicated context by checking if a task with this UUID exists
            is_task_context = (
                context_task is not None and context_task.context_id == ctx.id
            )

            if not is_task_context:
                ctxs.append(context_data)
            else:
                # If this is a task, get task details from the scheduler
                task_details = None # scheduler.serialize_task(ctx.id)
                if task_details:
                    # Add task details to context_data with the same field names
                    # as used in scheduler endpoints to maintain UI compatibility
                    context_data.update({
                        "task_name": task_details.get("name"),  # name is for context, task_name for the task name
                        "uuid": task_details.get("uuid"),
                        "state": task_details.get("state"),
                        "type": task_details.get("type"),
                        "system_prompt": task_details.get("system_prompt"),
                        "prompt": task_details.get("prompt"),
                        "last_run": task_details.get("last_run"),
                        "last_result": task_details.get("last_result"),
                        "attachments": task_details.get("attachments", []),
                        "context_id": task_details.get("context_id"),
                    })

                    # Add type-specific fields
                    if task_details.get("type") == "scheduled":
                        context_data["schedule"] = task_details.get("schedule")
                    elif task_details.get("type") == "planned":
                        context_data["plan"] = task_details.get("plan")
                    else:
                        context_data["token"] = task_details.get("token")

                tasks.append(context_data)

            # Mark as processed
            processed_contexts.add(ctx.id)

        # Sort tasks and chats by their creation date, descending
        ctxs.sort(key=lambda x: x["created_at"], reverse=True)
        tasks.sort(key=lambda x: x["created_at"], reverse=True)

        # data from this server
        return {
            "context": context.id,
            "contexts": ctxs,
            "tasks": tasks,
            "logs": logs,
            "log_guid": context.log.guid,
            "log_version": len(context.log.updates),
            "log_progress": context.log.progress,
            "log_progress_active": context.log.progress_active,
            "paused": context.paused,
            "notifications": notifications,
            "notifications_guid": "",
            "notifications_version": 0,
        }
