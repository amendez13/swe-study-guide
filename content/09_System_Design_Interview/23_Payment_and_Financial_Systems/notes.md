# Payment and Financial Systems

How to design systems that handle real money — the domain where bugs have legal and financial consequences. This topic covers the payment pipeline from user checkout through PSP integration, ledger management, and reconciliation. Common interview problems include designing a payment system, e-wallet, or marketplace payment flow.

## Key Points

- **Idempotency** — every payment operation must be safe to retry. Use client-generated idempotency keys stored server-side. Check before processing, not after.
- **PSP integration** — delegate money movement to Stripe/Adyen/Square. Handle the async webhook flow, verify signatures, and poll on timeout.
- **Double-entry bookkeeping** — every transaction creates balanced debit and credit entries. The ledger sum for each transaction must be zero.
- **Reconciliation** — daily comparison of internal ledger against PSP settlement reports. Flag orphan charges, phantom payments, and amount mismatches.
- **Payment state machine** — model payments as explicit states (CREATED → PROCESSING → SUCCEEDED/FAILED). Log every transition. Enforce valid transitions in code.
- **Refunds and chargebacks** — refunds reverse ledger entries via PSP; chargebacks are bank-initiated disputes requiring evidence submission within a deadline.

## Example

Designing the payment flow for an e-commerce marketplace:

```text
Requirements:
  50K orders/day. Buyers pay, platform takes 10% fee, merchants get 90%.
  Support credit cards and digital wallets. Refunds within 30 days.

Checkout flow:
  1. User clicks "Pay $100" → frontend sends POST /payments
     { order_id, amount: 100.00, method: "card", idempotency_key: "uuid-xyz" }
  2. Payment Service checks idempotency key → not seen → proceed.
  3. Create payment record: status = CREATED.
  4. Call Stripe API: create PaymentIntent for $100.
  5. Stripe processes → sends webhook: payment_intent.succeeded.

Webhook handler:
  Verify Stripe signature.
  Check idempotency (webhook may arrive twice).
  Update payment status: PROCESSING → SUCCEEDED.

  Write ledger entries:
    Debit:  Buyer account    -$100.00
    Credit: Merchant payout  +$90.00
    Credit: Platform fee     +$10.00
    Sum = 0 ✓

  Trigger order fulfillment event.

Daily reconciliation:
  Export: all payments with status SUCCEEDED for yesterday.
  Fetch: Stripe settlement report for yesterday.
  Match on Stripe payment_intent_id.
  Flag 3 orphan charges (in Stripe, not in our DB) → investigate.
  Flag 1 amount mismatch ($99.99 vs $100.00) → currency rounding → auto-resolve.
  Mismatch rate: 0.004% → within threshold.

Refund flow:
  User requests refund → POST /refunds { payment_id, amount: 100.00 }
  Call Stripe refund API → webhook: refund.succeeded.
  Reverse ledger:
    Debit:  Merchant payout  -$90.00
    Debit:  Platform fee     -$10.00
    Credit: Buyer account    +$100.00
```
