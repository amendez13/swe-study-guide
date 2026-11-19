# MCP, Evaluation, and AI Security

Share tools over MCP, test answer quality, watch cost, and limit the damage of prompt injection.

## Key points

- An MCP server publishes `@Tool` methods to any MCP client; the client starter brings remote tools into `ChatClient`.
- Connect only trusted MCP servers; their tool descriptions and results reach the model.
- `RelevancyEvaluator` and `FactCheckingEvaluator` score answers with a judge model.
- Spring AI observations record latency and token usage; prompt logging is off by default.
- Prompt injection cannot be prompted away: enforce permissions in code and keep keys out of prompts.

## Example

Turn the [catalog tools](#13_Spring_Boot/28_Spring_AI_ChatClient_Prompts_and_Tools/concepts/tool-calling-with-the-tool-annotation) into an MCP server with the [server configuration](#13_Spring_Boot/30_MCP_Evaluation_and_AI_Security/concepts/expose-tools-with-an-mcp-server). Start it, then inspect it with the MCP Inspector, which lists the tools and lets you call them.

```sh
./mvnw spring-boot:run -Dspring-boot.run.arguments=--server.port=8081
npx @modelcontextprotocol/inspector
```

In the inspector, choose the Streamable HTTP transport and connect to `http://localhost:8081/mcp`.
