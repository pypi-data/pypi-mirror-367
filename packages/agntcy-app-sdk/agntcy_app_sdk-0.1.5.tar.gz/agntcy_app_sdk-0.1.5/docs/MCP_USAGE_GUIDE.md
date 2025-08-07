# MCP Usage Guide

In this guide, we will walk through some of the key features of the Agntcy Application SDK and explore an end-to-end example of creating two MCP agents that communicate over a PubSub transport.

The following diagram illustrates how the MCP protocol maps to a transport implementation:

<p align="center">
  <img src="mcp-architecture.png" alt="architecture" width="90%">
</p>

The following table summarizes the current transport and protocol capabilities:

The following table summarizes the current transport and protocol implementations available in the SDK:

| Protocol \ Transport | SLIM | NATS | MQTT |
| -------------------- | :--: | :--: | :--: |
| **MCP**              |  ✅  |  ✅  |  🕐  |

Additional features incorporating AGNTCY's identity and observability components are coming soon.

### ⚡️ Connecting an MCP client to an MCP server over an abstract transport (SLIM | NATS | MQTT)

A benefit of decoupling protocols from transports is that you can easily create agents that communicate over non http, point-to-point transports such as NATS or Agntcy's SLIM. Below is an example of how to create an MCP client and server that communicate over SLIM's gateway server.

We will use `uv` for package management and virtual environments. If you don't have it installed, you can install it via:

```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

Create a new project directory:

```bash
uv init agntcy-mcp
cd agntcy-mcp
```

Install the Agntcy Application SDK and Langgraph:

```bash
uv add agntcy-app-sdk
```

Next we will create a simple weather agent that responds to weather queries. Create a file named `weather_agent.py` and implement the A2A agent and add a message bridge to a SLIM transport:

```python
from agntcy_app_sdk.factory import AgntcyFactory
from mcp.server.fastmcp import FastMCP

# create an MCP server instance
mcp = FastMCP()

# add a tool to the MCP server
@mcp.tool()
async def get_forecast(location: str) -> str:
    return "Temperature: 30°C\n" "Humidity: 50%\n" "Condition: Sunny\n"

# create an Agntcy factory transport instance
transport = factory.create_transport("SLIM", endpoint="http://localhost:46357")
# transport = factory.create_transport("NATS", endpoint="localhost:4222")

# serve the MCP server via a message bridge
bridge = factory.create_bridge(mcp, transport=transport, topic="my_weather_agent.mcp")
await bridge.start(blocking=block)
```

Next we will create a simple client agent that queries the weather agent. Create a file named `weather_client.py` and implement the A2A client with a SLIM transport:

```python
from agntcy_app_sdk.factory import AgntcyFactory

factory = AgntcyFactory()
transport = factory.create_transport("SLIM", endpoint="http://localhost:46357")
# transport = factory.create_transport("NATS", endpoint="localhost:4222")

# Create a MCP client
print("[test] Creating MCP client...")
mcp_client = factory.create_client(
    "MCP",
    agent_topic="my_weather_agent.mcp",
    transport=transport_instance,
)
async with mcp_client as client:
    # Build message request
    tools = await client.list_tools()
    print("[test] Tools available:", tools)

    result = await client.call_tool(
        name="get_forecast",
        arguments={"location": "Colombia"},
    )
    print(f"Tool call result: {result}")
```

A few notes about the code above:

- The weather agent is choosing not to provide a URL in its agent card, instead it will be discovered by a SLIM transport topic.
- Conversely, the client agent uses the `A2AProtocol.create_agent_topic` method to create a topic based on the agent` card, which is used to connect to the weather agent.

### 🏁 Running the Example

First lets run the SLIM transport server, see the agntcy-app-sdk [docker-compose.yaml](https://github.com/agntcy/app-sdk/blob/main/infra/docker/docker-compose.yaml) or SLIM [repo](https://github.com/agntcy/slim/tree/main).

Now we can run the weather agent server:

```bash
uv run python weather_agent.py
```

You should see a log message indicating that the message bridge is running:

```
...
2025-07-08 13:32:40 [agntcy_app_sdk.bridge] [INFO] [loop_forever:57] Message bridge is running. Waiting for messages...
```

Next, we can run the weather client:

```bash
uv run python weather_client.py
```

You should see a print output with the weather report:

```
root=SendMessageSuccessResponse(id='1c24a07e-45af-4800-81bc-cc2fd1b579e1', jsonrpc='2.0', result=Message(contextId=None, kind='message', messageId='e68913c7-312d-4bfe-88f6-4b4179d4b5bd', metadata=None, parts=[Part(root=TextPart(kind='text', metadata=None, text='The weather is sunny with a high of 75°F.'))], referenceTaskIds=None, role=<Role.agent: 'agent'>, taskId=None))
```

🚀 Congratulations! You have successfully created two A2A agents that communicate over a SLIM transport.

For a fully functional multi-agent example integrating A2A, Agntcy, and Langgraph, check out our [coffeeAgntcy](https://github.com/agntcy/coffeeAgntcy).

### ⚙️ Contributing additional Transports

To contribute a new transport implementation, follow these steps:

1. **Implement the Transport Interface**: Create a new class for your transport in the `src/agntcy_app_sdk/transports` directory. Ensure it inherits from the `BaseTransport` interface and implements all required methods.

2. **Update the Factory**: Modify the `AgntcyFactory` to include your new transport in the `create_transport` method.

3. **Add Tests**: Create unit tests for your transport in the `tests/e2e` directory. Ensure all tests pass.

4. **Documentation**: Update the documentation to include your new transport. This includes any relevant sections in the README and API reference.

5. **Submit a Pull Request**: Once your changes are complete, submit a pull request for review.

See [API Reference](API_REFERENCE.md) for detailed SDK API documentation.
