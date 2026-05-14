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

A minimal OpenAPI contract for an Orders API — the kind of artifact a design-first team reviews before writing any handler code:

```yaml
openapi: 3.0.3
info:
  title: Orders API
  version: "1.0"
paths:
  /orders:
    get:
      summary: List orders
      parameters:
        - name: status
          in: query
          schema: { type: string, enum: [pending, paid, shipped] }
      responses:
        "200":
          description: Paginated order list
    post:
      summary: Create an order
      requestBody:
        required: true
        content:
          application/json:
            schema:
              type: object
              required: [customerId, items]
              properties:
                customerId: { type: integer }
                items:
                  type: array
                  items:
                    type: object
                    properties:
                      sku: { type: string }
                      quantity: { type: integer }
      responses:
        "201":
          description: Order created
        "422":
          description: Validation error
```

This spec is reviewable before any code exists: a frontend team can build against it using a mock server, a reviewer can check naming and status codes, and CI can diff it against the previous version to catch breaking changes.
