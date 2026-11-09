# Object-Oriented Design — Drills

Original design drills for ambiguity, core types, relationships, actions, the object rules, SOLID, and a handful of patterns. Each card is one exercise: commit to an answer, then check it. The Python is a small model of the design, not a full program. No copyrighted book text.

## What you still have not pinned down

The interviewer says: "Design a courtyard bike cage. Members tap a fob and the gate opens." Then they stop talking. Which questions do you ask, and what assumption do you proceed with if they say "use your judgment"?

**Answer:** Ask who counts as a member, whether a guest can enter, how many bikes fit, what happens when the cage is full, whether one person may store two bikes, and whether this round includes payment or only admission. Also ask what is out of scope. If they hand it back, say the assumption and move: members only, one bike each, a fixed capacity, a full cage refuses the tap, no billing. The design that follows is allowed to be wrong in a way the interviewer can correct. A design that silently invented payments and a mobile app is not.

```python
def assumptions() -> dict:
    return {
        "actors": "members",
        "bikes_per_member": 1,
        "when_full": "refuse",
        "payments": False,
    }

print(assumptions()["when_full"])  # refuse
```

## Nouns that are not types

A neighborhood tool library lends hand tools for seven days. Each tool has a barcode. A person may hold three tools. An overdue tool blocks a new loan. Which of these become types: Person, Tool, Loan, Barcode, Week, Limit?

**Answer:** `Member` (the person), `Tool`, and `Loan`. Each owns state the others must not rewrite: a member's open loans, a tool's availability, a loan's due date. The barcode is a field on the tool. Seven days is a rule on the loan, not a class. Three is a constant the member's `borrow` checks. "Neighbor" is the same actor as the member.

```python
class Tool:
    def __init__(self, barcode: str) -> None:
        self.barcode = barcode
        self.on_loan = False

class Loan:
    def __init__(self, member_id: str, tool: Tool, days: int = 7) -> None:
        self.member_id = member_id
        self.tool = tool
        self.days = days
        tool.on_loan = True

saw = Tool("B-14")
loan = Loan("m1", saw)
print(saw.barcode, saw.on_loan, loan.days)  # B-14 True 7
```

## Is-a that is not

You have sketched `Member`, `Loan`, and `Tool` for that library. A teammate adds `class Loan(Member)` and `class Tool(Loan)` so they can "reuse fields." What is wrong, and what are the real relationships?

**Answer:** A loan is not a member, and a tool is not a loan. Inheritance would let you pass a `Tool` wherever a `Loan` or a `Member` is expected, which is nonsense. A member has zero or more loans. Each loan knows one member and one tool. A tool has at most one open loan. Those are associations with cardinality, not subtypes.

```python
def relationships() -> list[str]:
    return [
        "Member 1 has * Loan",
        "Loan * knows 1 Tool",
        "Tool is not a Loan",
        "Loan is not a Member",
    ]

print(relationships()[2])  # Tool is not a Loan
```

## Who receives the message

An office has two lift cabs. Each floor has a call button. Inside a cab, a rider presses a destination. A scheduler decides which cab moves. A design puts `request(floor)` on `Cab` and has every floor button call `cab_a.request`. What breaks, and where should the two kinds of button send their messages?

**Answer:** The floor button has chosen a cab before anything that can see both cabs has a say, so the second cab never gets the call. Floor buttons talk to the `Scheduler`, which owns assignment. A destination button, pressed by someone already in a cab, talks to that `Cab`. The scheduler's `request` looks at idle cabs and calls `go` on one of them. Adding a third cab changes the scheduler's collection, not the floor button.

```python
class Cab:
    def __init__(self, name: str) -> None:
        self.name = name
        self.idle = True
        self.goals: list[int] = []

    def go(self, floor: int) -> None:
        self.idle = False
        self.goals.append(floor)

class Scheduler:
    def __init__(self, cabs: list[Cab]) -> None:
        self.cabs = cabs

    def request(self, floor: int) -> str:
        cab = next(c for c in self.cabs if c.idle)
        cab.go(floor)
        return cab.name

a, b = Cab("A"), Cab("B")
a.idle = False
print(Scheduler([a, b]).request(4))  # B
```

## Bug hunt: the public counter

This hopper lets any caller set `stock`. Show a call that breaks the "never negative" rule, and move the rule inside the type.

```python
class Hopper:
    def __init__(self) -> None:
        self.stock = 1

def vend(hopper: Hopper) -> None:
    hopper.stock -= 1
```

