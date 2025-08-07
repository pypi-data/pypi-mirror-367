import os
from typing import Any, Dict, List, Optional

# Import Langchain core components
from langchain_core.language_models.chat_models import BaseChatModel
from langchain_core.messages import AIMessage, BaseMessage, HumanMessage, SystemMessage
from langchain_core.outputs import ChatGeneration, ChatResult

# Import Volcengine Ark SDK
try:
    from volcenginesdkarkruntime import Ark
except ImportError:
    raise ImportError(
        "Could not import volcenginesdkarkruntime. "
        "Please install it with `pip install volcenginesdkarkruntime`."
    )

class ChatVolcEngine(BaseChatModel):
    """
    A custom Langchain chat model for integrating Volcengine Ark large model API.
    This class is designed to be a drop-in replacement for Langchain's ChatOpenAI,
    allowing users to conduct conversations via the Volcengine Ark service.
    """

    model: str
    """The Model ID for Volcengine Ark, e.g., 'deepseek-v3-250324'."""
    ark_api_key: Optional[str] = None
    """Volcengine Ark API key. If not provided, it will try to fetch from the VOLCANO_API_KEY environment variable."""
    max_tokens: int = 4096
    """The maximum number of tokens for the model to generate in the response."""
    temperature: float = 0.7
    """Controls the randomness of the generated text. Higher values mean more randomness."""
    top_p: float = 1.0
    """Nucleus sampling parameter. The model considers tokens whose probability mass sums up to top_p."""
    client: Any = None
    """The Volcengine Ark API client instance."""

    def __init__(self, **data: Any):
        """
        Initializes the ChatVolcEngine instance.

        Args:
            **data: Keyword arguments used to set model parameters.
        """
        super().__init__(**data)
        # If API key is not provided directly, try to get it from environment variable
        if self.ark_api_key is None:
            self.ark_api_key = os.environ.get("VOLCANO_API_KEY")
        
        # Check if API key is set
        if not self.ark_api_key:
            raise ValueError(
                "Volcengine Ark API key not provided. "
                "Please provide it via the 'ark_api_key' parameter or by setting the 'VOLCANO_API_KEY' environment variable."
            )
        
        # Initialize Volcengine Ark client
        self.client = Ark(api_key=self.ark_api_key)

    @property
    def _llm_type(self) -> str:
        """
        Returns the type name of the LLM.
        """
        return "volcengine-ark-chat"

    def _generate(
        self,
        messages: List[BaseMessage],
        stop: Optional[List[str]] = None,
        **kwargs: Any,
    ) -> ChatResult:
        """
        Generates a chat response based on the provided list of messages.
        This is the core method for Langchain chat models.

        Args:
            messages: A list of chat messages, including system, human, and AI messages.
            stop: A list of strings to stop generation.
            **kwargs: Additional parameters to pass to the Volcengine Ark API.

        Returns:
            A ChatResult object containing the generated AI message.
        """
        ark_messages = []
        for msg in messages:
            if isinstance(msg, SystemMessage):
                ark_messages.append({"role": "system", "content": msg.content})
            elif isinstance(msg, HumanMessage):
                ark_messages.append({"role": "user", "content": msg.content})
            elif isinstance(msg, AIMessage):
                ark_messages.append({"role": "assistant", "content": msg.content})
            else:
                # Raise an error if an unsupported message type is encountered
                raise ValueError(f"Unsupported message type: {type(msg)}")

        try:
            # Call Volcengine Ark API
            completion = self.client.chat.completions.create(
                model=self.model,
                messages=ark_messages,
                max_tokens=self.max_tokens,
                temperature=self.temperature,
                top_p=self.top_p,
                stop=stop,
                **kwargs,
            )
            
            # Extract content from API response and convert to Langchain's AIMessage
            content = completion.choices[0].message.content
            ai_message = AIMessage(content=content)
            
            # Create ChatGeneration and ChatResult objects
            chat_generation = ChatGeneration(message=ai_message)
            return ChatResult(generations=[chat_generation])
        except Exception as e:
            # Catch and re-raise any errors that occur during the API call
            raise RuntimeError(f"Failed to call Volcengine Ark API: {e}")
