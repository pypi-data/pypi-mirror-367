"""
Help handler for Calliope magic commands.

This module contains all help-related functionality to keep the main magic.py file
more manageable and organized.
"""

from IPython.display import display, Markdown


class CalliopeHelpHandler:
    """Handler for Calliope help functionality."""
    
    def __init__(self, magic_instance=None):
        """Initialize the help handler with optional magic instance reference."""
        self.magic = magic_instance
    
    def handle_help(self):
        """Handle the help command and display comprehensive documentation."""
        help_text = """# 🔮 Calliope Magic Commands

## 📝 Usage
```
%%calliope [command] [datasource_id] [options]
```

## 🎯 Commands

| Command | Description |
|---------|-------------|
| `ask-sql` | Ask natural language questions → get SQL + results + charts |
| `generate-sql` | Convert questions to SQL (no execution) |
| `run-sql` | Execute SQL directly |
| `add-database` | Add datasource with auto-setup |
| `rag-train` | Train AI with schemas/docs/examples |
| `update-schema` | Refresh schema info |
| `clear-rag` | Clear training data |
| `followup-questions` | Generate follow-up questions |
| `generate-summary` | Summarize query results |
| `ask` | General AI assistant |
| `list-models` | Show available AI models |
| `help` | Show this help |

## ⚙️ Options

| Option | Description |
|--------|-------------|
| `--model [name]` | Choose AI model (for ask-sql: SQL generation, others: post-processing) |
| `--sql-model [name]` | Choose SQL generation model (ask-sql only) |
| `--to-ai` | Enhanced AI explanations |

## 🤖 SQL Models (for ask-sql)

| Provider | Best For |
|----------|----------|
| `openai` | General purpose, reliable |
| `anthropic` | Complex analytical queries |
| `gemini` | Fast, simple queries |
| `perplexity` | Real-time data |
| `ai21` | Enterprise reliability |
| `aws` | AWS workflows |
| `cohere` | Structured data |
| `mistral` | European compliance |
| `nvidia` | High performance |
| `ollama` | Local deployment |

## 📋 Examples

**Basic Query:**
```python
%%calliope ask-sql sales_db
What were our top products last quarter?
```

**With Model Selection:**
```python
%%calliope ask-sql sales_db --model openai
%%calliope ask-sql analytics_db --sql-model anthropic
```

**Enhanced Processing:**
```python
%%calliope ask-sql sales_db --model openai --to-ai --model claude3
```

**Database Setup:**
```python
%%calliope add-database
{
    "datasource_id": "my_db",
    "name": "My Database",
    "dialect": "postgresql",
    "connection_details": {
        "host": "localhost",
        "port": 5432,
        "database": "mydb",
        "user": "user",
        "password": "password"
    }
}
```

**RAG Training:**
```python
%%calliope rag-train my_db
{
    "ddl": ["CREATE TABLE users (id SERIAL, name VARCHAR(100))"]
}
```

Run `%calliope list-models` for all AI models."""
        display(Markdown(help_text))
        return None