"""
Agent Configuration Module

This module provides the AgentConfig class for managing agent configuration
including system messages, LLM settings, and agent identity.
"""

import json
from pathlib import Path
from typing import Dict, Any, Optional
from .agent_identity import AgentIdentity


class AgentConfig:
    """Manages agent configuration including system messages and settings."""
    
    def __init__(self):
        self.config_dir = Path.home() / ".metis_agent"
        self.config_file = self.config_dir / "config.json"
        self.config_dir.mkdir(exist_ok=True)
        self._load_config()
        
        # Initialize agent identity
        self.agent_identity = AgentIdentity(config=self)
    
    def _load_config(self):
        """Load configuration from file."""
        if self.config_file.exists():
            try:
                with open(self.config_file, 'r') as f:
                    self.config = json.load(f)
            except (json.JSONDecodeError, IOError):
                self.config = self._get_default_config()
        else:
            self.config = self._get_default_config()
    
    def _get_default_config(self) -> Dict[str, Any]:
        """Get default configuration."""
        return {
            "llm_provider": "groq",
            "llm_model": None,
            "ollama_base_url": "http://localhost:11434",
            "huggingface_device": "auto",
            "huggingface_quantization": "none",
            "huggingface_max_length": 512,
            "memory_enabled": True,
            "titans_memory": True,
            "session_timeout": 3600,
            "max_context_length": 4000,
            "auto_save": True
        }
    
    def save_config(self):
        """Save configuration to file."""
        try:
            with open(self.config_file, 'w') as f:
                json.dump(self.config, f, indent=2)
        except IOError as e:
            print(f"Error saving config: {e}")
    
    def get(self, key: str, default=None):
        """Get configuration value."""
        return self.config.get(key, default)
    
    def set(self, key: str, value: Any):
        """Set configuration value."""
        self.config[key] = value
        if self.config.get("auto_save", True):
            self.save_config()
    
    def show_config(self):
        """Display current configuration."""
        print("Current Configuration:")
        for key, value in self.config.items():
            print(f"  {key}: {value}")
    
    # LLM Configuration Methods
    def set_llm_provider(self, provider: str):
        """Set LLM provider (groq, openai, anthropic, huggingface, ollama)."""
        valid_providers = ["groq", "openai", "anthropic", "huggingface", "ollama"]
        if provider not in valid_providers:
            raise ValueError(f"Invalid provider. Must be one of: {valid_providers}")
        self.set("llm_provider", provider)
    
    def set_llm_model(self, model: str):
        """Set specific LLM model."""
        self.set("llm_model", model)
    
    def get_llm_provider(self) -> str:
        """Get current LLM provider."""
        return self.get("llm_provider", "groq")
    
    def get_llm_model(self) -> Optional[str]:
        """Get current LLM model."""
        return self.get("llm_model")
    
    def set_ollama_base_url(self, base_url: str):
        """Set Ollama server base URL."""
        self.set("ollama_base_url", base_url)
    
    def get_ollama_base_url(self) -> str:
        """Get Ollama server base URL."""
        return self.get("ollama_base_url", "http://localhost:11434")
    
    def set_huggingface_device(self, device: str):
        """Set HuggingFace model device (auto, cpu, cuda, mps)."""
        valid_devices = ["auto", "cpu", "cuda", "mps"]
        if device not in valid_devices:
            raise ValueError(f"Invalid device. Must be one of: {valid_devices}")
        self.set("huggingface_device", device)
    
    def get_huggingface_device(self) -> str:
        """Get HuggingFace model device."""
        return self.get("huggingface_device", "auto")
    
    def set_huggingface_quantization(self, quantization: str):
        """Set HuggingFace model quantization (none, 8bit, 4bit)."""
        valid_quant = ["none", "8bit", "4bit"]
        if quantization not in valid_quant:
            raise ValueError(f"Invalid quantization. Must be one of: {valid_quant}")
        self.set("huggingface_quantization", quantization)
    
    def get_huggingface_quantization(self) -> str:
        """Get HuggingFace model quantization."""
        return self.get("huggingface_quantization", "none")
    
    def set_huggingface_max_length(self, max_length: int):
        """Set HuggingFace model max sequence length."""
        if max_length < 1:
            raise ValueError("Max length must be positive")
        self.set("huggingface_max_length", max_length)
    
    def get_huggingface_max_length(self) -> int:
        """Get HuggingFace model max sequence length."""
        return self.get("huggingface_max_length", 512)
    
    # Memory Configuration Methods
    def set_memory_enabled(self, enabled: bool):
        """Enable or disable conversation memory."""
        self.set("memory_enabled", enabled)
    
    def set_titans_memory(self, enabled: bool):
        """Enable or disable Titans memory enhancement."""
        self.set("titans_memory", enabled)
    
    def is_memory_enabled(self) -> bool:
        """Check if memory is enabled."""
        return self.get("memory_enabled", True)
    
    def is_titans_memory_enabled(self) -> bool:
        """Check if Titans memory is enabled."""
        return self.get("titans_memory", True)
    
    # Session Configuration Methods
    def set_session_timeout(self, timeout: int):
        """Set session timeout in seconds."""
        self.set("session_timeout", timeout)
    
    def set_max_context_length(self, length: int):
        """Set maximum context length."""
        self.set("max_context_length", length)
    
    def get_session_timeout(self) -> int:
        """Get session timeout."""
        return self.get("session_timeout", 3600)
    
    def get_max_context_length(self) -> int:
        """Get maximum context length."""
        return self.get("max_context_length", 4000)
    
    # API Key Management Methods
    def set_api_key(self, provider: str, api_key: str):
        """Set API key for a provider."""
        from ..auth.api_key_manager import APIKeyManager
        key_manager = APIKeyManager()
        key_manager.set_key(provider, api_key)
    
    def get_api_key(self, provider: str) -> Optional[str]:
        """Get API key for a provider."""
        from ..auth.api_key_manager import APIKeyManager
        key_manager = APIKeyManager()
        return key_manager.get_key(provider)
    
    def has_api_key(self, provider: str) -> bool:
        """Check if API key exists for provider."""
        return self.get_api_key(provider) is not None
    
    # Identity Management Methods
    def get_agent_name(self) -> str:
        """Get agent name."""
        return self.agent_identity.agent_name
    
    def set_agent_name(self, name: str):
        """Set agent name."""
        self.agent_identity.update_name(name)
    
    def get_agent_id(self) -> str:
        """Get agent ID."""
        return self.agent_identity.agent_id
    
    def get_system_message(self) -> str:
        """Get full system message."""
        return self.agent_identity.get_full_system_message()
    
    def set_personality(self, personality: str):
        """Set custom personality."""
        self.agent_identity.update_custom_system_message(personality)
    
    def regenerate_identity(self):
        """Generate new agent identity."""
        self.agent_identity.regenerate_identity()
    
    # Utility Methods
    def reset_to_defaults(self):
        """Reset configuration to defaults."""
        self.config = self._get_default_config()
        self.save_config()
    
    def export_config(self) -> Dict[str, Any]:
        """Export current configuration."""
        return self.config.copy()
    
    def import_config(self, config_data: Dict[str, Any]):
        """Import configuration from dictionary."""
        self.config.update(config_data)
        self.save_config()
    
    def __str__(self) -> str:
        """String representation of configuration."""
        return f"AgentConfig(provider={self.get_llm_provider()}, memory={self.is_memory_enabled()}, agent={self.get_agent_name()})"
    
    def __repr__(self) -> str:
        """Detailed representation of configuration."""
        return f"AgentConfig({self.config})"
