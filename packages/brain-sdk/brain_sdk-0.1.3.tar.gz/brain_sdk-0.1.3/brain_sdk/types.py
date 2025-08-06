import os
from dataclasses import asdict, dataclass
from typing import Any, Dict, List, Literal, Optional
from pydantic import BaseModel, Field
from enum import Enum
import time

class AgentStatus(str, Enum):
    """Agent lifecycle status enum matching the Go backend"""
    STARTING = "starting"
    READY = "ready"
    DEGRADED = "degraded"
    OFFLINE = "offline"

@dataclass
class MCPServerHealth:
    """MCP server health information for heartbeat reporting"""
    alias: str
    status: str
    tool_count: int = 0
    port: Optional[int] = None
    process_id: Optional[int] = None
    started_at: Optional[str] = None
    last_health_check: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)

@dataclass
class HeartbeatData:
    """Enhanced heartbeat data with status and MCP information"""
    status: AgentStatus
    mcp_servers: List[MCPServerHealth]
    timestamp: str
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "status": self.status.value,
            "mcp_servers": [server.to_dict() for server in self.mcp_servers],
            "timestamp": self.timestamp
        }

@dataclass
class MemoryConfig:
    auto_inject: List[str]
    memory_retention: str
    cache_results: bool

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)

@dataclass
class ReasonerDefinition:
    id: str
    input_schema: Dict[str, Any]
    output_schema: Dict[str, Any]
    memory_config: Optional[MemoryConfig] = None # Optional for now, can be added later

    def to_dict(self) -> Dict[str, Any]:
        data = asdict(self)
        if self.memory_config is not None:
            data["memory_config"] = self.memory_config.to_dict()
        return data

@dataclass
class SkillDefinition:
    id: str
    input_schema: Dict[str, Any]
    tags: List[str]

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)

@dataclass
class WorkflowContext:
    workflow_id: str
    session_id: Optional[str] = None
    actor_id: Optional[str] = None
    parent_workflow_id: Optional[str] = None
    root_workflow_id: Optional[str] = None
    workflow_name: Optional[str] = None
    workflow_tags: Optional[List[str]] = None

    def to_headers(self) -> Dict[str, str]:
        headers = {
            "X-Workflow-ID": self.workflow_id,
        }
        if self.session_id:
            headers["X-Session-ID"] = self.session_id
        if self.actor_id:
            headers["X-Actor-ID"] = self.actor_id
        if self.parent_workflow_id:
            headers["X-Parent-Workflow-ID"] = self.parent_workflow_id
        if self.root_workflow_id:
            headers["X-Root-Workflow-ID"] = self.root_workflow_id
        if self.workflow_name:
            headers["X-Workflow-Name"] = self.workflow_name
        if self.workflow_tags:
            headers["X-Workflow-Tags"] = ",".join(self.workflow_tags)
        return headers

@dataclass
class ExecutionMetadata:
    execution_id: str
    brain_request_id: str
    agent_node_id: str
    duration_ms: int
    timestamp: str

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)

    @classmethod
    def from_headers(cls, headers: Dict[str, str]) -> Optional["ExecutionMetadata"]:
        execution_id = headers.get("X-Execution-ID")
        brain_request_id = headers.get("X-Brain-Request-ID")
        agent_node_id = headers.get("X-Agent-Node-ID")
        duration_ms_str = headers.get("X-Duration-MS")
        timestamp = headers.get("X-Timestamp") # Assuming server sends this

        if execution_id and brain_request_id and agent_node_id and duration_ms_str and timestamp:
            try:
                duration_ms = int(duration_ms_str)
                return cls(
                    execution_id=execution_id,
                    brain_request_id=brain_request_id,
                    agent_node_id=agent_node_id,
                    duration_ms=duration_ms,
                    timestamp=timestamp
                )
            except ValueError:
                return None
        return None

