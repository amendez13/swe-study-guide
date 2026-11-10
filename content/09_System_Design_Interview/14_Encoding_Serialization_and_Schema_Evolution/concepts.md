## JSON and XML

JSON and XML are text encodings. Each record carries its own field names, so a phone, a browser, or a person reading a log can see the shape without generated code.

A public order API has many readers you do not compile: the mobile app, a browser, and a partner script. Text is the format they already parse. The encoding itself does not check that `qty` is a number. A validator such as JSON Schema or an OpenAPI check is a separate step. Until that step runs, a bad value is still legal text, and it fails when the application reads the field.

One compact order shows where the bytes go.

```json
{"sku":"mug","qty":2,"size":"m","cents":1299}
```

```python
import json

ORDER = {"sku": "mug", "qty": 2, "size": "m", "cents": 1299}


def split_bytes(record: dict, count: int) -> tuple[int, int]:
    compact = len(json.dumps(record, separators=(",", ":")).encode())
    values = len(",".join(str(value) for value in record.values()).encode())
    return compact * count, values * count


print(split_bytes(ORDER, 1), split_bytes(ORDER, 6 * 60 * 60))
# (45, 12) (972000, 259200)
```

The compact object is 45 bytes. The values `mug,2,m,1299` are 12 of those bytes. The other 33 are the names and the braces, quotes, and colons that attach them. One response can spend 33 bytes. The same shape written once a second for six hours is 21,600 orders: 972,000 bytes of JSON, of which 259,200 are values and 712,800 are repeated structure.

JSON text has a single number syntax. It does not mark an integer as different from a fraction. A parser that stores every number as an IEEE-754 double, which is what JavaScript does, cannot represent every integer past 2^53. The integer 9007199254740993 becomes 9007199254740992. Python's `json` module keeps that integer, so the same digits are safe in one process and wrong in a browser. Send a large id as a string when both sides must agree on it. Keep money in integer cents. A JSON number such as 12.99 is a binary fraction a double does not store exactly, and 1299 is exact.

XML puts each value inside a tag. The same four fields, written as `<order><sku>mug</sku><qty>2</qty><size>m</size><cents>1299</cents></order>`, are 74 bytes. A person can still read them. XML remains in older partner APIs, in SOAP-style feeds, and in some configuration files. A new mobile API uses JSON. The HTTP method and URL that carry the body are REST in [Networking and Communication](../10_Networking_and_Communication/). This topic is the body.

MessagePack and CBOR keep the field names and encode them in binary. They shrink the punctuation. They still repeat the names, and they still need a separate check for the shape. Protocol Buffers, on the next card, drop the names when both sides share a schema.

**Trade-offs.** JSON wins when a person or a third-party client must read the payload, and when one response is small next to the work of handling the order. It loses when the same names are written tens of thousands of times, or when a large integer has to survive a JavaScript client. XML wins only when the other side already speaks XML. A hand-edited config file can stay JSON because a person is the reader and there is no stub to generate.

**In an interview.** Say JSON for the mobile API. Say integer cents, and say large ids travel as strings. Say OpenAPI or JSON Schema checks the shape, because the parser only checks that the text is JSON. When the interviewer asks about a high-rate internal call, move to a schema-backed binary format and explain the 33 bytes you would stop repeating.

**Recap**

- JSON and XML keep each field name inside the record, so a reader needs no generated code.
- The sample order is 45 bytes. Twelve are the values, and 33 are names and punctuation.
- At one order a second for six hours, those 33 bytes add up to 712,800 bytes of repeated structure.
- JavaScript rounds the integer 9007199254740993 to 9007199254740992. A large id can travel as a string.
- The same four fields are 74 bytes of XML. A new HTTP API uses JSON. XML remains for older partners and some config files.

![JSON and XML](/content/09_System_Design_Interview/14_Encoding_Serialization_and_Schema_Evolution/diagrams/encoding-1-json-and-xml.png)

*Source: [`diagrams/encoding.drawio`](/content/09_System_Design_Interview/14_Encoding_Serialization_and_Schema_Evolution/diagrams/encoding.drawio), page 1.*

## Protocol Buffers and Thrift

Protocol Buffers and Thrift are schema-backed binary encodings. The bytes carry a field number and a value. Generated code turns that number back into a name.

