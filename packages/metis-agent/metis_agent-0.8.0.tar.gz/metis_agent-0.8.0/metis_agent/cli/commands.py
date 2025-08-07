"""
Simplified CLI for Metis Agent.

This module provides a streamlined command-line interface focused on:
1. Interactive natural language interface
2. Configuration management  
3. Authentication management
"""
import os
import click
from pathlib import Path
from ..core.agent_config import AgentConfig
from ..auth.api_key_manager import APIKeyManager
from ..core import SingleAgent
from .code_commands import code as code_command
from .knowledge_commands import knowledge_cli


@click.group()
def cli():
    """Metis Agent - Intelligent AI Assistant"""
    pass


# Add the code command to the CLI
cli.add_command(code_command)


@cli.command()
@click.argument("query", required=False)
@click.option("--session", "-s", help="Session ID for context")
def chat(query, session):
    """Start interactive chat or process a single query."""
    config = AgentConfig()
    
    # Initialize agent with config settings
    agent = SingleAgent(
        use_titans_memory=config.is_titans_memory_enabled(),
        llm_provider=config.get_llm_provider(),
        llm_model=config.get_llm_model(),
        enhanced_processing=True,
        config=config
    )
    
    if query:
        # Single query mode
        try:
            response = agent.process_query(query, session_id=session)
            if isinstance(response, dict):
                click.echo(response.get("response", str(response)))
            else:
                click.echo(response)
        except Exception as e:
            click.echo(f"Error: {e}")
        return
    
    # Interactive mode
    _start_interactive_mode(agent, config, session)


def _show_welcome_logo():
    """Display colorful Metis Agent logo."""
    # ANSI color codes
    BLUE = '\033[94m'
    MAGENTA = '\033[95m'
    CYAN = '\033[96m'
    WHITE = '\033[97m'
    BOLD = '\033[1m'
    RESET = '\033[0m'
    
    logo = f"""
{BLUE}{BOLD}    ###   ### {MAGENTA}####### {CYAN}######## {WHITE}## {MAGENTA}#######{RESET}
{BLUE}{BOLD}    #### #### {MAGENTA}##      {CYAN}   ##    {WHITE}## {MAGENTA}##     {RESET}
{BLUE}{BOLD}    ## ### ## {MAGENTA}#####   {CYAN}   ##    {WHITE}## {MAGENTA}#######{RESET}
{BLUE}{BOLD}    ##  #  ## {MAGENTA}##      {CYAN}   ##    {WHITE}## {MAGENTA}     ##{RESET}
{BLUE}{BOLD}    ##     ## {MAGENTA}####### {CYAN}   ##    {WHITE}## {MAGENTA}#######{RESET}

{CYAN}{BOLD}                    AGENTS v0.6.0{RESET}
{WHITE}              General Purpose AI Agent{RESET}
"""
    click.echo(logo)


