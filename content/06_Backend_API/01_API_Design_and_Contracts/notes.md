# API Design and Contracts

This topic is about treating a backend API as a stable contract instead of an incidental implementation detail. The more consumers an API has, the more important it becomes to design names, schemas, and behaviors deliberately before the code ossifies around bad choices.

## Key Points

- **APIs are product surfaces** - Other software depends on them, so behavior and compatibility decisions have lasting cost.
- **Consumer-centered design** - Shape the contract around client workflows, not around raw storage tables.
- **Design-first and code-first differ** - Design-first favors explicit reviewable contracts; code-first favors speed and framework convenience.
- **Audience matters** - Public, partner, and private APIs need different levels of governance and compatibility discipline.
- **OpenAPI is executable documentation** - A spec can power docs, mocks, validation, diffing, and SDK generation.
- **Examples reduce ambiguity** - Sample requests and responses often clarify intent faster than paragraphs of prose.

## Example

```python
api_contract = {
    "name": "Orders API",
    "audience": "partner",
    "operations": {
        "createOrder": {
            "method": "POST",
            "path": "/orders",
            "response": 201,
        },
        "listOrders": {
            "method": "GET",
            "path": "/orders",
            "response": 200,
        },
    },
}

for name, operation in api_contract["operations"].items():
    print(f"{name}: {operation['method']} {operation['path']} -> {operation['response']}")
```

Even this tiny dictionary shows the core idea: an API contract is a named surface with explicit operations and responses that can be reviewed independently of the code that eventually serves it.
