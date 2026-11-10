# Encoding, Serialization, and Schema Evolution — Drills

Original practice for which bytes go on the wire, which layout a read wants, and which schema change may ship. Each card is one exercise: commit to an answer, then check it. The numbers are invented for Milepost Dome, which logs one sky sample a second. REST and RPC stay in Networking and Communication. The log and the broker stay in Message Queues and Async Processing. The lake, and event sourcing as a store, stay in Storage and Data Processing at Scale. The warehouse, and a column-family row, stay in Databases NoSQL and Specialized. Replica versions stay in Consistency and Replication.

## Serialization Format

Four readers ask for sky samples. Pick JSON, Protocol Buffers, Avro, or Parquet for each.

```text
1. public-board — a visitor's browser loads the latest sample. They will not generate a client.
2. dome-stub — the dome controller calls the log service. Both are code the station ships, and the call site is a function stub.
3. night-event — each sample is appended for consumers that upgrade on different nights. The schema rides with the sample.
4. season-scan — mean brightness for the year, one field across many nights, from files already in the lake.
```

```python
CALLERS = ["public-board", "dome-stub", "night-event", "season-scan"]
```

**Answer:** JSON, Protocol Buffers, Avro, then Parquet. The board is a browser in a visitor's hands, so the names stay in the text. The stub is an internal call the station generates, so the bytes are field numbers. That call is RPC. The night event will be read by a program whose schema differs from the writer's, matched by name, so the encoding is Avro. The year scan reads one column of a lake file, so the file is Parquet. The lake that holds the file stays in Storage and Data Processing at Scale. The warehouse that can answer the same mean stays in Databases NoSQL and Specialized.

```python
CALLERS = ["public-board", "dome-stub", "night-event", "season-scan"]
FORMAT = {
    "public-board": "json",
    "dome-stub": "protobuf",
    "night-event": "avro",
    "season-scan": "parquet",
}

print(" ".join(FORMAT[name] for name in CALLERS))
# json protobuf avro parquet
```

## JSON Cost

The public board sends one compact JSON sample. The sensor writes the same shape once a second for six hours, 21,600 times. How many bytes of that night are the values, and how many are the names and the punctuation around them?

```python
import json

SAMPLE = {"dome": "milepost", "second": 23, "facing": "nw", "brightness": 3}
NIGHT = 6 * 60 * 60
```

**Answer:** The values are 16 bytes, `milepost,23,nw,3`. The compact JSON is 60 bytes. The other 44 are the field names and the braces, quotes, and colons that attach them. One board sample can spend those 44 bytes without anyone noticing. The night spends them 21,600 times: 950,400 bytes of repeated structure beside 345,600 bytes of values. The JSON for the night is 1,296,000 bytes. That 16-byte line is a floor on the values, and a real Protocol Buffers payload is a different encoding of numbers and tags. The comparison still shows why the sensor path drops the repeated names, and why the board can keep them.

```python
import json

SAMPLE = {"dome": "milepost", "second": 23, "facing": "nw", "brightness": 3}
NIGHT = 6 * 60 * 60


def night_bytes(sample: dict, count: int) -> tuple[int, int]:
    compact = len(json.dumps(sample, separators=(",", ":")).encode())
    values = len(",".join(str(value) for value in sample.values()).encode())
    return compact * count, values * count


print(night_bytes(SAMPLE, 1), night_bytes(SAMPLE, NIGHT))
# (60, 16) (1296000, 345600)
```

## Field Number

The old stub was generated with `brightness = 4`. Two writers ship. What does the old stub still see in each case?

```text
rename — the definition now says magnitude = 4. The wire still carries 3 under number 4.
new-number — the definition says magnitude = 5, and the writer sends 3 under number 5 only.
```

```python
OLD_READER = {4: "brightness"}
RENAME = {4: 3}
NEW_NUMBER = {5: 3}
```

