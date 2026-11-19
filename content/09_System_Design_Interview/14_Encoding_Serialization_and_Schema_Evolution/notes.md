# Encoding, Serialization, and Schema Evolution

An order leaves a phone as JSON, an internal call as Protocol Buffers, a Kafka topic as Avro, and a yearly scan as Parquet. Schema evolution is the set of rules that let old and new code read each other's bytes while a rolling deploy, an installed app, or a retained log still holds the previous version. A schema registry enforces those rules before a producer writes the new shape.

## Key Points

- **JSON and XML** — text with the field names inside every record. The sample order is 45 bytes, 12 of them values. At one order a second for six hours, the names and punctuation add up to 712,800 bytes. JSON has one number syntax, so a JavaScript client stores 9007199254740993 as 9007199254740992. XML tags the same fields and costs more bytes. The HTTP call around the body is REST.
- **Protocol Buffers and Thrift** — a field number and a value, plus generated code. Renaming a field and keeping number 4 keeps the field. A new number is a different field, and a retired number stays reserved. Thrift is the same bargain. Its required fields make later changes brittle. The call is RPC.
- **Avro** — compact binary, schema stored with the data, fields matched by name. The reader skips a name it does not ask for and fills a missing name from the default on its own schema. A file keeps the schema in the header. A Kafka record keeps a schema id. The events ride a log.
- **Columnar storage formats** — one field laid out together inside each row group. Parquet puts the schema and the column offsets in the footer. Compression pays when that column is long and repetitive. A few dozen rows often do not. The lake and the warehouse are the stores around the file. A column-family row is a different layout.
- **Row or column** — fetching order `o-14` reads four fields and stops. The mean of quantities 3, 6, and 3 is 4, and it reads one column. The live API stays on rows. The yearly scan stays on columns.
- **Serialization format** — who reads the bytes, how large they are at this rate, and whether a schema is enforced on write. JSON for the phone, Protocol Buffers for the internal call, Avro for the Kafka order, Parquet for the lake scan.
- **Schema evolution** — changing fields while old and new programs both run. Backward means a new reader can read old bytes. Forward means an old reader can read new bytes. Full is both, so either side can deploy first. A type change breaks both directions. A versioned URL is a different lever, and so is a replica version.
- **Schema registry** — the gate in front of a publish. It checks the subject's rule, then issues a schema id or refuses the schema. A full rule accepts `gift_wrap` with a default and refuses a `cents` type change. The log still stores the bytes.

## Example

The compact JSON for one order is 45 bytes. The values alone are 12. The stream writes one order a second for six hours. A reader that asks for `gift_wrap` and finds it missing fills false. The mean quantity of three stored orders is 4.

```python
import json

ORDER = {"sku": "mug", "qty": 2, "size": "m", "cents": 1299}
WINDOW = 6 * 60 * 60
QTY = [3, 6, 3]


def window_bytes(record: dict, count: int) -> tuple[int, int]:
    compact = len(json.dumps(record, separators=(",", ":")).encode())
    values = len(",".join(str(value) for value in record.values()).encode())
    return compact * count, values * count


def with_default(record: dict, name: str, default: bool) -> bool:
    if name in record:
        return bool(record[name])
    return default


print(window_bytes(ORDER, WINDOW), with_default(ORDER, "gift_wrap", False), sum(QTY) // len(QTY))
# (972000, 259200) False 4
```

A six-hour window is 972,000 bytes of JSON and 259,200 bytes of values. The phone sends that JSON once, and that client has no generated code. The stream is where the repeated names add up. Checkout calls inventory with Protocol Buffers, so a rename that keeps the field number is still the old field. Each Kafka order that other programs will read under a newer schema uses Avro, matched by name, with the schema id resolved through the registry. The yearly file is Parquet, and mean quantity reads the quantity column. Adding `gift_wrap` with a default is full compatibility, so the writer or the reader can deploy first during a rolling update. A registry whose rule is full accepts that add and refuses a change of `cents` from an int to a string.

## See also

- [Networking and Communication](../10_Networking_and_Communication/) — REST and RPC. The phone call and the internal stub. A versioned URL is that topic's lever. This topic is the bytes those calls carry.
- [Message Queues and Async Processing](../11_Message_Queues_and_Async_Processing/) — Log or Queue. Orders may travel on the log. Retention and offsets stay there. The compatibility rule stays here.
- [Storage and Data Processing at Scale](../13_Storage_and_Data_Processing_at_Scale/) — Data Lake, and Event Sourcing as a store. The columnar file lands in the lake. Replaying events into a current order stays there.
- [Databases NoSQL and Specialized](../07_Databases_NoSQL_and_Specialized/) — Data Warehousing and Column-Family Store. A long scan can load the warehouse. A column-family row is a point read of one entity.
- [Consistency and Replication](../09_Consistency_and_Replication/) — the version token that picks a winning replica. Schema versions for an order event stay in this topic.
