## Idempotency in Payments

Halden Ropewalk sells consigned dock lines. A buyer pays the ropewalk, and the ropewalk asks Cove, the processor, to take the money. The call for line L-42, priced at 480, can time out after Cove has already charged it. A retry of that same try has to come back as the first result.

The client mints a key for one try, `l42-try-1`. The ropewalk looks the key up and reserves it before it calls Cove. A retry that finds a stored success gets that success, and Cove is not called. A retry that finds a stored failure gets the failure. Another payment of a line that failed under `l44-try-1` uses a new key, `l44-try-2`. The line's id is the wrong name for a try: the failed try would then be the stored result of every later payment of that line. A webhook that arrives twice for `evt-l42-9` is still that one try, and the ledger is written once. What a repeated POST means for a generic job is Idempotency in [Networking and Communication](../10_Networking_and_Communication/). This card is the lookup before the Cove call, the new key after a failed charge, and the replayed webhook.

```text
l42-try-1 stored success    return it, Cove is not called
l44-try-1 stored failure    return the failure
l44-try-2                   a new attempt, Cove may be called
evt-l42-9 delivered twice   one ledger write
generic repeated POST       Idempotency
```

## Payment Service Provider (PSP) Integration

Cove moves the money. The ropewalk creates a payment intent for L-42 and asks Cove to start it. Cove finishes later and sends `payment.succeeded` or `payment.failed`. The handler recomputes Cove's signature over the body and drops a mismatch. A signature that matches can still be a delivery the ropewalk has already applied. That replay is Idempotency in Payments.

No webhook inside the wait leaves the charge unknown. The ropewalk polls Cove for that intent and writes the status Cove returns. A poll that fails leaves the intent unknown, and the poll is tried again. Marking L-42 paid because the callback never came would record money Cove may not have taken. The deadline and that retry are Timeouts and Retries in [Distributed System Failure Modes](../15_Distributed_System_Failure_Modes/). An adapter around a vendor the ropewalk does not deploy is Third-Party Integration in [Microservices and System Decomposition](../12_Microservices_and_System_Decomposition/). This card is the intent, the signed webhook, and the poll.

```text
intent           L-42, then Cove is asked to start it
webhook          signature checked, then succeeded or failed
bad signature    dropped
no webhook       poll Cove; unknown stays unknown
wait, retry      Timeouts and Retries
vendor adapter   Third-Party Integration
```

## Double-Entry Bookkeeping

L-42 is 480. The ropewalk keeps a shed fee of 72. The splicer is credited 408. The buyer leg is -480, the splicer leg is +408, and the shed leg is +72. Negative is money leaving that account, positive is money arriving, and the three legs sum to 0. A write that stores the buyer and the splicer and drops the shed sums to -72. That gap is a missing leg.

The three legs are one commit. A crash after the buyer leg and before the splicer leg must roll back. That atomic write is a Transaction in [Transactions and Concurrency Control](../16_Transactions_and_Concurrency_Control/). Isolation, lock order, and two-phase commit stay on that topic. The balanced legs, shed fee included, stay here.

```text
buyer        -480
splicer      +408
shed         +72
sum          0
missing fee  buyer -480, splicer +408, sum -72
one commit   Transaction
```

## Reconciliation

Each morning the ropewalk reads Cove's settlement file for the closed day and compares it with the ledger. L-51 in the file and absent from the ledger is an orphan: Cove took money the ropewalk did not record. L-44 in the ledger and absent from the file is a phantom: the ropewalk recorded money the file does not show. The same id with two amounts waits for a person, unless a rounding rule the ropewalk already published explains the gap.

The comparison is the rule. The scheduled read of that finished file is Batch Processing in [Storage and Data Processing at Scale](../13_Storage_and_Data_Processing_at_Scale/).

```text
orphan    in Cove, missing from the ledger, L-51
phantom   in the ledger, missing from Cove, L-44
amount    one id, two figures
job       Batch Processing
```

## Payment State Machine

A charge at Halden has one state, and the next state has to be in the table. CREATED may become PROCESSING. PROCESSING may become SUCCEEDED, FAILED, or CANCELLED. FAILED may become PROCESSING when the buyer starts a new try. SUCCEEDED may become REFUND_PENDING, and that may become REFUNDED or REFUND_FAILED. SUCCEEDED does not become CREATED. FAILED does not become SUCCEEDED. A refund starts from SUCCEEDED.

The handler refuses any other pair. The row stores the current state, and each accepted move is appended. The desk reads that list when a line looks stuck. A retry of the charge is allowed from FAILED, and from PROCESSING while the ropewalk is still waiting on Cove.

```text
CREATED → PROCESSING
PROCESSING → SUCCEEDED | FAILED | CANCELLED
FAILED → PROCESSING
SUCCEEDED → REFUND_PENDING → REFUNDED | REFUND_FAILED
SUCCEEDED → CREATED    refused
FAILED → SUCCEEDED     refused
```

## Handling Refunds and Chargebacks

A refund starts at the ropewalk. The buyer brings L-42 back, and the ropewalk asks Cove to reverse 480. The charge moves to REFUND_PENDING on that ask, and to REFUNDED when Cove confirms. A failed reversal is REFUND_FAILED, and the original legs stay. The opposite legs are written once, on the confirmation: buyer +480, splicer -408, shed -72. That set sums to 0. A return of 120 reverses buyer +120, splicer -102, and shed -18, and that smaller set sums to 0. The card network can take days to show the credit. The ropewalk's state has already moved.

A chargeback starts at the buyer's bank. Cove notifies the ropewalk, and the ropewalk has 14 days to send the receipt, the handover of the line, and the buyer's note. A win returns the funds to the ropewalk. A loss leaves them with the buyer, and a dispute fee of 15 is its own pair, shed -15 and Cove's fee account +15. The refund is the ropewalk reversing a charge it accepts. The chargeback is the bank taking the funds while the ropewalk may still stand behind the sale.

```text
refund          the ropewalk asks Cove to reverse
on confirm      buyer +480, splicer -408, shed -72
return of 120   buyer +120, splicer -102, shed -18
chargeback      the bank opens it, evidence in 14 days
lost            buyer keeps 480, fee pair of 15
```

## Authorize and Capture

A buyer can ask Halden to hold L-42 while they check the coil on the dock. The ropewalk asks Cove to authorize 480. Cove places a hold. The ropewalk records AUTHORIZED. The buyer, splicer, and shed legs are not written, because nothing has been captured.

Confirm asks Cove to capture the 480. The in-flight capture is PROCESSING on Payment State Machine. When Cove reports success, the charge is SUCCEEDED and the three legs are written. The buyer leaving, or the hold expiring, is a void: Cove releases the 480, the ropewalk records VOIDED, and no fee is booked. AUTHORIZED and VOIDED are hold states, kept off the charge table. A void after SUCCEEDED is a refund. The coil, a seat, or any other reserved thing is Ticket Booking System in [Classic Design Problems](../24_Classic_Design_Problems/). This card is the hold, the capture, and the void.

```text
authorize      Cove holds 480, no settled legs
capture        on confirm, then SUCCEEDED and the three legs
void           on cancel or expiry, no fee
after success  a release is a refund
product        Ticket Booking System
```
