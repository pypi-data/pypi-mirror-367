import duckdb
from ase import Atoms
from pathlib import Path
from pydantic import validate_call
import pandas as pd
from typing import Any

from .converter import AtomsToDB, BaseAtomsToDB, DBToAtoms, BaseDBToAtoms


class QueryResult:
    """Wrapper class for DuckDB query results that enables method chaining.

    Uses lazy evaluation with context managers for robust resource management.
    Queries execute only when conversion methods (.df(), .atoms(), etc.) are
    called, or when __repr__ is called for display. Each operation uses its own
    connection to guarantee cleanup and exception safety."""

    @validate_call
    def __init__(
        self,
        db_file: Path,
        query: str,
        parameters: dict[str, Any] | list | None = None,
        db_instance=None,  # Remove type hint to avoid forward reference
    ):
        # Manual validation for db_instance
        if db_instance is not None and not isinstance(db_instance, DB):
            raise TypeError("db_instance must be a DB instance or None")

        self._db_file = db_file
        self._query = query
        self._parameters = parameters
        self._db_instance = db_instance

    def __repr__(self):
        """Return string representation by executing query."""
        with duckdb.connect(self._db_file) as con:
            return str(con.sql(self._query, params=self._parameters))

    def atoms(self) -> list[Atoms]:
        """Convert query result to Atoms objects. Only works for structures table queries."""
        if self._db_instance is None:
            raise ValueError("DB instance not available. Cannot convert to atoms.")

        # Execute query and get DataFrame
        result_df = self.df()

        # Check if query contains 'atoms' table name (safety check)
        if "atoms" in self._query.lower() and "structures" not in self._query.lower():
            raise ValueError(
                "Cannot convert atoms table query to atoms objects. Only structures table queries are supported."
            )

        # Extract structure IDs assuming the query is from structures table
        if "id" not in result_df.columns:
            raise ValueError(
                "Query result must include 'id' column to convert to atoms."
            )

        structure_ids = result_df["id"].tolist()
        return self._db_instance.get_atoms(structure_ids)

    def df(self) -> pd.DataFrame:
        """Convert query result to pandas DataFrame."""
        with duckdb.connect(self._db_file) as con:
            return con.sql(self._query, params=self._parameters).df()

    def fetchall(self) -> list:
        """Convert query result to Python objects."""
        with duckdb.connect(self._db_file) as con:
            return con.sql(self._query, params=self._parameters).fetchall()

    def fetchnumpy(self):
        """Convert query result to numpy arrays."""
        with duckdb.connect(self._db_file) as con:
            return con.sql(self._query, params=self._parameters).fetchnumpy()

    def arrow(self):
        """Convert query result to Arrow table."""
        with duckdb.connect(self._db_file) as con:
            return con.sql(self._query, params=self._parameters).arrow()

    def pl(self):
        """Convert query result to Polars DataFrame."""
        with duckdb.connect(self._db_file) as con:
            return con.sql(self._query, params=self._parameters).pl()


