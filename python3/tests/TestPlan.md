<!-- nav -->
[← Python package](../README.md) · [Home](../../README.md)

# Test plan

One suite per notebook; each case is a markdown cell `## ID · title` followed by one code cell. `support.py` holds
the shared helpers (`raises`, and `same`, which compares lists of objects by identity). Most suites start from the
example pipeline, `mbse.Architecture.Systems.Examples.Pipeline`.

| Notebook | Suite | Cases | Covers |
|---|---|---|---|
| `01_Structure.ipynb` | STR | 5 | The schemas `define` builds (names, members, descriptions, validity), once, and a store whose names are partly taken refused; hard containment (a set, `hard_containers`, `is_soft`, `organizer`), a second hard container, a cycle and what lies below it; soft containers (several holding one object, one nested in another, a member its hard container lacks, Organizes' unique clause); axes orienting soft containers, one on a container nothing organizes, Orients' unique clause; problems naming unnamed objects by their place in what is reached |
| `02_Interactions.ipynb` | INT | 5 | The schemas `define` builds after Structure's, their members, refinements, the library singleton, which adjacencies own, the meta-schemas extended once each, a store whose names are partly taken refused; modules in the library, interfaces and ports by name, read back, found by path, dotted names, a module outside the library refused, HasInterface's unique clause; implementations and instances, `module_of`, names and paths, an unnamed implementation, Instantiates' unique clause; message schemas of every value kind, a relation refused, `message_schema` and `distribution` with and without; `ends` and their roles, at instances, at the boundary both ways, and through a port without a direction |
| `03_Checks.ipynb` | CHK | 5 | The pipeline without problems, from several roots, and labels; ports without a direction, instances of no module, in no implementation, or named twice, and implementations of no module, named or not; channels of no schema, an unknown distribution, attached outside their implementation, to an interface or through a port that is not their instance's, without a source or a destination, in no implementation, attached nowhere; Structure's problems where an implementation holds its instances hard; a schema refining Interactions' checked and named as its own |
| `04_Serialization.ipynb` | SER | 3 | A snapshot read into a bare store, the extension `define` adds after, byte-identical; into a store that defined the schemas first; YAML; a reachable document's owned objects by path and counted ones whole, read into the same store and refused by one without the modules |
| `05_Conformance.ipynb` | CONF | 2 | The committed corpus current; each snapshot read back, valid, writing the same text |
| `06_Skill.ipynb` | SKL | 3 | The packaged skill current; its complete programs run; every link in the agent guides resolves |

Total: 23 cases.

## Not testable yet

The TypeScript implementation, and cross-language conformance. Choosing an implementation for an instance, and
elaborating a design into its tree of instances (docs/SYSARCH.md, Open questions).

---

<!-- nav -->
[← Python package](../README.md) · [Home](../../README.md)
