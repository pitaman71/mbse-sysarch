# mbse-sysarch in Python

Install `mbse-sysarch` (it brings `mbse-schemas`), then import from `mbse.Architecture.Systems.Framework`.

## A complete program

A producer sends `bus.Word`s to two consumers over one channel; the system's own `out` interface receives them too.

```python
from mbse.Schemas.Framework import Builders, JSON, Validators
from mbse.Architecture.Systems.Framework import Interactions

store = Builders.Store()
I = Interactions.define(store)  # the schemas, Structure's too, in this store; outside any transaction
library = store.singleton("Interactions.Library")

with store.transaction():
    Word = store.Schemas.OfObject(lambda o: o.name("bus.Word").properties([
        lambda t: t.name("bits").schema([store.Schemas.OfInt]),
    ]))


def module(name, interfaces):
    """A module in the library, with interfaces by name, each with ports by name and direction."""
    def interface(ports):
        return lambda i: i.ports(lambda a: [
            a.insert(lambda e, n=n, d=d: e.name(n).port(lambda p: p.direction(d))) for n, d in ports.items()])

    store.Interactions.Library(library, lambda lib: lib.modules(lambda a: a.insert(lambda e: e.name(name).module(
        lambda m: m.interfaces(lambda a: [
            a.insert(lambda e, n=n, p=p: e.name(n).intf(interface(p))) for n, p in interfaces.items()])))))
    return library.modules.at(name).module


def attach(channel, at, intf, port):
    """Attaches a channel to a port of an interface of `at`'s module: an instance's, or the implementation's own."""
    interface = Interactions.module_of(at).interfaces.at(intf).intf
    store.Interactions.Channel(channel, lambda c: c.connections(lambda a: a.insert(
        lambda e: e.instance(at).intf(interface).port(interface.ports.at(port).port))))


with store.transaction():
    producer = module("Producer", {"words": {"tx": "out"}})
    consumer = module("Consumer", {"words": {"rx": "in"}})
    system = module("System", {"out": {"tx": "out"}})

    def of(m):
        return lambda i: i.module(lambda a: a.insert(lambda e: e.module(m)))

    impl = store.Interactions.Implementation(lambda x: (
        x
        .name("main")
        .module(lambda a: a.insert(lambda e: e.module(system)))
        .instances(lambda a: (
            a
            .insert(lambda e: e.name("p").instance(of(producer)))
            .insert(lambda e: e.name("c1").instance(of(consumer)))
            .insert(lambda e: e.name("c2").instance(of(consumer)))
        ))
        .channels(lambda a: a.insert(lambda e: e.name("bus").channel(
            lambda c: c.distribution("ROUND_ROBIN").message(lambda a: a.insert(lambda e: e.schema(Word))))))
    ))
    bus = impl.channels.at("bus").channel
    attach(bus, impl.instances.at("p").instance, "words", "tx")
    attach(bus, impl.instances.at("c1").instance, "words", "rx")
    attach(bus, impl.instances.at("c2").instance, "words", "rx")
    attach(bus, impl, "out", "tx")  # the boundary: the system's own out port, a destination inside

assert [(Interactions.path(e.instance), e.role) for e in Interactions.ends(bus)] == [
    ("main.p", "source"), ("main.c1", "destination"), ("main.c2", "destination"), ("main", "destination")]
assert Interactions.message_schema(bus) is Word and Interactions.distribution(bus) == "ROUND_ROBIN"
assert Interactions.Check()(system) == []
assert Validators.Validate(store).Reachable(I.Module, system) == []

# Saved as the store's snapshot, loaded into another store, then defined there.
copy = Builders.Store()
JSON.FromJSON(copy).Snapshot(JSON.ToJSON(store).Snapshot())
Interactions.define(copy)
loaded = copy.singleton("Interactions.Library").modules.at("System").module
assert Interactions.Check()(loaded) == []
```

## Cheat sheet

