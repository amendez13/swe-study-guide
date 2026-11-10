## Idempotency in Payments

An idempotency key names one payment attempt. A retry of that attempt returns the result already stored for the key, and it does not create a second charge.

**Why it exists.** The call to the payment service provider can time out after the provider has already charged the card. The customer can also double-click Pay, and a webhook can arrive twice. Each of those has to be the same attempt, with one ledger posting. Order L-42 is a $480 marketplace checkout. The client mints one key for that click, `l42-try-1`.

**How it works.**

1. The client chooses the key for this attempt. A random id is enough. The order id is the wrong name for an attempt, which step 4 shows with a decline.
2. The merchant looks the key up and reserves a row before it calls Stripe, Adyen, or whichever PSP is moving the money. The row starts as in progress.
3. A retry that finds a stored success returns that success, and the PSP is not called. A retry that finds a stored failure returns the failure, and the PSP is not called. A retry that finds in progress keeps the same key, reads the PSP for that attempt, and fills in the result. It does not open a second charge.
4. A decline the PSP actually executed is a finished attempt. The customer paying again, with another card or another click of Pay, is a new attempt and gets a new key: `l44-try-2` after `l44-try-1` failed. Stored under the order id alone, that failure would be the result of every later payment of the order. On Stripe, a request rejected before the charge starts, such as a malformed amount, can be retried with the same key after the request is fixed, because Stripe saves a result only once execution has begun. The split is whether the PSP began the operation.
5. The PSP dedupes the same key on its side for a limited window. Stripe keeps the result of an executed POST for at least 24 hours, including many error responses, and a key reused after that window can start a new charge. Send the same parameters with the same key. A different amount under a key the PSP still remembers is rejected as a mismatch. The merchant's row is the record that outlives the PSP's cache.
6. A webhook that arrives twice for `evt-l42-9` is one event. The ledger is written once. The attempt key guards the charge. The event id guards the ledger write.

What a repeated POST means for a generic job is Idempotency in [Networking and Communication](../10_Networking_and_Communication/). This card is the lookup before the PSP call, the new key after a declined charge, and the webhook you have already applied.

**Trade-offs.** Reserving the key first leaves an in-progress row when the process dies before the PSP call. The retry resolves that row by reading the PSP, which is the path that keeps a single charge. Storing the key only after the PSP answers skips that row on the happy path, and a crash in the gap charges the customer twice. A fresh key on every HTTP retry is that same second charge, because the PSP treats a new key as a new operation. Reusing one key for a genuine new attempt, after a decline the customer can see, returns the old failure for as long as that row is stored.

**In an interview.** Say you persist the key before the PSP call, return the stored result on a retry, and mint a new key only for a new attempt whose previous outcome you already know. A timeout is an unknown outcome, so it keeps the original key. Name the webhook event id as a second record, so a replayed success event posts the ledger once.

**Recap.**

| Situation | What you do |
| --- | --- |
| `l42-try-1` is a stored success | Return the success. The PSP is not called. |
| `l44-try-1` is a stored failure | Return the failure. The PSP is not called. |
| `l44-try-2` has no row | Reserve it. The PSP may be called. This is a new attempt. |
| The key is in progress and the first call timed out | Keep the key. Read the PSP for that attempt. |
| `evt-l42-9` is delivered twice | Write the ledger once. |
| The order id is the only key | The failed attempt is the stored result of every later payment of that order. |

![Idempotency in Payments](/content/09_System_Design_Interview/23_Payment_and_Financial_Systems/diagrams/payments-1-idempotency-in-payments.png)

*Source: [`diagrams/payments.drawio`](/content/09_System_Design_Interview/23_Payment_and_Financial_Systems/diagrams/payments.drawio), page 1.*

## Payment Service Provider (PSP) Integration

A PSP such as Stripe or Adyen moves the money between the customer's card, the card network, and the merchant. The merchant creates a payment, checks a signed webhook when it finishes, and polls when the webhook has not arrived.

**Why it exists.** The merchant needs a durable answer to one question: was the $480 for order L-42 actually taken? The PSP holds the card number, the messages to Visa or Mastercard, and the settlement, so the shop stores a payment id. The browser's landing on a success page tells you the customer came back to the shop. The issuer's answer arrives on the webhook or on the poll.

