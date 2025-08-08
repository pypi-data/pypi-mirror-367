"""
Universal Tracing Middleware for Agentic Setups
===============================================

This module provides a framework-agnostic tracing interface that can work with
any tracing backend (Langfuse, OpenTelemetry, etc.) through a simple adapter pattern.
It also supports native framework integrations when available.
"""

import os
import importlib.util
from abc import ABC, abstractmethod
from functools import wraps
from typing import Optional, Dict, Any, Callable, Union
from contextlib import contextmanager
import asyncio
from dataclasses import dataclass

# Default to Langfuse, but allow other implementations
DEFAULT_TRACER = os.getenv('TRACENET_TRACER', 'langfuse')

# Global agent name - auto-read from environment variable
_AGENT_NAME = os.getenv('AGENT_NAME')

# Global session ID for grouping traces
_CURRENT_SESSION_ID = None

# Global user ID for tracking user-specific traces
_CURRENT_USER_ID = None

def set_agent_name(name: str):
    """Set the agent name that will be used to tag all traces."""
    global _AGENT_NAME
    _AGENT_NAME = name

def set_user_id(user_id: str):
    """
    Set the user ID that will be used to tag all subsequent traces.
    This should be called before starting any traces that you want associated with a specific user.
    
    Args:
        user_id: The user identifier to associate with traces
    """
    global _CURRENT_USER_ID
    _CURRENT_USER_ID = user_id

def get_user_id() -> Optional[str]:
    """Get the current user ID."""
    return _CURRENT_USER_ID

def clear_user_id():
    """Clear the current user ID."""
    global _CURRENT_USER_ID
    _CURRENT_USER_ID = None

def set_session_id(session_id: str):
    """
    Set the session ID that will be used to group all subsequent traces.
    This should be called before starting any traces that you want grouped together.
    
    Args:
        session_id: The session identifier to use for grouping traces
    """
    global _CURRENT_SESSION_ID
    _CURRENT_SESSION_ID = session_id

def get_session_id() -> Optional[str]:
    """Get the current session ID."""
    return _CURRENT_SESSION_ID

def clear_session_id():
    """Clear the current session ID."""
    global _CURRENT_SESSION_ID
    _CURRENT_SESSION_ID = None