```python fragment
from mbse.Architecture.Systems.Framework import Interactions, Structure
I = Interactions.define(store)                 # Interactions' schemas, after Structure's; again: the same ones
S = Structure.define(store)                    # Structure's alone
library = store.singleton("Interactions.Library")

# Modules, interfaces, ports: owned, by name; a module only in the library.
store.Interactions.Library(library, lambda lib: lib.modules(lambda a: a.insert(lambda e: e.name("M").module(lambda m: ...))))
store.Interactions.Module(m, lambda m: m.interfaces(lambda a: a.insert(lambda e: e.name("bus").intf(lambda i: ...))))
store.Interactions.Interface(i, lambda i: i.ports(lambda a: a.insert(lambda e: e.name("tx").port(lambda p: p.direction("out")))))
library.modules.at("M").module; m.interfaces.at("bus").intf; i.ports.at("tx").port   # find by name
store.Instances.Interactions.Library.modules({"name": "M"}).interfaces({"name": "bus"})  # find by path
Interactions.path(port)                        # "M.bus.tx"; an instance's "impl.name"; None where a name is missing

# Implementations, instances, channels.
store.Interactions.Implementation(lambda x: x.name("ref").module(lambda a: a.insert(lambda e: e.module(m)))
    .instances(lambda a: a.insert(lambda e: e.name("u0").instance(lambda i: i.module(lambda a: a.insert(lambda e: e.module(sub)))))))
    .channels(lambda a: a.insert(lambda e: e.name("ch").channel(lambda c: c.message(lambda a: a.insert(lambda e: e.schema(Msg))))))
store.Interactions.Channel(ch, lambda c: c.connections(lambda a: a.insert(lambda e: e.instance(u0).intf(i).port(p))))
store.Interactions.Channel(ch, lambda c: c.connections(lambda a: a.insert(lambda e: e.instance(impl).intf(i).port(p))))  # boundary
Interactions.module_of(instance_or_impl); Interactions.message_schema(ch); Interactions.distribution(ch)
Interactions.ends(ch)                          # [End(instance, intf, port, role)], role "source", "destination" or None

# Structure: containers, hard and soft; axes.
store.Structure.Container(lambda c: c.name("stage").organizer(lambda a: a.insert(lambda e: e.hard(impl)))
    .axis(lambda a: a.insert(lambda e: e.axis(flow))).contents(lambda a: a.insert(lambda e: e.c2(u0))))
store.Structure.Axis(lambda a: a.name("flow"))
Structure.is_soft(c); Structure.organizer(c); Structure.hard_containers(x)   # Structure.Contains alone
Interactions.Check().hard_containers(x)        # and the implementation an instance or channel is in

# Checks: every problem, each a line; [] when there are none.
Interactions.Check()(root); Structure.Check()(root)
Validators.Validate(store).Reachable(I.Module, root)
```

## Traps

- `Interactions.define` and `Structure.define` open transactions of their own: call them before or between yours,
  never inside one.
- A module built with `store.Interactions.Module(...)` and not inserted into the library is refused when the
  transaction ends ("needs an owner"). Build it inside the library's `insert`, or insert it in the same transaction.
- `Module` has no `name` property: `m.name("X")` raises `ReadOnlyError`. Name a module by its library entry.
- A channel's ends depend on where it attaches. An `"out"` port of the implemented module, reached through the
  implementation, is a destination, not a source.
- `Connects` needs all four links, so an interface without ports cannot be attached. Give it a port.
- Compare objects with `is`. In Python a proxy compares as itself, but a scalar member compares as its value.
- Loading a snapshot into a fresh store brings the schemas but not `define`'s meta-schema extension. Call
  `Interactions.define(store)` on it, or validation reports every channel's `schema` link.
- `Interactions.HasSchema` is ours; mbse-schemas' `Schemas.HasSchema` links a property to its schema. Say which.

## Go deeper

| Topic | Read |
|---|---|
| Checking, fixing and saving a design | [tutorial 4](https://github.com/pitaman71/mbse-sysarch/blob/main/python3/tutorials/04_Checking_And_Saving.ipynb) |
| The example pipeline, a self-checking program | [Examples/Pipeline.py](https://github.com/pitaman71/mbse-sysarch/blob/main/python3/mbse/Architecture/Systems/Examples/Pipeline.py) |
| Stores, builders and snapshots | [mbse-schemas' Python reference](https://github.com/pitaman71/mbse-schemas/blob/main/skills/mbse-schemas/references/python.md) |
