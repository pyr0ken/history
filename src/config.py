import os
from dotenv import load_dotenv


class Config:
    """Simple configuration class for environment variables."""
    
    def __init__(self):
        """Initialize config by loading environment variables."""
        load_dotenv()
        
        self.AGENTQL_API_KEY = os.environ.get("AGENTQL_API_KEY")
        self.AGENTQL_API_URL = os.environ.get("AGENTQL_API_URL")


# Create a global config instance
conf = Config()