Checkout calls inventory on every order. Both services are code you compile, so they can share one definition. Repeating the word `cents` on every call spends the 33 bytes of names from the JSON order, plus the quotes and colons, at a rate where that overhead is pure tax. The number is stable even when a developer renames the field in source code.

A definition assigns the numbers once:

```text
message Order {
  string sku = 1;
  int32 qty = 2;
  string size = 3;
  int32 cents = 4;
}
```

On the wire, field 4 is a tag and the integer 1299. The generated code on each side was built with a copy of the definition, and that copy says 4 means `cents`.

1. A rename that keeps the number is the same field. The definition now says `amount = 4`, and the writer still sends 1299 under number 4. An old binary reads 4 and stores 1299 in `cents`.
2. A new number is a different field. The definition says `amount = 5`, and the writer sends 1299 under number 5 only. The old binary was built to read 4. It skips 5, and `cents` is missing.
3. When you remove a field, reserve its number. A later author who reuses 4 for a new meaning makes every old reader treat the new value as `cents`.

```python
OLD_READER = {4: "cents"}


def project(reader: dict[int, str], wire: dict[int, int]) -> dict[str, int]:
    return {name: wire[number] for number, name in reader.items() if number in wire}


print(project(OLD_READER, {4: 1299}), project(OLD_READER, {5: 1299}))
# {'cents': 1299} {}
```

The tag is the field number plus a wire type. Numbers 1 through 15 fit that tag in one byte. Numbers 16 through 2047 take two bytes. Put the fields you send on every call in 1 through 15.

A reader skips a field number it does not know. That is what lets an old binary accept a record from a newer writer. In proto3, a missing number decodes as the zero value for its type: 0, false, or empty. That zero value is the default. If 0 is a real `cents` amount, the new reader cannot tell "the writer omitted this" from "the writer sent a free order." Mark the field `optional` when the reader must tell those two apart.

Thrift is the same bargain in another toolchain: an IDL, field numbers, generated code, and a binary protocol that leaves the names off the wire. Thrift still has `required` fields. A required field is hard to add, because old bytes do not contain it, and hard to remove, because old readers still demand it. New definitions use optional fields. The call that looks like a local function is RPC in [Networking and Communication](../10_Networking_and_Communication/). These bytes are the payload. The usual form of that call is gRPC, which uses Protocol Buffers.

**Trade-offs.** Protobuf fits an internal RPC where you ship both ends and you want small, fast payloads. Thrift stays where both sides already compile Thrift. A public mobile client usually stays on JSON, because a browser and a third-party script have no generated code. You can put protobuf on a public API when you own every client and you accept the work of shipping stubs. The public JSON body and the internal protobuf body can describe the same order.

**In an interview.** Say the field number is the contract and the name is a local label. A rename that keeps the number can roll out while old binaries are still running. Reusing a number cannot. Say you reserve retired numbers, and you put hot fields in 1 through 15. Point the RPC mechanics at Networking, and keep schema changes on the Schema Evolution card.

**Recap**

- The wire carries a field number and a value. Generated code maps the number back to a name.
- Keeping number 4 means a rename still delivers 1299 to an old reader that calls the field `cents`.
- Sending that value only under number 5 makes the old reader skip it, so `cents` is missing.
- Reserve a retired number so a later field cannot reuse it.
- Thrift uses field numbers the same way. Treat its required fields as a compatibility hazard, and prefer optional fields.

![Protocol Buffers and Thrift](/content/09_System_Design_Interview/14_Encoding_Serialization_and_Schema_Evolution/diagrams/encoding-2-protocol-buffers-and-thrift.png)

*Source: [`diagrams/encoding.drawio`](/content/09_System_Design_Interview/14_Encoding_Serialization_and_Schema_Evolution/diagrams/encoding.drawio), page 2.*

## Avro

Avro is a compact binary encoding that stores the writer's schema with the data and matches fields by name.

A Kafka order event outlives the process that wrote it. A consumer deployed next week has to read an event written today, and a consumer still on today's build has to read an event written next week. There is no field number to reserve. The bytes are values in schema order, with no names and no tags, so the reader cannot decode them unless it has the schema the writer used.

That schema travels in one of two places. A file of many orders stores it once, in the file header, and the records follow. A single Kafka record stores a schema id. The consumer fetches the writer schema for that id from a registry. That gate is the Schema Registry card. This compact schema text is 132 bytes:

```json
{"type":"record","name":"Order","fields":[{"name":"sku","type":"string"},{"name":"qty","type":"int"},{"name":"cents","type":"int"}]}
```

