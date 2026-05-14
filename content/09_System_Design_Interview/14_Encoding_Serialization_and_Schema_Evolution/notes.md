# Encoding, Serialization, and Schema Evolution

How data is encoded for storage and transmission, and how schemas change over time without breaking the system. In system design interviews, this matters when you're designing data pipelines, choosing communication protocols, or explaining how services can evolve independently.

## Key Points

- **JSON/XML** — human-readable, universally supported, verbose. Default for REST APIs and browser-facing services. No built-in schema enforcement.
- **Protocol Buffers / Thrift** — binary, schema-driven, code-generated. 2–10× smaller and faster than JSON. Default for gRPC and internal service communication.
- **Avro** — binary, schema stored with data, field matching by name. Default for Kafka, Spark, and data pipelines. Best for evolving schemas without recompilation.
- **Schema evolution** — backward compatible (new reader, old data), forward compatible (old reader, new data), full compatible (both). Use a Schema Registry to enforce rules on Kafka topics.

## Example

Choosing serialization formats across a system:

```text
Client → API Gateway:    JSON over REST
  Why: browser-friendly, human-readable, cacheable.

API Gateway → Services:  Protocol Buffers over gRPC
  Why: type-safe, fast, streaming support.
  Schema: .proto files shared via a schema repository.

Services → Kafka:        Avro with Schema Registry
  Why: schema evolution without redeploying consumers.
  Add a new field → new producer writes it, old consumer
  ignores it (forward compatible). No downtime.

Kafka → Data Warehouse:  Parquet files on S3
  Why: columnar format for analytical queries.
  Spark reads Avro from Kafka, writes Parquet to S3.
  Schema embedded in the Parquet file header.

Evolution example:
  v1: { user_id: int, name: string }
  v2: { user_id: int, name: string, email: string (default: null) }

  v2 producer writes events with email.
  v1 consumer reads events, ignores email field. ✓
  v2 consumer reads old events, email defaults to null. ✓
  → Full compatibility. Deploy in any order.
```
