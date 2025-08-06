import json
import requests
import shlex
import os
from IPython.core.magic import Magics, magics_class, line_cell_magic
from IPython.display import display, HTML, Markdown
import plotly.graph_objects as go
from ipykernel.comm import Comm
from .completer import register_magic_completer
from .help_handler import CalliopeHelpHandler

# Database connection imports for introspection
try:
    import psycopg2
    HAS_POSTGRES = True
except ImportError:
    HAS_POSTGRES = False

try:
    import mysql.connector
    HAS_MYSQL = True
except ImportError:
    HAS_MYSQL = False

try:
    import sqlite3
    HAS_SQLITE = True
except ImportError:
    HAS_SQLITE = False

# Global flag to track if the magic has been loaded
__MAGIC_LOADED__ = False

# Get API host from environment variable with default fallback
API_HOST = os.environ.get("CALLIOPE_API_HOST")
AGENT_ADMIN_TOKEN = os.environ.get("AGENT_ADMIN_TOKEN")

@magics_class
class CalliopeMagics(Magics):
    def __init__(self, shell):
        super(CalliopeMagics, self).__init__(shell)
        self.endpoint_map = {
            "ask-sql": "/api/sql/ask",
            "generate-sql": "/api/sql/generate_sql",
            "run-sql": "/api/sql/run_sql",
            "followup-questions": "/api/sql/generate_followup_questions",
            "generate-summary": "/api/sql/generate_summary",
            "rag-train": "/api/rag/train",
            "update-schema": "/api/rag/update_schema/{}",
            "clear-rag": "/api/rag/clear",
            "add-database": "/api/admin/datasources/{}",
            "add-secret": "/api/secrets/{}",
        }
        
        # Define available AI models and providers
        self.providers = {
            "ai21": {
                "name": "AI21",
                "models": ["j1-large", "j1-grande", "j1-jumbo", "j1-grande-instruct", 
                           "j2-large", "j2-grande", "j2-jumbo", "j2-grande-instruct", "j2-jumbo-instruct"]
            },
            "bedrock": {
                "name": "Amazon Bedrock",
                "models": ["amazon.titan-text-express-v1", "amazon.titan-text-lite-v1", "amazon.titan-text-premier-v1:0",
                           "ai21.j2-ultra-v1", "ai21.j2-mid-v1", "ai21.jamba-instruct-v1:0",
                           "cohere.command-light-text-v14", "cohere.command-text-v14", "cohere.command-r-v1:0", "cohere.command-r-plus-v1:0",
                           "meta.llama2-13b-chat-v1", "meta.llama2-70b-chat-v1", "meta.llama3-8b-instruct-v1:0", "meta.llama3-70b-instruct-v1:0",
                           "meta.llama3-1-8b-instruct-v1:0", "meta.llama3-1-70b-instruct-v1:0", "meta.llama3-1-405b-instruct-v1:0",
                           "mistral.mistral-7b-instruct-v0:2", "mistral.mixtral-8x7b-instruct-v0:1", "mistral.mistral-large-2402-v1:0", "mistral.mistral-large-2407-v1:0"]
            },
            "bedrock-chat": {
                "name": "Amazon Bedrock Chat",
                "models": ["amazon.titan-text-express-v1", "amazon.titan-text-lite-v1", "amazon.titan-text-premier-v1:0",
                           "anthropic.claude-v2", "anthropic.claude-v2:1", "anthropic.claude-instant-v1",
                           "anthropic.claude-3-sonnet-20240229-v1:0", "anthropic.claude-3-haiku-20240307-v1:0", "anthropic.claude-3-opus-20240229-v1:0",
                           "anthropic.claude-3-5-haiku-20241022-v1:0", "anthropic.claude-3-5-sonnet-20240620-v1:0", "anthropic.claude-3-5-sonnet-20241022-v2:0",
                           "meta.llama2-13b-chat-v1", "meta.llama2-70b-chat-v1", "meta.llama3-8b-instruct-v1:0", "meta.llama3-70b-instruct-v1:0",
                           "meta.llama3-1-8b-instruct-v1:0", "meta.llama3-1-70b-instruct-v1:0", "meta.llama3-1-405b-instruct-v1:0",
                           "mistral.mistral-7b-instruct-v0:2", "mistral.mixtral-8x7b-instruct-v0:1", "mistral.mistral-large-2402-v1:0", "mistral.mistral-large-2407-v1:0"]
            },
            "bedrock-custom": {
                "name": "Amazon Bedrock Custom",
                "help": "For Cross-Region Inference use the appropriate Inference profile ID (Model ID with a region prefix, e.g., us.meta.llama3-2-11b-instruct-v1:0). For custom/provisioned models, specify the model ARN (Amazon Resource Name) as the model ID."
            },
            "anthropic-chat": {
                "name": "Anthropic",
                "models": ["claude-2.0", "claude-2.1", "claude-3-opus-20240229", "claude-3-sonnet-20240229", 
                           "claude-3-haiku-20240307", "claude-3-5-haiku-20241022", "claude-3-5-sonnet-20240620", "claude-3-5-sonnet-20241022"]
            },
            "azure-chat-openai": {
                "name": "Azure OpenAI",
                "help": "This provider does not define a list of models."
            },
            "cohere": {
                "name": "Cohere",
                "models": ["command", "command-nightly", "command-light", "command-light-nightly", 
                           "command-r-plus", "command-r"]
            },
            "gemini": {
                "name": "Google Gemini",
                "models": ["gemini-1.5-pro", "gemini-1.5-flash", "gemini-1.0-pro", "gemini-1.0-pro-001", 
                           "gemini-1.0-pro-latest", "gemini-1.0-pro-vision-latest", "gemini-pro", "gemini-pro-vision"]
            },
            "gpt4all": {
                "name": "GPT4All",
                "models": ["ggml-gpt4all-j-v1.2-jazzy", "ggml-gpt4all-j-v1.3-groovy", "ggml-gpt4all-l13b-snoozy",
                           "mistral-7b-openorca.Q4_0", "mistral-7b-instruct-v0.1.Q4_0", "gpt4all-falcon-q4_0",
                           "wizardlm-13b-v1.2.Q4_0", "nous-hermes-llama2-13b.Q4_0", "gpt4all-13b-snoozy-q4_0",
                           "mpt-7b-chat-merges-q4_0", "orca-mini-3b-gguf2-q4_0", "starcoder-q4_0",
                           "rift-coder-v0-7b-q4_0", "em_german_mistral_v01.Q4_0"]
            },
            "huggingface_hub": {
                "name": "Hugging Face Hub",
                "help": "See https://huggingface.co/models for a list of models. Pass a model's repository ID as the model ID; for example, huggingface_hub:ExampleOwner/example-model."
            },
            "mistralai": {
                "name": "Mistral AI",
                "models": ["open-mistral-7b", "open-mixtral-8x7b", "open-mixtral-8x22b", "mistral-small-latest",
                           "mistral-medium-latest", "mistral-large-latest", "codestral-latest"]
            },
            "nvidia-chat": {
                "name": "NVIDIA AI",
                "models": ["playground_llama2_70b", "playground_nemotron_steerlm_8b", "playground_mistral_7b",
                           "playground_nv_llama2_rlhf_70b", "playground_llama2_13b", "playground_steerlm_llama_70b",
                           "playground_llama2_code_13b", "playground_yi_34b", "playground_mixtral_8x7b",
                           "playground_neva_22b", "playground_llama2_code_34b"]
            },
            "openai": {
                "name": "OpenAI",
                "models": ["babbage-002", "davinci-002", "gpt-3.5-turbo-instruct"]
            },
            "openai-chat": {
                "name": "OpenAI Chat",
                "models": ["gpt-3.5-turbo", "gpt-3.5-turbo-1106", "gpt-4", "gpt-4-turbo", "gpt-4-turbo-preview",
                           "gpt-4-0613", "gpt-4-0125-preview", "gpt-4-1106-preview", "gpt-4o", "gpt-4o-2024-11-20",
                           "gpt-4o-mini", "chatgpt-4o-latest"]
            },
            "openai-chat-custom": {
                "name": "OpenAI API Compatible",
                "help": "Supports non-OpenAI models that use the OpenAI API interface. Replace the OpenAI API key with the API key for the chosen provider."
            },
            "openrouter": {
                "name": "OpenRouter",
                "help": "This provider does not define a list of models."
            },
            "qianfan": {
                "name": "Qianfan",
                "models": ["ERNIE-Bot", "ERNIE-Bot-4"]
            },
            "sagemaker-endpoint": {
                "name": "SageMaker Endpoint",
                "help": "Specify an endpoint name as the model ID. In addition, you must specify a region name, request schema, and response path."
            },
            "togetherai": {
                "name": "Together AI",
                "models": ["Austism/chronos-hermes-13b", "DiscoResearch/DiscoLM-mixtral-8x7b-v2", "EleutherAI/llemma_7b",
                           "Gryphe/MythoMax-L2-13b", "Meta-Llama/Llama-Guard-7b", "Nexusflow/NexusRaven-V2-13B",
                           "NousResearch/Nous-Capybara-7B-V1p9", "NousResearch/Nous-Hermes-2-Yi-34B",
                           "NousResearch/Nous-Hermes-Llama2-13b", "NousResearch/Nous-Hermes-Llama2-70b"]
            }
        }
        
        # Define SQL providers for ask-sql command
        self.sql_providers = {  # TODO: get the providers list from the API using the endpoint /api/providers
            "ollama": {
                "id": "ollama",
                "sql_model": "gemma3:27b"
            },
            "openai": {
                "id": "openai",
                "sql_model": "gpt-4o"
            },
            "gemini": {
                "id": "gemini",
                "sql_model": "gemini-1.5-flash"
            },
            "anthropic": {
                "id": "anthropic",
                "sql_model": "claude-3-sonnet-20240229"
            },
            "perplexity": {
                "id": "perplexity",
                "sql_model": "sonar-medium-online"
            },
            "ai21": {
                "id": "ai21",
                "sql_model": "j2-ultra"
            },
            "aws": {
                "id": "aws",
                "sql_model": "anthropic.claude-3-sonnet-20240229-v1:0"
            },
            "cohere": {
                "id": "cohere",
                "sql_model": "command-r"
            },
            "mistral": {
                "id": "mistral",
                "sql_model": "mistral-medium-latest"
            },
            "nvidia": {
                "id": "nvidia",
                "sql_model": "playground_mixtral_8x7b"
            }
        }
        
        # Define model aliases
        self.model_aliases = {
            "gpt2": "huggingface_hub:gpt2",
            "gpt3": "openai:davinci-002",
            "chatgpt": "openai-chat:gpt-3.5-turbo",
            "gpt4": "openai-chat:gpt-4",
            "openrouter-claude": "openrouter:anthropic/claude-3.5-sonnet:beta",
            "anthropic-chat": "anthropic-chat:claude-2.0",
            "native-cohere": "cohere:command",
            "bedrock-cohere": "bedrock:cohere.command-text-v14",
            "anthropic": "anthropic:claude-v1",
            "bedrock": "bedrock:amazon.titan-text-lite-v1",
            "gemini": "gemini:gemini-1.0-pro-001",
            "gpto": "openai-chat:gpt-4o"
        }
        
        # Initialize help handler
        self.help_handler = CalliopeHelpHandler(self)
        
    @line_cell_magic
    def calliope(self, line, cell=None):
        args = shlex.split(line) if line else []
        
        if not args:
            return self.help_handler.handle_help()

        action = args[0].lower()
        match action:
            case "help":
                return self.help_handler.handle_help()
            case "list-models" | "list_models":
                return self._handle_list_models(args[1:] if len(args) > 1 else [])
            case "ask":
                if self._validate_has_content(cell):
                    return self._validate_has_content(cell)
                return self._handle_ask(args[1:], cell)
            case "add-database" | "add_database":
                if self._validate_has_content(cell):
                    return self._validate_has_content(cell)
                return self._handle_add_database(args[1:], cell)
            case _:
                if self._validate_has_content(cell):
                    return self._validate_has_content(cell)

                
                # Process remaining arguments
                remaining_args = args[1:]
                datasource_id = ""
                to_ai = False
                ai_model = "gpto"
                sql_model = None  # For ask-sql command
                
                i = 0
                while i < len(remaining_args):
                    if i == 0 and remaining_args[i] not in ["--to-ai", "--model", "--sql-model"]:
                        datasource_id = remaining_args[i]
                    elif remaining_args[i] == "--to-ai":
                        to_ai = True
                    elif remaining_args[i] == "--model" and i + 1 < len(remaining_args):
                        if action == "ask-sql":
                            sql_model = remaining_args[i + 1]
                        else:
                            ai_model = remaining_args[i + 1]
                        i += 1
                    elif remaining_args[i] == "--sql-model" and i + 1 < len(remaining_args):
                        sql_model = remaining_args[i + 1]
                        i += 1
                    i += 1
                    
                # Handle API commands
                return self._handle_api_command(action, datasource_id, cell, to_ai, ai_model, sql_model)
    
    def _handle_list_models(self, args):
        """Handle the list_models command to display available AI models"""
        # provider_filter = args[0] if args else None
        
        # markdown_output = self._format_models_markdown(provider_filter)
        # display(Markdown(markdown_output))
        self.shell.run_cell('%ai list')
        return None
    
    def _format_models_markdown(self, provider_filter=None):
        """Format the available models as markdown"""
        output = "# Available AI Models\n\n"
        output += "| Provider | Models |\n"
        output += "|----------|--------|\n"
        
        for provider_id, provider_info in self.providers.items():
            if provider_filter and provider_filter != provider_id:
                continue
                
            # Format the models list
            if "help" in provider_info:
                models_list = f"<p>{provider_info['help']}</p>"
            elif "models" in provider_info:
                models_list = "<ul>"
                for model in provider_info.get("models", []):
                    full_model_id = f"{provider_id}:{model}"
                    models_list += f"<li><code>{full_model_id}</code></li>"
                models_list += "</ul>"
            else:
                models_list = "<p>No models defined</p>"
            
            output += f"| **{provider_info.get('name')}** | {models_list} |\n"
        
        # Add model aliases section
        if not provider_filter and self.model_aliases:
            output += "\n## Model Aliases\n\n"
            output += "| Alias | Maps to |\n"
            output += "|-------|--------|\n"
            
            for alias, target in self.model_aliases.items():
                output += f"| `{alias}` | `{target}` |\n"
                
        return output

    def _validate_has_content(self, cell):
        """Validate that the cell has content"""
        if not cell or not cell.strip():
            return {"error": "Empty content provided"}
        return None


    def _handle_ask(self, args, cell):
        """Handle the ask command (proxy to %%ai)"""
        ai_args = " ".join(args) if args else ""
        ai_magic = f"%%ai {ai_args}\n{cell or ''}"
        self.shell.run_cell(ai_magic)
        return None

    def _handle_add_database(self, args, cell):
        """Handle the add_database command to create a new datasource with optional secret"""
        try:
            # Parse JSON content from cell
            try:
                data = json.loads(cell.strip())
            except json.JSONDecodeError:
                return {"error": "Cell must contain valid JSON with database configuration"}
            
            # Validate required fields
            required_fields = ['datasource_id', 'name', 'dialect', 'connection_details']
            for field in required_fields:
                if field not in data:
                    return {"error": f"Missing required field: {field}"}
            
            datasource_id = data['datasource_id']
            password_field = data.get('password_field')
            password_value = data.get('password_value')
            auth_token = AGENT_ADMIN_TOKEN
            
            results = {"secret_result": None, "datasource_result": None}
            
            # Step 1: Create secret if password_field and password_value are provided
            if password_field and password_value:
                secret_endpoint = f"{API_HOST}{self.endpoint_map['add-secret'].format(password_field)}"
                secret_payload = {
                    "value": password_value,
                    "encrypt": True
                }
                
                secret_response = requests.post(
                    secret_endpoint,
                    data=json.dumps(secret_payload),
                    headers={
                        "Content-Type": "application/json",
                        "Authorization": f"Bearer {auth_token}"
                    },
                    timeout=59900
                )
                
                secret_response.raise_for_status()
                results["secret_result"] = secret_response.json()
                
                # Update connection details to use the secret
                data['connection_details']['password'] = f"secret:{password_field}"
            
            # Step 2: Create datasource
            datasource_endpoint = f"{API_HOST}{self.endpoint_map['add-database'].format(datasource_id)}"
            datasource_payload = {
                "name": data['name'],
                "dialect": data['dialect'],
                "connection_details": data['connection_details']
            }
            
            datasource_response = requests.post(
                datasource_endpoint,
                data=json.dumps(datasource_payload),
                headers={
                    "Content-Type": "application/json",
                    "Authorization": f"Bearer {auth_token}"
                },
                timeout=59900
            )
            
            datasource_response.raise_for_status()
            results["datasource_result"] = datasource_response.json()
            
            # Display success message
            display(Markdown(f"✅ **Database '{data['name']}' successfully added!**\n\n**Datasource ID:** `{datasource_id}`"))
            
            # Perform database introspection
            try:
                display(Markdown("🔍 **Performing database introspection...**"))
                ddl_info = self._introspect_database(data['connection_details'], data['dialect'])
                if ddl_info:
                    display(Markdown("### 📋 **Database Schema (DDL)**"))
                    display(Markdown(f"```json\n{json.dumps(ddl_info, indent=2)}\n```"))
                    
                    # Automatically train RAG system with the extracted DDL
                    try:
                        display(Markdown("🧠 **Training RAG system with database schema...**"))
                        
                        # Use existing _handle_api_command method to train RAG
                        rag_cell_content = json.dumps({"ddl": ddl_info['ddl']})
                        rag_result = self._handle_api_command("rag-train", datasource_id, rag_cell_content, False, None)
                        
                        if rag_result is None or not rag_result.get('error'):
                            display(Markdown("✅ **RAG system successfully trained with database schema!**"))
                        else:
                            display(Markdown(f"⚠️ **RAG training failed:** {rag_result.get('error', 'Unknown error')}"))
                    except Exception as rag_error:
                        display(Markdown(f"⚠️ **RAG training failed:** {str(rag_error)}"))
                else:
                    display(Markdown("⚠️ **Could not retrieve database schema** - missing required database drivers or connection failed"))
            except Exception as e:
                display(Markdown(f"⚠️ **Database introspection failed:** {str(e)}"))
            
            return None
            
        except requests.RequestException as e:
            error_msg = str(e)
            return {
                "error": "Failed to connect to API endpoint",
                "details": error_msg
            }
        except Exception as e:
            return {
                "error": "Unexpected error occurred",
                "details": str(e)
            }

    def _introspect_database(self, connection_details, dialect):
        """Introspect database schema and return DDL information"""
        try:
            if dialect.lower() == 'postgresql' and HAS_POSTGRES:
                return self._introspect_postgresql(connection_details)
            elif dialect.lower() == 'mysql' and HAS_MYSQL:
                return self._introspect_mysql(connection_details)
            elif dialect.lower() == 'sqlite' and HAS_SQLITE:
                return self._introspect_sqlite(connection_details)
            else:
                return None
        except Exception as e:
            raise Exception(f"Database introspection failed: {str(e)}")

    def _introspect_postgresql(self, connection_details):
        """Introspect PostgreSQL database schema"""
        # Handle password from secret reference or direct value
        password = connection_details.get('password', '')
        if password.startswith('secret:'):
            # For now, we can't resolve secrets in introspection, skip
            return None
            
        conn = psycopg2.connect(
            host=connection_details['host'],
            port=connection_details['port'],
            database=connection_details['database'],
            user=connection_details['user'],
            password=password
        )
        
        cursor = conn.cursor()
        
        # Get table information
        cursor.execute("""
            SELECT table_name 
            FROM information_schema.tables 
            WHERE table_schema = 'public' AND table_type = 'BASE TABLE'
            ORDER BY table_name
        """)
        
        tables = cursor.fetchall()
        ddl_statements = []
        
        for (table_name,) in tables:
            # Get column information
            cursor.execute("""
                SELECT column_name, data_type, is_nullable, column_default,
                       character_maximum_length, numeric_precision, numeric_scale
                FROM information_schema.columns 
                WHERE table_name = %s AND table_schema = 'public'
                ORDER BY ordinal_position
            """, (table_name,))
            
            columns = cursor.fetchall()
            column_defs = []
            
            for col_name, data_type, is_nullable, col_default, char_max_len, num_precision, num_scale in columns:
                col_def = f"{col_name} {data_type.upper()}"
                
                # Add length/precision info
                if char_max_len:
                    col_def += f"({char_max_len})"
                elif num_precision and data_type in ['numeric', 'decimal']:
                    if num_scale:
                        col_def += f"({num_precision},{num_scale})"
                    else:
                        col_def += f"({num_precision})"
                
                # Add constraints
                if is_nullable == 'NO':
                    col_def += " NOT NULL"
                if col_default:
                    if 'nextval' in col_default:
                        col_def += " PRIMARY KEY"
                    elif col_default not in ['NULL', 'null']:
                        col_def += f" DEFAULT {col_default}"
                
                column_defs.append(col_def)
            
            # Get foreign keys
            cursor.execute("""
                SELECT kcu.column_name, ccu.table_name, ccu.column_name
                FROM information_schema.table_constraints tc
                JOIN information_schema.key_column_usage kcu ON tc.constraint_name = kcu.constraint_name
                JOIN information_schema.constraint_column_usage ccu ON ccu.constraint_name = tc.constraint_name
                WHERE tc.constraint_type = 'FOREIGN KEY' AND tc.table_name = %s
            """, (table_name,))
            
            foreign_keys = cursor.fetchall()
            for fk_column, ref_table, ref_column in foreign_keys:
                fk_def = f"FOREIGN KEY ({fk_column}) REFERENCES {ref_table}({ref_column})"
                column_defs.append(fk_def)
            
            ddl_statement = f"TABLE: {table_name} ({', '.join(column_defs)});"
            ddl_statements.append(ddl_statement)
        
        conn.close()
        return {"ddl": ddl_statements}

    def _introspect_mysql(self, connection_details):
        """Introspect MySQL database schema"""
        password = connection_details.get('password', '')
        if password.startswith('secret:'):
            return None
            
        conn = mysql.connector.connect(
            host=connection_details['host'],
            port=connection_details['port'],
            database=connection_details['database'],
            user=connection_details['user'],
            password=password
        )
        
        cursor = conn.cursor()
        
        # Get table names
        cursor.execute("SHOW TABLES")
        tables = cursor.fetchall()
        ddl_statements = []
        
        for (table_name,) in tables:
            cursor.execute(f"DESCRIBE {table_name}")
            columns = cursor.fetchall()
            column_defs = []
            
            for field, type_info, null, key, default, extra in columns:
                col_def = f"{field} {type_info.upper()}"
                
                if null == 'NO':
                    col_def += " NOT NULL"
                if key == 'PRI':
                    col_def += " PRIMARY KEY"
                if extra == 'auto_increment':
                    col_def += " AUTO_INCREMENT"
                if default is not None:
                    col_def += f" DEFAULT {default}"
                    
                column_defs.append(col_def)
            
            ddl_statement = f"TABLE: {table_name} ({', '.join(column_defs)});"
            ddl_statements.append(ddl_statement)
        
        conn.close()
        return {"ddl": ddl_statements}

    def _introspect_sqlite(self, connection_details):
        """Introspect SQLite database schema"""
        database_path = connection_details.get('database', connection_details.get('path', ''))
        
        conn = sqlite3.connect(database_path)
        cursor = conn.cursor()
        
        # Get table names
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%'")
        tables = cursor.fetchall()
        ddl_statements = []
        
        for (table_name,) in tables:
            cursor.execute(f"PRAGMA table_info({table_name})")
            columns = cursor.fetchall()
            column_defs = []
            
            for cid, name, type_info, notnull, dflt_value, pk in columns:
                col_def = f"{name} {type_info.upper()}"
                
                if pk:
                    col_def += " PRIMARY KEY"
                    if type_info.upper() == 'INTEGER':
                        col_def += " AUTOINCREMENT"
                
                if notnull and not pk:
                    col_def += " NOT NULL"
                if dflt_value is not None:
                    col_def += f" DEFAULT {dflt_value}"
                    
                column_defs.append(col_def)
            
            # Get foreign keys
            cursor.execute(f"PRAGMA foreign_key_list({table_name})")
            foreign_keys = cursor.fetchall()
            
            for id_fk, seq, ref_table, from_col, to_col, on_update, on_delete, match in foreign_keys:
                fk_def = f"FOREIGN KEY ({from_col}) REFERENCES {ref_table}({to_col})"
                column_defs.append(fk_def)
            
            ddl_statement = f"TABLE: {table_name} ({', '.join(column_defs)});"
            ddl_statements.append(ddl_statement)
        
        conn.close()
        return {"ddl": ddl_statements}

    def _handle_api_command(self, action, datasource_id, cell, to_ai, ai_model, sql_model=None):
        """Handle commands that use the API"""
        try:
            if action not in self.endpoint_map:
                valid_actions = ", ".join(f"'{a}'" for a in self.endpoint_map.keys())
                return {"error": f"Invalid action: {action}. Must be one of: {valid_actions}"}
            
            if action in ["sql-ask", "generate-sql", "run-sql", "generate-summary", "rag-train", "update-schema"] and not datasource_id:
                return {"error": f"Missing datasource_id. Usage: %%calliope {action} [datasource_id]"}
            
            if action == "update-schema":
                endpoint = f"{API_HOST}{self.endpoint_map[action].format(datasource_id)}"
            else:
                endpoint = f"{API_HOST}{self.endpoint_map[action]}"
            
            payload = self._prepare_payload(action, datasource_id, cell, sql_model)
            
            response = requests.post(
                endpoint,
                data=json.dumps(payload),
                headers={"Content-Type": "application/json"},
                timeout=59900
            )
            
            response.raise_for_status()
            
            try:
                result = response.json()

                if to_ai:
                    return self._process_with_ai(result, cell, ai_model)
                else:
                    if action == "ask-sql":
                        self._display_formatted_result(result, action)
                        return None
                    return result
                
            except json.JSONDecodeError:
                return {"error": "API response was not valid JSON", "response_text": response.text[:200]}
                
        except requests.RequestException as e:
            error_msg = str(e)
            return {
                "error": "Failed to connect to API endpoint",
                "details": error_msg,
                "endpoint": endpoint
            }
        
    
    def _prepare_payload(self, action, datasource_id, cell, sql_model=None):
        """Prepare the payload for the API request based on the action"""
        payload = {}
        
        match action:
            case "ask-sql":
                payload = {
                    "question": cell.strip(),
                    "datasource_id": datasource_id,
                    "generate_summary": True,
                    "generate_chart": True,
                    "generate_followups": True
                }
                
                # Add LLM model and provider if specified
                if sql_model and sql_model in self.sql_providers:
                    provider_info = self.sql_providers[sql_model]
                    payload["llm_provider"] = provider_info["id"]
                    payload["llm_model"] = provider_info["sql_model"]
            case "generate-sql":
                payload = {
                    "question": cell.strip(),
                    "datasource_id": datasource_id
                }
            case "run-sql":
                payload = {
                    "sql_query": cell.strip(),
                    "datasource_id": datasource_id
                }
            case "followup-questions":
                try:
                    data = json.loads(cell.strip())
                    question = data.get("question")
                    sql_query = data.get("sql_query") 
                    results = data.get("results")
                    
                    if not all([question, sql_query, results]):
                        return {"error": "Cell must contain JSON with format: {'question': '...', 'sql_query': '...', 'results': '...'}"}
                        
                except json.JSONDecodeError:
                    return {"error": "Cell must contain valid JSON with format: {'question': '...', 'sql_query': '...', 'results': '...'}"} 
                payload = {
                    "question": question,
                    "sql_query": sql_query,
                    "results": results
                }
            case "generate-summary":
                payload = {
                    "query_results": cell.strip(),
                    "datasource_id": datasource_id
                }
            case "rag-train":
                try:
                    data = json.loads(cell.strip())
                    
                    if "ddl" in data and isinstance(data["ddl"], list) and all(isinstance(x, str) for x in data["ddl"]):
                        payload = {
                            "ddl": data["ddl"],
                            "datasource_id": datasource_id
                        }
                    elif "documentation" in data and isinstance(data["documentation"], list) and all(isinstance(x, str) for x in data["documentation"]):
                        payload = {
                            "documentation": data["documentation"],
                            "datasource_id": datasource_id
                        }
                    elif ("question" in data and isinstance(data["question"], list) and all(isinstance(x, str) for x in data["question"]) and
                        "sql" in data and isinstance(data["sql"], list) and all(isinstance(x, str) for x in data["sql"])):
                        payload = {
                            "question": data["question"],
                            "sql": data["sql"],
                            "datasource_id": datasource_id
                        }
                    else:
                        return {"error": "Payload must contain either ddl: string[], documentation: string[], or both question: string[] and sql: string[]"}
                except json.JSONDecodeError:
                    return {"error": "Cell must contain valid JSON"}
            case "update-schema":
                pass
            case "clear-rag":
                pass
                
        return payload
    
    def _process_with_ai(self, result, cell, ai_model):
        """Process the API result with AI"""
        ai_prompt = f"""\
        Please interpret this response in the context of the question: {cell.strip()}. 
        Format the response strictly as a Jupyter notebook response with the appropriate markdown.

        ---BEGIN DATA---
        Summary: {result.get("summary")}
        Response: {result.get("response")}
        Followup Questions: {", ".join(result.get("followup_questions", []))}
        SQL Query: {result.get("sql_query")}
        ---END DATA---
        """

        ai_magic = f"%%ai {ai_model} --format code\n{ai_prompt}"
        self.shell.run_cell(ai_magic)
        return None
    
    def _display_formatted_result(self, result, action):
        """Format and display the result with proper markdown and visualizations"""
        if "error" in result:
            display(HTML(f"<div style='color: red; font-weight: bold;'>Error: {result['error']}</div>"))
            if "details" in result:
                display(HTML(f"<div style='color: red;'>Details: {result['details']}</div>"))
            return
        
        markdown_output = ""
        
        if "datasource_id" in result and result["datasource_id"]:
            markdown_output += f"## Query Results: {result.get('datasource_id', '')}\n\n"
        
        if "summary" in result and result["summary"]:
            markdown_output += f"### Summary\n{result['summary']}\n\n"
        
        if "response" in result and result["response"]:
            markdown_output += f"{result['response']}\n\n"
        
        if "visualization" in result and result["visualization"]:
            display(Markdown(markdown_output))
            
            try:
                visualization = result["visualization"]
                fig = go.Figure(
                    data=visualization.get("data", []),
                    layout=visualization.get("layout", {})
                )
                
                fig.show()
                
                markdown_output = ""
            except Exception as e:
                markdown_output += f"**Error displaying visualization:** {str(e)}\n\n"
        
        if "sql_query" in result and result["sql_query"]:
            markdown_output += f"### Executed SQL\n```sql\n{result['sql_query']}\n```\n\n"
        
        if "followup_questions" in result and result["followup_questions"]:
            markdown_output += "### Suggested Follow-up Questions\n"
            for question in result["followup_questions"]:
                markdown_output += f"- {question}\n"
            markdown_output += "\n"
        
        if markdown_output:
            display(Markdown(markdown_output))

def load_ipython_extension(ipython):
    """
    Register the magic with IPython.
    This function is called when the extension is loaded.
    
    Can be manually loaded in a notebook with:
    %load_ext pergamon_server_extension
    """
    global __MAGIC_LOADED__
    
    if not __MAGIC_LOADED__:
        ipython.register_magics(CalliopeMagics)
        
        # Register the completion system
        register_magic_completer(ipython)
        
        __MAGIC_LOADED__ = True
    else:
        pass

load_ext = load_ipython_extension 

