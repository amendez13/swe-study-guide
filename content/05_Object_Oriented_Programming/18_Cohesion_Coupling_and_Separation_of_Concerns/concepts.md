## Cohesion asks whether a class belongs together

Cohesion is about how strongly the contents of a class or module fit one clear purpose. A highly cohesive class feels like one idea; a low-cohesion class feels like several unrelated ideas packed into one file.

This is one of the fastest design smells to notice once you start looking for it.

## Coupling asks how much depends on how much

Coupling measures how entangled one part of the system is with another. If a class knows many implementation details of many collaborators, it is tightly coupled.

Tighter coupling makes change riskier because more assumptions must stay aligned.

## Separation of concerns keeps change local

Separation of concerns means different parts of the system should own different kinds of problems: domain rules, persistence, formatting, orchestration, delivery, rendering, scheduling.

That separation is not about bureaucracy. It is about making each kind of change land in fewer places.

## High cohesion usually improves readability

A class that only deals with discount policy is easier to understand than one that handles discount policy, database writes, email formatting, and PDF export. Readers can form a sharper mental model.

That narrower focus also makes naming easier, which is another good sign.

## Low coupling improves substitutability

The fewer assumptions a class makes about collaborator internals, the easier those collaborators are to replace, test, or evolve independently.

This is why interfaces, composition, and information hiding often improve coupling as a side effect.

## Mixed concerns create awkward change patterns

When one class mixes domain rules, logging, retry logic, SQL, and HTTP response formatting, unrelated requirements start landing in the same file. That is a strong signal that the design boundary is wrong.

Over time, those classes become the hardest places to change safely.

## Conceptual integrity matters too

Conceptual integrity means similar ideas are modeled similarly across the codebase. If one part uses rich domain objects, another uses giant static helpers, and a third uses ad hoc records for the same kind of problem, the system becomes harder to reason about.

Consistency is not everything, but incoherence is expensive.

## The goal is not zero coupling

Real systems need parts to talk to one another. The goal is not to eliminate coupling completely; the goal is to keep it proportionate, explicit, and aligned with real responsibilities.

Likewise, the goal is not microscopic classes. It is to choose boundaries where the work naturally hangs together.