def _setup_native_integration():
    """
    Attempts to detect and configure native framework integrations.
    Returns True if a native integration was configured.
    """
    try:
        # Try OpenAI Agents SDK integration
        if importlib.util.find_spec("agents"):
            import logfire
            logfire.configure(
                service_name=os.getenv('TRACENET_SERVICE_NAME', 'agent_service'),
                send_to_logfire=False
            )
            logfire.instrument_openai_agents()
            return True
            
        # Try Google ADK integration
        if importlib.util.find_spec("google.adk"):
            from langfuse import get_client
            client = get_client()
            if client.auth_check():
                return True
                
        # Try CrewAI integration
        if importlib.util.find_spec("crewai"):
            from langfuse.crewai import CrewAIInstrumentation
            CrewAIInstrumentation.setup()
            return True
            
        # Try LangChain integration
        if importlib.util.find_spec("langchain"):
            from langfuse.langchain import LangchainInstrumentation
            LangchainInstrumentation.setup()
            return True

        # Try Agno integration
        if importlib.util.find_spec("agno"):
            from openinference.instrumentation.agno import AgnoInstrumentor
            AgnoInstrumentor().instrument()
            return True

        # Try OpenAI SDK integration
        if importlib.util.find_spec("openai"):
            from openinference.instrumentation.openai import OpenAIInstrumentor
            OpenAIInstrumentor().instrument()
            return True

        # Try LlamaIndex integration
        if importlib.util.find_spec("llama_index"):
            from openinference.instrumentation.llama_index import LlamaIndexInstrumentor
            LlamaIndexInstrumentor().instrument()
            return True

        # Try DSPy integration
        if importlib.util.find_spec("dspy"):
            from openinference.instrumentation.dspy import DSPyInstrumentor
            DSPyInstrumentor().instrument()
            return True

        # Try AWS Bedrock integration
        if importlib.util.find_spec("boto3"):
            from openinference.instrumentation.bedrock import BedrockInstrumentor
            BedrockInstrumentor().instrument()
            return True

        # Try MCP integration
        if importlib.util.find_spec("mcp"):
            from openinference.instrumentation.mcp import MCPInstrumentor
            MCPInstrumentor().instrument()
            return True

        # Try MistralAI integration
        if importlib.util.find_spec("mistralai"):
            from openinference.instrumentation.mistralai import MistralAIInstrumentor
            MistralAIInstrumentor().instrument()
            return True

        # Try Portkey integration
        if importlib.util.find_spec("portkey"):
            from openinference.instrumentation.portkey import PortkeyInstrumentor
            PortkeyInstrumentor().instrument()
            return True

        # Try Guardrails integration
        if importlib.util.find_spec("guardrails"):
            from openinference.instrumentation.guardrails import GuardrailsInstrumentor
            GuardrailsInstrumentor().instrument()
            return True

        # Try VertexAI integration
        if importlib.util.find_spec("vertexai"):
            from openinference.instrumentation.vertexai import VertexAIInstrumentor
            VertexAIInstrumentor().instrument()
            return True

        # Try Haystack integration
        if importlib.util.find_spec("haystack"):
            from openinference.instrumentation.haystack import HaystackInstrumentor
            HaystackInstrumentor().instrument()
            return True

        # Try liteLLM integration
        if importlib.util.find_spec("litellm"):
            from openinference.instrumentation.litellm import LiteLLMInstrumentor
            LiteLLMInstrumentor().instrument()
            return True

        # Try Groq integration
        if importlib.util.find_spec("groq"):
            from openinference.instrumentation.groq import GroqInstrumentor
            GroqInstrumentor().instrument()
            return True

        # Try Instructor integration
        if importlib.util.find_spec("instructor"):
            from openinference.instrumentation.instructor import InstructorInstrumentor
            InstructorInstrumentor().instrument()
            return True

        # Try Anthropic integration
        if importlib.util.find_spec("anthropic"):
            from openinference.instrumentation.anthropic import AnthropicInstrumentor
            AnthropicInstrumentor().instrument()
            return True

        # Try BeeAI integration
        if importlib.util.find_spec("beeai"):
            from openinference.instrumentation.beeai import BeeAIInstrumentor
            BeeAIInstrumentor().instrument()
            return True

        # Try Google GenAI integration
        if importlib.util.find_spec("google.generativeai"):
            from openinference.instrumentation.google_genai import GoogleGenAIInstrumentor
            GoogleGenAIInstrumentor().instrument()
            return True

        # Try Autogen AgentChat integration
        if importlib.util.find_spec("autogen"):
            from openinference.instrumentation.autogen_agentchat import AutogenAgentChatInstrumentor
            AutogenAgentChatInstrumentor().instrument()
            return True

        # Try PydanticAI integration
        if importlib.util.find_spec("pydantic_ai"):
            from openinference.instrumentation.pydantic_ai import PydanticAIInstrumentor
            PydanticAIInstrumentor().instrument()
            return True
            
    except Exception as e:
        print(f"Warning: Framework detection failed: {e}")
        
    return False

# Try to set up native integration
USING_NATIVE_INTEGRATION = _setup_native_integration()

@dataclass
class SpanContext:
    """
    Context for a trace span
    
    Args:
        name: Name of the span
        input: Optional input data to record
        metadata: Optional metadata to attach
        user_id: Optional user identifier to associate with the trace
        session_id: Optional session identifier
        tags: Optional list of tags
    """
    name: str
    input: Optional[Any] = None
    metadata: Optional[Dict[str, Any]] = None
    user_id: Optional[str] = None
    session_id: Optional[str] = None
    tags: Optional[list] = None

class TracingBackend(ABC):
    """Abstract base class for tracing backends"""
    
    @abstractmethod
    def start_span(self, context: SpanContext) -> Any:
        """Start a new span"""
        pass
        
    @abstractmethod
    def end_span(self, span: Any, output: Optional[Any] = None):
        """End a span"""
        pass
        
    @abstractmethod
    def update_span(self, span: Any, **kwargs):
        """Update span data"""
        pass
        
    @abstractmethod
    def start_generation(self, context: SpanContext, model: str, **kwargs) -> Any:
        """Start an LLM generation span"""
        pass
        
    @abstractmethod
    def flush(self):
        """Flush traces to backend"""
        pass