**How it works.**

1. The merchant creates the payment for 480 and asks the PSP to start it, with the attempt key from Idempotency in Payments. Stripe calls this object a PaymentIntent. Adyen models the same idea as a payment identified by your merchant reference. The PSP sends the authorization over the card network to the issuer. Some methods finish later, after a 3-D Secure challenge, a bank redirect, or a wallet approval.
2. The PSP then sends a webhook, `payment.succeeded` or `payment.failed` in this example. Stripe's names for those are `payment_intent.succeeded` and `payment_intent.payment_failed`. Adyen's AUTHORISATION notification carries a success flag. The handler recomputes the signature over the raw body with the endpoint secret and drops a mismatch. Stripe's libraries also reject a signature timestamp that is too far from the current time, which limits a replay of a captured request. The PSP's own retries carry a fresh signature, so the timestamp check still leaves duplicate delivery to the event-id record on the previous card.
3. The merchant picks how long to wait before treating the webhook as missing. In this example the wait is 90 seconds. No webhook inside that wait leaves the charge unknown. The merchant polls the PSP for that payment and writes the status the PSP returns.
4. A poll that errors leaves the payment unknown, and the poll is tried again. Succeeded is written when the PSP reports succeeded. Failed is written when the PSP reports failed.

The 90-second deadline, the backoff, and the retry budget are Timeouts and Retries in [Distributed System Failure Modes](../15_Distributed_System_Failure_Modes/). An adapter around a vendor you do not deploy, the only code that knows the PSP's URLs and status codes, is Third-Party Integration in [Microservices and System Decomposition](../12_Microservices_and_System_Decomposition/).

**Trade-offs.** Webhooks push the result and still arrive late, twice, or never. Stripe retries a failing endpoint for up to about three days. Polling closes that gap and costs one read per payment that is still unknown. Marking the order paid from the success URL, or from a webhook that never came, records money the PSP may never take. Running the card network connection in-house drops the PSP fee and takes on PCI scope, scheme rules, and issuer certification. Most products keep the PSP and own three things: the payment object, the signature check, and the poll.

**In an interview.** Name the three messages: create the payment, verify the signed webhook, poll on silence. The success URL is the customer returning to the shop. Unknown stays unknown until a read of the PSP returns a status. Put the PSP behind an adapter so a second provider is a new adapter, while the order service still says "start payment" and "payment succeeded."

**Recap.**

| What happened | What you write |
| --- | --- |
| Webhook, signature matches | The status in the event. A duplicate event id writes nothing new. |
| Signature does not match | Drop the delivery. |
| No webhook, and the poll returns failed | Failed, the status the PSP returned. |
| No webhook, and the poll errors | Unknown. Poll again. |
| The customer landed on the success URL | Nothing about the money, until the webhook or the poll reports a status. |

![Payment Service Provider (PSP) Integration](/content/09_System_Design_Interview/23_Payment_and_Financial_Systems/diagrams/payments-2-payment-service-provider-psp-integration.png)

*Source: [`diagrams/payments.drawio`](/content/09_System_Design_Interview/23_Payment_and_Financial_Systems/diagrams/payments.drawio), page 2.*

## Double-Entry Bookkeeping

Every posting is a set of legs whose signed amounts sum to 0. A negative amount is money leaving that account. A positive amount is money arriving. The ledger refuses a set that does not balance.

**Why it exists.** A marketplace charge has to remember three facts together: the customer paid 480, the seller is owed 408, and the marketplace keeps a fee of 72. One `balance += 480` can drop the fee, pay the seller the whole charge, or die after a single account has moved. The sum is the check that the write conserved the money. The account name on each leg says who was paid.

**How it works.** 72 is 15% of 480, and 408 is the remainder. The three legs are one database commit:

| Account | Signed amount | What it records |
| --- | --- | --- |
| Customer | −480 | The customer paid 480. |
| Seller | +408 | The seller is credited 408. |
| Platform fee | +72 | The marketplace keeps 72. |
| Sum | 0 | The set balances. |

