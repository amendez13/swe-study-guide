# Encoding, Serialization, and Schema Evolution

Milepost Dome logs one sky sample a second: a dome name, a second offset, a facing, and a brightness. The public board, the dome's internal call, the night event, and the season file do not want the same bytes. A schema can gain a field while old and new programs still read each other, and a registry can refuse a change that they cannot.

## Key Points

- **JSON and XML** — text, with the field names inside every record. JSON is the usual public body. The names are cheap once and expensive all night. XML is the tagged form still seen in older exchanges. The call around the body is REST.
- **Protocol Buffers and Thrift** — a field number and a value, plus generated stubs. Renaming a field and keeping the number keeps the field. A new number is a different field. Thrift is the same bargain in another toolchain. The call is RPC.
- **Avro** — compact binary, schema stored with the data, fields matched by name. The writer schema and the reader schema can differ, and a missing name becomes the reader's default. The samples may travel on a log.
- **Columnar storage formats** — one field laid out together. Parquet is the usual lake file, with the schema in the footer. Compression pays when that column is long and repetitive. The lake and the warehouse are the stores around the file.
- **Row or column** — a row read fetches one whole sample. A column read scans one field across many samples. The live board stays rows. The season archive stays columns.
- **Serialization format** — who reads the bytes, how large they are at this rate, and whether a schema is enforced. JSON on the public board, Protocol Buffers on the internal stub, Avro on events that change, Parquet in the lake.
- **Schema evolution** — backward is a new reader on old bytes, forward is an old reader on new bytes, and full is both. A type change breaks both. A versioned URL is a different lever, and so is a replica version.
- **Schema registry** — a gate that rejects a schema the subject's rule cannot accept, then hands out an id. The log still stores the bytes. The rule lives here.

## Example

The compact JSON for one sample is 60 bytes. The values alone are 16. The dome writes one sample a second for six hours. A reader that asks for `cloud_ok` and finds it missing fills false.

```python
import json

SAMPLE = {"dome": "milepost", "second": 23, "facing": "nw", "brightness": 3}
NIGHT = 6 * 60 * 60


def night_bytes(sample: dict, count: int) -> tuple[int, int]:
    compact = len(json.dumps(sample, separators=(",", ":")).encode())
    values = len(",".join(str(value) for value in sample.values()).encode())
    return compact * count, values * count


def with_default(record: dict, name: str, default: bool) -> bool:
    if name in record:
        return bool(record[name])
    return default


print(night_bytes(SAMPLE, NIGHT), with_default(SAMPLE, "cloud_ok", False))
# (1296000, 345600) False
```

A six-hour night is 1,296,000 bytes of JSON and 345,600 bytes of values. The public board sends that JSON once, for a visitor who will not generate a stub. The sensor path is where the repeated names add up. The internal stub uses Protocol Buffers, so a rename that keeps the field number is still the old field. Each night sample that other programs will read under a newer schema uses Avro, matched by name. The season archive is a Parquet file of columns, and mean brightness reads the brightness column. Adding `cloud_ok` with a default is full compatibility, so the writer or the reader can ship first. A registry whose rule is full accepts that add and refuses a change of `brightness` from an int to a string.

## See also

- [Networking and Communication](../10_Networking_and_Communication/) — REST and RPC. The public call and the internal stub. A versioned URL is that topic's lever. This topic is the bytes those calls carry.
- [Message Queues and Async Processing](../11_Message_Queues_and_Async_Processing/) — Log or Queue. Samples may travel on the log. The compatibility rule stays here.
- [Storage and Data Processing at Scale](../13_Storage_and_Data_Processing_at_Scale/) — Data Lake, and Event Sourcing as a store. The season file lands in the lake. Replaying samples into a current value stays there.
- [Databases NoSQL and Specialized](../07_Databases_NoSQL_and_Specialized/) — Data Warehousing and Column-Family Store. A long scan can load the warehouse. A column-family row is a different layout.
