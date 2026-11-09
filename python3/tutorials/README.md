<!-- nav -->
[← mbse-sysarch](../../README.md) · [A module and its interfaces →](01_A_Module_And_Its_Interfaces.ipynb)

# Python tutorial

Four case studies, each a notebook that runs top to bottom and builds on the one before. They assume the basics of
[mbse-schemas](https://github.com/pitaman71/mbse-schemas/blob/main/python3/tutorials/README.md): a store,
transactions, and builders that take a callback.

| Notebook | You learn |
|---|---|
| [A module and its interfaces](01_A_Module_And_Its_Interfaces.ipynb) | Defining the schemas in your store; the library that owns every module by name; interfaces and ports, and each port's direction; paths, and finding a part by them; growing a module |
| [Implementing a module](02_Implementing_A_Module.ipynb) | Message schemas; an implementation, its instances and channels; attaching channels to ports, at instances and at the boundary; sources and destinations; how a message reaches several destinations |
| [Organizing a design](03_Organizing_A_Design.ipynb) | Hard containment (structure) and soft containment (organization); soft containers along axes; overlapping groupings; what a soft container may hold |
| [Checking and saving](04_Checking_And_Saving.ipynb) | What `Validators.Validate` reports and what `Interactions.Check` does; reading and fixing problems; saving a design as a snapshot, and loading it into another store |

---

<!-- nav -->
[← mbse-sysarch](../../README.md) · [A module and its interfaces →](01_A_Module_And_Its_Interfaces.ipynb)