class LangfuseBackend(TracingBackend):
    """Langfuse implementation of tracing backend"""
    
    def __init__(self):
        try:
            from langfuse import Langfuse
            self.client = Langfuse()
            self.span_stack = []  # Stack to track spans for cleanup
        except ImportError:
            raise ImportError(
                "Langfuse package is required for LangfuseBackend. "
                "Install it with: pip install langfuse"
            )
    
    def trace(self, name: Optional[str] = None, **kwargs):
        """
        A decorator that uses Langfuse's @observe for automatic tracing.
        
        Args:
            name: Optional name for the trace/span. If not provided, uses function name.
            **kwargs: Additional keyword arguments passed to observe.
            
        Returns:
            Decorated function with tracing enabled.
        """
        def decorator(func):
            # Use Langfuse's built-in observe decorator
            from langfuse import observe, get_client
            
            @wraps(func)
            async def async_wrapper(*args, **func_kwargs):
                global _AGENT_NAME, _CURRENT_SESSION_ID
                # Get the Langfuse client
                langfuse = get_client()
                
                # Call the function with observe
                result = await observe(name=name or func.__name__, **kwargs)(func)(*args, **func_kwargs)
                
                # Add agent name tag and session ID after the trace is created
                if _AGENT_NAME or _CURRENT_SESSION_ID:
                    trace_update = {}
                    if _AGENT_NAME:
                        trace_update['tags'] = [_AGENT_NAME]
                    if _CURRENT_SESSION_ID:
                        trace_update['session_id'] = _CURRENT_SESSION_ID
                    langfuse.update_current_trace(**trace_update)
                
                return result
                
            @wraps(func)
            def sync_wrapper(*args, **func_kwargs):
                global _AGENT_NAME, _CURRENT_SESSION_ID
                # Get the Langfuse client
                langfuse = get_client()
                
                # Call the function with observe
                result = observe(name=name or func.__name__, **kwargs)(func)(*args, **func_kwargs)
                
                # Add agent name tag and session ID after the trace is created
                if _AGENT_NAME or _CURRENT_SESSION_ID:
                    trace_update = {}
                    if _AGENT_NAME:
                        trace_update['tags'] = [_AGENT_NAME]
                    if _CURRENT_SESSION_ID:
                        trace_update['session_id'] = _CURRENT_SESSION_ID
                    langfuse.update_current_trace(**trace_update)
                
                return result
                
            return async_wrapper if asyncio.iscoroutinefunction(func) else sync_wrapper
        return decorator

    def start_span(self, context: SpanContext) -> Any:
        """Start a new span"""
        global _AGENT_NAME, _CURRENT_SESSION_ID
        if isinstance(context, str):
            context = SpanContext(name=context)
        
        if _AGENT_NAME:
            if context.tags is None:
                context.tags = []
            if _AGENT_NAME not in context.tags:
                context.tags.append(_AGENT_NAME)
        
        # Add session ID if set
        if _CURRENT_SESSION_ID and not context.session_id:
            context.session_id = _CURRENT_SESSION_ID
        
        # Add user ID if set
        if _CURRENT_USER_ID and not context.user_id:
            context.user_id = _CURRENT_USER_ID
        
        # Use Langfuse's context management for nested spans
        # This will automatically create child spans when called within an existing span context
        span_kwargs = {
            'name': context.name,
            'input': context.input,
            'metadata': context.metadata,
            'tags': context.tags
        }
        
        # Remove None values
        span_kwargs = {k: v for k, v in span_kwargs.items() if v is not None}
        
        # Use start_as_current_span to leverage Langfuse's automatic nesting
        span = self.client.start_as_current_span(**span_kwargs)
        
        # Update session ID after span creation if needed
        if context.session_id:
            self.client.update_current_trace(session_id=context.session_id)
        
        # Update user ID after span creation if needed
        if context.user_id:
            self.client.update_current_trace(user_id=context.user_id)
        
        # Track span for proper cleanup
        self.span_stack.append(span)
        return span
        
    def end_span(self, span: Any, output: Optional[Any] = None):
        if USING_NATIVE_INTEGRATION or not span:
            return
            
        if output is not None:
            span.update(output=output)
        span.end()
        
        # Remove span from stack
        if self.span_stack and self.span_stack[-1] == span:
            self.span_stack.pop()
        
    def update_span(self, span: Any, **kwargs):
        if USING_NATIVE_INTEGRATION or not span:
            return
            
        span.update(**kwargs)
        
    def start_generation(self, context: SpanContext, model: str, **kwargs) -> Any:
        """Start an LLM generation span"""
        global _AGENT_NAME, _CURRENT_SESSION_ID
        if isinstance(context, str):
            context = SpanContext(name=context)
            
        if _AGENT_NAME:
            if context.tags is None:
                context.tags = []
            if _AGENT_NAME not in context.tags:
                context.tags.append(_AGENT_NAME)
                
        # Add session ID if set
        if _CURRENT_SESSION_ID and not context.session_id:
            context.session_id = _CURRENT_SESSION_ID
                
        # Add user ID if set
        if _CURRENT_USER_ID and not context.user_id:
            context.user_id = _CURRENT_USER_ID
                
        # Filter out parameters that Langfuse start_generation doesn't accept
        generation_kwargs = {
            'name': context.name,
            'model': model,
            'input': context.input,
            'metadata': context.metadata,
            'tags': context.tags,
            **kwargs
        }
        
        # Remove None values
        generation_kwargs = {k: v for k, v in generation_kwargs.items() if v is not None}
        
        generation = self.client.start_generation(**generation_kwargs)
        
        # Update session ID after generation creation if needed
        if context.session_id:
            self.client.update_current_trace(session_id=context.session_id)
            
        # Update user ID after generation creation if needed
        if context.user_id:
            self.client.update_current_trace(user_id=context.user_id)
            
        return generation
        
    def flush(self):
        self.client.flush()

