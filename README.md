<!-- nav -->
[Python tutorial →](python3/tutorials/README.md)

# mbse-sysarch

An executable specification has to say what a system is made of before it can constrain how the parts behave. Which
components exist, where each meets the others, and which messages flow between them are the decisions an architecture
records, and today they live in diagrams that no program can check. mbse-sysarch states them once, as mbse-schemas
data, so the architecture can be checked, saved, compared and later generated from like any other part of the
specification.

It defines two packages of schemas, built in your store. **Interactions** covers modules, kept by name in the store's
library, with their interfaces and ports. It also covers implementations of a module: instances of other modules
cooperating asynchronously over channels, each channel carrying messages of one schema from its sources to its
destinations. **Structure** covers containers, which hold their contents hard (structure) or soft (organization), and
the axes that soft containers lie along. Checks report what the schemas' own constraints cannot express: a channel
without a source, an attachment to an interface the instance lacks, a soft container grouping something from
elsewhere.

Python only for now (`mbse.Architecture.Systems`), on [mbse-schemas](https://github.com/pitaman71/mbse-schemas) 0.22.0.

```python
from mbse.Schemas.Framework import Builders
from mbse.Architecture.Systems.Examples import Pipeline
from mbse.Architecture.Systems.Framework import Interactions

store = Builders.Store()
p = Pipeline.build(store)                     # a sensor, a filter and a logger, over two channels
for end in Interactions.ends(p.channel["filtered"]):
    print(end.role, Interactions.path(end.port))
print(Interactions.Check()(p.pipeline))       # []
```

## Where to go next

| You want to | Read |
|---|---|
| Know why the mbse repositories exist, and each one's part | [MBSE.md in mbse-basis](https://github.com/pitaman71/mbse-basis/blob/main/MBSE.md) |
| Learn it by example, from one module to a saved design | [the Python tutorial](python3/tutorials/README.md), four case studies |
| Use it, or have an agent use it | [the skill](skills/mbse-sysarch/SKILL.md) |
| Understand a decision, or what is still open | [the design](docs/SYSARCH.md) |
| Change it | [AGENTS.md](AGENTS.md) |

## Getting started

```sh
git clone git@github.com:pitaman71/mbse-basis.git
git clone git@github.com:pitaman71/mbse-sysarch.git
cd mbse-sysarch
python3 ../mbse-basis/scripts/polyrepo.py clone    # mbse-schemas, beside it, at its pinned commit
cd python3 && uv sync --all-extras
uv run coverage run -m pytest && uv run coverage combine && uv run coverage report
```

---

<!-- nav -->
[Python tutorial →](python3/tutorials/README.md)