def _start_interactive_mode(agent: SingleAgent, config: AgentConfig, session_id: str = None):
    """Start interactive chat mode."""
    current_dir = Path.cwd()
    current_session = session_id or "main"
    
    # Show colorful welcome logo
    _show_welcome_logo()
    click.echo(f"\nDirectory: {current_dir}")
    click.echo(f"Session: {current_session}")
    
    # Show project context if available
    try:
        from ..tools.project_context import ProjectContextTool
        project_tool = ProjectContextTool()
        project_summary = project_tool.get_project_summary(".")
        
        if project_summary.get("success"):
            summary = project_summary["summary"]
            if summary.get("primary_language"):
                context_info = f"Project: {summary['project_name']} ({summary['primary_language']}"
                if summary.get('framework'):
                    context_info += f", {summary['framework']}"
                context_info += f", {summary['file_count']} files)"
                click.echo(context_info)
    except Exception:
        pass  # Project context not available
    
    click.echo("\nJust type your request in natural language!")
    click.echo("Examples:")
    click.echo("  - 'Create a Python web app with FastAPI'")
    click.echo("  - 'Analyze the code in this project'")
    click.echo("  - 'Search for information about quantum computing'")
    click.echo("  - 'Help me debug this error'")
    click.echo("\nSpecial commands:")
    click.echo("  - 'exit' or 'quit' - Exit chat")
    click.echo("  - 'session <name>' - Switch session")
    click.echo("  - 'clear' - Clear screen")
    click.echo("  - 'help' - Show this help")
    click.echo("=" * 60)
    
    while True:
        try:
            user_input = input(f"\n[{current_session}] > ").strip()
            
            if not user_input:
                continue
            
            # Handle special commands
            if user_input.lower() in ['exit', 'quit', 'bye']:
                click.echo("Goodbye!")
                break
            
            elif user_input.lower() == 'clear':
                os.system('cls' if os.name == 'nt' else 'clear')
                continue
            
            elif user_input.lower() == 'help':
                click.echo("\nJust type your request in natural language!")
                click.echo("The agent will understand and help you with:")
                click.echo("  - Code generation and analysis")
                click.echo("  - Project scaffolding and management")
                click.echo("  - Web search and research")
                click.echo("  - Content creation and writing")
                click.echo("  - Git operations and version control")
                click.echo("  - File operations and project exploration")
                continue
            
            elif user_input.lower().startswith('session '):
                new_session = user_input[8:].strip()
                if new_session:
                    current_session = new_session
                    click.echo(f"Switched to session: {current_session}")
                continue
            
            # Process query with agent
            try:
                click.echo("Thinking...")
                response = agent.process_query(user_input, session_id=current_session)
                
                click.echo("\nMetis:")
                if isinstance(response, dict):
                    click.echo(response.get("response", str(response)))
                else:
                    click.echo(response)
                    
            except KeyboardInterrupt:
                click.echo("\nInterrupted. Type 'exit' to quit.")
                continue
            except Exception as e:
                click.echo(f"\nError: {e}")
                click.echo("Try rephrasing your request or check your configuration.")
                
        except KeyboardInterrupt:
            click.echo("\nGoodbye!")
            break
        except EOFError:
            click.echo("\nGoodbye!")
            break


@cli.group()
def config():
    """Manage agent configuration and settings."""
    pass


# Add knowledge commands to config group
config.add_command(knowledge_cli)


@config.command("show")
def show_config():
    """Show current configuration."""
    config = AgentConfig()
    config.show_config()
    
    # Show provider-specific status
    provider = config.get_llm_provider()
    
    if provider == "ollama":
        click.echo("\nOllama Status:")
        base_url = config.get_ollama_base_url()
        click.echo(f"  Base URL: {base_url}")
        
        try:
            import requests
            response = requests.get(f"{base_url}/api/tags", timeout=3)
            response.raise_for_status()
            models = response.json().get("models", [])
            click.echo(f"  Status: [OK] Connected ({len(models)} models available)")
        except Exception as e:
            click.echo(f"  Status: [NO] Not connected - {e}")
            click.echo("  Make sure Ollama is installed and running.")
    
    elif provider == "huggingface":
        click.echo("\nHuggingFace Configuration:")
        click.echo(f"  Device: {config.get_huggingface_device()}")
        click.echo(f"  Quantization: {config.get_huggingface_quantization()}")
        click.echo(f"  Max Length: {config.get_huggingface_max_length()}")
        
        # Check if transformers is installed
        try:
            import transformers
            import torch
            click.echo(f"  Transformers: [OK] Installed (v{transformers.__version__})")
            click.echo(f"  PyTorch: [OK] Installed (v{torch.__version__})")
            
            # Check device availability
            device = config.get_huggingface_device()
            if device == "auto" or device == "cuda":
                if torch.cuda.is_available():
                    click.echo(f"  CUDA: [OK] Available ({torch.cuda.device_count()} devices)")
                else:
                    click.echo(f"  CUDA: [NO] Not available")
            
            if device == "auto" or device == "mps":
                if hasattr(torch.backends, 'mps') and torch.backends.mps.is_available():
                    click.echo(f"  MPS: [OK] Available")
                else:
                    click.echo(f"  MPS: [NO] Not available")
                    
        except ImportError:
            click.echo(f"  Status: [NO] Missing dependencies")
            click.echo("  Install with: pip install transformers torch")