# Factory function to get the configured backend
def get_tracer() -> TracingBackend:
    """Get the configured tracing backend"""
    if DEFAULT_TRACER == 'langfuse':
        return LangfuseBackend()
    # Add more backends here as needed
    raise ValueError(f"Unknown tracing backend: {DEFAULT_TRACER}")

# Global tracer instance
_tracer = get_tracer()

# Global trace state to ensure all operations go into the same trace
_global_trace_context = None

def trace(name: Optional[str] = None, **kwargs):
    """
    A decorator that provides automatic tracing, independent of the backend.
    This will create custom spans even if native integration is present.
    WARNING: You may get duplicate traces if both native and custom spans are used for the same function.
    
    Args:
        name: Optional name for the trace/span. If not provided, uses function name.
        **kwargs: Additional keyword arguments passed to the span context.
        
    Returns:
        Decorated function with tracing enabled.
    """
    # If using Langfuse, delegate to its observe decorator for better integration
    if DEFAULT_TRACER == 'langfuse':
        return _tracer.trace(name, **kwargs)
        
    def decorator(func):
        @wraps(func)
        async def async_wrapper(*args, **func_kwargs):
            context = SpanContext(
                name=name or func.__name__,
                input={"args": args, "kwargs": func_kwargs},
                **kwargs
            )
            
            with start_span(context) as span:
                try:
                    result = await func(*args, **func_kwargs)
                    if span:
                        _tracer.update_span(span, output=result)
                    return result
                except Exception as e:
                    if span:
                        _tracer.update_span(span, error=str(e))
                    raise
                    
        @wraps(func)
        def sync_wrapper(*args, **func_kwargs):
            context = SpanContext(
                name=name or func.__name__,
                input={"args": args, "kwargs": func_kwargs},
                **kwargs
            )
            
            with start_span(context) as span:
                try:
                    result = func(*args, **func_kwargs)
                    if span:
                        _tracer.update_span(span, output=result)
                    return result
                except Exception as e:
                    if span:
                        _tracer.update_span(span, error=str(e))
                    raise
                    
        return async_wrapper if asyncio.iscoroutinefunction(func) else sync_wrapper
    return decorator

@contextmanager
def start_span(context: Union[str, SpanContext], **kwargs):
    """
    Start a new span using the configured backend.
    This will create custom spans even if native integration is present.
    WARNING: You may get duplicate traces if both native and custom spans are used for the same function.
    
    Args:
        context: Either a string name for the span or a SpanContext object
        **kwargs: Additional keyword arguments for the span context if using string name
        
    Yields:
        The created span object
    """
    global _global_trace_context
    
    if isinstance(context, str):
        context = SpanContext(name=context, **kwargs)
    
    # Use Langfuse's built-in context manager for proper nesting
    if DEFAULT_TRACER == 'langfuse':
        span_kwargs = {
            'name': context.name,
            'input': context.input,
            'metadata': context.metadata,
            'tags': context.tags
        }
        # Remove None values
        span_kwargs = {k: v for k, v in span_kwargs.items() if v is not None}
        
        # If this is the first span, it will create a new trace automatically
        # Subsequent spans will be nested within the current trace context
        with _tracer.client.start_as_current_span(**span_kwargs) as span:
            # Store trace context if this is the first span
            if _global_trace_context is None:
                _global_trace_context = _tracer.client.get_current_trace_id()
            yield span
    else:
        # Fallback for other backends
        span = _tracer.start_span(context)
        try:
            yield span
        finally:
            _tracer.end_span(span)

@contextmanager
def start_generation(name: str, model: str, **kwargs):
    """
    Start a new generation span using the configured backend.
    This will create custom spans even if native integration is present.
    WARNING: You may get duplicate traces if both native and custom spans are used for the same function.
    
    Args:
        name: Name for the generation span
        model: Name/identifier of the model being used
        **kwargs: Additional keyword arguments for the span context
        
    Yields:
        The created generation span object
    """
    context = SpanContext(name=name, **kwargs)
    span = _tracer.start_generation(context, model, **kwargs)
    try:
        yield span
    finally:
        _tracer.end_span(span)

def flush():
    """Flush traces to the configured backend."""
    _tracer.flush() 