Repeating those 132 bytes on all 21,600 events in a six-hour run is 2,851,200 bytes of schema. A four-byte id on each event is 86,400 bytes. The file pays the schema once in the header. The stream pays an id per record and keeps the text in the registry.

Resolution uses two schemas. The writer schema is the names that were encoded, in the order of the bytes. The reader schema is the names this program expects.

1. The reader loads the writer schema from the header or the registry.
2. For each name in the reader schema, it looks for the same name in the writer schema. An alias on the reader field counts as the same name.
3. When both sides have the name, the value moves across. Avro can promote a wider numeric read, such as an int read as a long. An int read as a string fails.
4. A name only the writer sent is skipped.
5. A name only the reader asks for becomes the default declared on the reader schema. If that default is missing, the read fails.

```python
def resolve(record: dict, fields: tuple[str, ...], defaults: dict) -> dict:
    found = {}
    for name in fields:
        if name in record:
            found[name] = record[name]
        else:
            found[name] = defaults[name]
    return found


# Name resolution only. The Avro payload is binary values in writer-schema order.
writer_v1 = {"sku": "mug", "qty": 2, "cents": 1299}
writer_v2 = {"sku": "mug", "qty": 2, "cents": 1299, "gift_wrap": True}
reader_v1 = ("sku", "qty", "cents")
reader_v2 = ("sku", "qty", "cents", "gift_wrap")
defaults = {"gift_wrap": False}

old_reader = resolve(writer_v2, reader_v1, defaults)
new_reader = resolve(writer_v1, reader_v2, defaults)
print(old_reader, new_reader["gift_wrap"])
# {'sku': 'mug', 'qty': 2, 'cents': 1299} False
```

Writer v2 added `gift_wrap` and set it true. The v1 reader has no such name, so it skips the value. That is an old reader on new bytes. The v2 reader, given a v1 record, fills `gift_wrap` with false from its own schema. That is a new reader on old bytes. The default lives on the reader schema. An old writer cannot supply a default the new reader forgot to declare.

The topic those events sit on is a log: Log or Queue in [Message Queues and Async Processing](../11_Message_Queues_and_Async_Processing/). Folding the events into the current order is Event Sourcing in [Storage and Data Processing at Scale](../13_Storage_and_Data_Processing_at_Scale/). This card is the encoding of the event.

**Trade-offs.** Avro fits events whose writers and readers upgrade separately, and files that should stay readable after the code that wrote them is gone. Protobuf fits an RPC where both ends share generated field numbers. JSON fits the phone. Avro's payload is small, and a person reads it by pairing the bytes with the schema. A rename without an alias fails both sides, because each side looks up a name the other omits. An alias on the new reader maps the writer's old name onto the new field. An old reader still looks up the old name.

**In an interview.** Say writer schema and reader schema, matched by name, with the default on the reader. Say a file stores the schema in the header, and a Kafka record stores an id. Then name the registry as the place that id is resolved. Keep offset and retention on the queue topic.

**Recap**

- Avro writes values in schema order and leaves names and field numbers off each record.
- The reader needs the writer schema, from the file header or from a schema id.
- Matching is by name. Extra writer fields are skipped. Missing reader fields use the reader schema's default.
- The sample schema text is 132 bytes. On 21,600 events, repeating it costs 2,851,200 bytes, and a four-byte id per event costs 86,400.
- An int may be read as a long. An int read as a string fails.

![Avro](/content/09_System_Design_Interview/14_Encoding_Serialization_and_Schema_Evolution/diagrams/encoding-3-avro.png)

*Source: [`diagrams/encoding.drawio`](/content/09_System_Design_Interview/14_Encoding_Serialization_and_Schema_Evolution/diagrams/encoding.drawio), page 3.*

## Columnar Storage Formats

A columnar file stores one field for many rows together. A row file stores every field of one row, then the next row.

The monthly question is the mean quantity of orders, or the sum of `cents`. That job reads one field and ignores `sku` and `region`. A row file still has to step through those other fields to reach the number. Laying every quantity together lets the job read one column and skip the rest.

Three orders are enough to see the layout. In a row file the bytes run `o-14`, `mug`, `nw`, `3`, then the same four fields for `o-15` and `o-16`. In a column file the ids sit together (`o-14`, `o-15`, `o-16`), then the regions, then the quantities `3`, `6`, `3`.