class AIConfig(BaseModel):
    """
    Configuration for AI calls, defining default models, temperatures, and other parameters.
    These settings can be overridden at the method call level.
    
    Leverages LiteLLM's standard environment variable handling for API keys:
    - OPENAI_API_KEY, ANTHROPIC_API_KEY, AZURE_OPENAI_API_KEY, etc.
    - LiteLLM automatically detects and uses these standard environment variables
    
    All fields have sensible defaults, so you can create an AIConfig with minimal configuration:
    
    Examples:
        # Minimal configuration - uses all defaults
        AIConfig()
        
        # Override just the API key
        AIConfig(api_key="your-key")
        
        # Override specific models for multimodal tasks
        AIConfig(audio_model="tts-1-hd", vision_model="dall-e-3")
    """
    model: str = Field(default="gpt-4o", description="Default LLM model to use (e.g., 'gpt-4o', 'claude-3-sonnet').")
    temperature: float = Field(default=0.7, ge=0.0, le=2.0, description="Creativity level (0.0-2.0).")
    max_tokens: Optional[int] = Field(default=None, description="Maximum response length.")
    top_p: float = Field(default=1.0, ge=0.0, le=1.0, description="Controls diversity via nucleus sampling.")
    stream: bool = Field(default=False, description="Enable streaming response.")
    response_format: Literal["auto", "json", "text"] = Field(default="auto", description="Desired response format.")

    # Multimodal settings - updated with better defaults for TTS
    vision_model: str = Field(default="dall-e-3", description="Model for vision/image generation tasks.")
    audio_model: str = Field(default="tts-1", description="Model for audio generation (tts-1, tts-1-hd, gpt-4o-mini-tts).")
    image_quality: Literal["low", "high"] = Field(default="high", description="Quality for image generation/processing.")
    audio_format: str = Field(default="wav", description="Default format for audio output (wav, mp3).")

    # Behavior settings
    timeout: int = Field(default=60, description="Timeout for AI calls in seconds.")
    retry_attempts: int = Field(default=3, description="Number of retry attempts for failed AI calls.")
    retry_delay: float = Field(default=1.0, description="Delay between retries in seconds.")

    # Cost controls
    max_cost_per_call: Optional[float] = Field(default=None, description="Maximum cost per AI call in USD.")
    daily_budget: Optional[float] = Field(default=None, description="Daily budget for AI calls in USD.")

    # Memory integration (defaults for auto-injection)
    auto_inject_memory: List[str] = Field(default_factory=list, description="List of memory scopes to auto-inject (e.g., ['workflow', 'session']).")
    preserve_context: bool = Field(default=True, description="Whether to preserve conversation context across calls.")
    context_window: int = Field(default=10, description="Number of previous messages to include in context.")

    # LiteLLM configuration - these get passed directly to litellm.completion()
    api_key: Optional[str] = Field(default=None, description="API key override (if not using env vars)")
    api_base: Optional[str] = Field(default=None, description="Custom API base URL")
    api_version: Optional[str] = Field(default=None, description="API version (for Azure)")
    organization: Optional[str] = Field(default=None, description="Organization ID (for OpenAI)")
    
    # Additional LiteLLM parameters that can be overridden
    litellm_params: Dict[str, Any] = Field(default_factory=dict, description="Additional parameters to pass to LiteLLM")
    fallback_models: List[str] = Field(default_factory=list, description="List of models to fallback to if primary fails.")

    def get_litellm_params(self, **overrides) -> Dict[str, Any]:
        """
        Get parameters formatted for LiteLLM, with runtime overrides.
        LiteLLM handles environment variable detection automatically.
        """
        params = {
            "model": self.model,
            "temperature": self.temperature,
            "max_tokens": self.max_tokens,
            "top_p": self.top_p,
            "stream": self.stream,
            "timeout": self.timeout,
            "num_retries": self.retry_attempts,
        }
        
        # Add optional parameters if set
        if self.api_key:
            params["api_key"] = self.api_key
        if self.api_base:
            params["api_base"] = self.api_base
        if self.api_version:
            params["api_version"] = self.api_version
        if self.organization:
            params["organization"] = self.organization
            
        # Add response format if not auto
        if self.response_format != "auto":
            params["response_format"] = {"type": self.response_format}
            
        # Add any additional litellm params
        params.update(self.litellm_params)
        
        # Apply runtime overrides (highest priority)
        params.update(overrides)
        
        # Remove None values
        return {k: v for k, v in params.items() if v is not None}

    def copy(self, *, include: Optional[Any] = None, exclude: Optional[Any] = None, update: Optional[Dict[str, Any]] = None, deep: bool = False) -> "AIConfig":
        """Create a copy of the configuration"""
        return super().copy(include=include, exclude=exclude, update=update, deep=deep)

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary representation"""
        return self.dict()

    @classmethod
    def from_env(cls, **overrides) -> "AIConfig":
        """
        Create AIConfig with smart defaults, letting LiteLLM handle env vars.
        This is the recommended way to create configs in production.
        """
        config = cls(**overrides)
        return config


@dataclass
class MemoryValue:
    """Represents a memory value stored in the Brain system."""
    key: str
    data: Any
    scope: str
    scope_id: str
    created_at: str
    updated_at: str

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "MemoryValue":
        return cls(**data)


@dataclass
class MemoryChangeEvent:
    """Represents a memory change event for reactive programming."""
    scope: str
    scope_id: str
    key: str
    action: str  # "set" or "delete"
    old_value: Optional[Any] = None
    new_value: Optional[Any] = None
    timestamp: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "MemoryChangeEvent":
        return cls(**data)