**Answer:** On the rename, the old stub still sees brightness 3. The number stayed 4, so the new name is the same field. On the new number, the old stub sees no brightness. It was built to read 4, it skips 5, and the writer stopped sending 4. A rename that keeps the number can ship as the same field. A new number is a different field, and the old stub will not find the value there.

```python
OLD_READER = {4: "brightness"}
RENAME = {4: 3}
NEW_NUMBER = {5: 3}


def project(reader: dict[int, str], wire: dict[int, int]) -> dict[str, int]:
    return {name: wire[number] for number, name in reader.items() if number in wire}


print(project(OLD_READER, RENAME), project(OLD_READER, NEW_NUMBER))
# {'brightness': 3} {}
```

## Avro Default

Writer v1 encodes dome, second, and brightness. Writer v2 adds `cloud_ok` and, in this sample, sets it true. The reader default for `cloud_ok` is false. What does a v1 reader return for the v2 sample, and what does a v2 reader put in `cloud_ok` for the v1 sample?

```python
WRITER_V1 = {"dome": "milepost", "second": 23, "brightness": 3}
WRITER_V2 = {"dome": "milepost", "second": 23, "brightness": 3, "cloud_ok": True}
READER_V1 = ("dome", "second", "brightness")
READER_V2 = ("dome", "second", "brightness", "cloud_ok")
DEFAULTS = {"cloud_ok": False}
```

**Answer:** The v1 reader returns dome, second, and brightness. It has no `cloud_ok`, so the extra name is skipped. That is an old reader on new bytes. The v2 reader fills `cloud_ok` with false, because the v1 sample has no such name and the reader schema supplies the default. That is a new reader on old bytes. The true on the v2 sample is visible to a reader whose schema still asks for `cloud_ok`. Matching is by name. The log those samples may ride stays in Message Queues and Async Processing.

```python
WRITER_V1 = {"dome": "milepost", "second": 23, "brightness": 3}
WRITER_V2 = {"dome": "milepost", "second": 23, "brightness": 3, "cloud_ok": True}
READER_V1 = ("dome", "second", "brightness")
READER_V2 = ("dome", "second", "brightness", "cloud_ok")
DEFAULTS = {"cloud_ok": False}


def resolve(record: dict, fields: tuple[str, ...], defaults: dict) -> dict:
    found = {}
    for name in fields:
        if name in record:
            found[name] = record[name]
        else:
            found[name] = defaults[name]
    return found


old_reader = resolve(WRITER_V2, READER_V1, DEFAULTS)
new_reader = resolve(WRITER_V1, READER_V2, DEFAULTS)
print(old_reader, new_reader["cloud_ok"])
# {'dome': 'milepost', 'second': 23, 'brightness': 3} False
```

## Row or Column

Three samples are on disk. Two jobs run: fetch `s-14`, and the mean of brightness. Which layout does each job want, and how many fields does it have to touch?

```python
SAMPLES = [
    {"id": "s-14", "second": 23, "facing": "nw", "brightness": 3},
    {"id": "s-15", "second": 24, "facing": "n", "brightness": 6},
    {"id": "s-16", "second": 25, "facing": "e", "brightness": 3},
]
JOBS = ["fetch-s-14", "mean-brightness"]
```

**Answer:** Fetching `s-14` is a row read. The board wants all four fields of that one sample, so the read touches four fields and stops. The mean is a column read. It touches the brightness column only, and the mean of 3, 6, and 3 is 4. Reading facing on the way to that mean is wasted work. The live board stays rows. The season file stays columns. Where that file sits in the lake stays in Storage and Data Processing at Scale.

```python
SAMPLES = [
    {"id": "s-14", "second": 23, "facing": "nw", "brightness": 3},
    {"id": "s-15", "second": 24, "facing": "n", "brightness": 6},
    {"id": "s-16", "second": 25, "facing": "e", "brightness": 3},
]
JOBS = ["fetch-s-14", "mean-brightness"]
BRIGHTNESS = [sample["brightness"] for sample in SAMPLES]


def layout(job: str) -> str:
    if job == "fetch-s-14":
        return "row"
    return "column"


def fields_touched(job: str) -> int:
    if job == "fetch-s-14":
        return len(SAMPLES[0])
    return 1


print([layout(job) for job in JOBS], [fields_touched(job) for job in JOBS])
print(sum(BRIGHTNESS) // len(BRIGHTNESS))
# ['row', 'column'] [4, 1]
# 4
```

