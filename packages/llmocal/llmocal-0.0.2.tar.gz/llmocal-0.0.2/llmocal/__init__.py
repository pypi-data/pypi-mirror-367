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
    >>> 
    >>> # First time: download a model
    >>> client = llmocal.LLMocal()
    >>> client.download_model()  # Explicit download
    >>> client.setup()          # Load the model
    >>> response = client.chat("Hello, how are you?")
    >>> print(response)
    >>> 
    >>> # Or download automatically
    >>> client = llmocal.LLMocal()
    >>> client.setup(auto_download=True)
    >>> 
    >>> # Custom model
    >>> client = llmocal.LLMocal(
    ...     repo_id="TheBloke/CodeLlama-7B-Instruct-GGUF",
    ...     filename="codellama-7b-instruct.Q4_K_M.gguf"
    ... )
    >>> client.download_model()
    >>> client.setup()

Author: Alex Nicita
License: MIT
"""

__version__ = "0.0.2"
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
    
    def setup(self, auto_download=False):
        """Set up the engine with a model.
        
        Args:
            auto_download: If True, downloads model if not found locally.
                         If False (default), requires model to exist locally.
        
        Returns:
            Self for method chaining
            
        Raises:
            RuntimeError: If model is not found and auto_download=False
            FileNotFoundError: If specified model file doesn't exist locally
        """
        # Check if model exists locally first
        model_path = self.model_manager.get_model_path(
            self.config.model_repo_id, 
            self.config.model_filename
        )
        
        if model_path.exists():
            self._model_path = model_path
        elif auto_download:
            self._model_path = self.model_manager.download_model_if_needed(
                self.config.model_repo_id, 
                self.config.model_filename
            )
            if not self._model_path:
                raise RuntimeError("Failed to download model")
        else:
            raise FileNotFoundError(
                f"Model not found at {model_path}\n\n"
                f"To download the model automatically, use:\n"
                f"  client.setup(auto_download=True)\n\n"
                f"Or download manually:\n"
                f"  client.download_model()\n"
                f"  client.setup()\n\n"
                f"Or specify a different model:\n"
                f"  client = LLMocal(repo_id='your-repo', filename='your-file.gguf')"
            )
        
        self.engine = LLMEngine(self._model_path, self.config)
        self.engine.load_model()
        return self
    
    def download_model(self):
        """Download the configured model.
        
        Returns:
            Path to the downloaded model
        """
        from rich.console import Console
        console = Console()
        
        console.print(f"[bold blue]📥 Downloading model...[/bold blue]")
        console.print(f"  Repository: {self.config.model_repo_id}")
        console.print(f"  Filename: {self.config.model_filename}")
        
        model_path = self.model_manager.download_model_if_needed(
            self.config.model_repo_id,
            self.config.model_filename
        )
        
        if model_path:
            console.print(f"[bold green]✅ Model downloaded successfully![/bold green]")
            console.print(f"  Location: {model_path}")
            return model_path
        else:
            raise RuntimeError("Failed to download model")
    
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