Customer −480 and seller +408, with the fee left out, sum to −72. That gap is a missing leg, and the commit is refused. Seller +480 with no fee leg also sums to 0. The zero check passes, and the seller was paid the fee that belongs to the marketplace. Check the sum, then check the accounts.

A crash after the customer leg and before the seller leg rolls the whole set back, because the three inserts are one commit. That atomic write is a Transaction in [Transactions and Concurrency Control](../16_Transactions_and_Concurrency_Control/). Isolation, lock order, and two-phase commit stay on that topic.

Journals in the accounting sense put debits in one column and credits in another, and those two columns are equal. This ledger stores one signed integer per leg, so the same rule reads `sum(legs) == 0`. A production book stores the minor unit, such as cents, so a dollar amount cannot drift through binary floating point. These cards keep one integer unit on every leg: 480 for the order, 408 for the seller, and 72 for the fee.

On the marketplace's own journal the same economics are a debit to cash at the PSP for 480, a credit to seller payable for 408, and a credit to fee revenue for 72. Debits equal credits. That journal replaces the customer leg with the cash debit. Adding cash on top of customer −480 would count the same 480 twice. The worked example on this card is the participant view: who paid, who is owed, and what the marketplace keeps.

**Trade-offs.** A single balance column is less code and updates in place. Separate legs make a missing fee and a crash between accounts visible, because each account is posted and the posts commit together. Tax, shipping, and a reserve for later refunds are more legs under the same sum. A wallet product, where the customer has a stored balance, uses the customer leg as that balance. A card checkout uses the same leg as the record that 480 came from the customer. The customer's bank account is not a row the marketplace holds. Both readings have to balance.

**In an interview.** Post the fee in the same commit as the customer and the seller, and give the sum. A balanced write can still name the wrong account, so the accounts are part of the check. Point the atomic commit at Transaction, and leave isolation and two-phase commit there. When you present the marketplace's journal, debit cash at the PSP and credit the seller and the fee, and keep debits equal to credits.

**Recap.**

| Write | Sum | What is wrong, if anything |
| --- | --- | --- |
| Customer −480, seller +408, platform +72 | 0 | The fee and the seller payout are both present. |
| Customer −480, seller +408 | −72 | The fee leg is missing. Refuse the commit. |
| Customer −480, seller +480 | 0 | The money is conserved and the seller received the marketplace's 72. |

![Double-Entry Bookkeeping](/content/09_System_Design_Interview/23_Payment_and_Financial_Systems/diagrams/payments-3-double-entry-bookkeeping.png)

*Source: [`diagrams/payments.drawio`](/content/09_System_Design_Interview/23_Payment_and_Financial_Systems/diagrams/payments.drawio), page 3.*

## Reconciliation

Reconciliation compares the PSP's settlement file for a closed day with the merchant's ledger. It lists every payment that appears on one side only, and every payment whose two amounts disagree.

**Why it exists.** Webhooks and polls are what the PSP said during the day. The settlement file is the set of payments included in a payout to the merchant's bank. Stripe exposes those rows as balance transactions and payout reports. Adyen provides a settlement detail report. A missed webhook leaves the customer charged and the seller uncredited. A ledger row for a charge that never settled pays the seller from money the payout will not contain. The comparison finds both before that payout is treated as final.

**How it works.** Each morning the merchant reads the file for the day that just closed and joins it to the ledger on the payment id.

- L-42 is in the file and in the ledger for the same amount. It matches.
- L-51 is in the file and missing from the ledger. That is an orphan. The PSP took the customer's money and the merchant has no row. Confirm the id and the amount with the PSP, then post the missing legs so the seller can be credited.
- L-44 is in the ledger and missing from the file. That is a phantom. The merchant recorded money this file does not show. Hold the seller payout for that id. If a later file for the right day still lacks it, reverse the legs.
- The same id with two amounts waits for a person, unless a rounding rule the merchant already published explains the gap. A conversion rounded to the cent can be that rule. A ledger amount of 480 against a file amount of 408 is a different split, and a person has to look.

Which side is missing, and what an amount mismatch requires, are the rules on this card. The scheduled read of a finished file is Batch Processing in [Storage and Data Processing at Scale](../13_Storage_and_Data_Processing_at_Scale/). A payment that arrives while the job is running waits for the next file.

