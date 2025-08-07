"""
LLMocal: Professional Local AI Client

A professional-grade, open-source client for running large language models
locally with complete privacy and control.

Features:
- Multiple model support (GGUF, Safetensors, etc.)
- Professional chat interface
- API server capabilities
- Model management and switching
- Performance optimization for various hardware
- Complete offline operation

Basic Usage:
    >>> import llmocal
    >>> # Quick start with default model
    >>> client = llmocal.LLMocal()
    >>> client.setup()  # Downloads model if needed
    >>> response = client.chat("Hello, how are you?")
    >>> print(response)
    
    >>> # Custom model
    >>> client = llmocal.LLMocal(
    ...     repo_id="microsoft/DialoGPT-medium",
    ...     filename="model.gguf"
    ... )

Author: Alex Nicita
License: MIT
"""

__version__ = "1.0.4"
__author__ = "Alex Nicita"
__email__ = "alex@llmocal.dev"
__description__ = "Professional open source client for running large language models locally"

# Public API - Import main classes for easy access
try:
    from .core.engine import LLMEngine
    from .core.config import LLMocalConfig
    from .models.manager import ModelManager
    from .core.chat import ChatInterface
except ImportError:
    # Handle import errors gracefully during installation
    pass

# Convenience class for easy usage
class LLMocal:
    """High-level interface to LLMocal for easy usage.
    
    This class provides a simple way to get started with LLMocal
    without needing to understand the internal architecture.
    """
    
    def __init__(self, repo_id=None, filename=None, config=None):
        """Initialize LLMocal client.
        
        Args:
            repo_id: Hugging Face repository ID (e.g., "TheBloke/Mistral-7B-Instruct-v0.2-GGUF")
            filename: Model filename (e.g., "mistral-7b-instruct-v0.2.Q4_K_M.gguf")
            config: LLMocalConfig instance for advanced configuration
        """
        try:
            from .core.config import LLMocalConfig
            from .models.manager import ModelManager
            from .core.engine import LLMEngine
            from .core.chat import ChatInterface
        except ImportError as e:
            raise ImportError(
                f"Failed to import LLMocal components: {e}\n"
                "Please ensure all dependencies are installed: pip install llmocal"
            )
            
        self.config = config or LLMocalConfig()
        if repo_id:
            self.config.model_repo_id = repo_id
        if filename:
            self.config.model_filename = filename
            
        self.model_manager = ModelManager()
        self.engine = None
        self.chat_interface = None
        self._model_path = None
    
    def setup(self):
        """Download model if needed and set up the engine."""
        self._model_path = self.model_manager.download_model_if_needed(
            self.config.model_repo_id, 
            self.config.model_filename
        )
        if not self._model_path:
            raise RuntimeError("Failed to download or locate model")
        
        self.engine = LLMEngine(self._model_path, self.config)
        self.engine.load_model()
        return self
    
    def chat(self, message):
        """Send a message and get a response.
        
        Args:
            message: The message to send to the AI
            
        Returns:
            The AI's response as a string
        """
        if not self.engine:
            raise RuntimeError("Please call setup() first")
            
        # Format the message for the model
        formatted_prompt = f"[INST] {message} [/INST]"
        
        # Collect the streaming response
        response_parts = []
        for token in self.engine.generate_response(formatted_prompt):
            response_parts.append(token)
        
        return "".join(response_parts).strip()
    
    def start_interactive_chat(self):
        """Start an interactive chat session."""
        if not self.engine:
            raise RuntimeError("Please call setup() first")
            
        if not self.chat_interface:
            self.chat_interface = ChatInterface(self.config)
            self.chat_interface.setup(self._model_path)
        
        self.chat_interface.start_chat_loop()

__all__ = [
    "__version__",
    "__author__",
    "__description__",
    "LLMocal",
    "LLMEngine", 
    "LLMocalConfig",
    "ModelManager",
    "ChatInterface",
]