@config.command("set")
@click.argument("key")
@click.argument("value")
def set_config(key, value):
    """Set a configuration value."""
    config = AgentConfig()
    
    # Handle boolean values
    if value.lower() in ['true', 'false']:
        value = value.lower() == 'true'
    
    # Handle numeric values
    elif value.isdigit():
        value = int(value)
    
    # Handle null values
    elif value.lower() in ['null', 'none']:
        value = None
    
    config.set(key, value)
    click.echo(f"Set {key} = {value}")


@config.command("system-message")
@click.option("--file", "-f", help="Load system message from file")
@click.option("--interactive", "-i", is_flag=True, help="Enter system message interactively")
@click.option("--layer", "-l", type=click.Choice(['base', 'custom']), default='custom', help="Which system message layer to modify")
def set_system_message(file, interactive, layer):
    """Set system message for the agent (base or custom layer)."""
    config = AgentConfig()
    
    if file:
        try:
            with open(file, 'r', encoding='utf-8') as f:
                message = f.read().strip()
            if layer == 'base':
                config.agent_identity.update_base_system_message(message)
            else:
                config.agent_identity.update_custom_system_message(message)
            click.echo(f"System message ({layer} layer) loaded from {file}")
        except Exception as e:
            click.echo(f"Error loading file: {e}")
            return
    
    elif interactive:
        current_msg = config.agent_identity.base_system_message if layer == 'base' else config.agent_identity.custom_system_message
        click.echo(f"Enter your {layer} system message (press Ctrl+D when done):")
        click.echo("Current message:")
        click.echo(f"  {current_msg[:200]}..." if len(current_msg) > 200 else f"  {current_msg}")
        click.echo("\nNew message:")
        
        try:
            lines = []
            while True:
                try:
                    line = input()
                    lines.append(line)
                except EOFError:
                    break
            
            message = '\n'.join(lines).strip()
            if message:
                if layer == 'base':
                    config.agent_identity.update_base_system_message(message)
                else:
                    config.agent_identity.update_custom_system_message(message)
                click.echo(f"System message ({layer} layer) updated")
            else:
                click.echo("No message entered")
                
        except KeyboardInterrupt:
            click.echo("\nCancelled")
    
    else:
        click.echo("Current system message layers:")
        click.echo("\nBase layer:")
        base_msg = config.agent_identity.base_system_message
        click.echo(f"  {base_msg[:200]}..." if len(base_msg) > 200 else f"  {base_msg}")
        
        if config.agent_identity.custom_system_message:
            click.echo("\nCustom layer:")
            custom_msg = config.agent_identity.custom_system_message
            click.echo(f"  {custom_msg[:200]}..." if len(custom_msg) > 200 else f"  {custom_msg}")
        else:
            click.echo("\nCustom layer: (not set)")
        
        click.echo("\nUse --interactive or --file to change it")
        click.echo("Use --layer base to modify the base system message")


@config.command("reset")
def reset_config():
    """Reset configuration to defaults."""
    if click.confirm("Are you sure you want to reset all configuration to defaults?"):
        config = AgentConfig()
        config.config = config._get_default_config()
        config.save_config()
        click.echo("Configuration reset to defaults")


@config.command("identity")
def show_identity():
    """Show agent identity information."""
    config = AgentConfig()
    identity_info = config.agent_identity.get_identity_info()
    
    click.echo("Agent Identity:")
    click.echo("=" * 30)
    click.echo(f"Agent ID: {identity_info['agent_id']}")
    click.echo(f"Agent Name: {identity_info['agent_name']}")
    click.echo(f"Created: {identity_info['creation_timestamp']}")
    
    click.echo("\nSystem Message Preview:")
    full_msg = identity_info['full_system_message']
    preview = full_msg[:300] + "..." if len(full_msg) > 300 else full_msg
    click.echo(f"{preview}")