**Trade-offs.** A daily file lags by hours and matches the way these PSPs pay out, one closed batch at a time. Comparing on every webhook finds an orphan the same day, and the payout file is still the check against the bank. Repairing an orphan whose id and amount you can retrieve from the PSP gets the seller paid. Reversing a phantom is how you stop paying out money the file does not contain. An automatic edit of an amount mismatch will also "repair" a real fee bug, so that case stays with a person unless the published rounding rule already accounts for it.

**In an interview.** Define orphan and phantom by which side is missing, and give one id for each. The settlement file is what you tie to the bank payout. An amount mismatch waits for a person unless a rounding rule you already published explains it. Point the schedule and the finished input at Batch Processing, and keep the match rules here.

**Recap.**

| Ledger | PSP settlement file | Name | What it means |
| --- | --- | --- | --- |
| L-42, amount 480 | L-42, amount 480 | Match | Both sides agree. |
| No row | L-51 | Orphan | The PSP took money the ledger did not record. |
| L-44 | No row | Phantom | The ledger recorded money the file does not show. |
| L-42 for 480 | L-42 for a different amount | Amount mismatch | One id, two figures. A person looks, unless a published rounding rule explains the gap. |

![Reconciliation](/content/09_System_Design_Interview/23_Payment_and_Financial_Systems/diagrams/payments-4-reconciliation.png)

*Source: [`diagrams/payments.drawio`](/content/09_System_Design_Interview/23_Payment_and_Financial_Systems/diagrams/payments.drawio), page 4.*

## Payment State Machine

A charge has one current state. The handler accepts a move only when that pair is in the table, and it appends every accepted move so support can read why an order looks stuck.

**Why it exists.** The expensive bugs are illegal jumps. A declined card gets marked succeeded because a later webhook was applied to the wrong row. A captured charge is put back to CREATED and sent to the PSP again. One current state, plus a list of accepted moves, makes that jump a refused write.

**How it works.**

| From | To | When |
| --- | --- | --- |
| CREATED | PROCESSING | The merchant has asked the PSP to take the money. |
| PROCESSING | SUCCEEDED | The PSP reports success. The settled legs can be written. |
| PROCESSING | FAILED | The PSP reports a decline or another hard failure. |
| PROCESSING | CANCELLED | The charge is stopped before it succeeds. |
| FAILED | PROCESSING | The customer starts a new attempt, and that attempt uses a new idempotency key. |
| SUCCEEDED | REFUND_PENDING | The merchant asks the PSP for a refund. |
| REFUND_PENDING | REFUNDED | The PSP confirms the reversal. |
| REFUND_PENDING | REFUND_FAILED | The reversal fails. The original legs stay. |

The handler refuses every other pair. SUCCEEDED → CREATED is refused: a finished charge stays finished. FAILED → SUCCEEDED is refused: a new attempt goes through PROCESSING, and only PROCESSING may become SUCCEEDED.

A retry of the same attempt, while the merchant is still waiting on the PSP, stays on PROCESSING and keeps the original key. AUTHORIZED and VOIDED belong to Authorize and Capture. They stay off this table, because a hold has not posted settled legs.

**Trade-offs.** A free-form status string is a small column and gives support no edge to point at. A closed table is stricter. A 3-D Secure challenge, or a bank debit that clears on a later day, has to be mapped onto PROCESSING or added as its own edge. Mapping it onto PROCESSING keeps this table small and hides the wait for the customer. A REQUIRES_ACTION state makes that wait visible, and it is a new edge you then have to draw. The accepted table for this card is the one above.

**In an interview.** Draw the legal edges before you talk about retries. A webhook may apply only a move the table allows, so a late failure event for a charge already in SUCCEEDED is refused and looked at, and the row stays SUCCEEDED. The history is append-only. A refund starts at SUCCEEDED. A new attempt after a decline is FAILED → PROCESSING with a new key. Replaying the old key returns the stored decline.

**Recap.**

