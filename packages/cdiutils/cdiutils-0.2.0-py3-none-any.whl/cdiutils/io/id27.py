import numpy as np

from cdiutils.io.loader import H5TypeLoader, h5_safe_load
from cdiutils.utils import wavelength_to_energy
import warnings


class ID27Loader(H5TypeLoader):
    """
    A class to handle loading/reading .h5 files that were created using
    Bliss on the ID27 beamline.
    """

    angle_names = {
        "sample_outofplane_angle": None,
        "sample_inplane_angle": "nath",
        "detector_outofplane_angle": None,
        "detector_inplane_angle": None
    }
    authorised_detector_names = ("eiger", )

    def __init__(
            self,
            experiment_file_path: str,
            scan: int = None,
            sample_name: str = None,
            detector_name: str = None,
            flat_field: np.ndarray | str = None,
            alien_mask: np.ndarray | str = None,
            **kwargs
    ) -> None:
        """
        Initialise ID27Loader with experiment data file path and
        detector information.

        Args:
            experiment_file_path (str): path to the bliss master file
                used for the experiment.
            scan (int, optional): the scan number. Defaults to None.
            sample_name (str, optional): name of the sample. Defaults
                to None.
            detector_name (str): name of the detector.
            flat_field (np.ndarray | str, optional): flat field to
                account for the non homogeneous counting of the
                detector. Defaults to None.
            alien_mask (np.ndarray | str, optional): array to mask the
                aliens. Defaults to None.
        """
        super().__init__(
            experiment_file_path,
            scan,
            sample_name,
            detector_name,
            flat_field,
            alien_mask
        )

    @h5_safe_load
    def load_detector_data(
            self,
            scan: int = None,
            sample_name: str = None,
            roi: tuple[slice] = None,
            rocking_angle_binning: int = None,
            binning_method: str = "sum"
    ) -> np.ndarray:
        """
        Load the detector data.

        Args:
            scan (int): the scan number. Defaults to None.
            sample_name (str, optional): the sample name.
                Defaults to None.
            roi (tuple[slice], optional): the region of interest to
                light load the data. Defaults to None.
            rocking_angle_binning (int, optional): the factor for the
                binning along the rocking curve axis. Defaults to None.
            binning_method (str, optional): the method for the binning
                along the rocking curve axis. Defaults to "sum".

        Raises:
            KeyError: if the key path is incorrect.

        Returns:
            np.ndarray: the detector data.
        """
        scan, sample_name = self._check_scan_sample(scan, sample_name)

        key_path = (
            "_".join((sample_name, str(scan)))
            + f".1/measurement/{self.detector_name}"
        )
        roi = self._check_roi(roi)
        try:
            if rocking_angle_binning:
                # we first apply the roi for axis1 and axis2
                data = self.h5file[key_path][(slice(None), roi[1], roi[2])]
            else:
                data = self.h5file[key_path][roi]
        except KeyError as exc:
            raise KeyError(
                f"key_path is wrong (key_path='{key_path}'). "
                "Are sample_name, scan number or detector name correct?"
            ) from exc

        if self.detector_name in ("eiger", "eiger9m", "e9m"):
            # Must apply mask on ID21 Eiger data
            mask = self.get_mask(
                channel=data.shape[0],
                detector_name="e9m",
                roi=(slice(None), roi[1], roi[2])
            )
            data = data * np.where(mask, 0, 1)

        return self.bin_flat_mask(
            data,
            roi,
            self.flat_field,
            self.alien_mask,
            rocking_angle_binning,
            binning_method
        )

    @h5_safe_load
    def load_motor_positions(
            self,
            scan: int = None,
            sample_name: str = None,
            roi: tuple[slice] = None,
            rocking_angle_binning: int = None,
    ) -> dict:
        """
        Load the motor positions, i.e diffractometer angles associated
        with a scan.

        Args:
            scan (int): the scan number. Defaults to None.
            sample_name (str, optional): the sample name.
                Defaults to None.
            roi (tuple[slice], optional): the region of interest.
                Defaults to None.
            rocking_angle_binning (int, optional): the factor for the
                binning along the rocking curve axis. Defaults to None.

        Returns:
            dict: the four diffractometer angles.
        """
        scan, sample_name = self._check_scan_sample(scan, sample_name)

        angles = self.load_angles(
            key_path=f"{sample_name}_{scan}.1/instrument/positioners/"
        )

        formatted_angles = {
            key: angles[name] if angles.get(name) is not None else 0.
            for key, name in ID27Loader.angle_names.items()
        }

        self.rocking_angle = "sample_inplane_angle"
        formatted_angles[self.rocking_angle] = self.bin_rocking_angle_values(
            formatted_angles[self.rocking_angle], rocking_angle_binning
        )
        # take care of the roi
        if isinstance(roi, (tuple, list)):
            if len(roi) == 2:
                roi = slice(None)
            else:
                roi = roi[0]
        elif roi is None:
            roi = slice(None)
        elif not isinstance(roi, slice):
            raise ValueError(
                f"roi should be tuple of slices, or a slice, not {type(roi)}"
            )

        formatted_angles[
            self.rocking_angle
        ] = formatted_angles[self.rocking_angle][roi]

        return formatted_angles

    @h5_safe_load
    def get_detector_name(self) -> str:
        key_path = ("_".join((self.sample_name, "1")) + ".1/measurement/")
        detector_names = []
        for key in self.h5file[key_path]:
            if key in self.authorised_detector_names:
                detector_names.append(key)
        if len(detector_names) == 0:
            raise ValueError(
                f"No detector name found in{self.authorised_detector_names}"
            )
        if len(detector_names) > 1:
            raise ValueError(
                f"Several detector names found ({detector_names}).\n"
                "Not handled yet."
            )
        return detector_names[0]

    @h5_safe_load
    def load_det_calib_params(self) -> dict:
        """
        Load the detector calibration parameters from the scan directly.
        Note that this will only provide the direct beam position, the
        sample-to-detector distance, and the pixel size. To get the
        tilt angles of the detector run the detector calibration
        notebook.
        """
        return None  # Data in id27 files are not reliable.

    @h5_safe_load
    def load_detector_shape(
            self,
            scan: int = None,
            sample_name: str = None,
    ) -> tuple:
        scan, sample_name = self._check_scan_sample(scan, sample_name)
        if self.detector_name in ("eiger", "eiger9m", "e9m"):
            shape = (3262, 3108)
            key_path = f"{sample_name}_{scan}.1/instrument/eiger/acq_nb_frames"
            try:
                return (int(self.h5file[key_path][()]), ) + shape
            except KeyError:
                print("Could not load original detector data shape.")
        return None

    @h5_safe_load
    def load_energy(
            self,
            scan: int = None,
            sample_name: str = None
    ) -> float:
        scan, sample_name = self._check_scan_sample(scan, sample_name)

        key_path = f"{sample_name}_{scan}.1/instrument/calibration/"
        try:
            # Convert from angstrom to m
            return wavelength_to_energy(
                float(self.h5file[key_path + "wavelength"][()]) * 1e-10
            )
        except KeyError:
            warnings.warn(f"Energy not found at {key_path + 'wavelength'}. ")
            return None
