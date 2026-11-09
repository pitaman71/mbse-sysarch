# Guide for AI agents

mbse-sysarch models system architectures as [mbse-schemas](https://github.com/pitaman71/mbse-schemas) data, in two
packages of schemas that `define(store)` builds in a caller's store. **Interactions** has modules in the store's
library, their interfaces and ports, and implementations whose instances exchange messages over channels.
**Structure** has containers, hard and soft, and axes. Checks list what no `unique` clause can express. One
implementation exists: `python3/` (`mbse.Architecture.Systems`). TypeScript is planned.

## Start here

| You want to | Read |
|---|---|
| Know why the mbse repositories exist, and this one's part in them | [MBSE.md in mbse-basis](https://github.com/pitaman71/mbse-basis/blob/main/MBSE.md) |
| Use the library: model a module, implement it, check and save it | [skills/mbse-sysarch/SKILL.md](skills/mbse-sysarch/SKILL.md), a skill. It loads its references only as needed |
| Learn it by example | [python3/tutorials/README.md](python3/tutorials/README.md), four case studies |
| Understand a design decision or an open question | [docs/SYSARCH.md](docs/SYSARCH.md) |
| Find or add a test case | [python3/tests/TestPlan.md](python3/tests/TestPlan.md) |
| Model the data underneath | [mbse-schemas' AGENTS.md](https://github.com/pitaman71/mbse-schemas/blob/main/AGENTS.md), in the sibling checkout |

## Invariants when changing code

- **One vocabulary across the mbse repositories.** A kind's or schema's named members are *properties*, never
  "fields", and what describes a value is its *schema*, never its "type" (mbse-basis V-026). What a specification
  requires is a *constraint*, never a "rule". Terms collide here more than anywhere: a SysML *port*, a Verilog
  `module`, a Go *channel*, a UML *interface*. Wherever ours meets another's, in docs and examples, qualify the
  colliding term with whose it is. Our relation `Interactions.HasSchema` is always written qualified, beside
  mbse-schemas' meta relation `Schemas.HasSchema`.
- **The README opens with why.** Its first paragraph says, TL;DR style, why this repository exists, in the terms of
  MBSE.md; what it is comes after. Keep that opening true as the repository changes.
- **Every human-facing document has navigation.** After adding, renaming or retitling one, run
  `python3 ../mbse-basis/scripts/update_doc_links.py`. Link text is human-readable, never a path.
- **Schemas are built in the caller's store.** `Structure.define(store)` and `Interactions.define(store)` build them
  outside any transaction, and give back what the store holds when called again. Never build a schema outside a store,
  and never link another store's.
- **What a `unique` clause can say, the schema says**; checks (`Structure.Check`, `Interactions.Check`) list only what
  it cannot, each problem a line naming the object by its schema and path, all of them, never stopping at the first.
- **Tutorials are tested too.** `pytest` runs `tutorials/` beside `tests/`. Re-execute a tutorial after a change that
  alters its output, and commit it with its outputs.
- **Tests are Jupyter notebooks**, one suite per notebook. Each case is a markdown cell `## ID · title` followed by
  one code cell. Notebooks are JSON written with `indent=1`, `sort_keys=True` and `ensure_ascii=False`, each cell with
  an `id`.
- **Coverage is 100%**, statements and branches. Close a gap with an assertion in a case.
- **The corpus is current.** After a change to what the package writes, run
  `uv run python -m mbse.Architecture.Systems.Conformance.write`, review the diff, and commit it; CONF-01 fails until
  then.
- **The skill is packaged with the implementation.** After editing `skills/mbse-sysarch/`, run `skills/sync.sh`;
  SKL-01 fails until the copies match. Every fenced block tagged `python` in the skill is a complete program that
  SKL-02 runs; tag fragments `python fragment`.
- **Behavior is decided in `docs/SYSARCH.md`.** Record a decision the user makes under Resolved, completely and as
  the user decided it; a decision an agent makes goes there too, marked as the agent's, for the user to confirm. Put
  what stays undecided under Open questions.

## Commands

```sh
python3 ../mbse-basis/scripts/polyrepo.py clone   # mbse-schemas, beside this repository, pinned
python3 ../mbse-basis/scripts/polyrepo.py check   # the siblings are present and compatible with siblings.json
cd python3 && uv sync --all-extras                # use uv, never pip
uv run coverage run -m pytest && uv run coverage combine && uv run coverage report
uv run python -m mbse.Architecture.Systems.Conformance.write
uv run python -m mbse.Architecture.Systems.Examples.Pipeline
```

## Related repositories

- [mbse-schemas](https://github.com/pitaman71/mbse-schemas): the data, its stores and their validation. A sibling
  checkout, `../mbse-schemas`, pinned by version and commit in `siblings.json` (see mbse-basis'
  `scripts/polyrepo.py`).
- [mbse-basis](https://github.com/pitaman71/mbse-basis): the shared features, principles, capabilities and
  vocabulary this repository cites, and the tools it runs.