| Move | Result |
| --- | --- |
| CREATED → PROCESSING | Accepted. |
| PROCESSING → SUCCEEDED, FAILED, or CANCELLED | Accepted. |
| FAILED → PROCESSING | Accepted. This is a new attempt and a new key. |
| SUCCEEDED → REFUND_PENDING → REFUNDED or REFUND_FAILED | Accepted. A refund starts at SUCCEEDED. |
| SUCCEEDED → CREATED | Refused. A finished charge stays finished. |
| FAILED → SUCCEEDED | Refused. Success is reached from PROCESSING. |
| Same attempt, still waiting on the PSP | Stay on PROCESSING. Keep the original key. |

![Payment State Machine](/content/09_System_Design_Interview/23_Payment_and_Financial_Systems/diagrams/payments-5-payment-state-machine.png)

*Source: [`diagrams/payments.drawio`](/content/09_System_Design_Interview/23_Payment_and_Financial_Systems/diagrams/payments.drawio), page 5.*

## Handling Refunds and Chargebacks

A refund is the merchant asking the PSP to reverse a charge the merchant accepts. A chargeback is the customer's bank taking the funds back while the merchant may still stand behind the sale.

**Why it exists.** Both can end with the customer holding the money again, and they start in different places, on different clocks, with different ledger rows. A refund is a reversal the merchant asked for. A chargeback is the issuer pulling the money after the customer complained to their bank. One "reversed" flag for both will claw the seller back twice, or never post the dispute fee.

**How it works.** The customer returns the order. The merchant asks the PSP to reverse 480, and the charge moves to REFUND_PENDING on that ask. It moves to REFUNDED when the PSP confirms. A failed reversal is REFUND_FAILED, and the original legs stay. The opposite legs are written once, on the confirmation, and that set sums to 0.

| Refund | Customer | Seller | Platform fee | Sum |
| --- | --- | --- | --- | --- |
| Full, 480 | +480 | −408 | −72 | 0 |
| Partial, 120 | +120 | −102 | −18 | 0 |

The partial uses the same 15% fee. Fifteen percent of 120 is 18, and the seller returns 102. Card networks often take several business days to show the credit on the customer's statement. The merchant's state is already REFUNDED once the PSP confirms.

A chargeback starts at the issuer. The PSP notifies the merchant and removes the 480 from the merchant's available balance while the case is open. The merchant sends evidence before the deadline on that dispute: the receipt, proof the goods were delivered, and the messages with the customer. This example uses 14 days. Across Visa, Mastercard, and the other networks the window is often 7 to 21 days, and the deadline on the PSP's dispute object is the one that counts. A win returns the 480 to the merchant. A loss leaves the 480 with the customer. The dispute fee, 15 in this example, is its own pair: platform −15, and the PSP's fee account +15. That pair sums to 0. It is a different posting from the sale.

**Trade-offs.** Ask for the refund while the order is undisputed and the complaint is one you accept. After a dispute is open, the PSP is already moving the 480, and a parallel refund races that movement. On Stripe in the US, the fee for receiving a dispute is $15, taken when the dispute opens, and that received fee generally stays taken if you win. Submitting evidence can add a further fee that is returned after a win. Post the fee the contract actually charges, as its own pair, when the PSP charges it. Who bears a lost 480 is a marketplace rule. Clawing 408 back from the seller is the same shape as the refund legs, and that set still sums to 0. A platform that keeps the seller whole posts the loss to its own account, and that set sums to 0 as well.

**In an interview.** Say who starts it. The merchant starts a refund, and the state moves when the PSP confirms, ahead of the customer's statement. The issuer starts a chargeback. Evidence goes in before the dispute's own deadline, a win puts the 480 back, and a loss leaves it with the customer. The dispute fee is a second, smaller pair. Append those legs. Leave the original 480, 408, and 72 rows in place as history.

**Recap.**

|  | Refund | Chargeback |
| --- | --- | --- |
| Who starts it | The merchant, by asking the PSP | The customer's bank |
| Sale amount | Opposite legs are written once, on the PSP's confirmation | The 480 leaves the available balance when the dispute opens. A win puts it back. A loss leaves it with the customer. |
| Fee | The fee share comes back with the sale: 72 on a full refund, 18 on a refund of 120 | A fee of 15 is its own pair: platform −15, PSP fee +15 |
| Failure | REFUND_FAILED, and the original legs stay | The evidence is still due, or the merchant accepts the loss |

