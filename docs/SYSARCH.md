<!-- nav -->
[← Checking and saving (Python)](../python3/tutorials/04_Checking_And_Saving.ipynb) · [Home](../README.md) · [Conformance corpus →](../conformance/README.md)

# System architecture and interaction models

mbse-sysarch models a system's architecture as mbse-schemas data: modules that meet the world at interfaces,
implementations of them by instances of other modules that cooperate by exchanging messages over channels, and
containers that hold those parts hard (structure) or soft (organization). This document records what is decided,
what was built, and what is still open. It cites the mbse basis by ID ([mbse-basis](https://github.com/pitaman71/mbse-basis))
and mbse-schemas' design ([FRAMEWORK.md](https://github.com/pitaman71/mbse-schemas/blob/main/docs/FRAMEWORK.md))
rather than restating them.

## The model

`Structure` and `Interactions` are two packages of schemas, each built in the caller's store by its `define(store)`
(`python3/mbse/Architecture/Systems/Framework/`). OBJECT is an `OfObject` reference object schema, RELATION an
`OfRelation`. A relation's `uniques` are given as mbse-schemas writes them: `unique(S)` says that the links and
properties outside `S` determine `S`.

### Structure

| Schema | Kind | Links and properties | `uniques` |
|---|---|---|---|
| `Structure.Container` | OBJECT | `name`, `description` | |
| `Structure.Axis` | OBJECT | `name`, `description` | |
| `Structure.Contains` | RELATION | `c1` contains `c2` | `[]`: a set |
| `Structure.Organizes` | RELATION | `hard` organizes `soft` | `hard`: a soft container lies in one hard container |
| `Structure.Orients` | RELATION | `axis` orients `soft_container` | `axis`: a soft container lies along one axis |

### Interactions

| Schema | Kind | Links and properties | `uniques` |
|---|---|---|---|
| `Interactions.Library` | OBJECT, the singleton `Interactions.Library` | | |
| `Interactions.Module` | OBJECT | `description` | |
| `Interactions.Interface` | OBJECT | `description` | |
| `Interactions.Port` | OBJECT | `direction` (`"in"` or `"out"`), `description` | |
| `Interactions.Implementation` | OBJECT, refines `Structure.Container` | (`name`, `description`) | |
| `Interactions.Instance` | OBJECT, refines `Structure.Container` | (`name`, `description`) | |
| `Interactions.Channel` | OBJECT | `distribution`, `description` | |
| `Interactions.HasModule` | RELATION | `library`, `name`, `module` | `[library, name]`, `[module]`: a directory |
| `Interactions.HasInterface` | RELATION | `module`, `name`, `intf` | `[module, name]`, `[intf]` |
| `Interactions.HasPort` | RELATION | `intf`, `name`, `port` | `[intf, name]`, `[port]` |
| `Interactions.Implements` | RELATION | `impl`, `module` | `module`: an implementation is of one module |
| `Interactions.Instantiates` | RELATION | `instance`, `module` | `module`: an instance is of one module |
| `Interactions.HasInstance` | RELATION | `impl`, `name`, `instance` | `[impl, name]`, `[instance]` |
| `Interactions.HasChannel` | RELATION | `impl`, `name`, `channel` | `[impl, name]`, `[channel]` |
| `Interactions.HasSchema` | RELATION | `channel`, `schema` | `schema`: a channel's messages have one schema |
| `Interactions.Connects` | RELATION | `channel`, `instance`, `intf`, `port` | `[]`: a set |

The module owns its interfaces, and an interface its ports (adjacencies marked `owner`), and the library owns every
module, so each has a path from the library (`Pipeline.readings.out`). `Interactions.Check` and `Structure.Check` list
the problems no `unique` clause expresses; mbse-schemas' `Validators.Validate` reports the rest.

`Interactions.HasSchema` is not mbse-schemas' meta relation `Schemas.HasSchema`, which links a property to its
schema; the two are always written qualified.

## Resolved

Decided by the user, as the user decided it:

1. **The repository and its scope.** A new repository, mbse-sysarch, whose Python package is
   `mbse.Architecture.Systems`, with its schemas under `Framework/`. It builds on the latest release of mbse-schemas
   on `main`, 0.22.0. Python only for now: "no ts for now". The TypeScript implementation every other mbse repository
   has (mbse-basis C-001) is planned, not started.
2. **The schemas listed in the plan** (the workspace's `TODO.md`, System Architecture + Interaction Models):
   `Structure.Container`, `Structure.Contains(c1, c2)` ("hard or soft containment depending on context"),
   `Structure.Axis` ("organizational direction"), `Structure.Organizes(hard, soft)` ("makes one container a 'soft'
   container inside of the 'hard' container"), `Structure.Orients(axis, soft_container)`; `Interactions.Module`
   ("nameable, instantiatable, addressible component"), `Interactions.Interface` ("place where messages exist relative
   to a containing Module"), `Interactions.HasInterface(module, name, intf)`, `Interactions.Port` ("optional
   designation of the sides/senses of an interface"), `Interactions.Implementation` ("a realization of a module using
   asynchronously cooperating submodules"), `Interactions.Implements(impl, module)`, `Interactions.Instance`
   ("structural instance"), `Interactions.HasInstance(impl, name, instance)`, `Interactions.Channel` ("directional
   carrier of messages between source and destination interface(s) whose messages' type is provided as a schema.
   Distribution semantics across multiple destinations are configurable and default to BROADCAST"),
   `Interactions.HasChannel(impl, name, channel)`, `Interactions.HasSchema(channel, schema)`.
3. **Hard or soft is the container's.** `Contains(c1, c2)` is soft where `c1` is the `soft` end of an `Organizes`
   entry, and hard otherwise.
4. **Implementations and instances are containers.** `Interactions.Implementation` and `Interactions.Instance` refine
   `Structure.Container`; `HasInstance` and `HasChannel` remain the named composition, and `Structure.Contains` adds
   containment of any kind (an implementation organizing soft containers that group its instances and channels).
5. **Structure is a package of its own**, `Framework/Structure.py`, beside `Framework/Interactions.py`.
6. **`HasPort(intf, name, port)`**: an interface owns its named ports. (The plan wrote `HasPort(module, name, intf)`,
   the same as `HasInterface`.)
7. **A channel is attached to a port, which carries the direction**: `Connects(channel, instance, intf, port)`,
   adding to the plan's `Connects(channel, intf, port)` the instance whose interface it is.
8. **A channel's message schema is a relation to the schema object**, `HasSchema(channel, schema)`.
9. **A library owns the modules.** The singleton `Interactions.Library` owns every module by name, through
   `Interactions.HasModule(library, name, module)`, so that modules, and the interfaces and ports they own, are
   addressable by path and held by the store's snapshot.

Decided by the agent while building, to confirm or overturn:

10. **`Interactions.Instantiates(instance, module)`**, which the plan does not list, says which module an instance is
    of; without it no attachment could be checked against the instance's interfaces.
11. **At the boundary, the implementation fills `Connects`' `instance`.** mbse-schemas 0.22.0 requires every link of
    an entry, so an attachment to the implemented module's own interface cannot leave `instance` out; the
    implementation stands for its module's boundary there. A port's `direction` is `"in"` or `"out"` as its module
    sees it, so an instance's `"out"` port is a source and its `"in"` port a destination, and at the boundary the other
    way round (`Interactions.ends`).
12. **Distributions** are `"BROADCAST"` (every destination; what an absent `distribution` means), `"ANYCAST"` (any
    one) and `"ROUND_ROBIN"` (each in turn); `Check` reports any other.
13. **Message schemas are value schemas.** `define` extends the store's meta-schemas `OfScalar`, `OfObject`,
    `OfUnion`, `OfIntersection`, `OfContainer` and `OfAny` (`store.extend`) with an anonymous adjacency through
    `HasSchema`'s `schema` link, so that their schemas fill it; a relation, a pattern or a module does not. A store's
    snapshot does not carry the extension, so `define` adds it to a store that holds the schemas without it.
14. **A module's name is its `HasModule` entry's**: `Interactions.Module` has no `name` property, so that the name
    cannot disagree with the library. Interfaces, ports, instances and channels are named by their entries likewise;
    an instance inherits `Structure.Container`'s `name`, and `Check` reports one that differs from its `HasInstance`
    name.
15. **Soft containment stays inside its hard container**: a soft container may hold what its hard container holds
    directly (through `Structure.Contains`, or, for an implementation, `HasInstance` and `HasChannel`) and the soft
    containers that container organizes, and nothing else.
16. **Checks are functions over a reachable graph.** `Structure.Check()(root)` and `Interactions.Check()(root)`
    (which adds an implementation's instances and channels to hard containment) list problems for every object
    `Reachable.of(root)` gives, as mbse-schemas' `Validate.Reachable` does, naming each object by its schema and
    dotted path (`Interactions.path`). They report: more than one hard container; containing oneself, hard; an axis
    on a container nothing organizes; soft containment outside the hard container; a port without a direction; an
    implementation or instance of no module; an instance in no implementation; a channel in no implementation, of no
    schema, with an unknown distribution, attached outside its implementation, to an interface its instance's module
    lacks, through a port its interface lacks, or without a source or a destination (where every attachment has a
    direction).

## Open questions

- **Paths below the module.** Implementations, instances and channels are counted objects: findable by name from
  their owner (`impl.instances.at("sensor")`), but without a path, and a reachable document writes them anew.
  Giving `Implements` a `name`, so that a module owns its implementations, would give every part a path
  (`Pipeline.reference.sensor`).
- **Ports are optional; attachments need one.** The plan calls a port an "optional designation", but every
  attachment names a port, so an interface without ports cannot be attached. Either an interface gains a direction
  of its own, or `Connects` an optional port, which mbse-schemas 0.22.0 cannot express.
- **An instance's two names**: the `HasInstance` name, and the `name` it inherits from `Structure.Container`.
- **Directions beyond in and out**: a bidirectional port, or request and response sides.
- **Distributions**: which semantics are wanted, and whether they belong to the channel or to its destinations.
- **Rendering with mbse-diagrams.** The user plans for mbse-sysarch to port, in the near future, to
  [mbse-diagrams](https://github.com/pitaman71/mbse-diagrams), a general-purpose utility for incremental rendering
  that is still under development. When, and what a design renders as, are not yet decided.
- **Choosing an implementation.** A module may have several; nothing yet says which one an instance uses, nor
  elaborates a design into its tree of instances.
- **Deeper soft containment**: whether a soft container may group what lies deeper in its hard container's
  structure.
- **Schema names**: `Interactions.*` and `Structure.*`, as the plan names them, or under a longer module such as
  `Architecture.Systems.*`, should other packages want those names.
- **mbse-schemas' store overhaul.** Its next release moves dependents to installs (its `docs/proposals/
  store-overhaul`, step 5); `define(store)` will become an install then.
- **TypeScript**, and with it the cross-language conformance this repository's corpus is ready for.

---

<!-- nav -->
[← Checking and saving (Python)](../python3/tutorials/04_Checking_And_Saving.ipynb) · [Home](../README.md) · [Conformance corpus →](../conformance/README.md)
