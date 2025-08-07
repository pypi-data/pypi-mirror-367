# AgentDNS Python SDK

**Overview**
This is the python sdk for AgentDNS. AgentDNS is a root domain naming and service discovery system designed to enable LLM agents to autonomously discover, resolve, and securely invoke third-party agent and tool services across organizational and technological boundaries.

For more details about AgentDNS, please refer to the original research paper: https://arxiv.org/abs/2505.22368

## 🎯 Features

- **🔍 Semantic Service Discovery**: Find the most suitable Agent or Tool service using natural language semantics
- **⚡ Unified Service Invocation**: Call various Agent or Tool services through a standardized interface
- **🔄 Async Support**: Supports both synchronous and asynchronous operation modes
- **💰 Cost Management**: Balance inquiry and usage tracking


## 📦 Installation

### Install with pip

```bash
pip install agentdns
```

### Development environment installation

```bash
git clone https://github.com/agentdns/agentdns-sdk.git
cd agentdns-sdk
pip install -e ".[dev]"
```

**Note**: This project uses the src-layout structure, with the package code located in the `src/agentdns/` directory.


## 🚀 Quick start

### Basic Use

```python
from agentdns import AgentDNS

# Set api_key (You need to register in advance on the AgentDNS root service web)
AGENTDNS_API_KEY = 'your_agentdns_api_key'

# Initialize the client
client = AgentDNS(
    api_key=AGENTDNS_API_KEY,
    base_url="https://agentdnsroot.com", 
)

# Service discovery
tools = client.search("I need a search service")
print(f"{len(tools)} tools found")

# View the information of the first tool
tool = tools[0]
print(f"Tool Name: {tool['name']}")
print(f"Organization: {tool['organization']}")
print(f"Price: {tool['cost']['price']} {tool['cost']['currency']}")

# Service request
data = {
    "q": "What is LLM Agent?",
    "scope": "webpage",
    "includeSummary": True,
    "includeRowContent": False,
    "size": 10
}

response = client.request(tool["agentdns_url"], json=data)
print(f"Result: {response}")
```


## 📄 Licence

This project uses [Apache-2.0 licence]。


---