![Handling Refunds and Chargebacks](/content/09_System_Design_Interview/23_Payment_and_Financial_Systems/diagrams/payments-6-handling-refunds-and-chargebacks.png)

*Source: [`diagrams/payments.drawio`](/content/09_System_Design_Interview/23_Payment_and_Financial_Systems/diagrams/payments.drawio), page 6.*

## Authorize and Capture

Authorization places a hold on the customer's card. Capture turns that hold into a taken payment, and it is the moment the settled legs are written. A void releases the hold and books no fee.

**Why it exists.** A marketplace often waits to take the $480 until the seller accepts the order. A shop often waits until the warehouse can ship. The card still has to be set aside, so the funds are there at ship time. A digital good delivered on the success webhook can capture immediately. A physical order that can still be cancelled is the case for the hold.

**How it works.**

1. The merchant asks the PSP to authorize 480. On Stripe this is a PaymentIntent created with manual capture. The PSP places a hold with the issuer through the card network. The merchant records AUTHORIZED.
2. The customer, seller, and platform-fee legs are not written. The hold reduces the customer's available funds by 480. The merchant has not been paid, and the seller is not yet owed 408.
3. The seller accepts, or the warehouse confirms the unit. The merchant asks the PSP to capture 480. While that call is in flight the charge follows Payment State Machine: PROCESSING, then SUCCEEDED when the PSP reports success. The three settled legs are written on that success.
4. The customer cancels, or the hold expires. That is a void. The PSP releases the 480, the merchant records VOIDED, and no fee is booked.
5. A release after SUCCEEDED is a refund, covered on Handling Refunds and Chargebacks. The capture has already taken the money.

AUTHORIZED and VOIDED stay off the settled-charge table. For a typical online payment the customer started, Visa, Mastercard, American Express, and Discover keep the hold for about 7 days. A merchant-initiated Visa authorization is shorter, about 5 days, and the exact deadline is a few hours inside that. Hotels, rentals, and similar categories can be allowed a longer hold, up to about 30 days where the network grants an extended authorization. The PSP returns a capture-by time for that specific charge. Past that time the issuer has released the 480, and the merchant records VOIDED so the row matches the bank.

The seat, the ticket, or the unit of stock reserved during the hold is Ticket Booking System in [Classic Design Problems](../24_Classic_Design_Problems/). This card is the money.

**Trade-offs.** Authorize-then-capture avoids taking money for an order you cannot fulfill, and the customer sees a pending hold. You then have to notice expiry: a row that still says AUTHORIZED after the capture-by time is a hold the bank has already dropped, and a late capture fails. Immediate capture is one PSP call and one webhook, and a cancellation after that is a refund, with a charge and a credit on the statement. Capturing less than 480 is a partial capture. The PSP releases the rest of the hold. Capturing more than the authorization is overcapture, which only some card payments allow, and only within the network's limit. Read that limit from the PSP for the charge in front of you.

**In an interview.** The settled legs are written on capture. Authorize only records the hold. Cancel or expiry voids the hold and books no fee. Giving the money back after SUCCEEDED is a refund. The inventory hold is Ticket Booking System. Tie the two at one point: capture succeeds, then confirm the stock; capture fails or the hold expires, then release the stock.

**Recap.**

| Event | State you record | Settled legs |
| --- | --- | --- |
| The PSP authorizes 480 | AUTHORIZED | None. The hold sits on the card. |
| The merchant confirms and the PSP captures | PROCESSING, then SUCCEEDED | Customer −480, seller +408, platform +72. |
| The customer cancels, or the hold expires | VOIDED | None. The PSP releases 480. No fee is booked. |
| A cancel or an expiry arrives after SUCCEEDED | The refund path | A refund writes the opposite legs. A void does not apply. |

![Authorize and Capture](/content/09_System_Design_Interview/23_Payment_and_Financial_Systems/diagrams/payments-7-authorize-and-capture.png)

*Source: [`diagrams/payments.drawio`](/content/09_System_Design_Interview/23_Payment_and_Financial_Systems/diagrams/payments.drawio), page 7.*
