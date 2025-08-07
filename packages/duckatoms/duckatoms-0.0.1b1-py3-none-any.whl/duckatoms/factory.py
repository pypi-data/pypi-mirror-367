from pydantic import validate_call
from typing import Literal
from pathlib import Path
import duckdb


class Factory:
    """Can be used to create a new DuckAtoms database and add / remove
    properties of an existing database.
    """

    @validate_call
    def __init__(self, db_file: Path | str):
        db_file = Path(db_file)
        if db_file.suffix not in {".db", ".duckdb"}:
            raise ValueError(
                f"Database file must have .db or .duckdb extension, got: {db_file.suffix}"
            )
        self._db_file = db_file

    def __repr__(self) -> str:
        return f"Factory('{self._db_file}')"

    @property
    def db_file(self) -> Path:
        return self._db_file

    @db_file.setter
    @validate_call
    def db_file(self, path: str | Path) -> None:
        db_file = Path(path)
        if db_file.suffix not in {".db", ".duckdb"}:
            raise ValueError(
                f"Database file must have .db or .duckdb extension, got: {db_file.suffix}"
            )
        self._db_file = db_file

    def create(self):
        """
        Creates a new db with minimal needed tables and columns.
        """
        if self._db_file.exists():
            msg = f"""A database under your given db-file name:
            {str(self._db_file)} already exists! If you want to create a new
            database under that name delete this file first."""
            raise FileExistsError(msg)

        with duckdb.connect(self._db_file) as con:
            create_structures_table = """
                                    CREATE SEQUENCE id_structures START 1;
                                    CREATE TABLE structures (
                                        id BIGINT PRIMARY KEY DEFAULT nextval('id_structures'),
                                        pbc BOOLEAN[3] NOT NULL,
                                        cell DOUBLE[9] NOT NULL,
                                    );
                                    """
            con.sql(create_structures_table)

            create_atoms_table = """
                                CREATE SEQUENCE id_atoms START 1;
                                CREATE TABLE atoms (
                                    id BIGINT PRIMARY KEY DEFAULT nextval('id_atoms'),
                                    structure_id BIGINT REFERENCES
                                    structures(id) ON DELETE RESTRICT NOT NULL,
                                    -- structures can only be deleted after their
                                    -- atoms are deleted first
                                    ase_atoms_id BIGINT NOT NULL,
                                    number BIGINT NOT NULL,
                                    x DOUBLE NOT NULL,
                                    y DOUBLE NOT NULL,
                                    z DOUBLE NOT NULL,
                                );
                                """
            con.sql(create_atoms_table)

    def show_db_structure(self) -> None:
        if not self._db_file.exists():
            raise FileNotFoundError(f"No database file exists at: {str(self._db_file)}")

        with duckdb.connect(self._db_file) as con:
            structures_table_description = con.sql("DESCRIBE structures;").df()
            atoms_table_description = con.sql("DESCRIBE atoms;").df()

        print("structures table")
        print("----------------")
        print(structures_table_description)
        print("\n")
        print("atoms table")
        print("-----------")
        print(atoms_table_description)

    @validate_call
    def add_property(
        self,
        table_name: Literal["structures", "atoms"],
        property_name: str,
        property_dtype: str,
    ):
        """
        Add a new property (column) to the specified table.

        Args:
            table_name: Name of the table ('structures' or 'atoms')
            property_name: Name of the new property column to add
            property_dtype: Data type for the new column (e.g., 'DOUBLE', 'BIGINT')

        Raises:
            ValueError: If column creation fails due to invalid property definition

        """
        # Basic validation for column name (must be valid SQL identifier)
        if not property_name.replace("_", "").replace("-", "").isalnum():
            raise ValueError(
                f"Property name '{property_name}' contains invalid characters. Use only letters, numbers, underscores, and hyphens."
            )

        # table_name is validated by Literal type hint above
        query = f"ALTER TABLE {table_name} ADD COLUMN {property_name} {property_dtype};"
        with duckdb.connect(self._db_file) as con:
            try:
                con.sql(query)
            except Exception as e:
                raise ValueError(
                    f"Invalid column definition for '{property_name}': {e}"
                )

    @validate_call
    def remove_property(
        self, table_name: Literal["structures", "atoms"], property_name: str
    ):
        """
        Remove a property (column) from the specified table.

        Args:
            table_name: Name of the table (only 'atoms' implemented!)
            property_name: Name of the property/column to remove

        Raises:
            NotImplementedError: If trying to remove from structures table
            ValueError: If trying to remove essential columns or removal fails

        Note: Columns from the structures table cannot be removed due to
              foreign key constraints.
        """
        if table_name == "structures":
            msg = """First note that due to the foreign key
            constraint in the structures table, columns in that table can not
            be removed. To avoid breaking referential integrity please rather
            create a new DB."""
            raise NotImplementedError(msg)
        elif property_name in {
            "id",
            "structure_id",
            "ase_atoms_id",
            "number",
            "x",
            "y",
            "z",
        }:
            raise ValueError(
                f"The property: {property_name} is necessary for other functions / classes and must remain in the table."
            )

        # Check if the column actually exists in the table
        with duckdb.connect(self._db_file) as con:
            existing_columns = (
                con.execute(f"DESCRIBE {table_name}").df().column_name.tolist()
            )
            if property_name not in existing_columns:
                raise ValueError(
                    f"Column '{property_name}' does not exist in table '{table_name}'. Available columns: {existing_columns}"
                )

        try:
            with duckdb.connect(self._db_file) as con:
                # property_name is validated above to exist in the table
                con.sql(f"ALTER TABLE {table_name} DROP COLUMN {property_name};")
        except Exception as e:
            raise ValueError(
                f"Cannot remove property: {property_name} from {table_name}: \n Error: {e}"
            )