A real Parquet file does this inside row groups. Each row group holds a column chunk per field. The schema and the offsets of those chunks sit in the footer, so a reader seeks to the footer and opens the quantity chunk from those offsets. ORC is the same column layout where a pipeline already reads ORC. The files live in the lake: Data Lake in [Storage and Data Processing at Scale](../13_Storage_and_Data_Processing_at_Scale/). The SQL that answers the month question runs in the warehouse: Data Warehousing in [Databases NoSQL and Specialized](../07_Databases_NoSQL_and_Specialized/).

Similar values in one chunk are why compression pays. Quantities `3`, `6`, `3` are a run of small integers, so dictionary encoding and run-length encoding have something to compress, and a codec such as Snappy or Zstandard then has a smaller input. A quantity squeezed between a sku and a region, which is the row layout, gives the codec a worse run. A column of unique order ids compresses poorly, because there is no repeated value to dictionary-encode. A file of a few dozen orders often spends more on the footer, the row-group metadata, and the codec than it saves. A year of orders is long enough for the quantity column to pay.

A column-family database is a different layout. One row key holds the cells of that entity, which is a point read of one order. That store is Column-Family Store in [Databases NoSQL and Specialized](../07_Databases_NoSQL_and_Specialized/). Parquet is a file of many orders, organized by column, for a scan.

**Trade-offs.** Parquet and ORC are the files you write for analytical scans. They are a poor store for "load order o-14," because that read opens several column chunks and stitches one row back together. The live API keeps a row store. A job copies settled orders into a columnar file. Tiny files and unique identifier columns are the cases where the columnar copy is larger or slower than the row file it came from.

**In an interview.** Say Parquet for a scan of a few fields across many orders, with the schema in the footer. Mention row groups: each group stores its own column chunks. Say a few dozen rows do not pay for the footer and the codec. Keep the column-family store on its own card.

**Recap**

- A row file stores one order's fields together. A columnar file stores one field for many orders together.
- Parquet keeps the schema and the column offsets in the footer. A reader jumps to the quantity column.
- ORC is the same idea where the pipeline already reads ORC.
- Compression pays when the column is long and repetitive. Unique ids and a few dozen rows often do not pay.
- The lake holds the file. The warehouse runs the month query. A column-family row is a point-read layout.

![Columnar Storage Formats](/content/09_System_Design_Interview/14_Encoding_Serialization_and_Schema_Evolution/diagrams/encoding-4-columnar-storage-formats.png)

*Source: [`diagrams/encoding.drawio`](/content/09_System_Design_Interview/14_Encoding_Serialization_and_Schema_Evolution/diagrams/encoding.drawio), page 4.*

## Row or Column

Use a row layout when the read wants one whole record. Use a column layout when the read wants one field across many records.

The same orders serve two jobs. The mobile API loads order `o-14` for a customer. The monthly report asks for the mean quantity. One layout makes one of those jobs read bytes it will throw away.

```python
ORDERS = [
    {"id": "o-14", "sku": "mug", "region": "nw", "qty": 3},
    {"id": "o-15", "sku": "cup", "region": "n", "qty": 6},
    {"id": "o-16", "sku": "bowl", "region": "e", "qty": 3},
]


def fields_touched(job: str) -> int:
    if job == "fetch-o-14":
        return len(ORDERS[0])
    return 1


qty = [order["qty"] for order in ORDERS]
print(fields_touched("fetch-o-14"), fields_touched("mean-qty"), sum(qty) // len(qty))
# 4 1 4
```

Fetching `o-14` reads four fields and stops. Those four fields are the whole order the phone renders. A columnar file would open the id column, the sku column, the region column, and the quantity column, pull one value from each, and stitch the row back. That is extra seeks for one order.

The mean reads quantity only. The values are 3, 6, and 3, and the mean is 4. A row file reads sku and region on the way to each quantity. A columnar file reads the quantity column and skips the rest. At three rows the waste is small. At a year of orders, reading three unused fields on every row dominates the scan.

The live API and the database of record stay rows. The file the monthly job scans stays columns. The file's home is Data Lake in [Storage and Data Processing at Scale](../13_Storage_and_Data_Processing_at_Scale/). The store that answers the SQL is Data Warehousing in [Databases NoSQL and Specialized](../07_Databases_NoSQL_and_Specialized/).