class DB:
    @validate_call(config={"arbitrary_types_allowed": True})
    def __init__(
        self,
        db_file: Path | str,
        writer: AtomsToDB | None = None,
        reader: DBToAtoms | None = None,
    ):
        self._db_file = self._validate_db_path(db_file)
        self._check_db_validity()

        self._writer = writer if writer is not None else BaseAtomsToDB()
        self._reader = reader if reader is not None else BaseDBToAtoms()

    def __repr__(self) -> str:
        return f"DB('{self._db_file}')"

    @staticmethod
    def _validate_db_path(path: Path | str) -> Path:
        """Validate database file path and extension."""
        db_file = Path(path)
        if db_file.suffix not in {".db", ".duckdb"}:
            raise ValueError(
                f"Database file must have .db or .duckdb extension, got: {db_file.suffix}"
            )
        return db_file

    @property
    def db_file(self) -> Path:
        """Database file path (read-only after initialization)."""
        return self._db_file

    @property
    def reader(self) -> DBToAtoms:
        """Database-to-atoms converter (mutable)."""
        return self._reader

    @reader.setter
    @validate_call(config={"arbitrary_types_allowed": True})
    def reader(self, reader: DBToAtoms) -> None:
        self._reader = reader

    @property
    def writer(self) -> AtomsToDB:
        """Atoms-to-database converter (mutable)."""
        return self._writer

    @writer.setter
    @validate_call(config={"arbitrary_types_allowed": True})
    def writer(self, writer: AtomsToDB) -> None:
        self._writer = writer

    def _check_db_validity(self):
        """
        Checks if the database contains required tables with (basic) correct
        structure.

        Raises:
            FileNotFoundError: If database file doesn't exist
            ValueError: If database validation fails
        """
        if not self._db_file.exists():
            raise FileNotFoundError(f"Database file does not exist: {self._db_file}")

        # check for required tables
        with duckdb.connect(self._db_file) as con:
            existing_tables = set(con.execute("""show tables""").df().name.to_list())

            required_tables = {"structures", "atoms"}
            missing_tables = required_tables - existing_tables

            if missing_tables:
                raise ValueError(f"Missing required table(s): {missing_tables}")

        # check structures table
        with duckdb.connect(self._db_file) as con:
            try:
                # check required columns and types
                schema_df = con.execute("DESCRIBE structures").df()
                existing_columns = schema_df.set_index(
                    "column_name"
                ).column_type.to_dict()

                required_columns = {
                    "id": "BIGINT",
                    "pbc": "BOOLEAN[3]",
                    "cell": "DOUBLE[9]",
                }

                for expected_name, expected_type in required_columns.items():
                    if expected_name not in existing_columns:
                        raise ValueError(
                            f"Missing column in structures table: {expected_name}"
                        )
                    elif expected_type != existing_columns[expected_name]:
                        raise ValueError(
                            f"Wrong type in {expected_name}-column of structures table: "
                            f"{existing_columns[expected_name]} instead of {expected_type}"
                        )

                # check that 'id' is primary key
                result = schema_df.query("column_name == 'id' and key == 'PRI'")
                if result.empty:
                    raise ValueError("'id' is not primary key in structures table")

            except Exception as e:
                raise ValueError(f"Error validating structures table: {e}") from e

        # check atoms table
        with duckdb.connect(self._db_file) as con:
            try:
                # check required columns and types
                schema_df = con.execute("DESCRIBE atoms").df()
                existing_columns = schema_df.set_index(
                    "column_name"
                ).column_type.to_dict()

                required_columns = {
                    "id": "BIGINT",
                    "structure_id": "BIGINT",
                    "ase_atoms_id": "BIGINT",
                    "number": "BIGINT",
                    "x": "DOUBLE",
                    "y": "DOUBLE",
                    "z": "DOUBLE",
                }

                for expected_name, expected_type in required_columns.items():
                    if expected_name not in existing_columns:
                        raise ValueError(
                            f"Missing column in atoms table: {expected_name}"
                        )
                    elif expected_type != existing_columns[expected_name]:
                        raise ValueError(
                            f"Wrong type in {expected_name}-column of atoms table: "
                            f"{existing_columns[expected_name]} instead of {expected_type}"
                        )

                # check that `id` is primary key
                result = schema_df.query("column_name == 'id' and key == 'PRI'")
                if result.empty:
                    raise ValueError("'id' is not primary key in atoms table")

                # check that `structure_id` is foreign key
                result = con.sql("""
                    SELECT constraint_name, constraint_type
                    FROM information_schema.table_constraints
                    WHERE (table_name LIKE 'atoms') and (constraint_name LIKE
                    'atoms_structure_id_id_fkey');
                    """).df()
                if (
                    not (len(result) == 1)
                    or result.loc[0, "constraint_type"] != "FOREIGN KEY"
                ):
                    raise ValueError(
                        "Atoms table does not use structure_id as foreign key"
                    )

            except Exception as e:
                raise ValueError(f"Error validating database: {e}") from e

    @validate_call
    def _check_columns_exist(self, table_name: str, columns_list: list[str]):
        """Raises ValueError if `table` does not contain given columns.

        Args:
            table (str): table name
            columns (list[str]): to be checked column names
        """
        if table_name not in {"atoms", "structures"}:
            raise ValueError("Table must be in `atoms` and `structures`.")

        columns = set(columns_list)
        try:
            with duckdb.connect(self._db_file) as con:
                # table_name can not be parametrized
                existing_cols = set(
                    con.execute(f"DESCRIBE {table_name}").df().column_name.to_list()
                )
            if not (columns.issubset(existing_cols)):
                raise ValueError(
                    f"Columns: {columns - existing_cols} do not exist in database"
                )

        except Exception as e:
            raise ValueError(
                f"Existing column check failed in table: {table_name} \nError: {e}"
            ) from e

    @validate_call
    def _check_ids_exist(self, table_name: str, ids: list[int]):
        """Raises ValueError if the given ids are not in the specified table.

        Args:
            table_name (str): table name
            ids (list[int]): ids whose existence is checked
        """
        if table_name not in {"atoms", "structures"}:
            raise ValueError("Table must be in `atoms` and `structures`.")

        with duckdb.connect(self._db_file) as con:
            # table_name can not be parametrized
            result = con.execute(
                f"""
                SELECT count(*) == $total_ids
                FROM {table_name}
                WHERE id = ANY($ids)
            """,
                {"total_ids": len(ids), "ids": ids},
            ).fetchone()

            if result is None:
                raise ValueError(f"All given ids are not in table: {table_name}")
            else:
                ids_exist = result[0]

            if not ids_exist:
                raise ValueError(f"Some or all ids are not in table: {table_name}")

    @validate_call(config={"arbitrary_types_allowed": True})
    def add_structures(
        self,
        atoms: Atoms | list[Atoms],
        batch_metadata: dict | None = None,
    ) -> list[int]:
        """
        Adds ase.atoms object(s) (aka structures) to a the database.

        Args:
            atoms: single or multiple atoms objects
            batch_metadata: information for the structures table, which is the
                same for all added atoms objects of this batch. Has to be of
                format: {'<column_name>': <value>}
        Returns:
            ids: structure_ids of the inserted atoms

        """
        insert_atoms = atoms if isinstance(atoms, list) else [atoms]

        if not insert_atoms:
            raise ValueError("No atoms were passed, i.e. only an empty list")

        for i, at in enumerate(insert_atoms):
            if not isinstance(at, Atoms):
                raise TypeError(f"Item {i} is not an Atoms object")
            if len(at) == 0:
                raise ValueError(f"Atoms object {i} is empty")

        # Use converter to create DataFrames
        structures_batch_df, atoms_batch_df = self.writer.convert(
            insert_atoms, batch_metadata
        )

        # check if all columns exist
        self._check_columns_exist(
            table_name="structures", columns_list=structures_batch_df.columns.to_list()
        )
        self._check_columns_exist(
            table_name="atoms",
            columns_list=atoms_batch_df.columns.drop("tmp_structure_id").to_list(),
        )

        # inserting structures from a pd.DataFrame
        with duckdb.connect(self._db_file) as con:
            con.execute("BEGIN TRANSACTION")
            try:
                # insert into structures table and get corresponding ids
                insertion_columns = ", ".join(structures_batch_df.columns.to_list())
                structure_ids_df = con.execute(f"""
                        INSERT INTO structures ({insertion_columns})
                        SELECT {insertion_columns} FROM structures_batch_df
                        RETURNING id
                        """).df()

                structure_ids = structure_ids_df.id.to_list()

                # convert tmp_structure_ids to structure_ids
                temp_id_to_structure_id = dict(
                    zip(atoms_batch_df.tmp_structure_id.unique(), structure_ids)
                )
                atoms_batch_df.loc[:, "structure_id"] = (
                    atoms_batch_df.tmp_structure_id.apply(
                        lambda x: temp_id_to_structure_id[x]
                    )
                )

                # insert into atoms table
                atom_columns = atoms_batch_df.columns.drop("tmp_structure_id").to_list()
                atom_columns = ", ".join(atom_columns)

                con.execute(f"""
                           INSERT INTO atoms ({atom_columns})
                           SELECT {atom_columns} FROM atoms_batch_df
                           """)

                con.execute("COMMIT")
                return structure_ids

            except Exception as e:
                con.execute("ROLLBACK")
                raise ValueError(f"Failed to insert atoms: {e}") from e

    @validate_call
    def remove_structures(self, structure_ids: list[int] | int):
        """
        Remove structure(s), all their associated atoms, and any additional
        custom data corresponding to the structure.

        Note: Due to over-eager foreign key constraint checking in DuckDB, this
        operation can't be wrapped in an error-handling transaction. Thus if an
        unexpected error occurs you the indices could only be deleted in one
        table and an error is raised. There are also no cascading deletes which
        would circumvent this.

        Args:
            structure_ids: single structure_id or list of structure_ids to remove
        """

        if isinstance(structure_ids, int):
            structure_ids = [structure_ids]

        if not structure_ids:
            raise ValueError("The list is empty, no ids were supplied")

        # remove duplicate ids
        structure_ids = list(set(structure_ids))

        self._check_ids_exist(table_name="structures", ids=structure_ids)

        # no better error-handling possible due to over-eager foreign key
        # constraint checking
        with duckdb.connect(self._db_file) as con:
            con.execute(
                """
                    DELETE FROM atoms
                    WHERE structure_id = ANY($ids)
                """,
                {"ids": structure_ids},
            )

            con.execute(
                """
                    DELETE FROM structures
                    WHERE id = ANY($ids)
                """,
                {"ids": structure_ids},
            )

    @validate_call
    def update_structure_properties(
        self, property_name: str, values_dict: dict[int, Any]
    ):
        """
        Update values of a specific property column by corresponding
        structure_id(s).

        Args:
            property_name: name of the property column to update
            values_dict: dictionary mapping structure_id -> value

        Examples:
            # Update energy values for structures 1, 2, and 3
            db.update_structure_properties('energy', {1: -5.2, 2: -5.1, 3: -5.3})

            # Update convergence status for a single structure
            db.update_structure_properties('converged', {1: True})
        """
        if not values_dict:
            raise ValueError("Values dict is empty!")

        structure_ids = list(values_dict.keys())
        property_values = list(values_dict.values())

        batch_df = pd.DataFrame({"id": structure_ids, property_name: property_values})

        self._check_columns_exist(table_name="structures", columns_list=[property_name])
        self._check_ids_exist(table_name="structures", ids=batch_df.id.to_list())

        with duckdb.connect(self._db_file) as con:
            try:
                con.execute("BEGIN TRANSACTION")
                con.execute(f"""
                    UPDATE structures
                    SET {property_name} = batch_df.{property_name}
                    FROM batch_df
                    WHERE structures.id = batch_df.id
                """)

                con.execute("COMMIT")
            except Exception as e:
                con.execute("ROLLBACK")
                raise ValueError(f"Failed to add structure properties: {e}") from e

    @validate_call
    def update_atom_properties(self, property_name: str, values_dict: dict[int, Any]):
        """
        Update property values for specific atoms by atom_id.

        Args:
            property_name: name of the property column to update
            values_dict: dictionary mapping atom_id -> property_value

        Examples:
            # Update charges for specific atoms by their atoms-table IDs
            db.update_atom_properties('charge', {
                10: 0.5,   # Atom ID 10 gets charge 0.5
                11: -0.3,  # Atom ID 11 gets charge -0.3
                12: 0.1    # Atom ID 12 gets charge 0.1
            })
        """
        if not values_dict:
            raise ValueError("Values dictionary cannot be empty")

        atom_ids = list(values_dict.keys())
        property_values = list(values_dict.values())

        # used by duckdb in an SQL statement, other comment for ruff
        batch_df = pd.DataFrame({"id": atom_ids, property_name: property_values})  # noqa: F841

        self._check_columns_exist(table_name="atoms", columns_list=[property_name])
        self._check_ids_exist(table_name="atoms", ids=batch_df.id.to_list())

        with duckdb.connect(self._db_file) as con:
            try:
                con.execute("BEGIN TRANSACTION")
                con.execute(f"""
                    UPDATE atoms
                    SET {property_name} = batch_df.{property_name}
                    FROM batch_df
                    WHERE atoms.id = batch_df.id
                """)

                con.execute("COMMIT")
            except Exception as e:
                con.execute("ROLLBACK")
                raise ValueError(f"Failed to add atom properties: {e}") from e

    @validate_call
    def update_atom_properties_by_structure_id(
        self, property_name: str, structures_dict: dict[int, list[Any]]
    ):
        """
        Changes the values of all atoms of a structure for a specific property
        (column). Also allows to do this for multiple structures in the same
        transaction.

        Args:
            property_name: name of the property column to update
            structure_dict: dictionary mapping structure_id -> list of atom
                property values for all atoms of the structure

        Note: The length and order of the list has to match the number of atoms
            and ase.Atoms ids, respectively.

        Examples:
            # Update magnetic moments for atoms in structures 1 and 2
            # Structure 1 has 3 atoms, structure 2 has 2 atoms
            db.update_atom_properties_by_structure_id('magnetic_moment', {
                1: [1.0, -1.0, 0.5],  # 3 values for 3 atoms in structure 1
                2: [0.2, 0.8]         # 2 values for 2 atoms in structure 2
            })
        """
        if not structures_dict:
            raise ValueError("Values dictionary cannot be empty")

        self._check_columns_exist(table_name="atoms", columns_list=[property_name])
        structure_ids = list(structures_dict.keys())
        self._check_ids_exist(table_name="structures", ids=structure_ids)

        with duckdb.connect(self._db_file) as con:
            try:
                con.execute("BEGIN TRANSACTION")
                # obtain atom_ids + build update_values dict
                values_dict = {}
                for structure_id, atom_values in structures_dict.items():
                    atom_ids = (
                        con.execute(
                            """
                        SELECT id FROM atoms
                        WHERE structure_id = $structure_id
                        ORDER BY ase_atoms_id
                    """,
                            {"structure_id": structure_id},
                        )
                        .df()
                        .id.to_list()
                    )

                    if len(atom_ids) != len(atom_values):
                        raise ValueError(
                            f"Structure {structure_id} has {len(atom_ids)} atoms, "
                            f"but {len(atom_values)} values provided."
                        )

                    for atom_id, value in zip(atom_ids, atom_values):
                        values_dict[atom_id] = value

            except Exception as e:
                raise ValueError(
                    f"Could not build insert dictionary (atom_id -> value): {e}"
                )

            self.update_atom_properties(
                property_name=property_name, values_dict=values_dict
            )

    @validate_call
    def sql(
        self, query: str, parameters: dict[str, Any] | list | None = None
    ) -> QueryResult:
        """
        Execute SQL query and return QueryResult for method chaining.

        Args:
            query: SQL query string to execute
            parameters: Optional parameters for parameterized queries

        Returns:
            QueryResult instance that supports method chaining (.df(), .fetchall(), etc.)
        """
        return QueryResult(self._db_file, query, parameters, self)

    @validate_call(config={"arbitrary_types_allowed": True})
    def get_atoms(self, ids: list[int]) -> list[Atoms]:
        """
        Query structures and atoms tables for given structure IDs and convert to Atoms objects.

        Args:
            ids: List of structure IDs to query

        Returns:
            List of ASE Atoms objects
        """
        atom_cols = self.reader.get_all_extracted_atoms_columns()
        structure_cols = self.reader.get_all_extracted_structures_columns()

        self._check_columns_exist("structures", columns_list=structure_cols)
        self._check_columns_exist("atoms", columns_list=atom_cols)
        self._check_ids_exist(table_name="structures", ids=ids)

        with duckdb.connect(self._db_file) as con:
            # Query structures table
            structure_cols_str = ", ".join(structure_cols)
            structures_query = f"""
                SELECT {structure_cols_str}
                FROM structures
                WHERE id = ANY($ids)
            """
            structures_df = con.execute(structures_query, {"ids": ids}).df()

            # Query atoms table
            atom_cols_str = ", ".join(atom_cols)
            atoms_query = f"""
                SELECT {atom_cols_str}
                FROM atoms
                WHERE structure_id = ANY($ids)
            """
            atoms_df = con.execute(atoms_query, {"ids": ids}).df()

        # Convert DataFrames to Atoms objects using the reader
        atoms_objects = self.reader.convert(structures_df, atoms_df)

        return atoms_objects
