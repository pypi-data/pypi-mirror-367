"""
A submodule for cxi file handling. The CXIFile class provides methods to
make CXI-compliant HDF5 files.
"""

import h5py
import numpy as np
import re


from cdiutils import __version__


__cxi_version__ = 150


# The group attributes as defined by the CXI conventions. The 'default'
# key corresponds to the hdf5 attribute 'default' and are here set to
# some values for each CXI group.
GROUP_ATTRIBUTES = {
    "image": {"default": "data", "nx_class": "NXdata"},
    "data": {"default": "data", "nx_class": "NXdata"},
    "geometry": {"default": "name", "nx_class": "NXgeometry"},
    "source": {"default": "energy", "nx_class": "NXsource"},
    "process": {"default": "comment", "nx_class": "NXprocess"},
    "detector": {"default": "description", "nx_class": "NXdetector"},
    "sample": {"default": "sample_name", "nx_class": "NXsample"},
    "parameters": {"default": None, "nx_class": "NXparameters"},
    "result": {"default": "description", "nx_class": "NXresult"},
}


class CXIFile:
    """The main class for handling .cxi file. It can create and load
    cxi file with simple code. The present code takes care of all the
    conventions described by the following document:
    see:
    https://raw.githubusercontent.com/cxidb/CXI/master/cxi_file_format.pdf
    """

    IMAGE_MEMBERS = (
        "title", "data", "data_error", "data_space", "data_type", "detector_",
        "dimensionality", "image_center", "image_size", "is_fft_shifted",
        "mask", "process_", "reciprocal_coordinates", "source_"
    )

    def __init__(self, file_path: str, mode: str = "r"):
        self.file_path = file_path
        self.mode = mode
        self.file = None

        # Tracks sub-group counters for each entry
        self._entry_counters = {}
        self._current_entry = None

    @property
    def entry_counters(self) -> None:
        return self._entry_counters

    @property
    def current_entry(self) -> None:
        return self._current_entry

    def open(self, mode: str = None):
        """Open the CXI file."""
        if mode is None:
            mode = self.mode
        if self.file is None:
            self.file = h5py.File(self.file_path, mode)
        return self

    def close(self):
        """Close the CXI file."""
        if self.file:
            self.file.close()
            self.file = None

    def __enter__(self):
        """Enter the runtime context related to this object."""
        return self.open()

    def __exit__(self, exc_type, exc_value, traceback):
        """Exit the runtime context related to this object."""
        self.close()

    def __getitem__(self, path: str):
        """
        Access data or groups in the CXI file, handling datasets
        and groups transparently.

        Args:
            path (str): Path to the dataset or group.

        Returns:
            Data if it's a dataset, or a nested dictionary if it's a group.
        """
        node = self.get_node(path)

        if node is None:
            raise KeyError(f"Entry '{path}' does not exist in the CXI file.")

        # If the node is a dataset, retrieve the data directly
        if isinstance(node, h5py.Dataset):
            data = node[()]
            # Check for byte-like data and decode if necessary
            if isinstance(data, bytes):  # Single byte string
                return data.decode('utf-8')
            # Array of byte strings
            if isinstance(data, np.ndarray):
                if data.dtype.kind == 'S':
                    return data.astype(str)
                if node.attrs.get("original_type") == "tuple":
                    for i, item in enumerate(data):
                        if isinstance(item, bytes):
                            data[i] = item.decode('utf-8')
                    return tuple(data)
            # Convert NaN to None if needed
            if isinstance(data, float) and np.isnan(data):  # Single NaN
                return None
            return data

        # If the node is a group, recursively read its contents
        if isinstance(node, h5py.Group):
            if node.attrs.get("original_type") == "inhomogeneous_list":
                return [self[f"{path}/{key}"] for key in node.keys()]
            return {key: self[f"{path}/{key}"] for key in node.keys()}

        # If neither, raise an error as a fallback
        raise TypeError(f"Unsupported node type at path '{path}'")

    def __setitem__(self, entry: str, data):
        """Allow adding data to an entry with cxi[entry] = data."""
        if entry in self.file:
            raise KeyError(f"Entry '{entry}' already exists.")
        self.create_cxi_dataset(entry, data=data)

    def __delitem__(self, entry: str):
        """Allow deletion of an entry with del cxi[entry]."""
        if entry in self.file:
            del self.file[entry]
        else:
            raise KeyError(f"Entry '{entry}' does not exist, cannot delete.")

    def __contains__(self, path: str) -> bool:
        """
        Check if the specified path exists in the CXI file.

        Args:
            path (str): Path to the node.

        Returns:
            bool: True if the path exists, False otherwise.
        """
        return path in self.file

    def get_node(self, path: str):
        """
        Retrieve the raw node (dataset or group) at the specified path.
        Allow direct access to entries with cxi[path].

        Args:
            path (str): Path to the node.

        Returns:
            The h5py Dataset or Group object.
        """
        if path in self:
            return self.file[path]
        raise KeyError(f"Entry '{path}' does not exist in the CXI file.")

    def copy(
            self,
            source_path: str,
            dest_file: str = None,
            dest_path: str = None,
            **kwargs
    ) -> None:
        """
        Copy a group or dataset from this CXI file to another location,
        either within the same file or to a different CXI file.

        Args:
            source_path (str): Path to the object to copy in the source
                file.
            dest_file (CXIFile or h5py.File, optional): Destination file
                object. If None, the copy will be within the same file.
                Defaults to None.
            dest_path (str, optional): Path in the destination file. If
                None, defaults to source_path in the destination.
                Defaults to None.
            **kwargs: Additional arguments for h5py copy method (e.g.,
                shallow, expand_soft).

        Raises:
            KeyError: if the source_path does not exist in the CXI file.
        """
        if source_path not in self.file:
            raise KeyError(
                f"Source path '{source_path}' does not exist in the CXI file.")

        # Determine the destination file
        if dest_file is None:
            dest_file = self.file  # Same file copy
        elif isinstance(dest_file, CXIFile):
            # Unwrap to h5py.File if another CXIFile instance
            dest_file = dest_file.file

        # Determine the destination path
        if dest_path is None:
            # Use the same name if dest_path is not specified
            dest_path = source_path
        # Perform the copy operation
        self.file.copy(source_path, dest_file, name=dest_path, **kwargs)

    def set_entry(self, index: int = None) -> str:
        """Create or switch to a specific entry group (e.g., 'entry_1')."""
        if index is None:
            # Get the next available index
            index = 1
            while f"entry_{index}" in self.file:
                index += 1
        entry_name = f"entry_{index}"

        if entry_name not in self.file:  # double check
            self.file.create_group(entry_name)
            self.file[entry_name].attrs["NX_class"] = "NXentry"
            self._entry_counters[entry_name] = {}  # Initialise counters

        self._current_entry = entry_name  # Set the current entry context
        return entry_name

    def _get_next_index(self, entry: str, group_type: str) -> int:
        """
        Get the next index for a specific group type (e.g., 'image')
        within an entry.
        """
        if entry not in self._entry_counters:
            self._entry_counters[entry] = {}

        if group_type not in self._entry_counters[entry]:
            return 1

        return self._entry_counters[entry][group_type] + 1

    def _increment_index(self, entry: str, group_type: str) -> int:
        self._entry_counters[entry][group_type] = self._get_next_index(
            entry, group_type
        )
        return self._entry_counters[entry][group_type]

    def create_cxi_group(
            self,
            group_type: str,
            default: str = None,
            index: int = None,
            attrs: dict = None,
            **kwargs,
    ) -> str:
        """
        Create a CXI-compliant group with optional NeXus class.

        Args:
            group_type (str): the type of group (e.g., 'image',
                'process').
            default (str, optional): the default hdf5 attribute. If not
                provided will use the one stored in GROUP_ATTRIBUTES.
                Defaults to None.
            index (int, optional): explicit index. If None, the next
                available index is used. Defaults to None.
            attrs: Additional attributes for the group.
            **kwargs: the data to save in the CXI group.

        Returns:
            str: The full path of the created group.
        """
        if not self._current_entry:
            self.set_entry()  # Ensure at least 'entry_1' exists

        # Determine the next available index if not specified
        if index is None:
            index = self._get_next_index(self._current_entry, group_type)

        # Determine default values from GROUP_ATTRIBUTES
        if group_type not in GROUP_ATTRIBUTES:
            raise ValueError(
                f"Unknown group_type ({group_type}), must be in "
                f"{GROUP_ATTRIBUTES.keys()}"
            )
        if group_type in GROUP_ATTRIBUTES:
            default = GROUP_ATTRIBUTES.get(group_type).get("default")
            nx_class = GROUP_ATTRIBUTES.get(group_type).get("nx_class")
        else:
            raise KeyError(f"No {group_type} in GROUP_ATTRIBUTES.")

        group_name = f"{group_type}_{index}"
        path = f"{self._current_entry}/{group_name}"

        increment = self.create_group(path, nx_class, attrs)
        if increment:
            self._increment_index(self._current_entry, group_type)

        if default:
            self.file[path].attrs["default"] = default

        self.create_cxi_dataset(path, data=kwargs)
        return path

    def create_group(
            self,
            path: str,
            nx_class: str = None,
            attrs: dict = None
    ) -> bool:
        """
        Method to handle the creation of groups in the context
        of H5 files, not in the context of CXI.

        Args:
            path (str): the path to create the group at
            nx_class (str, optional): NeXus class for the group.
                Defaults to None.
            attrs (dict, optional): Additional attributes for the group.

        returns: True if the group was created else False (i.e. if
            group already exists).
        """
        if path not in self.file:
            group = self.file.require_group(path)
            if nx_class:
                group.attrs["NX_class"] = nx_class
            if attrs:
                group.attrs.update(attrs)
            return True
        return False

    def create_cxi_dataset(
            self,
            path: str,
            data,
            dtype=None,
            nx_class: str = None,
            **attrs
    ) -> h5py.Dataset | h5py.Group:
        """
        Create a CXI-compliant dataset with optional NeXus class.

        Args:
            path (str): The path to the dataset.
            data: The data to store in the dataset (can be a dict).
            dtype (data-type, optional): The data type for the dataset.
                Defaults to None.
            nx_class (str, optional): The NeXus class for the dataset,
                if applicable. Defaults to None.

        Returns:
            h5py.Dataset: the dataset or group instance created.
        """
        # If data is a string or a list of strings, set dtype to store
        # as UTF-8.
        if isinstance(data, str):
            dtype = h5py.string_dtype(encoding='utf-8')
        elif isinstance(data, list) and all(
                isinstance(item, str) for item in data):
            dtype = h5py.string_dtype(encoding='utf-8')

        # Handle nested dictionary by creating a group and populating it
        # recursively.
        if isinstance(data, dict):
            self.create_group(path, nx_class, **attrs)
            for key, value in data.items():
                # Recursively create nested datasets or groups
                self.create_cxi_dataset(f"{path}/{key}", data=value)
            return self.get_node(path)

        # Handle the case where data is a list with mixed types
        if isinstance(data, list):
            if any(type(item) is not type(data[0]) for item in data):
                self.create_group(path, nx_class, **attrs)
                for i, item in enumerate(data):
                    self.create_cxi_dataset(f"{path}/{i}", data=item)
                self.get_node(path).attrs["original_type"] = (
                    "inhomogeneous_list"
                )
                return self.get_node(path)

        # Check if data contains tuples, which need to be handled
        elif isinstance(data, tuple):
            # Convert tuples to a numpy array
            self.create_cxi_dataset(path, data=np.array(data))
            self.get_node(path).attrs["original_type"] = "tuple"
            return self.get_node(path)

        # Otherwise, simply create a standard dataset.
        data = np.nan if data is None else data
        dataset = self.file.create_dataset(path, data=data, dtype=dtype)
        if nx_class:
            dataset.attrs["NX_class"] = nx_class
        dataset.attrs.update(attrs)
        return dataset

    def read_cxi_dataset(self, path: str):
        """
        Read a dataset or group and handle inhomogeneous lists.

        Args:
            path (str): Path to the dataset or group.

        Returns:
            The reassembled data, either as the original inhomogeneous
            list or a standard dataset.
        """
        node = self.file[path]

        # Check if this is a group representing an inhomogeneous list
        if node.attrs.get("original_type") == "inhomogeneous_list":
            # Reconstruct the list by iterating over each dataset in the group
            data = []
            for idx in sorted(node.keys(), key=int):  # Sort by index order
                item = node[idx][()]
                data.append(
                    item.tolist() if isinstance(item, np.ndarray) else item
                )
            return data

        # Return the standard dataset directly
        return node[()]

    def softlink(
            self,
            path: str,
            target: str,
            raise_on_error: bool = False
    ) -> None:
        """
        Create a soft link at the specified path pointing to an existing
        target path.

        Args:
            path (str): the path where the soft link will be created.
            target (str): the target path that the soft link points to.

        Raises:
            ValueError: if the target path does not exist in self.file.
        """
        if not target.startswith("/"):
            target = "/" + target
        if target in self.file:
            self.file[path] = h5py.SoftLink(target)
        elif raise_on_error:
            raise ValueError(f"The target path '{target}' does not exist.")
        else:
            print(f"Warning: The target path '{target}' does not exist.")

    def stamp(self):
        """
        Add metadata to the CXI file, recording information about the
        software and file creation details.
        """
        # Store software information
        self.file.attrs["creator"] = "CdiUtils"
        self.file.attrs["version"] = __version__
        self.create_cxi_dataset("creator", "CdiUtils")
        self.create_cxi_dataset("version", __version__)

        # Store file path, CXI version, and timestamp
        self.create_cxi_dataset("file_path", data=self.file_path)
        self.create_cxi_dataset("cxi_version", data=__cxi_version__)
        self.create_cxi_dataset(
            "time",
            data=np.bytes_(np.datetime64("now").astype(str))
        )

    def create_cxi_image(
            self,
            data: np.ndarray,
            link_data: bool = True,
            **members
    ) -> str:
        """
        Create a minimal CXI image entry with associated metadata and
        soft links.

        Args:
            data (np.ndarray): the image data.
            link_data (bool, optional): whether to link to a data_N
                group. Defaults to True.
            **members: additional members to add to the image group.
                Keys ending in a digit will be indexed accordingly.

        Returns:
            str: The full path of the created group.
        """
        # Minimal CXI image entry.
        path = self.create_cxi_group("image", data=data, image_size=data.shape)
        self.file[f"{path}"].attrs["interpretation"] = "image"
        self.file[f"{path}"].attrs["signal"] = "data"

        for k, v in members.items():
            # Match the member base and any trailing digit
            match = re.match(r"(.*?)(\d+)?$", k)
            member_base, index = match.groups()

            # Check if the base member is allowed by CXI convention
            if member_base in self.IMAGE_MEMBERS:
                # Construct the full member name, adding the index if present
                if index:
                    self.softlink(
                        f"{path}/{member_base}{index}",
                        f"{self._current_entry}/{v}"
                    )
                else:
                    self.create_cxi_dataset(f"{path}/{k}", v)
            else:
                print(
                    f"Warning: '{k}' is not allowed in CXI image convention."
                )

        # link the image to a data entry
        if link_data:
            data_path = self.create_cxi_group("data")
            self.softlink(f"{data_path}/data", f"{path}/data")
            self.file[f"{data_path}"].attrs["signal"] = "data"
            self.file[f"{data_path}"].attrs["interpretation"] = "image"

        # Handle the default attribute of the current_entry. If this is
        # the first image, it should be default attribute of the parent
        # entry_.
        if "default_entry" not in self._entry_counters[self._current_entry]:
            self._entry_counters[
                self._current_entry
            ]["default_entry"] = "data_1" if link_data else "image_1"
            self.file[
                self._current_entry
            ].attrs["default"] = "data_1" if link_data else "image_1"

        return path


