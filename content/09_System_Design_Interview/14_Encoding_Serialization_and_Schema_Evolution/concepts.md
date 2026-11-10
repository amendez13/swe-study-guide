## JSON and XML

JSON is text. A visitor, a browser, and a quick command can all read the latest sky sample from Milepost Dome: the dome name, the second offset, the facing, and the brightness. The field names sit inside the record, so a reader that has never seen a definition can still find `brightness`. Nothing is compiled first. A check that the shape is right is a separate step, and a bad value shows up when something reads the record.

The names ride along every time. One sample on the public board is a small cost. One sample a second, all night, repeats the same names, and the quotes and colons that attach them travel too. JSON has one number type. A whole-number counter can lose low bits when a parser stores every JSON number as a float.

XML is the older text form. Each value sits inside a tag, so the same four fields take more bytes, and a person can still read them. It still arrives from older partners and in some configuration files. A new public board does not start there. The URL and the HTTP method that carry this JSON are REST in [Networking and Communication](../10_Networking_and_Communication/). This card is the text in the body.

```text
{"dome":"milepost","second":23,"facing":"nw","brightness":3}
names        inside every record
one board    the repeated names are cheap
all night    the same names, once a second
XML          tags around the same fields; older exchanges
```

## Protocol Buffers and Thrift

The dome controller and the log service are both code the station ships. They leave the field names off the wire. A definition assigns each field a number. The bytes are that number and the value. A generated stub in each language turns number 4 back into the name that stub was built with. The call that looks like a local function is RPC in [Networking and Communication](../10_Networking_and_Communication/). These bytes are the payload of that call. The usual form of that call is gRPC.

The number is the identity of the field. Renaming field 4 from `brightness` to `magnitude` in the definition, and leaving the number at 4, keeps the same field. An old stub still reads 4 and fills `brightness`. A new stub reads 4 and fills `magnitude`. Giving the new name number 5, and stopping the writer from sending 4, creates a different field. The old stub has no slot for 5. It skips 5, and `brightness` is missing.

Thrift is the same bargain in another toolchain: a definition, field numbers, generated code, and a compact binary. The station's internal calls use Protocol Buffers. The public board stays JSON, because a visitor has no generated stub.

```text
brightness = 4          the number is the field
rename, number stays 4  an old stub still fills brightness
new number 5            the old stub never asked for 5
```

## Avro

Avro writes compact binary, and the schema travels with the data. A file of samples stores the schema in the header. A single sample can carry a schema id, and the reader looks that id up. Fields match by name. The writer schema is the set of names that were encoded. The reader schema is the set of names this program expects. Where a name appears on both, the value moves across. A name only the writer sent is skipped. A name only the reader asks for becomes the default on the reader schema.

That resolution is how `cloud_ok` can appear on a new writer while an older tally still runs. Nobody has to reserve a field number. The place those samples may travel is a log: Log or Queue in [Message Queues and Async Processing](../11_Message_Queues_and_Async_Processing/). Replaying the samples into a current value is Event Sourcing in [Storage and Data Processing at Scale](../13_Storage_and_Data_Processing_at_Scale/). This card is the encoding of the sample.

```text
writer schema    names that were encoded
reader schema    names this program asks for
match            by name
schema           in the file header, or fetched by id
```

## Columnar Storage Formats

A row encoding lays one sample's fields together, then the next sample. A columnar file lays one field together: every brightness, then every facing. Parquet is the file the season archive uses, and the schema sits in the footer. ORC is the same layout where a stack already reads that file. The raw landing those files sit in is the Data Lake in [Storage and Data Processing at Scale](../13_Storage_and_Data_Processing_at_Scale/). The long question, mean brightness by month, runs in the warehouse: Data Warehousing in [Databases NoSQL and Specialized](../07_Databases_NoSQL_and_Specialized/). This card is the file layout.

Values of one field sit next to each other, so a compression codec sees a long run of small integers. A brightness squeezed between two strings gives the codec less of a run. A season file is long enough for the codec to pay. A file of a few dozen samples often spends more on the codec and the footer than it saves. A column-family store, one row key and a slice of that row, is Column-Family Store in [Databases NoSQL and Specialized](../07_Databases_NoSQL_and_Specialized/).

