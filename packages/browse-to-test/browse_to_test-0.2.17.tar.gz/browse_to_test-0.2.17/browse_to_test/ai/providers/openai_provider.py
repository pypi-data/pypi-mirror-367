"""OpenAI provider implementation."""

import time
import asyncio
import aiohttp
import logging
from typing import Dict, List, Optional, Any
from ..base import AIProvider, AIResponse, AIProviderError
from ..error_handler import AIErrorHandler, ExponentialBackoffStrategy, ErrorType
from ..prompt_optimizer import PromptOptimizer, PromptTemplate


logger = logging.getLogger(__name__)


class OpenAIProvider(AIProvider):
    """OpenAI API provider for generating test code."""
    
    def __init__(self, api_key: Optional[str] = None, **kwargs):
        """Initialize OpenAI provider."""
        super().__init__(api_key=api_key, **kwargs)
        
        # Set configuration attributes
        self.model = kwargs.get('model', 'gpt-4')
        self.temperature = kwargs.get('temperature', 0.1)
        self.max_tokens = kwargs.get('max_tokens', 4000)
        self.timeout = kwargs.get('timeout', 30)
        self.retry_attempts = kwargs.get('retry_attempts', 3)
        self.api_base_url = kwargs.get('api_base_url', 'https://api.openai.com/v1')
        self.extra_params = {k: v for k, v in kwargs.items()
                             if k not in ['model', 'temperature', 'max_tokens', 'timeout', 'retry_attempts', 'api_base_url']}
        
        # Initialize enhanced error handling and optimization
        self.error_handler = AIErrorHandler(
            retry_strategy=ExponentialBackoffStrategy(
                base_delay=1.0,
                max_delay=30.0,
                max_attempts=self.retry_attempts
            )
        )
        self.prompt_optimizer = PromptOptimizer()
        
        # Import OpenAI here to avoid dependency issues
        try:
            import openai
            self.openai = openai
        except ImportError:
            raise AIProviderError(
                "OpenAI package not installed. Please install with: pip install openai",
                provider="openai"
            )
        
        # Set up the client only if we have an API key (either provided or in environment)
        import os
        effective_api_key = self.api_key or os.getenv("OPENAI_API_KEY")
        
        if effective_api_key:
            self.client = self.openai.OpenAI(
                api_key=effective_api_key,
                base_url=kwargs.get('api_base_url'),
                timeout=self.timeout
            )
            # Set up async client
            self.async_client = self.openai.AsyncOpenAI(
                api_key=effective_api_key,
                base_url=kwargs.get('api_base_url'),
                timeout=self.timeout
            )
        else:
            # No API key available - don't create clients to avoid hanging
            # Validation will catch this and provide a proper error message
            self.client = None
            self.async_client = None
    
    @property
    def provider_name(self) -> str:
        """Return the provider name."""
        return "openai"
    
    @property
    def supported_models(self) -> List[str]:
        """Return list of supported models."""
        return [
            "gpt-4.1",
            "gpt-4.1-mini",
            "gpt-4o-mini",
        ]
    
    def validate_config(self) -> List[str]:
        """Validate the provider configuration."""
        errors = []
        
        # Check if API key is available (either provided or in environment)
        if not self.api_key:
            import os
            if not os.getenv("OPENAI_API_KEY"):
                errors.append("OpenAI API key not provided and OPENAI_API_KEY environment variable not set")
        
        # Validate model
        if self.model not in self.supported_models:
            errors.append(f"Model '{self.model}' is not supported by OpenAI provider. Supported models: {', '.join(self.supported_models)}")
        
        # Validate parameters
        if self.temperature < 0 or self.temperature > 2:
            errors.append("Temperature must be between 0 and 2")
        
        if self.max_tokens <= 0:
            errors.append("max_tokens must be positive")
        
        return errors
    
    def generate(
        self, 
        prompt: str, 
        system_prompt: Optional[str] = None,
        **kwargs
    ) -> AIResponse:
        """Generate content using OpenAI."""
        
        # Check if client is available (API key was provided)
        if not self.client:
            raise AIProviderError(
                "OpenAI API key not available. Please provide an API key or set OPENAI_API_KEY environment variable.",
                provider=self.provider_name,
                model=self.model
            )
        
        start_time = time.time()
        
        # Prepare messages
        messages = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        messages.append({"role": "user", "content": prompt})
        
        # Calculate message character counts for logging
        total_chars = len(prompt) + (len(system_prompt) if system_prompt else 0)
        logger.info(f"🔄 OpenAI API call starting - Model: {self.model}, Characters: {total_chars:,}")
        
        # Merge any additional parameters
        generation_params = {
            "model": self.model,
            "messages": messages,
            "temperature": self.temperature,
            "max_tokens": self.max_tokens,
            **self.extra_params,
            **kwargs
        }
        
        try:
            response = self._make_request_with_retry(
                self.client.chat.completions.create,
                **generation_params
            )
            
            end_time = time.time()
            response_time = end_time - start_time
            
            # Extract response data
            content = response.choices[0].message.content
            usage = response.usage
            
            # Log completion details
            response_chars = len(content) if content else 0
            prompt_tokens = usage.prompt_tokens if usage else 0
            completion_tokens = usage.completion_tokens if usage else 0
            total_tokens = usage.total_tokens if usage else 0
            
            logger.info(f"✅ OpenAI API call completed - "
                       f"Time: {response_time:.2f}s, "
                       f"Response chars: {response_chars:,}, "
                       f"Tokens: {total_tokens:,} ({prompt_tokens:,} prompt + {completion_tokens:,} completion)")
            
            return AIResponse(
                content=content,
                model=self.model,
                provider=self.provider_name,
                tokens_used=usage.total_tokens if usage else None,
                finish_reason=response.choices[0].finish_reason,
                metadata={
                    "prompt_tokens": usage.prompt_tokens if usage else None,
                    "completion_tokens": usage.completion_tokens if usage else None,
                    "response_time": response_time,
                    "response_id": response.id,
                    "created": response.created,
                    "input_chars": total_chars,
                    "output_chars": response_chars,
                }
            )
            
        except Exception as e:
            end_time = time.time()
            error_time = end_time - start_time
            
            # Handle OpenAI-specific errors
            if hasattr(self.openai, 'OpenAIError') and isinstance(e, self.openai.OpenAIError):
                if hasattr(e, 'code'):
                    error_msg = f"OpenAI API error ({e.code}): {e}"
                else:
                    error_msg = f"OpenAI API error: {e}"
            else:
                error_msg = f"OpenAI request failed: {e}"
            
            logger.error(f"❌ OpenAI sync API call failed - "
                        f"Time: {error_time:.2f}s, "
                        f"Input chars: {total_chars:,}, "
                        f"Error: {error_msg}")
            
            raise AIProviderError(
                error_msg,
                provider=self.provider_name,
                model=self.model
            ) from e
    
    async def generate_async(
        self, 
        prompt: str, 
        system_prompt: Optional[str] = None,
        **kwargs
    ) -> AIResponse:
        """Generate content using OpenAI asynchronously."""
        
        # Check if client is available (API key was provided)
        if not self.async_client:
            raise AIProviderError(
                "OpenAI API key not available. Please provide an API key or set OPENAI_API_KEY environment variable.",
                provider=self.provider_name,
                model=self.model
            )
        
        start_time = time.time()
        
        # Prepare messages
        messages = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        messages.append({"role": "user", "content": prompt})
        
        # Calculate message character counts for logging
        total_chars = len(prompt) + (len(system_prompt) if system_prompt else 0)
        logger.info(f"🔄 OpenAI async API call starting - Model: {self.model}, Characters: {total_chars:,}")
        
        # Merge any additional parameters
        generation_params = {
            "model": self.model,
            "messages": messages,
            "temperature": self.temperature,
            "max_tokens": self.max_tokens,
            **self.extra_params,
            **kwargs
        }
        
        try:
            response = await self._make_async_request_with_retry(
                self.async_client.chat.completions.create,
                **generation_params
            )
            
            end_time = time.time()
            response_time = end_time - start_time
            
            # Extract response data
            content = response.choices[0].message.content
            usage = response.usage
            
            # Log completion details
            response_chars = len(content) if content else 0
            prompt_tokens = usage.prompt_tokens if usage else 0
            completion_tokens = usage.completion_tokens if usage else 0
            total_tokens = usage.total_tokens if usage else 0
            
            logger.info(f"✅ OpenAI async API call completed - "
                       f"Time: {response_time:.2f}s, "
                       f"Response chars: {response_chars:,}, "
                       f"Tokens: {total_tokens:,} ({prompt_tokens:,} prompt + {completion_tokens:,} completion)")
            
            return AIResponse(
                content=content,
                model=self.model,
                provider=self.provider_name,
                tokens_used=usage.total_tokens if usage else None,
                finish_reason=response.choices[0].finish_reason,
                metadata={
                    "prompt_tokens": usage.prompt_tokens if usage else None,
                    "completion_tokens": usage.completion_tokens if usage else None,
                    "response_time": response_time,
                    "response_id": response.id,
                    "created": response.created,
                    "input_chars": total_chars,
                    "output_chars": response_chars,
                }
            )
            
        except Exception as e:
            end_time = time.time()
            error_time = end_time - start_time
            
            # Handle OpenAI-specific errors
            if hasattr(self.openai, 'OpenAIError') and isinstance(e, self.openai.OpenAIError):
                if hasattr(e, 'code'):
                    error_msg = f"OpenAI API error ({e.code}): {e}"
                else:
                    error_msg = f"OpenAI API error: {e}"
            else:
                error_msg = f"OpenAI request failed: {e}"
            
            logger.error(f"❌ OpenAI async API call failed - "
                        f"Time: {error_time:.2f}s, "
                        f"Input chars: {total_chars:,}, "
                        f"Error: {error_msg}")
            
            raise AIProviderError(
                error_msg,
                provider=self.provider_name,
                model=self.model
            ) from e
    
    def is_available(self) -> bool:
        """Check if the OpenAI provider is available."""
        try:
            # Check if we have an API key (either provided or in environment)
            if self.api_key:
                return True
            
            import os
            return bool(os.getenv("OPENAI_API_KEY"))
        except Exception:
            return False
    
    def get_model_info(self) -> Dict[str, Any]:
        """Get information about the current model."""
        import os
        return {
            "name": self.model,
            "provider": self.provider_name,
            "max_tokens": self.max_tokens,
            "temperature": self.temperature,
            "supported_models": self.supported_models,
            "api_key_available": bool(self.api_key or os.getenv("OPENAI_API_KEY")),
        }
    
    def _make_request_with_retry(self, request_func, **kwargs):
        """Make request with enhanced retry logic."""
        return self.error_handler.handle_with_retry_sync(
            request_func,
            provider="openai",
            model=self.model,
            **kwargs
        )
    
    async def _make_async_request_with_retry(self, request_func, **kwargs):
        """Make async request with enhanced retry logic."""
        async def wrapped_request():
            return await request_func(**kwargs)
        
        return await self.error_handler.handle_with_retry(
            wrapped_request,
            provider="openai",
            model=self.model
        )