**Answer:** `vend` twice, or `hopper.stock = -5`, both leave a negative count, and nothing in `Hopper` can stop them. Keep the count private. `vend` returns whether it dispensed, and it refuses when the count is already 0. Callers can read `stock` and cannot assign it.

```python
class Hopper:
    def __init__(self, stock: int) -> None:
        self._stock = stock

    @property
    def stock(self) -> int:
        return self._stock

    def vend(self) -> bool:
        if self._stock == 0:
            return False
        self._stock -= 1
        return True

hopper = Hopper(1)
print(hopper.vend(), hopper.vend(), hopper.stock)  # True False 0
```

## A compact cage is not every cage

`BikeCage.park` accepts cargo bikes. `CompactCage` subclasses it and raises on a cargo bike. A function annotated to take a `BikeCage` parks a cargo bike and now crashes when it is handed a compact cage. Why is the subclass the wrong fix?

**Answer:** Callers of `BikeCage` were promised that `park` accepts a cargo bike. The subclass narrowed that promise, so it cannot stand in for the parent. A compact cage is a cage with a different admission rule, not a bike cage that is safe everywhere a bike cage is safe. Put the rule in a policy the cage holds (`accepts(cargo) -> bool`) and stop claiming the is-a relationship. Inheritance is the wrong reuse here.

```python
class Cage:
    def __init__(self, accepts) -> None:
        self.accepts = accepts

    def park(self, cargo: bool) -> str:
        return "parked" if self.accepts(cargo) else "refused"

any_bike = Cage(lambda cargo: True)
compact = Cage(lambda cargo: not cargo)
print(any_bike.park(True), compact.park(True))  # parked refused
```

## One call, three scoring rules

A shed game deals each player a few small integers. Three ways to score a hand exist: the highest single integer, one point per matched pair, and the sum only when it is under ten (otherwise zero). A `Round` currently switches on a string. Replace the switch so a fourth rule does not edit `Round`.

**Answer:** Each rule is an object with `score(cards)`. `Round` asks the rule. High card, pairs, and the sum cap do not share an inheritance tree beyond that one method; they are interchangeable strategies. A fourth rule is a new class passed into the round. `Round.winner` stays a max over `rule.score`.

```python
class HighCard:
    def score(self, cards: list[int]) -> int:
        return max(cards)

class Pairs:
    def score(self, cards: list[int]) -> int:
        return sum(1 for value in set(cards) if cards.count(value) >= 2)

class SumUnder:
    def __init__(self, limit: int) -> None:
        self.limit = limit

    def score(self, cards: list[int]) -> int:
        total = sum(cards)
        return total if total < self.limit else 0

def winner(rule, hands: list[list[int]]) -> int:
    return max(range(len(hands)), key=lambda i: rule.score(hands[i]))

hands = [[3, 3, 1], [9], [4, 4]]
print(winner(HighCard(), hands), winner(Pairs(), hands))  # 1 0
```

## Stop subclassing the cup

Someone has `class Latte(Cup)`, `class Mocha(Latte)`, and `class ExtraShotMocha(Mocha)` so each drink can override `price`. What goes wrong on the next syrup, and what do you put in the cup instead?

**Answer:** Every combination wants its own subclass, and a drink that is both extra-shot and a different syrup does not fit the chain. The cup is one type. It has a list of additions. Each addition knows its own price. Milk, syrup, and an extra shot are three classes, not eight. The cup's price is the base plus the sum of the parts. That is composition. Inheritance would be appropriate only for a true subtype of cup that still honors `Cup`'s contract, which these flavors are not.

```python
class Addition:
    def __init__(self, cents: int) -> None:
        self.cents = cents

    def price(self) -> int:
        return self.cents

class Cup:
    def __init__(self, additions: list[Addition]) -> None:
        self.additions = additions

    def price(self) -> int:
        return 300 + sum(item.price() for item in self.additions)

print(Cup([Addition(50), Addition(75)]).price())  # 425
```

## Interface or base class

You are about to add three ways through a door: a fob, a QR code, and a keypad. They share no fields. A teammate wants an abstract `Reader` with a protected retry counter "in case we need it." Which do you publish to `Door`, and when would the abstract class become the right call?

