"""
Autocomplete support for Calliope magic commands using IPython Completer API.

This module provides comprehensive tab completion for %%calliope magic command actions,
options, and contextual suggestions based on the command structure.
"""

from typing import List, Set, Dict, Optional
from IPython.core.magic import Magics
from IPython import get_ipython
import requests
import json
import os





def register_magic_completer(ip):
    """
    Register the enhanced Calliope magic completer with IPython.
    """
    try:
        if hasattr(ip, 'set_hook'):
            def calliope_completer(self, event):
                # Extract line content from event
                line = getattr(event, 'line_buffer', None) or getattr(event, 'line', None) or str(event)
                
                if not line or not (line.strip().startswith('%%calliope') or line.strip().startswith('%calliope')):
                    return []
                
                # Get the magic instance to access command data
                magic_instance = None
                try:
                    from pergamon_server_extension.magic import CalliopeMagics
                    magic_instance = ip.find_magic('calliope')
                except:
                    pass
                
                completer = CalliopeCompleter(magic_instance)
                return completer.complete(line)
            
            # Register the completer for both cell and line magics
            ip.set_hook('complete_command', calliope_completer, str_key=r'%%calliope')
            ip.set_hook('complete_command', calliope_completer, str_key=r'%calliope')
            
        else:
            print("Warning: IPython completion hooks not available")
            
    except Exception as e:
        print(f"Warning: Could not register Calliope autocomplete: {e}")
    
    return True


