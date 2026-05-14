## JSON and XML

Human-readable text formats widely used for APIs, configuration, and data interchange. Schema-optional — you can validate against a schema but it's not required.

```json
{
  "user_id": 42,
  "name": "Alex",
  "email": "alex@example.com",
  "roles": ["admin", "user"]
}
```

```text
Advantages:
  ✓ Human-readable, easy to debug (curl, browser dev tools)
  ✓ Universally supported across languages and platforms
  ✓ Self-describing (field names are in the data)
  ✓ Flexible — no compilation step needed

Disadvantages:
  ✗ Verbose — field names repeated in every record
  ✗ Slower to parse than binary formats
  ✗ No built-in schema enforcement (runtime errors)
  ✗ Number precision issues (JSON has no integer type)
```

JSON is the default for REST APIs and browser-facing services. XML is largely legacy but still appears in SOAP, enterprise integrations, and configuration files.

## Protocol Buffers and Thrift

Binary serialization formats with explicit schemas and code generation. Each field is identified by a number rather than a name, making the payload compact and parsing fast.

```text
Protocol Buffers (.proto definition):
  message User {
    int32 user_id = 1;
    string name = 2;
    string email = 3;
    repeated string roles = 4;
  }

  Serialized: ~30 bytes (vs. ~90 bytes for JSON equivalent)
  No field names in the wire format — just field numbers and values.

Thrift (similar concept, different ecosystem):
  Originally from Facebook. Supports multiple serialization formats
  (binary, compact, JSON) and includes an RPC framework.
```

```text
Advantages over JSON:
  ✓ 2–10× smaller payloads (no field names, binary encoding)
  ✓ 2–10× faster to serialize/deserialize
  ✓ Schema enforcement at compile time (type-safe clients)
  ✓ Code generation for any language from one .proto file

Disadvantages:
  ✗ Not human-readable (binary)
  ✗ Requires compilation step (protoc compiler)
  ✗ Harder to debug without tooling
```

Protocol Buffers are the standard for gRPC. Use them for internal service-to-service communication where performance matters and both sides control the schema.

## Avro

A binary serialization format where the schema is stored alongside the data rather than embedded in each record. Designed for data pipelines and Hadoop ecosystems.

```text
Avro schema (JSON):
  {
    "type": "record",
    "name": "User",
    "fields": [
      {"name": "user_id", "type": "int"},
      {"name": "name", "type": "string"},
      {"name": "email", "type": ["null", "string"]}
    ]
  }

How it differs from Protocol Buffers:
  - No field numbers — fields matched by name during schema resolution
  - Writer's schema and reader's schema can differ (schema resolution)
  - Schema is stored in the file header (self-describing files)
  - Better for dynamic schemas (no compilation needed)
```

Avro is the default for Kafka (with a Schema Registry), Spark, and Hadoop data pipelines. Choose it when data flows through systems where the schema evolves frequently and the consumer may use a different schema version than the producer.

## Schema Evolution

The ability to change a data format — add fields, remove fields, rename fields — without breaking existing readers or writers. Essential in distributed systems where producers and consumers are deployed independently.

```text
Backward compatible:
  New schema can read data written with old schema.
  Rule: new fields must have defaults.
  Example: add "phone" field with default null.
  → New reader reads old data (no phone) → gets null. ✓

Forward compatible:
  Old schema can read data written with new schema.
  Rule: old reader ignores unknown fields.
  Example: old reader encounters "phone" field → ignores it. ✓

Full compatible:
  Both backward AND forward compatible.
  Safest — deploy producer and consumer in any order.

Breaking changes:
  ✗ Removing a required field
  ✗ Changing a field's type (int → string)
  ✗ Renaming a field (in Protobuf — field number stays, name is cosmetic)
```

```text
Schema Registry (Kafka ecosystem):
  Central store for Avro/Protobuf schemas.
  Enforces compatibility rules on schema changes.
  Producers register schemas; consumers fetch them by ID.
  Prevents incompatible schemas from being published.
```

In interviews, mention schema evolution when designing any data pipeline, event bus, or API versioning strategy. "We'd use Avro with a Schema Registry to ensure backward-compatible evolution of our Kafka events."
