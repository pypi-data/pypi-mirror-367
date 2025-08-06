"""
Configuration Module - Manages system configuration and environment variables
"""

import os
from dataclasses import dataclass
from typing import Optional
from dotenv import load_dotenv

@dataclass
class Config:
    """Configuration Class
    
    Used to manage all configuration items for the application, including:
    - MongoDB configuration: database connection information
    - Qdrant configuration: vector database connection information
    - Model configuration: embedding model and LLM model configuration
    - OpenAI configuration: API key
    """
    # Required configurations
    mongo_user: str
    mongo_passwd: str
    mongo_host: str
    qdrant_url: str
    embedding_model_path: str
    embedding_dim: int
    openai_api_key: str
    llm_model: str
    
    # Optional configurations
    openai_api_base: Optional[str] = None
    mongo_replset: Optional[str] = None

    # Memory configurations
    max_recent_history: int = 20  # Number of recent conversations to keep in main table

    # Prompt length limit configurations
    max_total_prompt_length: int = 4000  # Maximum total prompt length in characters
    max_immediate_override_length: int = 2000  # Maximum immediate override length in characters
    prompt_warning_threshold: int = 3200  # Warning threshold (80% of max)

    # Similarity configurations
    similarity_threshold: float = 0.5  # Threshold for detecting similar content
    local_similarity_threshold: float = 0.4  # Threshold for local similarity screening

    def __post_init__(self):
        """Validate configuration"""
        # Validate required configurations
        required_configs = {
            "MongoDB User": self.mongo_user,
            "MongoDB Password": self.mongo_passwd,
            "MongoDB Host": self.mongo_host,
            "Qdrant URL": self.qdrant_url,
            "Embedding Model Path": self.embedding_model_path,
            "Embedding Dimension": self.embedding_dim,
            "OpenAI API Key": self.openai_api_key,
            "LLM Model": self.llm_model
        }
        
        missing_configs = [name for name, value in required_configs.items() if not value]
        if missing_configs:
            raise ValueError(f"Missing required configurations: {', '.join(missing_configs)}")
        
        # Validate numeric configurations
        if self.embedding_dim <= 0:
            raise ValueError("Embedding dimension must be positive")

    @classmethod
    def from_env(cls, env_file: Optional[str] = None) -> 'Config':
        """Load configuration from environment variables
        
        Args:
            env_file: Path to environment variable file, if None uses default .env file
            
        Returns:
            Config: Configuration object
            
        Raises:
            ValueError: When required configuration is missing or configuration value is invalid
        """
        if env_file:
            load_dotenv(env_file)
        else:
            load_dotenv()

        return cls(
            # MongoDB configuration
            mongo_user=os.getenv("MONGO_USER"),
            mongo_passwd=os.getenv("MONGO_PASSWD"),
            mongo_host=os.getenv("MONGO_HOST"),

            # Qdrant configuration
            qdrant_url=os.getenv("QDRANT_URL"),

            # Model configuration
            embedding_model_path=os.getenv("EMBEDDING_MODEL_PATH"),
            embedding_dim=int(os.getenv("EMBEDDING_DIM")),

            # OpenAI configuration
            openai_api_key=os.getenv("OPENAI_API_KEY"),
            openai_api_base=os.getenv("OPENAI_API_BASE", "https://api.openai.com/v1"),
            llm_model=os.getenv("LLM_MODEL"),

            # Other configuration
            mongo_replset=os.getenv("MONGO_REPLSET"),

            # Memory configuration
            max_recent_history=int(os.getenv("MAX_RECENT_HISTORY", "20")),

            # Prompt length limit configurations
            max_total_prompt_length=int(os.getenv("MAX_TOTAL_PROMPT_LENGTH", "4000")),
            max_immediate_override_length=int(os.getenv("MAX_IMMEDIATE_OVERRIDE_LENGTH", "2000")),
            prompt_warning_threshold=int(os.getenv("PROMPT_WARNING_THRESHOLD", "3200")),

            # Similarity configurations
            similarity_threshold=float(os.getenv("SIMILARITY_THRESHOLD", "0.5")),
            local_similarity_threshold=float(os.getenv("LOCAL_SIMILARITY_THRESHOLD", "0.4"))
        )
    
    @property
    def mongodb_uri(self) -> str:
        """Generate MongoDB URI from components"""
        auth = f"{self.mongo_user}:{self.mongo_passwd}"
        replset = f"?replicaSet={self.mongo_replset}" if self.mongo_replset else ""
        return f"mongodb://{auth}@{self.mongo_host}/admin{replset}"
    
    @property
    def qdrant_host(self) -> str:
        """Extract Qdrant host from URL"""
        return self.qdrant_url.replace("http://", "").replace("https://", "").split(":")[0]
    
    @property
    def qdrant_port(self) -> int:
        """Extract Qdrant port from URL"""
        try:
            return int(self.qdrant_url.split(":")[-1])
        except:
            return 6333  # Default Qdrant port