**Trade-offs.** A system that serves both jobs keeps both layouts. The row store answers the phone. A copy in Parquet answers the mean. Writing that copy has lag: the mean is as fresh as the last export. Serving the phone from Parquet, or running the year-long mean against the live row store, each makes the other job pay.

**In an interview.** Ask which fields the query touches before you name a store. Four fields of one order is a row. One field of a year is a column. If the interviewer wants both, say the row store serves the API and a columnar copy serves the scan, and say how fresh that copy has to be.

**Recap**

- Fetching order `o-14` touches four fields of one row, then stops.
- The mean of quantities 3, 6, and 3 is 4, and it touches one column.
- The live API stays on rows. The year-long scan stays on columns.
- Keeping both means a copy, and the copy is as fresh as the last export.

![Row or Column](/content/09_System_Design_Interview/14_Encoding_Serialization_and_Schema_Evolution/diagrams/encoding-5-row-or-column.png)

*Source: [`diagrams/encoding.drawio`](/content/09_System_Design_Interview/14_Encoding_Serialization_and_Schema_Evolution/diagrams/encoding.drawio), page 5.*

## Serialization Format

The format follows who reads the bytes, how large the payload is at the rate you have, and whether a schema is enforced before the write.

One shop produces the same order four ways. The phone loads it. Checkout calls inventory with it. Kafka carries it to billing and to search. A yearly job scans one field of it. Those readers do not want the same bytes, and picking one format for all four makes three of them pay.

| Reader | Format | Why this one |
| --- | --- | --- |
| Phone or browser, no generated client | JSON | Names stay in the text. One response can spend the extra 33 bytes. |
| Checkout calling inventory, both compiled here | Protocol Buffers | Field numbers, no names. The call is an RPC. |
| Kafka consumers that upgrade on their own | Avro | Names matched, schema id on the record, default on the reader. |
| Mean quantity across a year of lake files | Parquet | One column, schema in the footer. |

Apply the three questions in order.

1. Who reads it? A person, a browser, or a partner you do not ship code to reads JSON. Two services you generate read protobuf. A consumer that will be upgraded while old events are still in the log reads Avro. A scan of one field reads Parquet.
2. What does the rate do to the size? One order of 45 bytes is a JSON response. The same shape 21,600 times spends 712,800 bytes on repeated names. That is the point where an internal call or a log drops the names.
3. Is a schema enforced before the write? JSON can be validated by OpenAPI, and the check is optional. Protobuf and Avro refuse to encode a field the schema does not have. The registry card is the gate that applies that rule to a stream. Parquet writes the schema into the file footer, so a later job knows the columns.

A file a person edits by hand stays JSON. The size is beside the point, and there is no stub to generate. Thrift stays the contract where both sides already compile Thrift. One order rarely pays for a columnar file or for a codec. The year file is where that layout earns its cost.

**Trade-offs.** You can send protobuf to a mobile app you own. You then ship a generated client with the app, and an old app build still has the old field numbers, so schema evolution still applies. JSON remains the default when any reader is a browser or a third party. Using Avro for a synchronous checkout call works and is unusual. The caller wants a response now, and both sides can share generated code, which is the protobuf case. Using Parquet as the response body of the phone call makes the client stitch a row out of columns.

**In an interview.** Say the three questions out loud, then name one format for each reader. Offer JSON to the phone, protobuf on the internal RPC, Avro on the Kafka order, and Parquet for the yearly scan. Say Thrift only when it is already the toolchain. The HTTP status line and the RPC framework stay in [Networking and Communication](../10_Networking_and_Communication/).

**Recap**

- Choose from who reads the bytes, the size at this rate, and whether a schema is enforced on write.
- The phone gets JSON. The internal call gets Protocol Buffers. The Kafka order gets Avro. The year scan gets Parquet.
- A hand-edited file stays JSON. Thrift stays where both sides already compile it.
- One order does not pay for a columnar file. A year of one field does.

![Serialization Format](/content/09_System_Design_Interview/14_Encoding_Serialization_and_Schema_Evolution/diagrams/encoding-6-serialization-format.png)

*Source: [`diagrams/encoding.drawio`](/content/09_System_Design_Interview/14_Encoding_Serialization_and_Schema_Evolution/diagrams/encoding.drawio), page 6.*

## Schema Evolution

Schema evolution is changing the fields of a message over time while programs still on the previous version can read and write it.

