from abc import ABC, abstractmethod
import pandas as pd
import numpy as np
from ase import Atoms
from pydantic import validate_call
from typing import Any


class AtomsToDB(ABC):
    """
    Abstract base class for converting ASE Atoms objects to database format.

    All converter classes inherit from this to ensure consistent interface.
    Subclasses must implement extract_structure_data() and extract_atom_data().

    Note:
        When inserting arrays (e.g., 3D forces, 3D magnetic moments, ..) as
        column values use .tolist() to convert numpy arrays to Python lists.

        Example:
            forces = atoms.get_forces()  # Shape: (n_atoms, 3)
            return {'forces': forces.tolist()}  # Converts to list of
            [x,y,z]-values lists.
    """

    @abstractmethod
    @validate_call(config={"arbitrary_types_allowed": True})
    def extract_structure_data(self, atoms: Atoms) -> dict:
        """
        Extract data for the `structures`-table from an Atoms object.

        Args:
            atoms: ASE Atoms object

        Returns:
            Dictionary with column names as keys and corresponding data as
            values
        Note:
            - pbc, cell are always included
            - Return empty dict if no additional structure data needed
        """
        pass

    @abstractmethod
    @validate_call(config={"arbitrary_types_allowed": True})
    def extract_atom_data(self, atoms: Atoms) -> dict:
        """
        Extract data for the `atoms`-table from an Atoms object.

        Args:
            atoms: ASE Atoms object

        Returns:
            Dictionary with column names as keys and lists of values (one per atom)

        Note:
            - ase_atoms_id, positions (x, y, z) and (atomic)numbers are always included
            - All lists must have length equal to len(atoms)
            - Return empty dict if no additional atom data needed
        """
        pass

    @validate_call(config={"arbitrary_types_allowed": True})
    def convert(
        self, atoms: list[Atoms] | Atoms, batch_metadata: dict[str, Any] | None = None
    ) -> tuple[pd.DataFrame, pd.DataFrame]:
        """
        Converts one or a batch of ASE Atoms objects into  DataFrames for
        database insertion. The first DataFrame is inserted into the
        `structures`-table and the second into the `atoms`-table. Additionally
        you can provide fixed values for all structures of the batch, that are
        added to the corresponding columns of the structures table.

        Args:
            atoms(Atoms | list[Atoms]): structures that are added to the db
            batch_metadata: Dictionary of column names and values, that should
                be added for all atoms of this batch.
                Example: {'surface_cut': 'slab_001', 'method': 'vasp'})
        Note: You have to ensure, that a property with the same name was created
        in the structures table! The tmp_structure_id of the atoms_df
        corresponds to the index of the structures_df.

        Returns:
            Tuple of (structures_df, atoms_df) ready for database insertion
        """
        if batch_metadata is None:
            batch_metadata = {}

        if isinstance(atoms, Atoms):
            atoms = [atoms]

        if not atoms:
            raise ValueError("Empty list, no atoms objects were supplied!")

        structures_batch = []
        atoms_batch = []

        for struct_idx, at in enumerate(atoms):
            # Required structure data
            structure_data = {"pbc": [at.pbc], "cell": [at.cell.array.flatten()]}

            # Add batch metadata to all structures
            for key, value in batch_metadata.items():
                structure_data[key] = [value]

            # Additional structure data from subclass
            additional_structure_data = self.extract_structure_data(at)
            for key, value in additional_structure_data.items():
                structure_data[key] = [value]

            structures_batch.append(pd.DataFrame(structure_data))

            # Required atom data
            atom_data = {
                "tmp_structure_id": [struct_idx] * len(at),
                "ase_atoms_id": list(range(len(at))),
                "number": at.numbers,
                "x": at.positions[:, 0],
                "y": at.positions[:, 1],
                "z": at.positions[:, 2],
            }

            # Additional atom data from subclass
            additional_atom_data = self.extract_atom_data(at)
            for key, values in additional_atom_data.items():
                if len(values) != len(at):
                    raise ValueError(
                        f"Atom data '{key}' has length {len(values)} but should have length {len(at)}"
                    )
                atom_data[key] = values

            atoms_batch.append(pd.DataFrame(atom_data))

        structures_df = pd.concat(structures_batch, ignore_index=True)
        atoms_df = pd.concat(atoms_batch, ignore_index=True)

        return structures_df, atoms_df


class BaseAtomsToDB(AtomsToDB):
    """
    Simple implementation that handles minimal data import from an atoms
    object. Only saves pbc, cell, positions, and atomic numbers.
    """

    def extract_structure_data(self, atoms: Atoms) -> dict:
        """No additional structure data - just the basics."""
        return {}

    def extract_atom_data(self, atoms: Atoms) -> dict:
        """No additional atom data - just the basics."""
        return {}


