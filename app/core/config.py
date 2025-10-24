"""
Configuration management for FinanceBot Multi-Agent System
"""
import os
from typing import Optional, List
from pydantic_settings import BaseSettings
from pydantic import Field


class Settings(BaseSettings):
    """Application settings with environment variable support"""
    
    # OpenAI Configuration
    openai_api_key: str = Field(..., env="OPENAI_API_KEY")
    openai_model: str = Field(default="gpt-4", env="OPENAI_MODEL")
    openai_temperature: float = Field(default=0.7, env="OPENAI_TEMPERATURE")
    openai_max_tokens: int = Field(default=4000, env="OPENAI_MAX_TOKENS")
    
    # Agent Configuration
    agent_timeout: int = Field(default=30, env="AGENT_TIMEOUT")
    max_agent_iterations: int = Field(default=10, env="MAX_AGENT_ITERATIONS")
    enable_agent_memory: bool = Field(default=True, env="ENABLE_AGENT_MEMORY")
    
    # API Configuration
    api_host: str = Field(default="0.0.0.0", env="API_HOST")
    api_port: int = Field(default=8000, env="API_PORT")
    api_debug: bool = Field(default=False, env="API_DEBUG")
    api_title: str = Field(default="FinanceBot Multi-Agent API", env="API_TITLE")
    api_version: str = Field(default="1.0.0", env="API_VERSION")
    
    # Database Configuration
    database_url: str = Field(default="sqlite:///./financebot.db", env="DATABASE_URL")
    redis_url: str = Field(default="redis://localhost:6379", env="REDIS_URL")
    
    # Market Data Configuration
    market_data_provider: str = Field(default="yfinance", env="MARKET_DATA_PROVIDER")
    market_data_cache_ttl: int = Field(default=300, env="MARKET_DATA_CACHE_TTL")  # 5 minutes
    
    # Security Configuration
    secret_key: str = Field(default="your-secret-key-here", env="SECRET_KEY")
    access_token_expire_minutes: int = Field(default=30, env="ACCESS_TOKEN_EXPIRE_MINUTES")
    
    # Logging Configuration
    log_level: str = Field(default="INFO", env="LOG_LEVEL")
    log_file: Optional[str] = Field(default=None, env="LOG_FILE")
    
    # Monitoring Configuration
    monitoring_provider: str = Field(default="none", env="MONITORING_PROVIDER")  # langfuse, logfire, wandb, none
    enable_monitoring: bool = Field(default=False, env="ENABLE_MONITORING")
    
    # Langfuse Configuration
    langfuse_public_key: Optional[str] = Field(default=None, env="LANGFUSE_PUBLIC_KEY")
    langfuse_secret_key: Optional[str] = Field(default=None, env="LANGFUSE_SECRET_KEY")
    langfuse_host: Optional[str] = Field(default=None, env="LANGFUSE_HOST")
    enable_langfuse: bool = Field(default=True, env="ENABLE_LANGFUSE")
    
    # Logfire Configuration
    enable_logfire: bool = Field(default=False, env="ENABLE_LOGFIRE")
    
    # Weights & Biases Configuration
    wandb_project: str = Field(default="financebot-agents", env="WANDB_PROJECT")
    wandb_api_key: Optional[str] = Field(default=None, env="WANDB_API_KEY")
    enable_wandb: bool = Field(default=False, env="ENABLE_WANDB")
    
    # Agent-specific configurations
    compliance_agent_config: dict = Field(default_factory=lambda: {
        "enabled": True,
        "tools": ["compliance_checker", "regulation_lookup"],
        "temperature": 0.3
    })
    
    fin_doc_agent_config: dict = Field(default_factory=lambda: {
        "enabled": True,
        "tools": ["document_parser", "pdf_analyzer", "text_extractor"],
        "temperature": 0.2
    })
    
    quant_agent_config: dict = Field(default_factory=lambda: {
        "enabled": True,
        "tools": ["chart_analyzer", "technical_indicators", "backtesting"],
        "temperature": 0.1
    })
    
    research_agent_config: dict = Field(default_factory=lambda: {
        "enabled": True,
        "tools": ["news_analyzer", "market_research", "sentiment_analysis"],
        "temperature": 0.5
    })
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = False


# Global settings instance
settings = Settings()


def get_settings() -> Settings:
    """Get application settings"""
    return settings


def validate_environment() -> bool:
    """Validate that all required environment variables are set"""
    required_vars = ["OPENAI_API_KEY"]
    missing_vars = []
    
    for var in required_vars:
        if not os.getenv(var):
            missing_vars.append(var)
    
    if missing_vars:
        raise ValueError(f"Missing required environment variables: {', '.join(missing_vars)}")
    
    return True


def validate_monitoring_config() -> bool:
    """Validate monitoring configuration"""
    provider = os.getenv("MONITORING_PROVIDER", "langfuse").lower()
    enable_monitoring = os.getenv("ENABLE_MONITORING", "true").lower() in ["true", "1", "yes"]
    
    if not enable_monitoring:
        print("ℹ️  Monitoring is disabled")
        return True
    
    if provider == "langfuse":
        return validate_langfuse_config()
    elif provider == "logfire":
        return validate_logfire_config()
    elif provider == "wandb":
        return validate_wandb_config()
    elif provider == "none":
        print("ℹ️  No monitoring provider configured")
        return True
    else:
        print(f"⚠️  Unknown monitoring provider: {provider}")
        return False


def validate_langfuse_config() -> bool:
    """Validate Langfuse configuration if enabled"""
    if not os.getenv("ENABLE_LANGFUSE", "true").lower() in ["true", "1", "yes"]:
        return True  # Langfuse is disabled
    
    langfuse_vars = ["LANGFUSE_PUBLIC_KEY", "LANGFUSE_SECRET_KEY", "LANGFUSE_HOST"]
    missing_vars = []
    
    for var in langfuse_vars:
        if not os.getenv(var):
            missing_vars.append(var)
    
    if missing_vars:
        print(f"⚠️  Langfuse is enabled but missing variables: {', '.join(missing_vars)}")
        print("   Langfuse tracing will be disabled.")
        return False
    
    return True


def validate_logfire_config() -> bool:
    """Validate Logfire configuration if enabled"""
    if not os.getenv("ENABLE_LOGFIRE", "false").lower() in ["true", "1", "yes"]:
        return True  # Logfire is disabled
    
    print("ℹ️  Logfire monitoring enabled")
    return True


def validate_wandb_config() -> bool:
    """Validate Weights & Biases configuration if enabled"""
    if not os.getenv("ENABLE_WANDB", "false").lower() in ["true", "1", "yes"]:
        return True  # W&B is disabled
    
    if not os.getenv("WANDB_API_KEY"):
        print("⚠️  W&B is enabled but missing WANDB_API_KEY")
        print("   W&B monitoring will be disabled.")
        return False
    
    print("ℹ️  Weights & Biases monitoring enabled")
    return True