class CalliopeCompleter:
    """
    Advanced completer for Calliope magic commands.
    """
    
    def __init__(self, magic_instance: Optional[Magics] = None):
        self.magic = magic_instance
        
        # Extract data from magic instance or use defaults
        if magic_instance and hasattr(magic_instance, 'endpoint_map'):
            self.api_commands = list(magic_instance.endpoint_map.keys())
            self.providers = getattr(magic_instance, 'providers', {})
            self.model_aliases = getattr(magic_instance, 'model_aliases', {})
            self.sql_providers = getattr(magic_instance, 'sql_providers', {})
        else:
            # Fallback command lists (using user-friendly names)
            self.api_commands = [
                'ask-sql', 'generate-sql', 'run-sql', 'followup-questions', 
                'generate-summary', 'rag-train', 'update-schema', 'clear-rag', 'add-database'
            ]
            self.providers = {}
            self.model_aliases = {
                'gpto': 'openai-chat:gpt-4o',
                'gpt4': 'openai-chat:gpt-4',
                'claude3': 'anthropic-chat:claude-3-sonnet-20240229',
                'gemini': 'gemini:gemini-1.0-pro-001'
            }
            self.sql_providers = {}
        
        # Handle command aliases and alternative names
        self.command_aliases = {
            'sql-ask': 'ask-sql',  # Map internal name to user-friendly name
            'list_models': 'list-models',
            'add_database': 'add-database'
        }
        
        # Define command categories (using user-friendly names)
        self.command_categories = {
            'data_querying': ['ask-sql', 'generate-sql', 'run-sql', 'followup-questions', 'generate-summary'],
            'database_management': ['add-database'],
            'rag_management': ['rag-train', 'update-schema', 'clear-rag'],
            'ai_utilities': ['ask', 'help', 'list-models']
        }
        
        # All available commands
        self.all_commands = ['help', 'list-models', 'ask'] + self.api_commands
        
        # Global options
        self.global_options = ['--to-ai', '--model', '--sql-model']
        
        # Commands that require datasource_id (using user-friendly names)
        self.datasource_commands = [
            'ask-sql', 'generate-sql', 'run-sql', 'followup-questions', 
            'generate-summary', 'rag-train', 'update-schema'
        ]
        
        # Cache for datasources to avoid repeated API calls
        self._datasources_cache = None
        self._cache_timestamp = None
        
        # Cache for SQL providers to avoid repeated API calls
        self._sql_providers_cache = None
        self._sql_providers_cache_timestamp = None
    
    def _normalize_command(self, command: str) -> str:
        """Normalize command name using aliases"""
        return self.command_aliases.get(command, command)
    
    def _fetch_datasources(self) -> List[Dict]:
        """Fetch available datasources from the API with caching."""
        import time
        
        # Check cache validity (5 minutes)
        if (self._datasources_cache is not None and 
            self._cache_timestamp is not None and 
            time.time() - self._cache_timestamp < 300):
            return self._datasources_cache
        
        try:
            api_host = os.environ.get("CALLIOPE_API_HOST")
            if not api_host:
                return []
            
            response = requests.get(
                f"{api_host}/api/datasources",
                timeout=5  # Short timeout for completion
            )
            response.raise_for_status()
            
            data = response.json()
            datasources = data.get('datasources', [])
            
            # Cache the results
            self._datasources_cache = datasources
            self._cache_timestamp = time.time()
            
            return datasources
            
        except Exception:
            # On any error, return empty list and don't cache
            return []
    
    def _get_datasource_suggestions(self, current: str = "") -> List[str]:
        """Get datasource ID suggestions from the API."""
        datasources = self._fetch_datasources()
        
        suggestions = []
        for ds in datasources:
            ds_id = ds.get('id', '')
            ds_name = ds.get('name', '')
            ds_description = ds.get('description', '')
            
            if ds_id:
                # Add the ID as the main suggestion
                if current == "" or ds_id.startswith(current):
                    # Create a helpful suggestion with context
                    context = f"# {ds_name}" if ds_name else f"# {ds_description}" if ds_description else ""
                    if context:
                        suggestions.append(f"{ds_id}  {context}")
                    else:
                        suggestions.append(ds_id)
        
        # If no API results, fall back to just returning what the user typed
        if not suggestions and current:
            suggestions.append(current)
        
        return suggestions
    
    def _fetch_sql_providers(self) -> List[Dict]:
        """Fetch available SQL providers from the API with caching."""
        import time
        
        # Check cache validity (5 minutes)
        if (self._sql_providers_cache is not None and 
            self._sql_providers_cache_timestamp is not None and 
            time.time() - self._sql_providers_cache_timestamp < 300):
            return self._sql_providers_cache
        
        try:
            api_host = os.environ.get("CALLIOPE_API_HOST")
            if not api_host:
                return []
            
            response = requests.get(
                f"{api_host}/api/providers",
                timeout=5  # Short timeout for completion
            )
            response.raise_for_status()
            
            data = response.json()
            providers = data.get('providers', [])
            
            # Cache the results
            self._sql_providers_cache = providers
            self._sql_providers_cache_timestamp = time.time()
            
            return providers
            
        except Exception:
            # On any error, return empty list and don't cache
            return []
    
    def _get_dynamic_sql_model_suggestions(self, current: str = "") -> List[str]:
        """Get SQL model suggestions from the API for --sql-model flag."""
        providers = self._fetch_sql_providers()
        
        suggestions = []
        for provider in providers:
            # Only show active providers
            if not provider.get('active', False):
                continue
                
            provider_id = provider.get('id', '')
            models = provider.get('models', {})
            sql_model = models.get('sql', '')
            provider_name = provider.get('name', provider_id)
            
            if provider_id:
                # Add the provider ID as the main suggestion
                if current == "" or provider_id.startswith(current):
                    # Create a helpful suggestion with context showing the SQL model
                    context = f"# {sql_model} ({provider_name})" if sql_model else f"# {provider_name}"
                    suggestions.append(f"{provider_id}  {context}")
        
        # If no API results, fall back to hardcoded SQL providers from magic instance
        if not suggestions and hasattr(self, 'sql_providers') and self.sql_providers:
            for provider_name in self.sql_providers.keys():
                if current == "" or provider_name.startswith(current):
                    sql_model = self.sql_providers[provider_name].get('sql_model', '')
                    context = f"# {sql_model}" if sql_model else ""
                    if context:
                        suggestions.append(f"{provider_name}  {context}")
                    else:
                        suggestions.append(provider_name)
        
        return suggestions
    
    def complete(self, line: str) -> List[str]:
        """
        Main completion method that analyzes the line and provides appropriate suggestions.
        """
        # Determine if it's a cell magic or line magic
        if line.startswith('%%calliope'):
            return self._complete_cell_magic(line[10:].lstrip())
        elif line.startswith('%calliope'):
            return self._complete_line_magic(line[9:].lstrip())
        else:
            return []
    
    def _complete_cell_magic(self, line_content: str) -> List[str]:
        """Complete cell magic commands (%%calliope)"""
        tokens = line_content.split()
        
        # No tokens yet - suggest all commands
        if not tokens or (len(tokens) == 1 and not line_content.endswith(' ')):
            current = tokens[0] if tokens else ""
            return self._filter_commands(self.all_commands, current)
        
        command = tokens[0].lower()
        
        # Complete based on command type and position
        if len(tokens) == 1 and line_content.endswith(' '):
            # Just completed command, suggest next argument
            return self._get_next_argument_suggestions(command, [])
        
        elif len(tokens) >= 2:
            # Complete subsequent arguments
            return self._complete_command_arguments(command, tokens[1:], line_content)
        
        return []
    
    def _complete_line_magic(self, line_content: str) -> List[str]:
        """Complete line magic commands (%calliope)"""
        tokens = line_content.split()
        
        # Line magic typically only supports help and list-models
        line_commands = ['help', 'list-models']
        
        if not tokens or (len(tokens) == 1 and not line_content.endswith(' ')):
            current = tokens[0] if tokens else ""
            return self._filter_commands(line_commands, current)
        
        command = tokens[0].lower()
        if command == 'list-models' and len(tokens) >= 2:
            # Complete provider names for list-models
            current = tokens[1] if len(tokens) == 2 and not line_content.endswith(' ') else ""
            provider_names = list(self.providers.keys())
            return [p for p in provider_names if p.startswith(current)]
        
        return []
    
    def _get_next_argument_suggestions(self, command: str, existing_args: List[str]) -> List[str]:
        """Get suggestions for the next argument based on command type"""
        suggestions = []
        
        # Commands that need datasource_id as first argument
        if command in self.datasource_commands:
            if not any(arg for arg in existing_args if not arg.startswith('--')):
                # Try to get actual datasource IDs if available
                datasource_suggestions = self._get_datasource_suggestions("")
                if datasource_suggestions:
                    suggestions.extend(datasource_suggestions)
                else:
                    suggestions.append('<datasource_id>')
        
        # Global options available for most commands
        if command in self.api_commands:
            if '--to-ai' not in existing_args:
                suggestions.append('--to-ai')
            if '--model' not in existing_args:
                suggestions.append('--model')
            
            # Add --sql-model specifically for ask-sql command
            if command == 'ask-sql' and '--sql-model' not in existing_args:
                suggestions.append('--sql-model')
        
        # Command-specific suggestions
        if command == 'list-models':
            provider_names = list(self.providers.keys())
            suggestions.extend(provider_names)
        
        return suggestions
    
    def _complete_command_arguments(self, command: str, args: List[str], full_line: str) -> List[str]:
        """Complete arguments for a specific command"""
        # Handle --model completion
        if len(args) >= 2 and args[-2] == '--model':
            current_model = args[-1] if not full_line.endswith(' ') else ""
            if command == 'ask-sql':
                return self._complete_ask_sql_model_name(current_model)
            else:
                return self._complete_model_name(current_model)
        
        # Handle --model when it's the last token and line ends with space
        if args and args[-1] == '--model' and full_line.endswith(' '):
            if command == 'ask-sql':
                return self._get_ask_sql_model_suggestions()
            else:
                return self._get_model_suggestions()
        
        # Handle --sql-model completion
        if len(args) >= 2 and args[-2] == '--sql-model':
            current_model = args[-1] if not full_line.endswith(' ') else ""
            return self._complete_sql_model_name(current_model)
        
        # Handle --sql-model when it's the last token and line ends with space
        if args and args[-1] == '--sql-model' and full_line.endswith(' '):
            return self._get_sql_model_suggestions()
        
        # Handle other option completions
        if not full_line.endswith(' ') and args:
            current_arg = args[-1]
            if current_arg.startswith('--'):
                return self._filter_commands(self.global_options, current_arg)
            
            # Handle partial datasource ID completion
            elif command in self.datasource_commands:
                # Check if this is the first non-option argument (datasource_id)
                non_option_args = [arg for arg in args if not arg.startswith('--')]
                if len(non_option_args) == 1 and non_option_args[0] == current_arg:
                    return self._get_datasource_suggestions(current_arg)
        
        # Suggest remaining options
        return self._get_next_argument_suggestions(command, args)
    
    def _complete_model_name(self, current: str) -> List[str]:
        """Complete model names and aliases"""
        suggestions = []
        
        # Add model aliases
        for alias in self.model_aliases.keys():
            if alias.startswith(current):
                suggestions.append(alias)
        
        # Add full model names from providers
        for provider_id, provider_info in self.providers.items():
            if 'models' in provider_info:
                for model in provider_info['models']:
                    full_name = f"{provider_id}:{model}"
                    if full_name.startswith(current):
                        suggestions.append(full_name)
        
        return sorted(suggestions)
    
    def _get_model_suggestions(self) -> List[str]:
        """Get all available model suggestions"""
        suggestions = []
        
        # Popular aliases first
        popular_aliases = ['gpto', 'gpt4', 'claude3', 'gemini']
        suggestions.extend(popular_aliases)
        
        # Other aliases
        other_aliases = [alias for alias in self.model_aliases.keys() if alias not in popular_aliases]
        suggestions.extend(sorted(other_aliases))
        
        return suggestions
    
    def _complete_ask_sql_model_name(self, current: str) -> List[str]:
        """Complete model names for --model flag with ask-sql command (uses hardcoded providers)"""
        # For --model with ask-sql, use hardcoded providers (no dynamic API suggestions)
        suggestions = []
        for provider_id in self.sql_providers.keys():
            if provider_id.startswith(current):
                suggestions.append(provider_id)
        
        return sorted(suggestions)
    
    def _get_ask_sql_model_suggestions(self) -> List[str]:
        """Get model suggestions for --model flag with ask-sql command (uses hardcoded providers)"""
        # For --model with ask-sql, use hardcoded providers (no dynamic API suggestions)
        return sorted(list(self.sql_providers.keys()))
    
    def _complete_sql_model_name(self, current: str) -> List[str]:
        """Complete SQL model names specifically for --sql-model flag using dynamic API data"""
        # Always use dynamic suggestions for --sql-model flag
        dynamic_suggestions = self._get_dynamic_sql_model_suggestions(current)
        if dynamic_suggestions:
            return dynamic_suggestions
        
        # Fallback to hardcoded providers if API fails
        suggestions = []
        for provider_id in self.sql_providers.keys():
            if provider_id.startswith(current):
                suggestions.append(provider_id)
        
        return sorted(suggestions)
    
    def _get_sql_model_suggestions(self) -> List[str]:
        """Get all available SQL model suggestions specifically for --sql-model flag using dynamic API data"""
        # Always use dynamic suggestions for --sql-model flag
        dynamic_suggestions = self._get_dynamic_sql_model_suggestions("")
        if dynamic_suggestions:
            return dynamic_suggestions
        
        # Fallback to hardcoded providers if API fails
        return sorted(list(self.sql_providers.keys()))
    

    
    def _add_contextual_help(self, suggestions: List[str], command: str) -> List[str]:
        """Add contextual help comments to suggestions"""
        if not suggestions:
            return []
        
        # Add helpful context for certain commands
        help_map = {
            'ask-sql': '# Ask questions → get SQL + results + charts',
            'generate-sql': '# Convert questions to SQL (no execution)',
            'run-sql': '# Execute SQL directly',
            'add-database': '# Add datasource with auto-setup',
            'rag-train': '# Train AI with schemas/docs/examples',
            '--model': '# SQL models: fetched dynamically from API',
            '--sql-model': '# SQL models: fetched dynamically from API',
        }
        
        if command in help_map:
            return [help_map[command]] + suggestions
        
        return suggestions
    
    def _filter_commands(self, commands: List[str], current: str) -> List[str]:
        """Filter commands based on current input"""
        filtered = [cmd for cmd in commands if cmd.startswith(current)]
        
        # Sort commands by relevance - put exact matches first, then partial matches
        exact_matches = [cmd for cmd in filtered if cmd == current]
        partial_matches = [cmd for cmd in filtered if cmd != current]
        
        return exact_matches + sorted(partial_matches) 