@config.command("set-name")
@click.argument("name")
def set_agent_name(name):
    """Set the agent's name."""
    config = AgentConfig()
    old_name = config.agent_identity.agent_name
    config.agent_identity.update_name(name)
    click.echo(f"Agent name changed from '{old_name}' to '{name}'")


@config.command("set-personality")
@click.option("--file", "-f", help="Load personality from file")
@click.option("--interactive", "-i", is_flag=True, help="Enter personality interactively")
def set_personality(file, interactive):
    """Set the agent's personality (custom system message)."""
    config = AgentConfig()
    
    if file:
        try:
            with open(file, 'r', encoding='utf-8') as f:
                message = f.read().strip()
            config.agent_identity.update_custom_system_message(message)
            click.echo(f"Agent personality loaded from {file}")
        except Exception as e:
            click.echo(f"Error loading file: {e}")
            return
    
    elif interactive:
        current_msg = config.agent_identity.custom_system_message
        click.echo("Enter your agent's personality/role (press Ctrl+D when done):")
        click.echo("Current personality:")
        if current_msg:
            click.echo(f"  {current_msg[:200]}..." if len(current_msg) > 200 else f"  {current_msg}")
        else:
            click.echo("  (not set)")
        click.echo("\nNew personality:")
        
        try:
            lines = []
            while True:
                try:
                    line = input()
                    lines.append(line)
                except EOFError:
                    break
            
            message = '\n'.join(lines).strip()
            if message:
                config.agent_identity.update_custom_system_message(message)
                click.echo("Agent personality updated")
            else:
                click.echo("No personality entered")
                
        except KeyboardInterrupt:
            click.echo("\nCancelled")
    
    else:
        click.echo("Current agent personality:")
        current_msg = config.agent_identity.custom_system_message
        if current_msg:
            click.echo(f"  {current_msg[:200]}..." if len(current_msg) > 200 else f"  {current_msg}")
        else:
            click.echo("  (not set)")
        click.echo("\nUse --interactive or --file to change it")


@config.command("regenerate-identity")
def regenerate_identity():
    """Generate a new agent identity (ID and name)."""
    config = AgentConfig()
    old_id = config.agent_identity.agent_id
    old_name = config.agent_identity.agent_name
    
    if click.confirm(f"Are you sure you want to regenerate identity for {old_name} ({old_id})?"):
        config.agent_identity.regenerate_identity()
        click.echo(f"Identity regenerated:")
        click.echo(f"  Old: {old_name} ({old_id})")
        click.echo(f"  New: {config.agent_identity.agent_name} ({config.agent_identity.agent_id})")
        click.echo("Custom personality preserved.")
    else:
        click.echo("Identity regeneration cancelled.")


@cli.group()
def auth():
    """Manage API keys and authentication."""
    pass


@auth.command("set")
@click.argument("service")
@click.argument("key", required=False)
def set_key(service, key):
    """Set an API key for a service."""
    if not key:
        key = click.prompt(f"Enter API key for {service}", hide_input=True)
    
    key_manager = APIKeyManager()
    key_manager.set_key(service, key)
    click.echo(f"API key for {service} set successfully")


@auth.command("list")
def list_keys():
    """List configured API keys."""
    key_manager = APIKeyManager()
    services = key_manager.list_services()
    
    if not services:
        click.echo("No API keys configured")
        click.echo("\nSet API keys with: metis auth set <service> <key>")
        click.echo("Supported services: openai, groq, anthropic, huggingface, google")
        return
    
    click.echo("Configured API keys:")
    for service in services:
        click.echo(f"  {service}")


@auth.command("remove")
@click.argument("service")
def remove_key(service):
    """Remove an API key."""
    if click.confirm(f"Remove API key for {service}?"):
        key_manager = APIKeyManager()
        key_manager.remove_key(service)
        click.echo(f"API key for {service} removed")


