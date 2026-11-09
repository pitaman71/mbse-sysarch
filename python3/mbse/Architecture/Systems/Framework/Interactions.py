"""Interactions: modules, their interfaces, and implementations of them by instances that exchange messages.

A *module* (`Interactions.Module`) is a component that can be named, instantiated and addressed: the store's library
(`Interactions.Library`, a singleton) owns it under its name (`Interactions.HasModule(library, name, module)`), which
starts its path and its interfaces' and ports'. Its *interfaces*
(`Interactions.Interface`, owned through `Interactions.HasInterface(module, name, intf)`) are where messages exist
relative to it, and an interface's *ports* (`Interactions.Port`, owned through `Interactions.HasPort(intf, name, port)`)
designate its sides or senses: a port's `direction` is `"in"` or `"out"`, as the module sees it.

An *implementation* (`Interactions.Implementation`, of a module through `Interactions.Implements(impl, module)`)
realizes a module with asynchronously cooperating submodules: its *instances* (`Interactions.Instance`, named in it
through `Interactions.HasInstance(impl, name, instance)`), each of one module (`Interactions.Instantiates(instance,
module)`), and its *channels* (`Interactions.Channel`, named in it through `Interactions.HasChannel(impl, name,
channel)`). A channel carries messages of one schema (`Interactions.HasSchema(channel, schema)`, linking the schema
object itself) from its sources to its destinations, delivered to them as its `distribution` says, `"BROADCAST"` where
it says nothing. `Interactions.Connects(channel, instance, intf, port)` attaches a channel to a port of an interface:
of an instance's module, or, where the implementation itself fills `instance`, of the module it implements, at its
boundary. The port's direction gives the end: an instance's `"out"` port is a source and its `"in"` port a
destination; at the boundary, the other way round.

Implementations and instances are `Structure.Container`s, so an implementation may organize soft containers that
group its instances and channels (`mbse.Architecture.Systems.Framework.Structure`).

`define(store)` builds these schemas in a store; `Check()(root)` lists the problems of the architecture reachable from
`root` that the relations' `unique` clauses cannot express, Structure's included.
"""

from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass
from typing import Any

from . import Structure

__all__ = ["BROADCAST", "DISTRIBUTIONS", "DIRECTIONS", "MESSAGE_KINDS", "Check", "Defined", "End", "define",
           "distribution", "ends", "message_schema", "module_of", "path"]

BROADCAST = "BROADCAST"
DISTRIBUTIONS = (BROADCAST, "ANYCAST", "ROUND_ROBIN")
"""How a channel delivers each message to its destinations: to every one, to any one, or to each in turn."""
DIRECTIONS = ("in", "out")
"""A port's direction, as its module sees it."""

MESSAGE_KINDS = ("OfScalar", "OfObject", "OfUnion", "OfIntersection", "OfContainer", "OfAny")
"""The meta-schemas whose schemas a channel's messages may have: every schema of a value."""


@dataclass(frozen=True)
class Defined:
    """The Interactions schemas, as `define` built them in one store."""

    Library: Any
    Module: Any
    Interface: Any
    Port: Any
    Implementation: Any
    Instance: Any
    Channel: Any
    HasModule: Any
    HasInterface: Any
    HasPort: Any
    Implements: Any
    Instantiates: Any
    HasInstance: Any
    HasChannel: Any
    HasSchema: Any
    Connects: Any