```text
row file      one sample, then the next
column file   every brightness, then every facing
parquet       the usual lake file; schema in the footer
compress      pays when one column is long and repetitive
```

## Row or Column

Showing sample `s-14` on the board wants the whole record: second, facing, brightness, and the rest. A row layout reads that record and stops. A columnar file would open each column, pull one value, and stitch the row back. That work is a poor fit for "this sample."

Mean brightness for the season wants one field. A row file reads the facing and the dome name on the way to the brightness. A columnar file reads the brightness column and skips the rest. The live board stays rows. The season archive stays columns. The file's home in the lake is Data Lake in [Storage and Data Processing at Scale](../13_Storage_and_Data_Processing_at_Scale/). The store that answers the month question is Data Warehousing in [Databases NoSQL and Specialized](../07_Databases_NoSQL_and_Specialized/).

```text
fetch s-14                 row, the whole sample
mean brightness, season    column, one field
live board                 row
season archive             column
```

## Serialization Format

The format follows who reads the bytes, how large the payload is at the rate you have, and whether a schema is enforced before the write. A visitor or a browser reads JSON. Two services the station generates read Protocol Buffers. A sample whose writer and reader change on different nights reads Avro: names matched, schema with the data. A scan of one field across a season reads Parquet.

A file a person edits by hand can stay JSON. The size is beside the point, and there is no stub to generate. Thrift stays the contract where that toolchain is already what both sides compile. One sample rarely pays for a columnar file or for compressing a column. The night stream and the season file are where that layout and that codec earn their cost.

```text
public board, a browser          JSON
internal stub                    Protocol Buffers
events that change over nights   Avro
season scan in the lake          Parquet
who, size, schema enforced       the three questions
```

## Schema Evolution

The writer and the reader ship on different nights. Compatibility is which of those nights can still read the other night's bytes.

Backward compatible means a new reader can read bytes an old writer produced. A new field needs a default, because the old bytes omit it. Adding `cloud_ok` with default false is backward compatible: the new reader fills false when the name is absent. Forward compatible means an old reader can read bytes a new writer produced. The old reader skips a field it does not know, so the same add is forward compatible. Full compatibility is both directions. The writer or the reader can ship first.

A type change breaks both directions. An int in `brightness` cannot be read as a string, and the reverse fails too. Adding a required `note` with no default is forward compatible and fails backward: the old reader skips it, and the new reader cannot invent the string from old bytes. Removing `second` when the old reader still requires it, and has no default, is backward compatible and fails forward: the new reader no longer asks for `second`, and the old reader cannot fill it. In a name-matched format, renaming `brightness` with no alias fails both sides, because each side looks up a name the other omits. In Protocol Buffers that rename keeps the field when the number stays put.

A `/v2/` path, or a version header on the public board, is a different lever. That is the HTTP API, REST in [Networking and Communication](../10_Networking_and_Communication/). A replica's version, the token used to pick a winner among copies, stays off this card. Folding the samples into a current value is Event Sourcing in [Storage and Data Processing at Scale](../13_Storage_and_Data_Processing_at_Scale/).

```text
backward    new reader, old bytes; a new field has a default
forward     old reader, new bytes; unknown fields are skipped
full        both, so either side can ship first
breaking    a type change, or a rename with no alias when matching by name
```

## Schema Registry

A schema registry is the gate in front of publish. The producer proposes a schema for a subject, the night samples. The registry compares that schema with the compatibility rule on the subject, backward, forward, or full, and rejects the proposal when the change fails the rule. An accepted schema gets an id. The sample can carry the id, and a consumer fetches the schema by id.

The log that keeps the sample is Log or Queue in [Message Queues and Async Processing](../11_Message_Queues_and_Async_Processing/). How long the record stays, and which reader keeps which offset, stay on that card. The rule that allows or refuses the schema is this one. Under a full rule, a type change on `brightness` is refused. An optional `cloud_ok` with a default is accepted.

```text
propose     a schema for the night-sample subject
rule        backward, forward, or full
refuse      a change the rule cannot read in the direction it promises
accept      an optional field with a default, under a full rule
id          the consumer fetches the schema; the log holds the bytes
```
