"""Pipeline example: a sensor, a filter and a logger, cooperating through channels inside one implementation.

The module `Pipeline` has one interface, `readings`, whose port `out` gives filtered samples to whatever uses the
pipeline. Its implementation, `reference`, instantiates three modules and connects them with two channels: `raw`
carries `dsp.Sample`s from the sensor to the filter, and `filtered` carries `dsp.Sample`s from the filter to the logger
and, at the boundary, out through `readings`. Two soft containers, `acquisition` and `processing`, group the instances
and channels along the axis `dataflow`.

`build(store)` writes it into a store and gives its parts; run as a script, it checks itself.
"""

from __future__ import annotations

from types import SimpleNamespace
from typing import Any

from mbse.Architecture.Systems.Framework import Interactions, Structure

__all__ = ["build", "module", "connect"]


def module(store: Any, name: str, interfaces: dict[str, dict[str, str]]) -> Any:
    """A module in the store's library, under `name`, with interfaces by name, each with ports by name and direction."""
    def interface(ports: dict[str, str]) -> Any:
        return lambda i: i.ports(lambda a: [
            a.insert(lambda e, n=n, d=d: e.name(n).port(lambda p: p.direction(d))) for n, d in ports.items()
        ])

    library = store.singleton("Interactions.Library")
    store.Interactions.Library(library, lambda lib: lib.modules(lambda a: a.insert(lambda e: e.name(name).module(
        lambda m: m.interfaces(lambda a: [
            a.insert(lambda e, n=n, p=p: e.name(n).intf(interface(p))) for n, p in interfaces.items()
        ])
    ))))
    return library.modules.at(name).module


def connect(store: Any, channel: Any, at: Any, intf: str, port: str) -> None:
    """Attaches `channel` to the port `port` of the interface `intf` of `at`'s module: an instance's, or the
    implementation's own module's, at its boundary."""
    interface = Interactions.module_of(at).interfaces.at(intf).intf
    store.Interactions.Channel(channel, lambda c: c.connections(lambda a: a.insert(
        lambda e: e.instance(at).intf(interface).port(interface.ports.at(port).port))))


def build(store: Any) -> SimpleNamespace:
    """Writes the pipeline into `store`, defining the Interactions schemas first where it lacks them, and gives its
    parts by name."""
    schemas = Interactions.define(store)
    structure = Structure.define(store)
    with store.transaction():
        Sample = store.Schemas.OfObject(lambda o: o.name("dsp.Sample").description("One reading").properties([
            lambda t: t.name("time").schema([store.Schemas.OfFloat]).description("Seconds since start"),
            lambda t: t.name("value").schema([store.Schemas.OfFloat]),
        ]))
    with store.transaction():
        sensor = module(store, "Sensor", {"samples": {"tx": "out"}})
        filter_ = module(store, "Filter", {"samples": {"rx": "in"}, "filtered": {"tx": "out"}})
        logger = module(store, "Logger", {"records": {"rx": "in"}})
        pipeline = module(store, "Pipeline", {"readings": {"out": "out"}})
        def of(m: Any) -> Any:
            return lambda i: i.module(lambda a: a.insert(lambda e: e.module(m)))

        def carrying(schema: Any) -> Any:
            return lambda c: c.message(lambda a: a.insert(lambda e: e.schema(schema)))

        impl = store.Interactions.Implementation(lambda x: (
            x
            .name("reference")
            .module(lambda a: a.insert(lambda e: e.module(pipeline)))
            .instances(lambda a: (
                a
                .insert(lambda e: e.name("sensor").instance(of(sensor)))
                .insert(lambda e: e.name("filter").instance(of(filter_)))
                .insert(lambda e: e.name("logger").instance(of(logger)))
            ))
            .channels(lambda a: (
                a
                .insert(lambda e: e.name("raw").channel(carrying(Sample)))
                .insert(lambda e: e.name("filtered").channel(lambda c: carrying(Sample)(c.distribution("BROADCAST"))))
            ))
        ))
        instance = {name: impl.instances.at(name).instance for name in ("sensor", "filter", "logger")}
        channel = {name: impl.channels.at(name).channel for name in ("raw", "filtered")}
        connect(store, channel["raw"], instance["sensor"], "samples", "tx")
        connect(store, channel["raw"], instance["filter"], "samples", "rx")
        connect(store, channel["filtered"], instance["filter"], "filtered", "tx")
        connect(store, channel["filtered"], instance["logger"], "records", "rx")
        connect(store, channel["filtered"], impl, "readings", "out")

        dataflow = store.Structure.Axis(lambda a: a.name("dataflow").description("From the sensor to the readings"))
        sections = {}
        for name, members in (("acquisition", [instance["sensor"], channel["raw"]]),
                              ("processing", [instance["filter"], instance["logger"], channel["filtered"]])):
            sections[name] = store.Structure.Container(lambda c, name=name, members=members: (
                c
                .name(name)
                .organizer(lambda a: a.insert(lambda e: e.hard(impl)))
                .axis(lambda a: a.insert(lambda e: e.axis(dataflow)))
                .contents(lambda a: [a.insert(lambda e, m=m: e.c2(m)) for m in members])
            ))
    return SimpleNamespace(schemas=schemas, structure=structure, Sample=Sample, sensor=sensor, filter=filter_,
                           logger=logger, pipeline=pipeline, impl=impl, instance=instance, channel=channel,
                           dataflow=dataflow, sections=sections)


if __name__ == "__main__":
    from mbse.Schemas.Framework import Builders, JSON, Validators

    store = Builders.Store()
    p = build(store)
    assert Interactions.Check()(p.pipeline) == []
    assert Validators.Validate(store).Reachable(p.schemas.Module, p.pipeline) == []
    assert [end.role for end in Interactions.ends(p.channel["filtered"])] == ["source", "destination", "destination"]
    text = JSON.ToJSON(store).Snapshot()  # the library reaches every part: the store's snapshot holds them all
    copy = Builders.Store()
    JSON.FromJSON(copy).Snapshot(text)
    Interactions.define(copy)  # the schemas came with the snapshot; this extends the meta-schemas they rely on
    assert JSON.ToJSON(copy).Snapshot() == text
    print("Pipeline: all checks passed")
