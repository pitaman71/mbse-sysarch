"""Structure: containers, and how they contain one another, hard or soft.

A *container* (`Structure.Container`) holds what it contains through `Structure.Contains(c1, c2)`: `c1` contains `c2`.
Whether that containment is hard or soft depends on `c1` (docs/SYSARCH.md, Resolved, 3): a container that some
container *organizes* (`Structure.Organizes(hard, soft)`) is a *soft container*, and what it contains it contains
softly; any other container contains hard. Hard containment is structure: an object has at most one hard container,
and none contains itself. Soft containment is organization: a soft container groups, inside the one hard container
that organizes it, what that hard container holds, and an object may sit in several soft containers at once. An
*axis* (`Structure.Axis`) is a direction of organization, and orients (`Structure.Orients(axis, soft_container)`) the
soft containers that lie along it: rows along one axis, columns along another.

`define(store)` builds these schemas in a store; `Check()(root)` lists the problems of the structure reachable from
`root` that the relations' `unique` clauses cannot express.
"""

from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass, fields
from typing import Any

from mbse.Schemas.Framework import Reachable

__all__ = ["Check", "Defined", "define", "hard_containers", "is_soft", "organizer"]


@dataclass(frozen=True)
class Defined:
    """The Structure schemas, as `define` built them in one store."""

    Container: Any
    Axis: Any
    Contains: Any
    Organizes: Any
    Orients: Any


def _registered(store: Any, names: type, module: str) -> Any | None:
    """The schemas `define` built in `store` before, or None where it built none; refuses a store holding some only."""
    found = {}
    for f in fields(names):
        try:
            found[f.name] = store.registered(f"{module}.{f.name}")
        except LookupError:
            pass
    if not found:
        return None
    if len(found) < len(fields(names)):
        missing = sorted(f"{module}.{f.name}" for f in fields(names) if f.name not in found)
        raise ValueError(f"the store holds some of the {module} schemas but not {', '.join(missing)}: "
                         "its names are taken")
    return names(**found)


def define(store: Any) -> Defined:
    """Builds the Structure schemas in `store`, in a transaction of their own, and gives them; a store that holds them
    already gives the ones it holds. Call it outside any transaction."""
    held = _registered(store, Defined, "Structure")
    if held is not None:
        return held
    Text = store.Schemas.OfStr

    def text(name: str, description: str) -> Callable[[Any], Any]:
        return lambda t: t.name(name).schema([Text]).description(description)

    with store.transaction():
        Container = store.Schemas.OfObject(lambda o: (
            o
            .name("Structure.Container")
            .ref(True)
            .description("Holds what it contains, hard or soft: soft where some container organizes it")
            .properties([text("name", "The container's name"), text("description", "What the container is for")])
        ))
        Axis = store.Schemas.OfObject(lambda o: (
            o
            .name("Structure.Axis")
            .ref(True)
            .description("A direction of organization, along which soft containers lie")
            .properties([text("name", "The axis's name"), text("description", "What the axis orders")])
        ))
        Contains = store.Schemas.OfRelation(lambda r: (
            r
            .name("Structure.Contains")
            .description("c1 contains c2: softly where c1 is a soft container, otherwise hard")
            .links([lambda t: t.name("c1"), lambda t: t.name("c2")])
            .uniques([])  # a set: containing twice is containing once
        ))
        Organizes = store.Schemas.OfRelation(lambda r: (
            r
            .name("Structure.Organizes")
            .description("Makes soft a soft container inside the hard container hard")
            .links([lambda t: t.name("hard"), lambda t: t.name("soft")])
            .uniques("hard")  # a soft container lies in one hard container
        ))
        Orients = store.Schemas.OfRelation(lambda r: (
            r
            .name("Structure.Orients")
            .description("The soft container lies along the axis")
            .links([lambda t: t.name("axis"), lambda t: t.name("soft_container")])
            .uniques("axis")  # a soft container lies along one axis
        ))
        store.Schemas.OfObject(Container, lambda o: o.adjacencies([
            lambda t: t.name("contents").relation([Contains]).me("c1").description("What it contains"),
            lambda t: t.name("containers").relation([Contains]).me("c2").description("The containers that contain it"),
            lambda t: t.name("organizes").relation([Organizes]).me("hard").description("Its soft containers"),
            lambda t: t.name("organizer").relation([Organizes]).me("soft").description("The hard container it lies in"),
            lambda t: t.name("axis").relation([Orients]).me("soft_container").description("The axis it lies along"),
        ]))
        store.Schemas.OfObject(Axis, lambda o: o.adjacencies([
            lambda t: t.name("orients").relation([Orients]).me("axis").description("The soft containers along it"),
        ]))
    return Defined(Container, Axis, Contains, Organizes, Orients)


def organizer(container: Any) -> Any | None:
    """The hard container that organizes `container`, or None where none does."""
    return next((entry.hard for entry in container.organizer), None)


def is_soft(container: Any) -> bool:
    """Whether `container` is a soft container: one that some container organizes."""
    return organizer(container) is not None


def hard_containers(obj: Any) -> list[Any]:
    """The containers that contain `obj` hard, through Structure.Contains: those that are not soft."""
    return [entry.c1 for entry in obj.containers if not is_soft(entry.c1)]


class Check:
    """Lists the problems of the structure reachable from a root that no `unique` clause expresses, each a line naming
    the object it is about. A subclass adds containment that other relations declare (`hard_containers`), its own
    problems (`problems`), and its own way of naming objects (`label`)."""

    def __call__(self, root: Any) -> list[str]:
        self._labels: dict[int, str] = {}
        objects = Reachable.of(root)
        for i, obj in enumerate(objects):
            self._labels[id(obj)] = f"{obj.as_schema().name} #{i}"
        found: list[str] = []
        for obj in objects:
            found.extend(self.problems(obj))
        return found

    def hard_containers(self, obj: Any) -> list[Any]:
        """The containers that hold `obj` hard: Structure.Contains', unless a subclass adds others."""
        return hard_containers(obj)

    def label(self, obj: Any) -> str:
        """How a problem names `obj`: its schema and its name, or its schema and its place among the objects reached."""
        name = obj.name.get()  # a schema without a name property reads as absent
        if name is not None:
            return f"{obj.as_schema().name} {name!r}"
        return self._labels.get(id(obj), obj.as_schema().name)

    def problems(self, obj: Any) -> list[str]:
        """The problems of one object."""
        found = []
        parents = self.hard_containers(obj)
        if len(parents) > 1:
            found.append(f"{self.label(obj)} has {len(parents)} hard containers, "
                         f"{', '.join(self.label(p) for p in parents)}: an object has at most one")
        if self._contains_itself(obj):
            found.append(f"{self.label(obj)} contains itself, hard")
        hard = organizer(obj)
        if hard is None and any(True for _ in obj.axis):
            found.append(f"{self.label(obj)} lies along an axis, but no container organizes it: only a soft container "
                         "lies along an axis")
        if hard is not None:
            for entry in obj.contents:
                member = entry.c2
                if not any(p is hard for p in self.hard_containers(member)) and organizer(member) is not hard:
                    found.append(f"{self.label(obj)} contains {self.label(member)} softly, but its hard container, "
                                 f"{self.label(hard)}, does not contain it")
        return found

    def _contains_itself(self, obj: Any) -> bool:
        """Whether following hard containers up from `obj` comes back to it."""
        seen: set[int] = set()
        frontier = self.hard_containers(obj)
        while frontier:
            parent = frontier.pop()
            if parent is obj:
                return True
            if id(parent) not in seen:
                seen.add(id(parent))
                frontier.extend(self.hard_containers(parent))
        return False