class DBToAtoms(ABC):
    """
    Abstract base class for converting database records back to ASE Atoms objects.

    To define a custom converter you need to inherit from this class and implement:
    1. get_additional_structures_columns() - specify additional structure-table
    columns needed
    2. get_additional_atoms_columns() - specify additional atom-table columns needed
    3. convert_single_structure() - convert preprocessed data to a single Atoms
    object

    You can find an example implementation in the BaseDBToAtoms class.

    The ABC automatically handles:
    - Extracting data from multi-structure DataFrames
    - Preprocessing data into clean arrays for each structure
    """

    @abstractmethod
    @validate_call
    def get_additional_structures_columns(self) -> list[str]:
        """
        Specify which additional columns to extract from the structures table.

        Returns:
            List of additional column names from structures table

        Note:
            Required columns (id, pbc, cell) are automatically included.
        """
        pass

    @abstractmethod
    @validate_call
    def get_additional_atoms_columns(self) -> list[str]:
        """
        Specify which additional columns to extract from the atoms table.

        Returns:
            List of additional column names from atoms table

        Note:
            Required columns (structure_id, ase_atoms_id, number, x, y, z)
            are automatically included.
        """
        pass

    @abstractmethod
    @validate_call
    def convert_single_structure(self, **values) -> Atoms:
        """
        Convert preprocessed data for a single structure to an ASE Atoms object.

        Args:
            **values: Preprocessed data as keyword arguments. Always includes:
                - pbc: periodic boundary conditions (3-element array)
                - cell: unit cell matrix (3x3 array)
                - x, y, z: atomic positions (1D arrays, sorted by ase_atoms_id)
                - number: atomic numbers (1D array, sorted by ase_atoms_id)
                - Additional columns as specified in get_additional_structures_columns() and get_additional_atoms_columns()

        Returns:
            ASE Atoms object reconstructed from database data
        """
        pass

    @validate_call
    def get_all_extracted_structures_columns(self) -> list[str]:
        """
        Get complete structures column list including required columns.

        Returns:
            List of all structures columns (required + additional)
        """
        additional_cols = self.get_additional_structures_columns()
        required_cols = ["id", "pbc", "cell"]

        # Combine and deduplicate
        return required_cols + [
            col for col in additional_cols if col not in required_cols
        ]

    @validate_call
    def get_all_extracted_atoms_columns(self) -> list[str]:
        """
        Get complete atoms column list including required columns.

        Returns:
            List of all atoms columns (required + additional)
        """
        additional_cols = self.get_additional_atoms_columns()
        required_cols = ["structure_id", "ase_atoms_id", "number", "x", "y", "z"]

        # Combine and deduplicate
        return required_cols + [
            col for col in additional_cols if col not in required_cols
        ]

    @validate_call(config={"arbitrary_types_allowed": True})
    def convert(
        self, structures_df: pd.DataFrame, atoms_df: pd.DataFrame
    ) -> list[Atoms]:
        """
        Convert multiple structures from DataFrames to list of Atoms objects.

        Args:
            structures_df: DataFrame with structure-level data (multiple structures)
            atoms_df: DataFrame with atom-level data (multiple structures)

        Returns:
            List of ASE Atoms objects, one per structure
        """
        atoms_objects = []

        # Process each structure
        for _, structure_row in structures_df.iterrows():
            structure_id = structure_row["id"]

            # Extract atoms for this structure, sorted by ase_atoms_id
            structure_atoms = atoms_df[
                atoms_df["structure_id"] == structure_id
            ].sort_values("ase_atoms_id")

            properties = {}

            # Add structure-level data
            for col_name in structures_df.columns:
                if col_name == "cell":
                    # Reshape cell from flat array to 3x3 matrix
                    properties[col_name] = np.array(structure_row[col_name]).reshape(
                        3, 3
                    )
                else:
                    properties[col_name] = structure_row[col_name]

            # Add atom-level data as arrays
            for col_name in structure_atoms.columns:
                if col_name in ["structure_id", "ase_atoms_id"]:
                    continue  # Skip these utility columns
                else:
                    properties[col_name] = structure_atoms[col_name].to_list()

            # Convert single structure using user's method
            atoms_obj = self.convert_single_structure(**properties)
            atoms_objects.append(atoms_obj)

        return atoms_objects


class BaseDBToAtoms(DBToAtoms):
    """
    Simple implementation that creates Atoms objects with only basic data:
    positions, atomic numbers, cell, and pbc. No additional properties.
    """

    def get_additional_structures_columns(self) -> list[str]:
        """No additional structure columns beyond the required ones."""
        return []

    def get_additional_atoms_columns(self) -> list[str]:
        """No additional atom columns beyond the required ones."""
        return []

    def convert_single_structure(self, **values) -> Atoms:
        """Create Atoms object with basic structure and atom data."""
        # Combine x, y, z into positions array
        positions = np.stack([values["x"], values["y"], values["z"]], axis=-1)

        # Create and return Atoms object
        atoms = Atoms(
            numbers=values["number"],
            positions=positions,
            cell=values["cell"],
            pbc=values["pbc"],
        )

        return atoms
