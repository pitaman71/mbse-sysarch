# Modeling an architecture

How to express an architecture with the Interactions and Structure schemas. Terms from other languages collide with
ours, so each is qualified with whose it is.

## Concepts mapped to schemas

| Concept (SysML / UML / hardware / actors) | Schema |
|---|---|
| Block, component, Verilog `module` definition, actor class | `Interactions.Module`, in the library under its name |
| SysML port, UML interface realization, a bus or stream a component exposes | `Interactions.Interface`, owned by its module (`HasInterface`) |
| A side of it: transmit and receive, request and response, a Verilog `input` or `output` | `Interactions.Port`, owned by its interface (`HasPort`), its `direction` `"in"` or `"out"` |
| SysML internal block diagram, a Verilog `module` body, an actor system's wiring | `Interactions.Implementation` of a module (`Implements`) |
| Part property, Verilog instance, actor instance | `Interactions.Instance`, in its implementation (`HasInstance`), of a module (`Instantiates`) |
| Connector, wire, net, queue, topic, Go channel | `Interactions.Channel`, in its implementation (`HasChannel`), carrying one message schema (`Interactions.HasSchema`) |
| Item flow, signal, the data type on a wire | the channel's message schema: any mbse-schemas value schema |
| Connector end, binding to a port | an `Interactions.Connects` entry: channel, instance (or the implementation, for its own module's boundary), interface, port |
| Delegation connector, a port of the enclosing block | `Connects` with the implementation as `instance`: the implemented module's own interface |
| Fan-out, multicast, a work queue | a channel with several destinations; its `distribution`, `"BROADCAST"`, `"ANYCAST"` or `"ROUND_ROBIN"` |
| Package, subsystem boundary that is pure structure | a `Structure.Container` holding parts hard |
| Swimlane, pipeline stage, clock or power domain, diagram page | a soft container: a `Structure.Container` that an implementation organizes |
| The dimension those groupings run along (stages, domains) | a `Structure.Axis`, orienting its soft containers |

## Decisions

**Interface or port?** An interface is where messages exist; a port is a side of it. A UART has one `serial`
interface with ports `tx` and `rx`, not two interfaces. Attach a channel to the port whose direction is its end.

**Instance or module?** A module is the kind of component, kept once in the library. An instance is one use of it
inside one implementation. Two filters in a pipeline are two instances of one `Filter` module.

**Inside or at the boundary?** A channel between two instances attaches to each instance. A channel reaching the
outside of the module being implemented attaches to the implementation itself, on its module's interface. Directions
turn around there: the module's `"out"` port is a destination of the channel inside.

**Hard or soft?** Hard containment is what an implementation is made of, and every part has one hard container. Soft
containment is how people look at it: overlapping groupings, along axes, that change nothing that runs. Use soft
containers for stages and domains, and leave `HasInstance` and `HasChannel` to say what an implementation holds.

**Several implementations.** A module may have several: a reference model and an optimized one. Nothing yet chooses
which one an instance uses (the repository's `docs/SYSARCH.md`, Open questions).

## Go deeper

| Topic | Read |
|---|---|
| Modules, interfaces, ports, paths | [tutorial 1](https://github.com/pitaman71/mbse-sysarch/blob/main/python3/tutorials/01_A_Module_And_Its_Interfaces.ipynb) |
| Implementations, channels, ends, distributions | [tutorial 2](https://github.com/pitaman71/mbse-sysarch/blob/main/python3/tutorials/02_Implementing_A_Module.ipynb) |
| Soft containers and axes | [tutorial 3](https://github.com/pitaman71/mbse-sysarch/blob/main/python3/tutorials/03_Organizing_A_Design.ipynb) |
| Every schema and decision | [SYSARCH.md](https://github.com/pitaman71/mbse-sysarch/blob/main/docs/SYSARCH.md#the-model) |
