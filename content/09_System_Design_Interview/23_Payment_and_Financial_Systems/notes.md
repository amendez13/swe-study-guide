# Payment and Financial Systems

A marketplace checkout takes a card payment through a PSP such as Stripe or Adyen, then records who paid, who is owed, and what the marketplace keeps. Those ledger legs sum to 0. The attempt key is reserved before the PSP is called. A webhook is signed, and a second delivery of the same event posts the ledger once. Silence stays unknown until a poll returns a status. Refunds start with the merchant. Chargebacks start with the customer's bank. An authorization is a hold until a capture writes the legs or a void releases the card. The generic meaning of a repeated POST, the vendor adapter, the batch job, the deadline and the retry, the atomic commit, and the reserved stock stay in the topics that own them.

## Key Points

- **Idempotency in Payments** — look up `l42-try-1` and reserve it before calling the PSP. A stored success or a stored failure is that attempt's result, and the PSP is not called. A timeout keeps the same key and reads the PSP. `l44-try-2` is a new attempt after `l44-try-1` failed. A second delivery of `evt-l42-9` writes the ledger once. What a repeated POST means in general is Idempotency.
- **Payment Service Provider (PSP) Integration** — create the payment, verify the signed webhook, and poll when the wait ends with no webhook. A bad signature is dropped. Unknown stays unknown until the PSP returns a status. The success URL is the customer coming back to the shop. The vendor boundary is Third-Party Integration. The 90-second wait and the retry are Timeouts and Retries.
- **Double-Entry Bookkeeping** — customer −480, seller +408, platform fee +72, sum 0. A missing fee leg sums to −72 and is refused. A set that pays the seller the whole 480 can still sum to 0, so the account names are checked too. The three legs are one Transaction.
- **Reconciliation** — L-51 in the PSP's closed-day file and missing from the ledger is an orphan. L-44 in the ledger and missing from the file is a phantom. The same id with two amounts waits for a person unless a published rounding rule explains it. The morning job's shape is Batch Processing.
- **Payment State Machine** — CREATED goes to PROCESSING, and PROCESSING goes to SUCCEEDED, FAILED, or CANCELLED. A new attempt after a decline goes FAILED to PROCESSING with a new key. SUCCEEDED does not go back to CREATED. FAILED does not jump to SUCCEEDED. A refund starts at SUCCEEDED.
- **Handling Refunds and Chargebacks** — the merchant asks the PSP to reverse a charge it accepts. The opposite legs are written when the PSP confirms, and they sum to 0, including a partial refund of 120 as +120, −102, and −18. The customer's bank opens a chargeback, and the PSP pulls the 480 from the available balance while the case is open. Evidence is due on that dispute's deadline, 14 days in the example. A win puts the 480 back. A loss leaves it with the customer. The dispute fee is its own pair of 15.
- **Authorize and Capture** — authorize holds 480 and writes no settled legs. Confirm captures, and the three legs are written on success. Cancel or expiry voids the hold and books no fee. A release after SUCCEEDED is a refund. The reserved stock is Ticket Booking System.

## Example

Order L-42's three legs, the two charge moves a support tool has to allow, and a failed attempt followed by a new one:

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


legs = (("customer", -480), ("seller", 408), ("platform", 72))
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

The legs of the $480 order sum to 0, so the 72 fee commits with the customer's payment and the seller's 408. SUCCEEDED may open a refund, and the handler refuses a return to CREATED. The failed key is a stored result. The new key is the one that can call the PSP. After 90 quiet seconds the merchant polls the PSP and writes the status the PSP returns. L-51, present in the settlement file and missing from the ledger, is the orphan the morning comparison flags. A hold of 480 becomes a capture when the seller accepts and a void when the hold expires. The unit of stock reserved during that hold is Ticket Booking System.

## See also

- [Networking and Communication](../10_Networking_and_Communication/) — Idempotency. What a repeated POST means stays there. The lookup before the PSP call, the new key after a declined charge, and a replayed webhook stay here.
- [Microservices and System Decomposition](../12_Microservices_and_System_Decomposition/) — Third-Party Integration. The adapter around a vendor stays there. The payment object, the signed webhook, and the poll stay here.
- [Storage and Data Processing at Scale](../13_Storage_and_Data_Processing_at_Scale/) — Batch Processing. The scheduled read of a finished file stays there. Orphan, phantom, and amount mismatch stay here.
- [Distributed System Failure Modes](../15_Distributed_System_Failure_Modes/) — Timeouts and Retries. The deadline and the retry stay there. A missing webhook leaves the charge unknown, which stays here.
- [Transactions and Concurrency Control](../16_Transactions_and_Concurrency_Control/) — Transaction. The atomic commit of the legs stays there. The balanced customer, seller, and fee legs stay here.
- [Classic Design Problems](../24_Classic_Design_Problems/) — Ticket Booking System. The reserved seat, ticket, or unit of stock stays there. Authorize, capture, and void stay here.