It exists because old and new code run at the same time. Eight API servers, replaced two at a time, spend the rollout with both versions serving traffic. A new server writes an order that an old consumer still reads. An old server writes an order that a new consumer reads. The phone is slower than the rollout: the app installed last month keeps calling the API after the servers are done. Kafka's default retention is seven days, so a new consumer also reads events that were written under an older schema and are still in the log.

Two directions name which of those readers still works. Assume a reader skips a field it does not know. JSON does that when the client ignores unknown keys. A strict parser that rejects unknown keys gives up the forward direction. Protobuf and Avro skip unknown fields by rule.

Backward compatible means a new reader can read bytes an old writer produced. The new code looks back at old data. Forward compatible means an old reader can read bytes a new writer produced. The old code accepts data from a writer that is ahead of it. Full compatibility is both directions, so either side can deploy first. A change that works in only one direction has a required order. A breaking change fails both directions, so neither side can deploy first while the other version is still live.

Who deploys first follows the direction that works.

- Full: either the writer or the reader deploys first.
- Backward only: deploy every reader first, then the writers. An old reader fails on the new bytes.
- Forward only: deploy the writers first. Deploy the readers afterward, once old bytes are gone, because a new reader fails on those bytes. On a log, retention has to drop them, or a job has to rewrite them.
- Breaking: deploy neither side onto the same stream. Add a new field, move readers, move writers, and remove the old field as its own change.

The order `{sku, qty, cents}` walks the common edits. `cents` is an int. Readers skip unknown fields. A missing field is filled only when the reader has a default: application code for JSON, the zero value or an explicit default for protobuf, and the reader schema for Avro.

| Change | New reader, old bytes | Old reader, new bytes | Result |
| --- | --- | --- | --- |
| Add `gift_wrap`, a bool, default false | Fills false | Skips `gift_wrap` | Full. Either side first. |
| Add required `note`, a string, no default | Cannot invent the string | Skips `note` | Forward only. Writers first. |
| Stop writing `sku`. Old readers still require it and have no default. | The new reader no longer asks | The old reader cannot fill `sku` | Backward only. Readers first. |
| Change `cents` from int to string | Fails | Fails | Breaking. Neither side first. |
| Rename `cents` to `amount`, no alias, matched by name | Looks up a name the old bytes omit | Looks up a name the new bytes omit | Breaking for Avro and for JSON bound by name. |

A type change is the usual break. Avro will promote an int to a long. It will not read an int as a string. Treat any type change you have not checked against the format's promotion list as breaking.

A rename that keeps protobuf field number 4 is still `cents` on the wire. The old generated code keeps working. An alias on a new Avro reader maps the writer's old name onto the new field, which restores the backward direction for readers that have the alias. Old readers still look for the old name. The safe rename is a new field, written beside the old one, until every reader has moved.

Those seven days of events stay after the writer process restarts. A new consumer that lacks backward compatibility with them fails on replay. A registry rule that compares only with the latest schema can miss an older generation still inside the window. The registry card is where that check is enforced. Folding the events into a current order is Event Sourcing in [Storage and Data Processing at Scale](../13_Storage_and_Data_Processing_at_Scale/).

A `/v2/` path, or a version header, is a different lever. That is the HTTP API, REST in [Networking and Communication](../10_Networking_and_Communication/). Use it when the change is breaking and old phones must keep calling the old contract. A version token that picks a winning replica among copies is a different version. That token stays in [Consistency and Replication](../09_Consistency_and_Replication/).

**Trade-offs.** Full compatibility is the rule when you cannot order the deploys, which is the phone and a Kafka topic with independent consumer teams. Backward-only is enough when you can stop the writers, upgrade every reader, and then start the writers, and when no old bytes remain to be read. Adding fields with defaults keeps the door open. Required fields and renames close it. A new URL is the clean break when the old contract has to live for the life of an installed app.

**In an interview.** Define the term first. Backward means a new reader reads old bytes. Forward means an old reader reads new bytes. Full means either side deploys first. Then take one change and say who rolls first. For a type change, say neither, and describe the extra field: add `cents_text` with a default, keep the int, move every reader, then the writers, and remove the int later as its own check. Mention the installed phone and the seven-day log as the reasons both directions show up in real systems.

**Recap**

