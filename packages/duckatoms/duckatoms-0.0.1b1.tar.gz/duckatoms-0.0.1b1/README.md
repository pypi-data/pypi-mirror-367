# 🦆⚛️ DuckAtoms

**Fast, flexible databases for atomic structures with minimal SQL**

[![Python](https://img.shields.io/badge/python-3.11+-blue.svg)](https://python.org)
[![DuckDB](https://img.shields.io/badge/powered%20by-DuckDB-yellow.svg)](https://duckdb.org)

DuckAtoms helps you to efficiently store and analyze your growing collection of
atomic structures with a [DuckDB](https://duckdb.org) database. The database is
structured to allow you to add custom per-structure or per-atom properties such
as MACE embeddings, SOAP vectors, etc., which are challenging to manage with a
standard ASE database. In essence this package bridges ASE's familiar interface
to DuckDB's analytical speed.

## ✨ Key Features

- **Fast**: DuckDB is [one of the fastest
databases](https://github.com/duckdblabs/db-benchmark) for single-node
environments
- **SQL Queryable**: All per-structure and per-atom properties are directly
accessible via SQL
- **Flexible Storage**: Store data as numbers, arrays, text and any other type
DuckDB has to offer
- **Seamless Integration**: Native ASE Atoms compatibility, with the ability
to define custom conversions
- **Scalable**: Handle thousands to millions of structures efficiently
- **Future Plans**: Including vector similarity search
using either the [VSS](https://duckdb.org/docs/extensions/vss.html) or
[FAISS](https://duckdb.org/community_extensions/extensions/faiss.html) -
extension.

## 🚀 Quick Start

```python
from ase import Atoms
from duckatoms import Factory, DB

# Create a new database
factory = Factory("my_structures.duckdb")
factory.add_property("structures", "energy", "DOUBLE")
factory.add_property("atoms", "mace", "DOUBLE[128]")

# Add your atomic structures
db = DB("my_structures.duckdb")
structures = [atoms1, atoms2, atoms3]  # Your ASE Atoms objects
db.add_structures(structures)

mace_descriptors = {1: mace1, 2: mace2, 3: mace3}
db.update_atom_properties('mace', mace_descriptors) # Your mace descriptors

# Query with SQL - get lowest energy structures
high_energy_atoms = db.sql("""
    SELECT id
    FROM structures
    ORDER BY energy
    LIMIT 10;
""").atoms()

# Query with SQL - obtain specific descriptors and keep track of their indices
mace_df = db.sql("""
    SELECT id, structure_id, mace
    FROM atoms
    WHERE number == 44 and z > 6 -- Ru atoms above 6 Angstrom in z direction.
""").df()
```

For further details check out the
[documentation](https://duckatoms-718d8e.gitlab.io/).

## 📦 Installation

### Using pip
```bash
pip install duckatoms
```

### Development Installation
```bash
git clone https://gitlab.com/cedhan/duckatoms.git
cd duckatoms

# Install with development dependencies (for contributors)
poetry install --with dev,docs
```

## FAQ
### How is the data stored?
The data managed by this package is inserted into a DuckDB database, which
contains a *structures* and a *atoms* table. When you add an atomic structure
to the database, all structure related data, like the cell vectors or pbc, are
stored in the *structures* table. The position of each atom, its atomic number
and other single atom properties are stored in the *atoms* table. To both
tables, you can add arbitrary columns to store custom data.

### Why not use an ASE database?
* Many properties of atomic structures, such as positions, forces, etc. are
  saved in a binary format (BLOB), which does not allow to query them
  directly with SQL. DuckAtoms prevents this by using a database that can
  handle the storage of numbers, arrays and more without using a not readable
  binary format and still maintain its speed.
* DuckDB allows state of the art (fast) column first analytics.
* Once queried the most interesting properties, you can transform them to
  numpy.arrays and pandas.DataFrames
* DuckDB is serverless and thus there is no need to set up a server

### I've never used SQL before, where can I start?
Taking a very basic introduction, like [sqlbolt](https://sqlbolt.com/) offers
it for free, should suffice for most queries.

## Architecture
* **Type Safety**: Pydantic models ensure data validation and type checking
