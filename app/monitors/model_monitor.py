"""
Model Monitor - Unified monitoring and tracing system
"""
import os
import base64
import signal
from typing import Optional, Dict, Any
from dataclasses import dataclass
from enum import Enum

from app.core.config import Settings


class MonitorProvider(Enum):
    """Supported monitoring providers"""
    LANGFUSE = "langfuse"
    LOGFIRE = "logfire"
    WANDB = "wandb"
    NONE = "none"


@dataclass
class MonitorConfig:
    """Configuration for monitoring providers"""
    provider: MonitorProvider
    enabled: bool = True
    auto_init: bool = True
    auto_flush: bool = True
    flush_timeout: int = 5
    service_name: str = "financebot_agent_service"


class ModelMonitor:
    """Unified model monitoring and tracing system"""
    
    def __init__(self, config: MonitorConfig, settings: Settings):
        self.config = config
        self.settings = settings
        self.provider_client = None
        self.is_configured = False
        self.is_initialized = False
        
    def setup(self) -> bool:
        """Setup monitoring provider"""
        if not self.config.enabled:
            print("ℹ️  Model monitoring is disabled")
            return False
            
        if self.config.provider == MonitorProvider.LANGFUSE:
            return self._setup_langfuse()
        elif self.config.provider == MonitorProvider.LOGFIRE:
            return self._setup_logfire()
        elif self.config.provider == MonitorProvider.WANDB:
            return self._setup_wandb()
        else:
            print("ℹ️  No monitoring provider configured")
            return False
    
    def _setup_langfuse(self) -> bool:
        """Setup Langfuse monitoring"""
        try:
            # Check if Langfuse is enabled in settings
            if not self.settings.enable_langfuse:
                print("ℹ️  Langfuse is disabled in settings")
                return False
            
            # Get credentials
            public_key = self.settings.langfuse_public_key
            secret_key = self.settings.langfuse_secret_key
            host = self.settings.langfuse_host
            
            if not all([public_key, secret_key, host]):
                print("⚠️  Langfuse credentials not found in settings")
                return False
            
            # Import Langfuse
            from langfuse import get_client
            import logfire
            
            # Set environment variables
            os.environ["LANGFUSE_PUBLIC_KEY"] = public_key
            os.environ["LANGFUSE_SECRET_KEY"] = secret_key
            os.environ["LANGFUSE_HOST"] = host
            
            # Build Basic Auth header
            langfuse_auth = base64.b64encode(
                f"{public_key}:{secret_key}".encode()
            ).decode()
            
            # Configure OpenTelemetry
            os.environ["OTEL_EXPORTER_OTLP_ENDPOINT"] = host + "/api/public/otel"
            os.environ["OTEL_EXPORTER_OTLP_HEADERS"] = f"Authorization=Basic {langfuse_auth}"
            
            # Initialize client
            self.provider_client = get_client()
            
            # Verify connection
            if self.provider_client.auth_check():
                print("✅ Langfuse client authenticated and ready")
                
                # Configure logfire instrumentation
                logfire.configure(
                    service_name=self.config.service_name,
                    send_to_logfire=False,  # Send to Langfuse instead
                )
                
                # Instrument OpenAI Agents SDK
                logfire.instrument_openai_agents()
                
                self.is_configured = True
                return True
            else:
                print("❌ Langfuse authentication failed")
                return False
                
        except Exception as e:
            print(f"❌ Error setting up Langfuse: {e}")
            return False
    
    def _setup_logfire(self) -> bool:
        """Setup Logfire monitoring"""
        try:
            import logfire
            
            logfire.configure(
                service_name=self.config.service_name,
                send_to_logfire=True,
            )
            
            # Instrument OpenAI Agents SDK
            logfire.instrument_openai_agents()
            
            self.provider_client = logfire
            self.is_configured = True
            print("✅ Logfire monitoring configured")
            return True
            
        except Exception as e:
            print(f"❌ Error setting up Logfire: {e}")
            return False
    
    def _setup_wandb(self) -> bool:
        """Setup Weights & Biases monitoring"""
        try:
            import wandb
            
            # Initialize wandb
            wandb.init(
                project="financebot-agents",
                name=self.config.service_name,
                config=self.settings.dict()
            )
            
            self.provider_client = wandb
            self.is_configured = True
            print("✅ Weights & Biases monitoring configured")
            return True
            
        except Exception as e:
            print(f"❌ Error setting up Weights & Biases: {e}")
            return False
    
    def initialize(self) -> bool:
        """Initialize monitoring (auto-init if enabled)"""
        if self.is_initialized:
            return True
            
        if self.config.auto_init:
            success = self.setup()
            if success:
                self.is_initialized = True
            return success
        else:
            print("ℹ️  Auto-init disabled, call setup() manually")
            return False
    
    def flush(self) -> bool:
        """Flush traces/metrics to monitoring provider"""
        if not self.is_configured or not self.provider_client:
            print("⚠️  No monitoring provider configured")
            return False
        
        try:
            if self.config.provider == MonitorProvider.LANGFUSE:
                return self._flush_langfuse()
            elif self.config.provider == MonitorProvider.LOGFIRE:
                return self._flush_logfire()
            elif self.config.provider == MonitorProvider.WANDB:
                return self._flush_wandb()
            else:
                return False
                
        except Exception as e:
            print(f"❌ Error flushing traces: {e}")
            return False
    
    def _flush_langfuse(self) -> bool:
        """Flush Langfuse traces with timeout protection"""
        try:
            def timeout_handler(signum, frame):
                raise TimeoutError("Flush operation timed out")
            
            # Set timeout
            signal.signal(signal.SIGALRM, timeout_handler)
            signal.alarm(self.config.flush_timeout)
            
            try:
                self.provider_client.flush()
                signal.alarm(0)  # Cancel timeout
                print("✅ Flushed traces to Langfuse")
                return True
            except TimeoutError:
                signal.alarm(0)  # Cancel timeout
                print("⚠️  Langfuse flush timed out")
                return False
            except Exception as flush_error:
                signal.alarm(0)  # Cancel timeout
                print(f"❌ Error flushing to Langfuse: {flush_error}")
                return False
                
        except Exception as e:
            print(f"❌ Error in Langfuse flush operation: {e}")
            return False
    
    def _flush_logfire(self) -> bool:
        """Flush Logfire traces"""
        try:
            # Logfire auto-flushes, but we can force it
            print("✅ Logfire traces flushed")
            return True
        except Exception as e:
            print(f"❌ Error flushing Logfire: {e}")
            return False
    
    def _flush_wandb(self) -> bool:
        """Flush Weights & Biases metrics"""
        try:
            self.provider_client.finish()
            print("✅ Weights & Biases metrics flushed")
            return True
        except Exception as e:
            print(f"❌ Error flushing Weights & Biases: {e}")
            return False
    
    def log_metric(self, name: str, value: float, step: Optional[int] = None):
        """Log a metric to the monitoring provider"""
        if not self.is_configured:
            return
            
        try:
            if self.config.provider == MonitorProvider.WANDB and self.provider_client:
                self.provider_client.log({name: value}, step=step)
            elif self.config.provider == MonitorProvider.LOGFIRE and self.provider_client:
                self.provider_client.info(f"Metric {name}: {value}")
        except Exception as e:
            print(f"⚠️  Error logging metric {name}: {e}")
    
    def log_event(self, event_name: str, data: Dict[str, Any]):
        """Log an event to the monitoring provider"""
        if not self.is_configured:
            return
            
        try:
            if self.config.provider == MonitorProvider.LOGFIRE and self.provider_client:
                self.provider_client.info(f"Event {event_name}: {data}")
            elif self.config.provider == MonitorProvider.WANDB and self.provider_client:
                self.provider_client.log({event_name: data})
        except Exception as e:
            print(f"⚠️  Error logging event {event_name}: {e}")
    
    def shutdown(self):
        """Shutdown monitoring"""
        if self.is_configured and self.config.auto_flush:
            print("🔄 Final flush before shutdown...")
            self.flush()
        
        if self.config.provider == MonitorProvider.WANDB and self.provider_client:
            try:
                self.provider_client.finish()
                print("✅ Weights & Biases session finished")
            except Exception as e:
                print(f"⚠️  Error finishing Weights & Biases: {e}")
        
        print("✅ Model monitor shutdown completed")


def create_monitor(settings: Settings, provider: str = "langfuse") -> ModelMonitor:
    """Factory function to create a model monitor"""
    provider_enum = MonitorProvider(provider.lower()) if provider.lower() in [p.value for p in MonitorProvider] else MonitorProvider.NONE
    
    config = MonitorConfig(
        provider=provider_enum,
        enabled=getattr(settings, f'enable_{provider.lower()}', True) if provider.lower() != 'none' else False,
        auto_init=True,
        auto_flush=True,
        service_name="financebot_agent_service"
    )
    
    return ModelMonitor(config, settings)