- Schema evolution is a field change that old and new code can both survive while they run side by side.
- Backward compatibility: the new reader reads old bytes. Forward compatibility: the old reader reads new bytes. Full is both.
- Add `gift_wrap` with a default and the change is full. Add a required `note` with no default and it is forward only.
- Drop a field old readers still require and the change is backward only. Change `cents` from int to string and it breaks both directions.
- A protobuf rename that keeps the field number stays compatible. A name-matched rename without an alias does not.
- A breaking HTTP change gets a new URL. A replica's version token is a different problem.

![Schema Evolution](/content/09_System_Design_Interview/14_Encoding_Serialization_and_Schema_Evolution/diagrams/encoding-7-schema-evolution.png)

*Source: [`diagrams/encoding.drawio`](/content/09_System_Design_Interview/14_Encoding_Serialization_and_Schema_Evolution/diagrams/encoding.drawio), page 7.*

## Schema Registry

A schema registry stores schemas for a stream and rejects a new schema that breaks the compatibility rule on that subject.

Producers and consumers deploy on different days, and the topic keeps old events. Without a gate, one producer can publish a `cents` string into a topic whose consumers still decode an int. Those bytes stay for the retention window. The registry runs the Schema Evolution rules at publish time, so a bad schema gets no id and the bytes are never written.

The subject is the name the rule hangs on. For a topic called `orders`, the usual subject for the value is `orders-value`. The key can have its own subject. The steps for one change:

1. The producer proposes a schema for `orders-value`.
2. The registry compares it with the rule on that subject: backward, forward, full, or none. A non-transitive rule compares the proposal with the latest schema. A transitive rule compares it with every registered version, which is what you want when the topic still holds events from more than the latest schema. Kafka's default retention is seven days, so more than one version is a normal state.
3. Under a full rule, changing `cents` from int to string is refused. Dropping `sku` while existing readers still require it, with no default, is refused. The producer gets an error and does not publish the new encoding.
4. Adding optional `gift_wrap`, a bool with default false, passes a full rule. The registry stores the schema and returns an id, such as 7.
5. The producer writes the Kafka record with that id. Confluent's serializer prefixes the Avro bytes with one magic byte and a four-byte schema id.
6. The consumer reads the id, fetches schema 7, and resolves its reader schema against that writer schema. It caches schema 7, so the next record with the same id does not ask again.

The log stores the event bytes, the id, and the offsets. How long the record stays, and which consumer keeps which offset, are Log or Queue in [Message Queues and Async Processing](../11_Message_Queues_and_Async_Processing/). The rule that allows or refuses the schema is this card. An accepted schema does not rewrite events already in the log. Those events keep the id they were written with.

**Trade-offs.** Confluent Schema Registry defaults to backward, and that check is non-transitive: the new schema is compared with the latest schema, and you upgrade every consumer before the producers. A new consumer can then rewind through data the previous schema wrote. Set the subject to full when an old consumer must also keep reading during the producer rollout. That is a rolling deploy whose order you do not control, and a phone that stays installed. A transitive rule extends the check from the latest schema to every registered version, so a seven-day log that holds more than one generation stays covered. Forward matches writers first, and the new readers wait until older bytes are gone. None turns the gate off, which fits a topic you can wipe. The registry stops a publish the readers cannot survive. It leaves events already in the log on the id they were written with, and it leaves the consumer deploy to you. The same gate exists for Protobuf and for JSON Schema. Avro plus a registry is the common Kafka pairing because those bytes need the writer schema.

**In an interview.** Say the registry is the gate and the log is the data. Name the subject and the rule before you describe the field. The usual default is backward, so consumers upgrade first and can rewind one schema. Under a full rule, `gift_wrap` with a default is accepted and a `cents` type change is rejected. Say the consumer uses the id on the record to fetch the writer schema. Mention a transitive check when the log holds more than the latest version.

**Recap**

- The registry checks a proposed schema against the subject's rule and then issues an id, or it refuses the proposal.
- The usual subject for topic `orders` is `orders-value`.
- A full rule accepts `gift_wrap` with a default and refuses an int-to-string change and a removal that old readers still require.
- A transitive rule checks every registered version, not only the latest, so events still inside retention stay readable.
- The record carries the schema id. The log keeps the bytes. The consumer fetches and caches the schema.

![Schema Registry](/content/09_System_Design_Interview/14_Encoding_Serialization_and_Schema_Evolution/diagrams/encoding-8-schema-registry.png)

*Source: [`diagrams/encoding.drawio`](/content/09_System_Design_Interview/14_Encoding_Serialization_and_Schema_Evolution/diagrams/encoding.drawio), page 8.*