def save_as_cxi(output_path: str, **to_be_saved: dict) -> None:
    """
    A helper function to quickly save data to a CXI file without
    dealing with CXIFile complexity. However, this function is less
    flexible than using CXIFile directly.

    Args:
        output_path (str): the path to save the CXI file.
        to_be_saved (dict): the data to save in the CXI file.
    """
    if len(to_be_saved) == 0:
        raise ValueError("No data to save. No file created.")
    with CXIFile(output_path, "w") as cxi:
        cxi.stamp()
        cxi.set_entry()

        results = {}

        for key, value in to_be_saved.items():
            if isinstance(value, np.ndarray) and value.ndim >= 2:
                path = cxi.create_cxi_image(data=value, title=key)
                cxi.softlink(f"entry_1/{key}", path)
            else:
                results[key] = value

        # Simply save all the rests of the data in "result_1" group
        cxi.create_cxi_group("result", **results)


def load_cxi(path: str, *key: str) -> dict:
    """
    Load a CXI file and return its content as a dictionary.

    Args:
        path (str): the path to the CXI file.

    Returns:
        dict: the content of the CXI file.
    """
    data = {}
    with CXIFile(path, "r") as cxi:
        # Handle case where key_path is not provided
        if len(key) == 0:
            for k in cxi["entry_1"]:
                if k.startswith("result"):
                    for subk in cxi[f"entry_1/{k}"]:
                        data[subk] = cxi[f"entry_1/{k}/{subk}"]
                elif not k.startswith("image") and not k.startswith("data"):
                    data[k] = cxi[f"entry_1/{k}/data"]
            return data

        # key_path provided
        for k in key:
            if k.startswith("entry"):  # assume that the exact path is provided
                data[k] = cxi[k]
            else:
                # If the key_path is not a full path, we search for the data
                e_counter = 1  # entry counter
                while f"entry_{e_counter}" in cxi:
                    key_path = f"entry_{e_counter}/{k}"
                    if (
                            key_path in cxi and cxi.get_node(
                                key_path
                            ).attrs["NX_class"] == "NXdata"
                    ):
                        data[k] = cxi[f"{key_path}/data"]
                        e_counter = 0
                    else:
                        # We search the data in result groups
                        r_counter = 1  # result counter
                        while f"entry_{e_counter}/result_{r_counter}" in cxi:
                            key_path = (
                                f"entry_{e_counter}/result_{r_counter}/{k}"
                            )
                            if key_path in cxi:
                                data[k] = cxi[key_path]
                                e_counter, r_counter = 0, 0
                            else:
                                e_counter += 1
                                r_counter += 1
    if len(data) == 1:
        return data[list(data.keys())[0]]
    return data