## Compatibility Pick

The current sample is dome, second, and brightness, an int. Readers skip fields they do not know. Classify each edit as backward, forward, full, or breaking.

```text
1. add-cloud-default — add cloud_ok, a bool, default false.
2. add-note-required — add note, a string, required, with no default.
3. drop-second — stop writing second. Old readers still require second and have no default. New readers no longer ask for it.
4. brightness-to-string — brightness becomes a string.
```

```python
EDITS = ["add-cloud-default", "add-note-required", "drop-second", "brightness-to-string"]
```

**Answer:** Full, forward, backward, breaking. The optional add is full: a new reader fills false on old bytes, and an old reader skips `cloud_ok` on new bytes. The required note is forward only. An old reader skips it, and a new reader cannot invent the string from old bytes, so the add is not backward. Dropping second is backward only. A new reader no longer asks for it, and an old reader cannot fill a required second that the new bytes omit, so the removal is not forward. The type change breaks both directions. An int and a string are different values. A `/v2/` path on the board is REST, and that path leaves this int still an int.

```python
EDITS = ["add-cloud-default", "add-note-required", "drop-second", "brightness-to-string"]
KIND = {
    "add-cloud-default": "full",
    "add-note-required": "forward",
    "drop-second": "backward",
    "brightness-to-string": "breaking",
}

print(" ".join(KIND[name] for name in EDITS))
# full forward backward breaking
```

## Registry Gate

The night-sample subject uses a full rule. Three proposals arrive. Which ones does the registry accept?

```text
1. add-cloud-default — cloud_ok, a bool, default false.
2. brightness-to-string — brightness changes from an int to a string.
3. drop-second — second goes away. Existing readers still require it and have no default.
```

```python
RULE = "full"
PROPOSALS = ["add-cloud-default", "brightness-to-string", "drop-second"]
```

**Answer:** Accept the optional add. Reject the type change and the removal. A full rule requires both directions. `cloud_ok` with a default is readable by a new consumer on old bytes, and an old consumer can skip it on new bytes. An int that becomes a string is readable in neither direction. Dropping second leaves an old consumer, which still requires second, unable to read the new bytes. A backward-only rule would allow that removal. A full rule refuses it. The registry is the gate. The log that would have stored the sample stays in Message Queues and Async Processing.

```python
RULE = "full"
PROPOSALS = ["add-cloud-default", "brightness-to-string", "drop-second"]


def gate(rule: str, proposal: str) -> str:
    if rule == "full" and proposal == "add-cloud-default":
        return "accept"
    return "reject"


print(RULE, " ".join(gate(RULE, name) for name in PROPOSALS))
# full accept reject reject
```

## Deploy Order

Two changes are ready. For each, say whether the writer, the reader, or either side can ship first.

```text
1. add-cloud-default — full compatibility, as on the cards above.
2. brightness-to-string — the type change.
```

```python
CHANGES = ["add-cloud-default", "brightness-to-string"]
```

**Answer:** Either side can ship the add. Writer first: new samples carry `cloud_ok`, and the old reader skips it. Reader first: the new reader fills false on samples that omit `cloud_ok`. Neither side can ship the type change first. Writer first sends a string the old reader cannot decode. Reader first expects a string and cannot decode the int still on the wire. The path through that break is a new optional field. Add `brightness_text` with a default, leave the int in place until every reader has moved, and treat a later removal as its own compatibility check.

```python
CHANGES = ["add-cloud-default", "brightness-to-string"]


def ship(change: str) -> str:
    if change == "add-cloud-default":
        return "either"
    return "neither"


print(" ".join(ship(name) for name in CHANGES))
# either neither
```
