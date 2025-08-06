
# 🧠 Bruce Agent

**AgentX** is a lightweight, extensible agentic framework for building custom LLM agents with structured tool use, prompt templates, and integration with OpenAI and Gemini models.

## 🚀 Features

- 🔁 Custom reasoning loop (`AgentRunner`)
- 🧩 Structured tool execution (Pydantic-based)
- 💬 Prompt templating and management
- 🔌 LLM-agnostic: supports **OpenAI function calling** and **Google Gemini**
- 🪄 Easy-to-use API for building agents

## 📦 Installation

published to PyPI:

```sh
pip install AgentX-Dev
```

## Example use

```python
from AgentXL import AgentRunner, AgentType,ChatModel
from pydantic import BaseModel
from AgentXL.Tools import StructuredTool
# Define a sample tool
class MultiplyTool(StructuredTool):
    name = "multiply"
    description = "Multiply two numbers"

    class Schema(BaseModel):
        a: int
        b: int

    def run(self, a: int, b: int) -> int:
        return a * b

# Create chat model and agent
ReAct=AgentType.ReAct
chat_model = ChatModel.GPT(model="gpt-4", temperature=0.7)
tools = [MultiplyTool()]
agent = AgentRunner(model=chat_model,Agent=ReAct, tools=tools)

response = agent.Initialize("What is 5 times 8?")
print(response.content)



```

``` bruce_framework/
├── src/
│   └── bruce_framework/
│       ├── __init__.py
│       ├── agent/
│       │   ├── __init__.py
│       │   └── agent.py
│       ├── runner/
│       │   ├── __init__.py
│       │   └── agent_run.py
│       └── chatmodel.py
├── README.md
├── LICENSE
└── pyproject.toml

```

## 📚 Documentation (Coming Soon)
### More tutorials, tool examples, and structured prompting guides coming soon.

## 🧑‍💻 Author
#### Bruce-Arhin Shadrach
#### 📧 brucearhin098@gmail.com
#### 🌐 GitHub

📝 License
MIT License