def define(store: Any) -> Defined:
    """Builds the Interactions schemas in `store`, after Structure's (`Structure.define`), and extends the store's
    meta-schemas so that a channel links its message schema; a store that holds them already gives the ones it holds.
    Call it outside any transaction."""
    held = Structure._registered(store, Defined, "Interactions")
    if held is not None:
        _extend(store, held.HasSchema)  # a snapshot read into a bare store brings the schemas, not the extension
        return held
    structure = Structure.define(store)
    Text = store.Schemas.OfStr

    def text(name: str, description: str) -> Callable[[Any], Any]:
        return lambda t: t.name(name).schema([Text]).description(description)

    def named(relation: str, owner: str, owned: str, description: str) -> Any:
        """A directory: an owner's members by name, each member in one owner under one name."""
        return store.Schemas.OfRelation(lambda r: (
            r
            .name(relation)
            .description(description)
            .links([lambda t: t.name(owner), lambda t: t.name(owned)])
            .properties([text("name", "The member's name within its owner")])
            .uniques([[owner, "name"], [owned]])  # the member determines its owner and name; they determine it
        ))

    def of(relation: str, link: str, target: str, description: str) -> Any:
        """Each object of `link` is of at most one `target`."""
        return store.Schemas.OfRelation(lambda r: (
            r
            .name(relation)
            .description(description)
            .links([lambda t: t.name(link), lambda t: t.name(target)])
            .uniques(target)
        ))

    with store.transaction():
        Library = store.Schemas.OfObject(lambda o: (
            o
            .name("Interactions.Library")
            .ref(True)
            .singleton("Interactions.Library")
            .description("The store's modules, by name: where every module's path starts")
        ))
        Module = store.Schemas.OfObject(lambda o: (
            o
            .name("Interactions.Module")
            .ref(True)
            .description("A component that can be named, instantiated and addressed: named by its HasModule entry")
            .properties([text("description", "What the module does")])
        ))
        Interface = store.Schemas.OfObject(lambda o: (
            o
            .name("Interactions.Interface")
            .ref(True)
            .description("A place where messages exist relative to the module that has it")
            .properties([text("description", "What passes through the interface")])
        ))
        Port = store.Schemas.OfObject(lambda o: (
            o
            .name("Interactions.Port")
            .ref(True)
            .description("A side or sense of an interface")
            .properties([
                text("direction", "'in' or 'out', as the interface's module sees it"),
                text("description", "What the port carries"),
            ])
        ))
        Implementation = store.Schemas.OfObject(lambda o: (
            o
            .name("Interactions.Implementation")
            .ref(True)
            .refines([structure.Container])
            .description("A realization of a module by asynchronously cooperating submodules")
        ))
        Instance = store.Schemas.OfObject(lambda o: (
            o
            .name("Interactions.Instance")
            .ref(True)
            .refines([structure.Container])
            .description("A structural instance of a module within an implementation, named by its HasInstance entry")
        ))
        Channel = store.Schemas.OfObject(lambda o: (
            o
            .name("Interactions.Channel")
            .ref(True)
            .description("A directional carrier of messages of one schema, from its sources to its destinations")
            .properties([
                text("distribution", "How each message reaches the destinations: BROADCAST (absent), ANYCAST or "
                                     "ROUND_ROBIN"),
                text("description", "What the channel carries"),
            ])
        ))
        HasModule = named("Interactions.HasModule", "library", "module", "The library's modules, by name")
        HasInterface = named("Interactions.HasInterface", "module", "intf", "A module's interfaces, by name")
        HasPort = named("Interactions.HasPort", "intf", "port", "An interface's ports, by name")
        Implements = of("Interactions.Implements", "impl", "module", "The module an implementation realizes")
        Instantiates = of("Interactions.Instantiates", "instance", "module", "The module an instance is of")
        HasInstance = named("Interactions.HasInstance", "impl", "instance", "An implementation's instances, by name")
        HasChannel = named("Interactions.HasChannel", "impl", "channel", "An implementation's channels, by name")
        HasSchema = of("Interactions.HasSchema", "channel", "schema", "The schema of a channel's messages")
        Connects = store.Schemas.OfRelation(lambda r: (
            r
            .name("Interactions.Connects")
            .description("Attaches a channel to a port of an interface: an instance's, or, where the implementation "
                         "fills instance, its module's, at its boundary")
            .links([
                lambda t: t.name("channel"),
                lambda t: t.name("instance"),
                lambda t: t.name("intf"),
                lambda t: t.name("port"),
            ])
            .uniques([])  # a set: connecting twice is connecting once
        ))

        def adjacency(name: str, relation: Any, me: str, description: str, owner: bool = False) -> Any:
            return lambda t: t.name(name).relation([relation]).me(me).owner(owner).description(description)

        store.Schemas.OfObject(Library, lambda o: o.adjacencies([
            adjacency("modules", HasModule, "library", "Its modules, by name"),
        ]))
        store.Schemas.OfObject(Module, lambda o: o.adjacencies([
            adjacency("library", HasModule, "module", "The library that has it, and its name there", owner=True),
            adjacency("interfaces", HasInterface, "module", "Its interfaces, by name"),
            adjacency("implementations", Implements, "module", "Its implementations"),
            adjacency("instances", Instantiates, "module", "The instances of it"),
        ]))
        store.Schemas.OfObject(Interface, lambda o: o.adjacencies([
            adjacency("module", HasInterface, "intf", "The module that has it, and its name there", owner=True),
            adjacency("ports", HasPort, "intf", "Its ports, by name"),
            adjacency("connections", Connects, "intf", "The channels attached to it"),
        ]))
        store.Schemas.OfObject(Port, lambda o: o.adjacencies([
            adjacency("interface", HasPort, "port", "The interface that has it, and its name there", owner=True),
            adjacency("connections", Connects, "port", "The channels attached through it"),
        ]))
        store.Schemas.OfObject(Implementation, lambda o: o.adjacencies([
            adjacency("module", Implements, "impl", "The module it realizes"),
            adjacency("instances", HasInstance, "impl", "Its instances, by name"),
            adjacency("channels", HasChannel, "impl", "Its channels, by name"),
            adjacency("connections", Connects, "instance", "Its channels' attachments to its module's interfaces"),
        ]))
        store.Schemas.OfObject(Instance, lambda o: o.adjacencies([
            adjacency("implementation", HasInstance, "instance", "The implementation it is in, and its name there"),
            adjacency("module", Instantiates, "instance", "The module it is of"),
            adjacency("connections", Connects, "instance", "The channels attached to its interfaces"),
        ]))
        store.Schemas.OfObject(Channel, lambda o: o.adjacencies([
            adjacency("implementation", HasChannel, "channel", "The implementation it is in, and its name there"),
            adjacency("message", HasSchema, "channel", "The schema of its messages"),
            adjacency("connections", Connects, "channel", "Where it is attached"),
            adjacency("containers", structure.Contains, "c2", "The soft containers that group it"),
        ]))

    _extend(store, HasSchema)
    return Defined(Library, Module, Interface, Port, Implementation, Instance, Channel, HasModule, HasInterface,
                   HasPort, Implements, Instantiates, HasInstance, HasChannel, HasSchema, Connects)


