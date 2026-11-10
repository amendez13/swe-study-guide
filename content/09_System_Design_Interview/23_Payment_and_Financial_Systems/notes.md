# Payment and Financial Systems

Halden Ropewalk sells consigned dock lines. Buyers pay the ropewalk, Cove moves the money, and the ledger records a buyer leg, a splicer leg, and a shed fee that sum to 0. A key is checked before Cove is called, a webhook is signed and safe to replay, and silence is polled. Refunds start at the ropewalk. Chargebacks start at the bank. An authorization holds funds until a capture or a void. The generic retry key, the vendor adapter, the batch job, the wait, the atomic commit, and the reserved product stay in the topics that own them.

## Key Points

- **Idempotency in Payments** — look up `l42-try-1` before calling Cove. A stored failure is that try's result. `l44-try-2` is the next try of a line that failed. A second delivery of `evt-l42-9` writes the ledger once. The generic POST rule is Idempotency.
- **Payment Service Provider (PSP) Integration** — an intent, a signed webhook, and a poll when the wait ends in silence. A bad signature is dropped. Unknown stays unknown. The vendor boundary is Third-Party Integration. The wait is Timeouts and Retries.
- **Double-Entry Bookkeeping** — buyer -480, splicer +408, shed +72, sum 0. A missing fee leg sums to -72. The three legs are one Transaction.
- **Reconciliation** — L-51 in Cove's file and missing from the ledger is an orphan. L-44 in the ledger and missing from Cove is a phantom. The morning job's shape is Batch Processing.
- **Payment State Machine** — CREATED goes to PROCESSING, and PROCESSING goes to SUCCEEDED, FAILED, or CANCELLED. SUCCEEDED does not go to CREATED. FAILED does not go to SUCCEEDED. A refund starts at SUCCEEDED.
- **Handling Refunds and Chargebacks** — the ropewalk reverses a charge through Cove. The opposite legs are written when Cove confirms, and they sum to 0. The buyer's bank opens a chargeback. Evidence is due in 14 days. A loss adds a fee pair of 15.
- **Authorize and Capture** — authorize holds 480 and writes no settled legs. Confirm captures. Cancel or expiry voids. A void after SUCCEEDED is a refund. The reserved product is Ticket Booking System.

## Example

L-42's three legs, two charge moves, and a failed key followed by a new key:

```python
def net(legs: tuple[tuple[str, int], ...]) -> int:
    return sum(amount for _name, amount in legs)


def allowed(src: str, dst: str) -> bool:
    legal = {
        "CREATED": {"PROCESSING"},
        "PROCESSING": {"SUCCEEDED", "FAILED", "CANCELLED"},
        "FAILED": {"PROCESSING"},
        "SUCCEEDED": {"REFUND_PENDING"},
    }
    return dst in legal.get(src, set())


def take(store: dict[str, str], key: str) -> str:
    if key in store:
        return "stored"
    store[key] = "succeeded"
    return "charged"


legs = (("buyer", -480), ("splicer", 408), ("shed", 72))
store = {"l44-try-1": "failed"}
print(
    net(legs),
    allowed("SUCCEEDED", "CREATED"),
    allowed("SUCCEEDED", "REFUND_PENDING"),
    take(store, "l44-try-1"),
    take(store, "l44-try-2"),
)
# 0 False True stored charged
```

The legs of L-42 sum to 0, so the shed fee is in the same commit as the payment and the payout. SUCCEEDED may open a refund and may not return to CREATED. The failed key is a stored result. The new key is the one that can charge Cove. After 90 quiet seconds the ropewalk polls Cove and writes the status Cove returns. L-51, present at Cove and missing from the ledger, is the orphan the morning comparison flags. A hold of 480 becomes a capture on confirm and a void on expiry, and the coil reserved during that hold is Ticket Booking System.

## See also

- [Networking and Communication](../10_Networking_and_Communication/) — Idempotency. What a repeated POST means stays there. The lookup before Cove, the new key after a failed charge, and a replayed webhook stay here.
- [Microservices and System Decomposition](../12_Microservices_and_System_Decomposition/) — Third-Party Integration. The adapter around a vendor stays there. The payment intent, the signed webhook, and the poll stay here.
- [Storage and Data Processing at Scale](../13_Storage_and_Data_Processing_at_Scale/) — Batch Processing. The scheduled read of a finished file stays there. Orphan, phantom, and amount mismatch stay here.
- [Distributed System Failure Modes](../15_Distributed_System_Failure_Modes/) — Timeouts and Retries. The deadline and the retry stay there. A missing webhook leaves the charge unknown, which stays here.
- [Transactions and Concurrency Control](../16_Transactions_and_Concurrency_Control/) — Transaction. The atomic commit of the legs stays there. The balanced debit and credit, shed fee included, stay here.
- [Classic Design Problems](../24_Classic_Design_Problems/) — Ticket Booking System. The reserved coil, seat, or other product stays there. Authorize, capture, and void stay here.
