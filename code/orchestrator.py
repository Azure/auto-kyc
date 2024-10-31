import asyncio
import copy
from semantic_kernel import Kernel
from semantic_kernel.connectors.ai.open_ai import AzureChatCompletion
from semantic_kernel.connectors.ai.function_choice_behavior import FunctionChoiceBehavior
from semantic_kernel.connectors.ai.chat_completion_client_base import ChatCompletionClientBase
from semantic_kernel.contents.chat_history import ChatHistory
from semantic_kernel.contents.utils.author_role import AuthorRole
from semantic_kernel.functions.kernel_arguments import KernelArguments
from semantic_kernel.core_plugins import MathPlugin
from semantic_kernel.connectors.ai.open_ai.prompt_execution_settings.azure_chat_prompt_execution_settings import (
    AzureChatPromptExecutionSettings,
)
from semantic_kernel.contents.function_result_content import FunctionResultContent
from semantic_kernel.filters.prompts.prompt_render_context import PromptRenderContext

from semantic_kernel.filters.filter_types import FilterTypes
from semantic_kernel.filters.auto_function_invocation.auto_function_invocation_context import (
    AutoFunctionInvocationContext,
)
from semantic_kernel.functions.function_result import FunctionResult


import time

from typing import List, Optional, Annotated
from typing import TypedDict, Optional
import copy
from env_vars import *
from utils.openai_helpers import *
from utils.general_helpers import *


from utils.base_logger import BaseLogger


module_directory = os.path.dirname(os.path.abspath(__file__))



class Orchestrator(BaseLogger):

    def __init__(self, messages = None,  work_dir=WORK_DIR) -> None:
        super().__init__()
        # 1. Create the kernel with the Lights plugin
        service_id="chat-gpt"
        self.work_dir = work_dir

        # Create a history of the conversation
        self.history = ChatHistory()

        orchestrator_system_prompt = read_file(os.path.join(module_directory, 'prompts/orchestrator_system_prompt.txt'))
        self.history.add_message(
            ChatMessageContent(
                role = AuthorRole.SYSTEM, 
                content = orchestrator_system_prompt.format()
            )
        )


        self.logged_messages = []

        if messages is not None:
            self.build_chat_history(messages)


        self.plugins = []

        self.kernel = Kernel()
        self.kernel.add_service(AzureChatCompletion(
            deployment_name=AZURE_OPENAI_MODEL,
            api_key=AZURE_OPENAI_KEY,
            endpoint=f"https://{os.getenv('AZURE_OPENAI_RESOURCE')}.openai.azure.com/",
            service_id=service_id
        ))

        self.kernel.add_plugin(MathPlugin(), plugin_name="math")

        self.kernel.add_plugin(
            self.aca_workflow,
            plugin_name="DockerDeploymentToACA",
            description=self.aca_workflow.description,
        )


        self.chat_completion : AzureChatCompletion = self.kernel.get_service(type=ChatCompletionClientBase)

        # FunctionChoiceBehavior.Auto(filters={"included_plugins": ["math", "time"]})
        self.execution_settings = AzureChatPromptExecutionSettings(tool_choice="auto")
        self.execution_settings.function_choice_behavior = FunctionChoiceBehavior.Auto()

        @self.kernel.filter(FilterTypes.AUTO_FUNCTION_INVOCATION)
        async def auto_function_invocation_filter(context: AutoFunctionInvocationContext, next):

            """A filter that will be called for each function call in the response."""
            

            self.custom_print(60*"-")
            self.custom_print("**Automatic Function Call**")
            self.custom_print("Plugin:", context.function.plugin_name )
            self.custom_print(f"Function: {context.function.name}")
            self.custom_print("Function Arguments", context.arguments)            
            # result = context.function_result
            self.custom_print(60*"-")

            await next(context)



    def build_chat_history(self, messages):
        for m in messages:
            self.history.add_message(
                ChatMessageContent(
                    role = AuthorRole.SYSTEM if m['role'] == "system" else (AuthorRole.USER if m['role'] == "user" else AuthorRole.ASSISTANT),
                    content = m['content']
                )
            )


    def collect_logged_messages(self):
        self.logged_messages = []

        for p in self.plugins:
            if hasattr(p, 'logged_messages'):
                self.logged_messages.extend(copy.deepcopy(p.logged_messages))
                p.logged_messages = []



    async def chat(self, query, connection = None):
        self.interaction_counter = 0

        # Terminate the loop if the user says "exit"
        if query == "exit":
            return "Goodbye!", self.logged_messages

        # Add user input to the history
        self.history.add_user_message(query)


        result = (await self.chat_completion.get_chat_message_contents(
            chat_history=self.history,
            settings=self.execution_settings,
            kernel=self.kernel,
            arguments=KernelArguments(),
            temperature=0.2
        ))[0]


        # Print the results
        print("Assistant > " + str(result))

        # Add the message from the agent to the chat history
        self.history.add_message(result)

        self.collect_logged_messages()

        # Share final results
        return str(result), self.logged_messages