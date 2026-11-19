# Spring AI ChatClient, Prompts, and Tools

Call an LLM from Spring Boot with ChatClient, stream its answers, get typed output, and let it use your methods as tools.

## Key points

- Spring AI 2.0 targets Boot 4; one starter per provider autoconfigures a `ChatModel` and a `ChatClient.Builder`.
- Keep application instructions in the system prompt and user input in the user message.
- `stream().content()` returns a `Flux<String>` for server-sent events.
- Prompt templates take parameters; `entity(Class)` parses the reply into a record.
- `@Tool` methods let the model fetch data; advisors such as `MessageChatMemoryAdvisor` add conversation memory.

## Example

Add the Spring AI BOM and the Anthropic starter from [LLMs and Spring AI](#13_Spring_Boot/28_Spring_AI_ChatClient_Prompts_and_Tools/concepts/llms-and-spring-ai), plus the [librarian controller](#13_Spring_Boot/28_Spring_AI_ChatClient_Prompts_and_Tools/concepts/call-a-model-with-chatclient). Export your key and ask for recommendations. Every call is billed by the provider.

```sh
export ANTHROPIC_API_KEY=...
./mvnw spring-boot:run
curl -s 'http://localhost:8080/api/recommend?topic=space%20travel'
```