def _extend(store: Any, HasSchema: Any) -> None:
    """Lets a schema object fill HasSchema's schema link: each meta-schema of a value that lacks it gains an anonymous
    adjacency for it, in one extension of the store."""
    lacking = [meta for meta in (getattr(store.Schemas, kind).as_schema() for kind in MESSAGE_KINDS)
               if not any(a.relation is HasSchema and a.me == "schema" for a in meta.anonymous)]
    if lacking:
        store.extend(lambda s: [
            s.Schemas.OfObject(meta, lambda o: o.adjacencies([lambda t: t.relation([HasSchema]).me("schema")]))
            for meta in lacking
        ])


def _one(adjacency: Any, link: str) -> Any | None:
    """The object `link` of an adjacency's first entry, or None where it has none."""
    return next((getattr(entry, link) for entry in adjacency), None)


def _owned_name(adjacency: Any) -> str | None:
    """The name an object has in its owner, through an adjacency of a named relation."""
    return next((entry.name.get() for entry in adjacency), None)


def module_of(at: Any) -> Any | None:
    """The module an instance is of, or that an implementation realizes; None where it says none."""
    return _one(at.module, "module")


def message_schema(channel: Any) -> Any | None:
    """The schema of a channel's messages, or None where it has none."""
    return _one(channel.message, "schema")


def distribution(channel: Any) -> str:
    """How a channel delivers each message to its destinations: its `distribution`, `"BROADCAST"` where absent."""
    value = channel.distribution.get()
    return BROADCAST if value is None else value


@dataclass(frozen=True)
class End:
    """One attachment of a channel: where it is (an instance, or the implementation for its module's boundary), the
    interface and port, and the end it makes: "source", "destination", or None where the port has no direction."""

    instance: Any
    intf: Any
    port: Any
    role: str | None


def ends(channel: Any) -> list[End]:
    """A channel's attachments, in order, each with the end its port's direction makes it."""
    found = []
    for entry in channel.connections:
        direction = entry.port.direction.get()
        boundary = entry.instance is _one(channel.implementation, "impl")
        role = None
        if direction in DIRECTIONS:
            role = "source" if (direction == "out") != boundary else "destination"
        found.append(End(entry.instance, entry.intf, entry.port, role))
    return found


