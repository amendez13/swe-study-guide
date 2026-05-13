## Objects are useful because they collaborate

A single object is rarely the whole system. Real software works because objects call one another, pass data, and coordinate behavior. That collaboration is what turns isolated classes into working features.

OOP is not just about defining types; it is about deciding who should talk to whom and for what purpose.

## A message is a request, not a field grab

In classic OOP language, a **message** is one object asking another object to do something. In everyday code, that usually means calling a method like `inventory.reserve(product_id, qty)` or `email_service.send(...)`.

The important idea is that the caller expresses intent. It asks for an action instead of pulling out internals and performing the action manually.

## "Tell, don't ask" improves collaboration

One strong OOP instinct is to tell collaborators what you want done rather than asking them for raw data and reimplementing their rules elsewhere.

```python
# weaker collaboration
if cart.item_count() > 0:
    cart.items.append(product)


# stronger collaboration
cart.add_item(product)
```

The second version keeps the cart responsible for cart rules. The caller describes intent; the cart handles the mechanics.

## Collaboration should follow responsibilities

Objects should collaborate where their responsibilities meet. An `Order` may ask `PaymentGateway` to charge, `Inventory` to reserve stock, and `ReceiptService` to send a receipt. Those are natural boundaries because each collaborator owns a different kind of work.

If one class knows too much about all the internals of all its collaborators, the design usually becomes tangled.

## Avoid reaching through too many layers

A common smell is long chains like `order.customer.account.settings.timezone`. Every extra hop means the caller knows more about internal object graphs than it probably should.

This is sometimes called a "train wreck." It often signals that the caller is reaching through one object to manipulate another object's details instead of asking the right collaborator directly.

## Collaboration graphs can get complicated fast

As systems grow, object interactions form a graph: controllers call services, services call repositories, domain objects call policies, background workers call schedulers, and so on. That is normal.

The design job is to keep those edges legible. If every class talks to everything, the graph stops being architecture and becomes spaghetti.

## Fewer collaborators usually means simpler objects

An object with one or two clear collaborators is easier to understand than one that coordinates ten services, three repositories, and a metrics emitter directly.

Many dependencies are sometimes necessary, but they are never free. They widen the mental model a reader must hold to understand one operation.

## Good collaboration keeps behavior near the rule owner

When one object asks another to do work, the callee should own the rule being applied. `Order.apply_discount()` belongs on the order; `Inventory.reserve()` belongs on inventory; `RetryPolicy.should_retry()` belongs on the retry policy.

That ownership keeps the design honest. The more callers reimplement collaborator rules themselves, the weaker the collaboration model becomes.