**Answer:** Publish a tiny capability, `admit(token) -> bool`, and have `Door` depend on that. There is no shared representation, so a common base class only pretends the three readers are one type. An abstract class earns a place later if you truly share code and state, for example one lockout timer and one `failures` counter implemented once, with a hook for how a token is checked. Until that shared code exists, the interface is the smaller promise. Say so: "I am not inventing a base class for a counter we do not have."

```python
class Door:
    def __init__(self, admitter) -> None:
        self.admitter = admitter

    def try_open(self, token: str) -> str:
        return "open" if self.admitter.admit(token) else "shut"

class Fob:
    def admit(self, token: str) -> bool:
        return token.startswith("fob-")

print(Door(Fob()).try_open("fob-17"))  # open
```

## Which letter broke

`LoanDesk.borrow` checks the three-tool limit, appends a row to a CSV file, and sends an email. A change to the email template edits the same class as a change to the limit. Which SOLID concern is that, and how do you split it?

**Answer:** Single responsibility: the desk has three reasons to change (the rule, the storage, the message). It also leans on concrete file and mail types, so the high-level borrow flow is not inverted onto interfaces. Leave the limit on `Member`, where the open loans already live. Pass in a store and a notifier. `borrow` orchestrates; it does not format mail or know about CSV. The open/closed benefit shows up next: a different notifier is a new class, not an edit.

```python
class Member:
    def __init__(self, limit: int = 3) -> None:
        self.limit = limit
        self.open_loans = 0

    def borrow(self) -> bool:
        if self.open_loans >= self.limit:
            return False
        self.open_loans += 1
        return True

class MemoryStore:
    def __init__(self) -> None:
        self.rows: list[str] = []

    def save(self, row: str) -> None:
        self.rows.append(row)

def borrow(member: Member, store: MemoryStore, notes: list[str]) -> bool:
    if not member.borrow():
        return False
    store.save("loan")
    notes.append("mail")
    return True

notes: list[str] = []
print(borrow(Member(limit=1), MemoryStore(), notes), notes)  # True ['mail']
```

## The registry the tests share

`Registry` builds one instance on first use and both bike cages call `Registry.instance()` for the member map. Test A inserts member `ada`. Test B, run in the same process, finds `ada` already present. Why, and what do you pass instead?

**Answer:** The singleton is process-global, so the cages do not have their own members and the tests do not have a fresh one either. Construction order and leftovers become part of the design. Give each cage a map (or a `MemberBook`) in its constructor. The test builds a new book per test. A singleton would be defensible only for something that truly must be unique in the process, and even then the test needs an explicit reset. Hidden global access is the part to refuse.

```python
class Cage:
    def __init__(self, members: dict[str, str]) -> None:
        self.members = members

    def add(self, member_id: str, name: str) -> None:
        self.members[member_id] = name

test_a = Cage({})
test_a.add("ada", "Ada")
test_b = Cage({})
print("ada" in test_b.members)  # False
```

## One place that knows the kinds

Every caller that starts a visit switches on `"fob"` versus `"qr"` and constructs `FobSession` or `QrSession` itself. Adding a keypad code means editing each caller. Move the decision so callers stay on one type.

**Answer:** Put the branch in a factory the door already owns, and return a session the caller can ask `valid()` without knowing the concrete class. A plain function is enough when nothing else is shared. If admit, lockout, and logging are a fixed skeleton, make `open_session` the hook a subclass overrides (the factory method) and keep those steps on the base reader. Either way, a keypad session is a new class plus one arm in the factory, not a sweep of the callers. Say that trade-off: the factory is now the one type that must know every kind.

```python
class FobSession:
    def valid(self) -> bool:
        return True

class QrSession:
    def valid(self) -> bool:
        return True

def open_session(kind: str):
    if kind == "fob":
        return FobSession()
    if kind == "qr":
        return QrSession()
    raise ValueError(kind)

def admit(kind: str) -> bool:
    return open_session(kind).valid()

print(admit("qr"))  # True
```

## A fee you can swap

Member day is free. An event day is 200 cents per hour. The cage's `park` currently contains both formulas behind a boolean `event_day`. A third formula, "first hour free, then 100 cents," is coming next month. How do you extend `park` without editing it again?

**Answer:** Pull the formula into a strategy with `price(hours) -> int`. The cage stores the strategy and adds `self.fee.price(hours)` to the receipt. Member flat, event hourly, and later first-hour-free are three classes. `park` does not grow a branch. This is worth the extra types because a third rule is already promised. If the boolean were permanent, the strategy would be ceremony, and you should say that before introducing it.

