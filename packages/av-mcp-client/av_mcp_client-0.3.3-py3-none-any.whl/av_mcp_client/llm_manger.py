import os
import logging
from re import A
from token import OP
from dotenv import load_dotenv
from typing import Union, List, Callable, Dict, Any

# Optional: LangChain imports for supported LLMs and tools

# Token counting utility
import tiktoken
from typing import Optional, List
from google.genai import Client as GeminiClient, types as gemini_types
from pydantic import BaseModel as PydanticBaseModel
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_openai import ChatOpenAI
from mcp.types import Tool
from langchain.tools import StructuredTool
from langchain_core.messages import AIMessage, BaseMessage

# The client gets the API key from the environment variable `GEMINI_API_KEY`.


load_dotenv()





class LLM:
    def __init__(self, api_key=None, model_name=None, **kwargs):
        self.api_key = api_key
        self.model_name = model_name
        self.kwargs = kwargs
        self.llm= None
        
    
    def register_tools(self, tools: List[Tool]):
        available_tools = [StructuredTool(
        name=tool.name,
        description=tool.description or "",
        args_schema=tool.inputSchema,
    )
      for tool in tools]
        self.llm = self.llm.bind_tools(available_tools) # type: ignore

    
    def register_llm(self):
        raise NotImplementedError("Subclasses should implement this method.")

    def generate_response(self):
        raise NotImplementedError("Subclasses should implement this method.")

    def __call__(self, messages, tools=None):
        """
        Allows the LLM instance to be called as a function.
        Calls generate_response under the hood.
        """
        raise NotImplementedError("Subclasses should implement this method.")



class Gemini_LLM(LLM):
    def __init__(self, api_key_env_var='GEMINI_API_KEY', model="gemini-2.5-flash", **kwargs):
        api_key = os.getenv(api_key_env_var)
        super().__init__(api_key=api_key, model_name=model, **kwargs)
        self.register_llm()

    def register_llm(self):
        """
        Register the Gemini LLM with the client.
        """
        if not self.api_key:
            raise ValueError("API key is required for Gemini LLM.")
        # Here you would typically register the LLM with your framework or service
        self.llm = ChatGoogleGenerativeAI(
                google_api_key=self.api_key,
                model=self.model_name,
                temperature=0.7,
                max_retries=3,
                **self.kwargs
            )


    def generate_response(self, prompt, tools=None):
        return self.llm.invoke(prompt)
                

    def __call__(self, prompt, tools = None):
        return self.generate_response(prompt, tools)

class OpenAI_LLM(LLM):
    def __init__(self, api_key_env_var='OPENAI_API_KEY', model="gpt-4o", **kwargs):
        api_key = os.getenv(api_key_env_var)
        super().__init__(api_key=api_key, model_name=model, **kwargs)
        self.register_llm(**kwargs)

    def register_llm(self, **kwargs):
        """
        Register the Gemini LLM with the client.
        """
        if not self.api_key:
            raise ValueError("API key is required for Gemini LLM.")
        # Here you would typically register the LLM with your framework or service
        self.llm = ChatOpenAI(
            model=self.model_name, # type: ignore
            api_key=self.api_key,
            **self.kwargs
        )


    def generate_response(self, prompt, tools=None):
        return self.llm.invoke(prompt)
    

    def __call__(self, prompt, tools = None):
        return self.generate_response(prompt, tools)
                




class LLMManager:
    """
    Generic LLM manager for MCP clients.
    Supports OpenAI, Azure, Gemini, and custom tool registration.
    """

    def __init__(self, provider:str):
        self.tools: Dict[str, Dict[str, Any]] = {}
        self.memory = None  # Optional: for conversational agents
        self.create_llm(provider)

    def create_llm(self, provider: str, **kwargs):
        """
        Initialize the LLM instance for the given provider.
        Supported providers: 'openai', 'azure', 'gemini'
        """

        llm_classes = {
            "openai": OpenAI_LLM,
            "gemini": Gemini_LLM
        }

        if provider not in llm_classes:
            raise ValueError(f"Unsupported LLM type: {provider}")

        self.llm_instance = llm_classes[provider](**kwargs)
        return self.llm_instance 
    
    def get_llm_instance(self):
        return self.llm_instance

    def register_tools(self, tools: list[Tool]):
        """
        Register a tool for use with the LLM agent.
        """
        self.llm_instance.register_tools(tools)

    def list_tools(self) -> List[Dict[str, Any]]:
        """
        List all registered tools with their metadata.
        """
        return [
            {
                "name": name,
                "description": meta["description"],
                "input_schema": meta["input_schema"]
            }
            for name, meta in self.tools.items()
        ]

    def invoke_tool(self, name: str, **kwargs):
        """
        Invoke a registered tool by name with provided arguments.
        """
        if name not in self.tools:
            raise ValueError(f"Tool '{name}' not registered.")
        return self.tools[name]["func"](**kwargs)

    def get_response(self, prompt: List[BaseMessage] | str)-> AIMessage:
        """
        Call the LLM with a string or list of messages.
        Returns the LLM response and logs token usage.
        """
        input_tokens = self._count_tokens(prompt)
        print(f"Input tokens: {input_tokens}")
        response = self.llm_instance(prompt)

        output_tokens = self._count_tokens([response])
        print(f"Output tokens: {output_tokens}")

        # Optional: log token usage to DB or file
        # log_tokens(input_tokens, output_tokens)

        return response

    def _count_tokens(self, messages: Union[str, List[Any]], model: str = "gpt-4o-mini") -> int:
        """
        Count tokens for a string or list of messages.
        """
        try:
            encoding = tiktoken.encoding_for_model(model)
            if isinstance(messages, str):
                return len(encoding.encode(messages))
            elif isinstance(messages, list):
                # Concatenate all messages into a single string
                final_string = "\n".join(str(m) for m in messages)
                return len(encoding.encode(final_string))
            else:
                raise ValueError("messages must be a string or a list")
        except Exception as e:
            print(f"Token counting error: {e}")
            return 0

