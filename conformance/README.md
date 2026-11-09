<!-- nav -->
[← System architecture and interaction models](../docs/SYSARCH.md) · [Home](../README.md) · [Python package →](../python3/README.md)

# Conformance corpus

`python3/` holds each example architecture's store snapshot, as JSON, written by
`uv run python -m mbse.Architecture.Systems.Conformance.write` from the cases in
`python3/mbse/Architecture/Systems/Conformance/Corpus.py`. CONF-01 checks that the committed snapshots are current,
and CONF-02 that each reads back, valid, into a store and writes the same text.

A snapshot holds the schemas the architecture uses and everything the library reaches. Once a TypeScript
implementation exists, its corpus, in `typescript5/`, will be compared with this one byte for byte
(mbse-basis C-001).

| Case | What it holds |
|---|---|
| `pipeline` | The example pipeline: four modules, one implementation of three instances and two channels of `dsp.Sample`s, one attached at the boundary, and two soft containers along one axis |

---

<!-- nav -->
[← System architecture and interaction models](../docs/SYSARCH.md) · [Home](../README.md) · [Python package →](../python3/README.md)