```python
class MemberFlat:
    def price(self, hours: int) -> int:
        return 0

class EventHourly:
    def price(self, hours: int) -> int:
        return 200 * hours

class Cage:
    def __init__(self, fee) -> None:
        self.fee = fee

    def park(self, hours: int) -> int:
        return self.fee.price(hours)

print(Cage(MemberFlat()).park(3), Cage(EventHourly()).park(3))  # 0 600
```

## Who hears the cab arrive

When a cab reaches a floor, the hall lantern lights and a log line is written. The first design imports `Lantern` and `LogBook` inside `Cab.arrive`. A third consumer, a speech chime, is now required. What do you change, and what do you refuse to promise?

**Answer:** `Cab` keeps listeners and calls them with the floor. The lantern, the log, and the chime subscribe. `arrive` does not gain a third import. Do not promise a call order unless a caller depends on it; if the chime must follow the log, say so and sort the list deliberately. A listener that raises should be isolated if one flaky display must not block the log. If there will only ever be one consumer, skip the list and take that collaborator in the constructor.

```python
class Cab:
    def __init__(self) -> None:
        self._listeners: list = []

    def listen(self, fn) -> None:
        self._listeners.append(fn)

    def arrive(self, floor: int) -> None:
        for fn in self._listeners:
            fn(floor)

heard: list[str] = []
cab = Cab()
cab.listen(lambda floor: heard.append(f"lantern:{floor}"))
cab.listen(lambda floor: heard.append(f"log:{floor}"))
cab.arrive(6)
print(heard)  # ['lantern:6', 'log:6']
```

## Wrap, or translate

Your doors speak `open(credential) -> bool`. A vendor gate speaks `unlock(pin) -> int`, with `0` meaning the latch moved. You also want a line written every time any door opens. Which of those two needs is a decorator, which is an adapter, and why can't one wrapper do both jobs cleanly?

**Answer:** The vendor gap is an adapter: it changes `unlock` into `open` and the integer code into a boolean. Logging is a decorator: same `open` signature, extra behavior, then a call to the inner door. Stack them as `LoggingDoor(VendorGateAdapter(gate))` if you need both. One class that both translates `unlock` and logs is harder to reuse on a door that already speaks `open`, and harder to test as two separate jobs. Identity also changes: the object the building holds is the outer wrapper, not the vendor gate.

```python
class VendorGate:
    def unlock(self, pin: str) -> int:
        return 0 if pin == "ok" else 1

class VendorGateAdapter:
    def __init__(self, gate: VendorGate) -> None:
        self.gate = gate

    def open(self, credential: str) -> bool:
        return self.gate.unlock(credential) == 0

class LoggingDoor:
    def __init__(self, inner) -> None:
        self.inner = inner
        self.log: list[str] = []

    def open(self, credential: str) -> bool:
        opened = self.inner.open(credential)
        self.log.append(f"{credential}:{opened}")
        return opened

door = LoggingDoor(VendorGateAdapter(VendorGate()))
print(door.open("ok"), door.log)  # True ['ok:True']
```

## Legal moves of a dispenser

A workshop dispenser starts `idle`. A badge moves it to `authorized`. Choosing a tool moves it to `vending`. A finished vend returns to `idle`. A fault during a vend moves it to `jammed`, and only a reset returns to `idle`. Choosing a tool while idle, and badging a jammed machine, must not change state. Implement the rule so an illegal pair is obvious in one place.

**Answer:** Write the legal edges as a map from `(state, event)` to the next state, and treat a missing key as a refusal. The interesting design is the set of edges, not a cluster of booleans. Select-from-idle and badge-from-jammed are absent, so they refuse. A State-pattern alternative (one object per state, each deciding the next object) fits if each state grows real behavior; for five edges the table is the thing you can read in the interview. Say that. Extending the machine with a `refund` event is one new key, not a new flag tangled with the others.

```python
NEXT = {
    ("idle", "badge"): "authorized",
    ("authorized", "select"): "vending",
    ("vending", "finished"): "idle",
    ("vending", "fault"): "jammed",
    ("jammed", "reset"): "idle",
}

def step(state: str, event: str) -> str:
    return NEXT.get((state, event), state)

state = "idle"
state = step(state, "select")   # still idle
state = step(state, "badge")    # authorized
state = step(state, "select")   # vending
state = step(state, "fault")    # jammed
print(state, step(state, "badge"))  # jammed jammed
```
