---
name: mbse-sysarch
description: Model a system's architecture as mbse-schemas data, then check and save it. Covers modules with interfaces and ports, implementations whose instances exchange messages of a given schema over directional channels, and containers that hold parts hard (structure) or soft (organization, along axes). Use when formalizing a block diagram, component/connector or SysML internal block structure, a hardware module hierarchy, a dataflow or actor network, or when writing code that imports mbse.Architecture.Systems.
---

# mbse-sysarch

An architecture here is data in an mbse-schemas store, not a diagram. `Interactions.define(store)` builds the schemas
(and `Structure.define(store)`, which it calls). From then on, modules, interfaces, implementations and channels are
built, read, validated and saved like any other mbse-schemas data. Python only for now:
`mbse.Architecture.Systems.Framework`, on mbse-schemas 0.22.0.

## When to use it

- You are writing down what a system is made of: components, where they meet, and what flows between them.
- The components run concurrently and cooperate by messages: hardware modules, actors, services, dataflow stages.
- You want the architecture checked (every channel has a source and a destination, every attachment matches an
  interface the instance has) and kept as data beside the rest of an executable specification.

It is a poor fit for call graphs or class hierarchies, where parts call each other synchronously rather than exchange
messages.

Why the mbse repositories exist, and this one's part: [MBSE.md](https://github.com/pitaman71/mbse-basis/blob/main/MBSE.md).

## Practices that prevent most mistakes

1. **Define the schemas once per store, outside any transaction.** `I = Interactions.define(store)`. Calling it
   again gives back the same schemas, and on a store loaded from a snapshot it also restores the meta-schema extension
   that lets a channel link its message schema.
2. **Every module lives in the library.** `library = store.singleton("Interactions.Library")`. Add a module with
   `store.Interactions.Library(library, lambda lib: lib.modules(lambda a: a.insert(lambda e: e.name("Uart").module(...))))`.
   A module outside it is refused when its transaction ends. Its name is its library entry's: `Module` has no `name`
   property.
3. **Names are entry keys.** Interfaces (`HasInterface`), ports (`HasPort`), instances (`HasInstance`) and channels
   (`HasChannel`) are named by their owner's entry. Find one with `owner.<adjacency>.at(name).<link>`, for example
   `module.interfaces.at("serial").intf`.
4. **A port's direction is `"in"` or `"out"`, as its own module sees it.** At an instance, `"out"` is a channel's
   source and `"in"` its destination. At the implementation's boundary, where the implementation itself fills
   `Connects`' `instance` link, they are the other way round. `Interactions.ends(channel)` works out each end's role.
5. **A channel links its message schema itself**, through `Interactions.HasSchema`:
   `c.message(lambda a: a.insert(lambda e: e.schema(Sample)))`. Any value schema works (object, scalar, container,
   union, intersection, any); a relation does not.
6. **Hard or soft is decided by the container.** A container that another container organizes
   (`organizer(... hard(impl))`) is soft, and everything it contains, it contains softly. An object has at most one
   hard container. A soft container groups only what its hard container holds, and lies along at most one axis.
7. **Two checks, both asked for.** `Validators.Validate(store).Reachable(I.Module, root)` reports what the schemas
   say: `unique` clauses, scalar types, which schemas may fill a link. `Interactions.Check()(root)` reports what they
   cannot. Neither runs on its own.
8. **Save the store, not a module.** The library reaches everything, so `JSON.ToJSON(store).Snapshot()` holds the
   whole design. A reachable document (`.Reachable(...)`) refers to modules by path and writes implementations anew
   each time it is read.

## Load the reference for your task

| Task | Read |
|---|---|
| Decide how to model something: SysML, UML, hardware or actor concepts mapped to these schemas | [references/modeling.md](references/modeling.md) |
| Write Python: a complete program, cheat sheet, traps | [references/python.md](references/python.md) |
| The data underneath: stores, builders, validation, snapshots | the [mbse-schemas skill](https://github.com/pitaman71/mbse-schemas/blob/main/skills/mbse-schemas/SKILL.md) |

Deeper material is in the repository: `docs/SYSARCH.md` holds every schema, decision and open question, and four
tutorial case studies explain the reasoning. Links use `https://github.com/pitaman71/mbse-sysarch/blob/main/<path>`;
in a checkout, `<path>` is relative to the repository root.