class Check(Structure.Check):
    """Lists the problems of the architecture reachable from a root: Structure's, where an implementation holds its
    instances and channels hard too, and those of its modules, interfaces, ports, implementations, instances and
    channels that no `unique` clause expresses."""

    def hard_containers(self, obj: Any) -> list[Any]:
        """Structure's, and the implementation an instance or a channel is in."""
        return [*super().hard_containers(obj), *(entry.impl for entry in obj.implementation)]

    def label(self, obj: Any) -> str:
        """An Interactions object with a path by its schema and path (`Interactions.Port 'Pipeline.readings.out'`);
        anything else as Structure names it."""
        dotted = path(obj)
        return f"{obj.as_schema().name} {dotted!r}" if dotted is not None else super().label(obj)

    def problems(self, obj: Any) -> list[str]:
        """Structure's problems of one object, and its own as an Interactions object."""
        found = super().problems(obj)
        kind = _kind(obj)
        if kind == "Port" and obj.direction.get() not in DIRECTIONS:
            found.append(f"{self.label(obj)} has no direction: give it 'in' or 'out'")
        if kind == "Implementation" and module_of(obj) is None:
            found.append(f"{self.label(obj)} implements no module")
        if kind == "Instance":
            if module_of(obj) is None:
                found.append(f"{self.label(obj)} is of no module")
            if _one(obj.implementation, "impl") is None:
                found.append(f"{self.label(obj)} is in no implementation")
            named = _owned_name(obj.implementation)
            if obj.name.get() is not None and named is not None and obj.name.get() != named:
                found.append(f"{self.label(obj)} is named {obj.name.get()!r} as a container, not {named!r}")
        if kind == "Channel":
            found.extend(self._channel(obj))
        return found

    def _channel(self, channel: Any) -> list[str]:
        """A channel's problems: its schema, its distribution, and each attachment."""
        found = []
        me = self.label(channel)
        impl = _one(channel.implementation, "impl")
        if impl is None:
            found.append(f"{me} is in no implementation")
        if message_schema(channel) is None:
            found.append(f"{me} carries messages of no schema")
        if distribution(channel) not in DISTRIBUTIONS:
            found.append(f"{me} distributes {distribution(channel)!r}, not one of {', '.join(DISTRIBUTIONS)}")
        attached = ends(channel)
        for end in attached:
            at = end.instance
            if impl is not None and at is not impl and _one(at.implementation, "impl") is not impl:
                found.append(f"{me} is attached to {self.label(at)}, outside its implementation")
            module = module_of(at)
            if module is not None and not any(entry.intf is end.intf for entry in module.interfaces):
                found.append(f"{me} is attached to {self.label(end.intf)}, not an interface of {self.label(module)}")
            if not any(entry.port is end.port for entry in end.intf.ports):
                found.append(f"{me} is attached through {self.label(end.port)}, not a port of {self.label(end.intf)}")
        roles = {end.role for end in attached}
        if None not in roles:  # where a port gives no direction, its port's own problem says so
            for role in ("source", "destination"):
                if role not in roles:
                    found.append(f"{me} has no {role}")
        return found


_OWNERS = {"Module": ("library", "library"), "Interface": ("module", "module"), "Port": ("interface", "intf"),
           "Instance": ("implementation", "impl"), "Channel": ("implementation", "impl")}
"""Each named kind's adjacency to its owner, and the owner's link: its name is that entry's."""


def path(obj: Any) -> str | None:
    """An Interactions object's dotted name: a module's own (`Pipeline`), an interface's or port's below it
    (`Pipeline.readings.out`), an implementation's own (`reference`), an instance's or channel's below it
    (`reference.sensor`); None where a name on the way is missing, and for anything else."""
    kind = _kind(obj)
    if kind == "Implementation":
        return obj.name.get()
    if kind not in _OWNERS:
        return None
    adjacency, link = _OWNERS[kind]
    name, owner = _owned_name(getattr(obj, adjacency)), _one(getattr(obj, adjacency), link)
    if name is None or kind == "Module":
        return name
    above = path(owner)
    return None if above is None else f"{above}.{name}"


_KINDS = ("Library", "Module", "Interface", "Port", "Implementation", "Instance", "Channel")


def _kind(obj: Any) -> str | None:
    """Which Interactions object schema `obj` is of, through refinements; None for any other."""
    schema = obj.as_schema()
    while schema is not None:
        module, _, local = (schema.name or "").rpartition(".")
        if module == "Interactions" and local in _KINDS:
            return local
        schema = schema.refines  # the one schema it refines, or None
    return None