@auth.command("test")
@click.argument("service", required=False)
def test_key(service):
    """Test API key connectivity."""
    key_manager = APIKeyManager()
    
    if service:
        services = [service]
    else:
        services = key_manager.list_services()
    
    if not services:
        click.echo("No API keys to test")
        return
    
    for svc in services:
        key = key_manager.get_key(svc)
        if key:
            click.echo(f"Testing {svc}...", nl=False)
            # TODO: Add actual API connectivity tests
            click.echo(" Key present")
        else:
            click.echo(f"{svc}: No key configured")





@config.command("ollama-url")
@click.argument("url")
def set_ollama_url(url):
    """Set Ollama server URL."""
    config = AgentConfig()
    config.set_ollama_base_url(url)
    click.echo(f"Ollama base URL set to: {url}")


@config.command("hf-device")
@click.argument("device")
def set_hf_device(device):
    """Set HuggingFace model device (auto, cpu, cuda, mps)."""
    config = AgentConfig()
    try:
        config.set_huggingface_device(device)
        click.echo(f"HuggingFace device set to: {device}")
    except ValueError as e:
        click.echo(f"Error: {e}")


@config.command("hf-quantization")
@click.argument("quantization")
def set_hf_quantization(quantization):
    """Set HuggingFace model quantization (none, 8bit, 4bit)."""
    config = AgentConfig()
    try:
        config.set_huggingface_quantization(quantization)
        click.echo(f"HuggingFace quantization set to: {quantization}")
    except ValueError as e:
        click.echo(f"Error: {e}")


@config.command("hf-max-length")
@click.argument("max_length", type=int)
def set_hf_max_length(max_length):
    """Set HuggingFace model max sequence length."""
    config = AgentConfig()
    try:
        config.set_huggingface_max_length(max_length)
        click.echo(f"HuggingFace max length set to: {max_length}")
    except ValueError as e:
        click.echo(f"Error: {e}")


@config.command("list-models")
def list_models():
    """List available models for the current provider."""
    config = AgentConfig()
    provider = config.get_llm_provider()
    
    if provider == "ollama":
        _list_ollama_models(config)
    elif provider == "huggingface":
        _list_huggingface_models(config)
    else:
        click.echo(f"Model listing not supported for provider: {provider}")
        click.echo("Supported providers for model listing: ollama, huggingface")


def _list_ollama_models(config):
    """List available Ollama models."""
    base_url = config.get_ollama_base_url()
    
    try:
        import requests
        response = requests.get(f"{base_url}/api/tags", timeout=5)
        response.raise_for_status()
        models = response.json().get("models", [])
        
        if models:
            click.echo("Available Ollama models:")
            for model in models:
                name = model.get("name", "Unknown")
                size = model.get("size", 0)
                size_gb = size / (1024**3) if size > 0 else 0
                click.echo(f"  - {name} ({size_gb:.1f}GB)")
        else:
            click.echo("No models found.")
            click.echo("Pull a model with: ollama pull <model-name>")
            
    except Exception as e:
        click.echo(f"Error connecting to Ollama: {e}")
        click.echo("Make sure Ollama is running and accessible.")


def _list_huggingface_models(config):
    """List information about HuggingFace model setup."""
    click.echo("Local HuggingFace Models:")
    click.echo("")
    click.echo("Popular models you can download:")
    click.echo("  Small models (< 1GB):")
    click.echo("    - microsoft/DialoGPT-small")
    click.echo("    - distilgpt2")
    click.echo("    - gpt2")
    click.echo("")
    click.echo("  Medium models (1-5GB):")
    click.echo("    - microsoft/DialoGPT-medium")
    click.echo("    - QuixiAI/TinyDolphin-2.8-1.1b")
    click.echo("    - TinyLlama/TinyLlama-1.1B-Chat-v1.0")
    click.echo("")
    click.echo("  Large models (5GB+):")
    click.echo("    - microsoft/DialoGPT-large")
    click.echo("    - EleutherAI/gpt-neo-2.7B")
    click.echo("")
    click.echo("To use a model:")
    click.echo("  1. Set provider: metis config set llm_provider huggingface")
    click.echo("  2. Set model: metis config set llm_model <model-name>")
    click.echo("  3. The model will be downloaded automatically on first use")


if __name__ == "__main__":
    cli()
