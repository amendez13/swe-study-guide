## Start from the problem, not the syntax

Class design begins before code. You are trying to model a problem space: orders, subscriptions, users, invoices, shipments, retries, approvals, permissions, reports.

If you start by thinking in language features alone, you often end up with classes that mirror your current implementation instead of the underlying domain.

## Nouns are a starting point, not a final answer

One common technique is to scan requirements for nouns: customer, order, payment, cart, invoice, shipment. Those nouns often hint at candidate classes.

That is useful as a first pass, but not every noun should become a class. Some nouns are just data fields, some are temporary concepts, and some are really verbs in disguise.

## Verbs reveal behavior

Requirements are not just nouns; they also contain actions: approve, ship, reserve, refund, retry, notify. Those verbs tell you where behavior needs to live.

Good class discovery uses both. Nouns suggest possible objects; verbs tell you what those objects may need to do.

## Use cases expose real responsibilities

A use case like "a customer places an order" forces you to think through the moving parts: who initiates the action, what state changes, which collaborators are involved, and what success or failure means.

That is often where class boundaries become clearer. Reading the workflow reveals whether you need an `Order`, an `Inventory`, a `PaymentGateway`, a `CheckoutService`, or some combination.

## CRC cards are a lightweight design tool

CRC stands for **Class, Responsibility, Collaborator**. The exercise is simple: write down a candidate class, what it is responsible for, and which other classes it must talk to.

This is valuable because it forces you to test whether a class has a coherent job or whether you are stuffing unrelated concerns into one box.

## Good class names reflect the domain

Names like `Order`, `Invoice`, `Subscription`, and `RetryPolicy` tell the reader what role the object plays. Names like `DataProcessor`, `Manager`, `Handler`, or `Utils` often hide vague responsibilities.

The name is not the whole design, but it is an early truth signal. If the name is muddy, the class boundary often is too.

## Not every responsibility deserves its own class

Over-modeling is real. Some logic fits cleanly as a function, helper, or small value object inside a larger class. Creating a new class for every tiny concept can turn simple code into ceremony.

The goal is not "maximum number of classes." The goal is to isolate meaningful responsibilities where that isolation actually helps.

## Refine the model as requirements sharpen

Early class models are often provisional. As you learn more, some candidate classes disappear, some split, and some merge. That is normal.

Good design is iterative. The mistake is treating the first set of classes you sketch as sacred even after the requirements make their flaws obvious.
