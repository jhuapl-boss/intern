import pathlib
import psutil
import warnings

from intern import array
import numpy as np
from PIL import Image

import math
from tqdm.auto import tqdm


class ZSliceIngestJob:
    def __init__(
        self,
        channel_uri: str,
        image: dict,
        annotations: list[dict] = None,  # type: ignore
        voxel_size: tuple[float, float, float] = (1.0, 1.0, 1.0),
        voxel_unit: str = "nanometers",
        verify_data: bool = True,
        ram_pct_to_use: float = 0.75,
    ):
        """
        Create a new ZSliceIngestJob.

        A note on `ram_pct_to_use`: This is a percentage of currently-available
        RAM, so if you have a 100 GB machine and you're using 50 GB of RAM,
        "0.5" will allow this upload to use 25 GB of RAM.

        Arguments:
            channel_uri (str): URI of the channel to upload to.
            image (dict): Information about the image.
            annotations (list[dict]): Information about the annotations.
            voxel_size (tuple[float, float, float]): Size of a voxel. ZYX.
            voxel_unit (str, optional): Unit of the voxel size. Defaults to
                "nanometers". Other options are "micrometers" and "millimeters".
            verify_data (bool): Whether to verify that the data are the correct
                size and dtype before uploading. Defaults to True.
            ram_pct_to_use (float): Percentage of free RAM to use for uploading.

        """
        self.channel_uri = channel_uri
        self.image = image
        self.annotations = annotations or []
        self.voxel_size = voxel_size or (1, 1, 1)
        self.voxel_unit = voxel_unit
        self._ram_pct_to_use = ram_pct_to_use
        if verify_data:
            self._verify_paths()
            self._verify_shapes()

    def _verify_paths(self, warn: bool = True) -> bool:
        """
        Verify that the paths exist.

        Arguments:
            warn (bool): Whether to warn if the paths do not exist.

        Returns:
            bool: Whether the paths exist.

        """
        if not self.image["path"].exists():
            warnings.warn(f"Image path {self.image['path']} does not exist.")
            return False

        for annotation in self.annotations:
            if not annotation["path"].exists():
                warnings.warn(f"Annotation path {annotation['path']} does not exist.")
                return False

        return True

    def _get_ram_bytes_available(self):
        """
        Get the amount of RAM available on the system.

        Returns:
            int: Amount of RAM in bytes.

        """
        return psutil.virtual_memory().available

    def _get_shape_px_of_zslice(
        self,
    ):
        """
        Get the size of a z-slice in pixels.

        Uses the IMAGE as a reference.

        Returns:
            int: Size of a z-slice in pixels.

        """
        # Read in the first image
        image = Image.open(self.image["path"].glob(self.image["pattern"])[0])

    def _get_size_bytes_of_zslice(self, dtype):
        """
        Get the size of a z-slice in bytes.

        Arguments:
            dtype (numpy.dtype): The data type of the array.

        Returns:
            int: Size of a z-slice in bytes.

        """
        return self._get_shape_px_of_zslice() * dtype.itemsize

    def _get_permitted_zcount(self, dtype):
        """
        Get the number of z-slices that can be uploaded at once.

        Arguments:
            dtype (numpy.dtype): The data type of the array.

        Returns:
            int: Number of z-slices that can be uploaded at once.

        """
        if isinstance(dtype, str):
            dtype = np.dtype(dtype)
        count = int(
            self._get_ram_bytes_available()
            * self._ram_pct_to_use
            / self._get_size_bytes_of_zslice(dtype)
        )

        if count == 0:
            raise ValueError(
                "The dtype is too large to fit in the available RAM. "
                "Try a larger AVAILABLE_RAM_PERCENT_TO_USE."
            )

        if count < 4:
            warnings.warn(
                "The z slices are very large compared to available RAM, and will "
                f"only be uploaded in groups of {count}. This may result in a "
                "long upload time."
            )

        return count

    def _get_zslice_image_paths(self) -> list[pathlib.Path]:
        """
        Get the paths to the z-slices.

        Returns:
            list[pathlib.Path]: Paths to the z-slices.

        """
        return list(sorted(self.image["path"].glob(self.image["pattern"])))

    def _get_zslice_annotation_paths(self) -> list[list[pathlib.Path]]:
        """
        Get the paths to the z-slices.

        Returns:
            list[list[pathlib.Path]]: Paths to the z-slices.

        """
        return [
            list(sorted(annotation["path"].glob(annotation["pattern"])))
            for annotation in self.annotations
        ]

    def _get_zslice_count(self):
        """
        Get the number of z-slices.

        Returns:
            int: Number of z-slices.

        """
        return len(self._get_zslice_image_paths())

    def _verify_shapes(self, warn: bool = True):
        """
        Verify the shape of every image in the stacks.

        Note that this can be a bit slow if the image stacks are large enough.

        Arguments:
            None

        Returns:
            bool: True if all the images are the same size, else False.

        """
        image_slice_count = self._get_zslice_count()
        anno_slice_counts = [len(s) for s in self._get_zslice_annotation_paths()]
        for anno_count, anno in zip(anno_slice_counts, self.annotations):
            if anno_count != image_slice_count:
                if warn:
                    warnings.warn(
                        "Not all stacks have the same number of z-slices. "
                        f"Annotation [{anno['name']}] has {anno_count} z-slices, but the image has {image_slice_count}."
                    )
                return False

        # Get the shape of the first image
        shape = Image.open(self._get_zslice_image_paths()[0]).size

        # Check that all the other images are the same size
        for path in self._get_zslice_image_paths()[1:]:
            if Image.open(path).size != shape:
                if warn:
                    warnings.warn(
                        "Not all image stacks have the same shape. "
                        f"Image [{path}] has shape {Image.open(path).size}, but the first image has shape {shape}."
                    )
                return False

        return True

    def upload_images(self, progress: bool = True) -> bool:
        """
        Upload the images to the channel.

        Arguments:
            progress (bool): Whether to show a progress bar.

        Returns:
            bool: Whether the upload was successful.

        """
        # Get the z-slice paths
        zslice_paths = self._get_zslice_image_paths()

        # Get the number of z-slices
        zslice_count = len(zslice_paths)

        # Get the shape of the images
        shape = Image.open(zslice_paths[0]).size

        # Get the number of images to upload per batch
        batch_size = self._get_permitted_zcount(self.image["dtype"])
        # Get the number of batches
        batch_count = math.ceil(zslice_count / batch_size)

        # Set the progress bar lambda
        if progress:
            progress_bar = tqdm(total=zslice_count, desc="Uploading images")

        # Try making the array pointer. If it already exists, then make sure
        # that the shape is the same.
        try:
            # Does it already exist?
            dataset = array(self.image["name"])
        except:
            # Create the array
            dataset = array(
                self.image["name"],
                create_new=True,
                dtype=self.image["dtype"],
                extents=(zslice_count, shape[1], shape[0]),
                voxel_size=self.voxel_size,  # type: ignore
                voxel_unit=self.voxel_unit,
            )

        # Now break up the images into batches and upload them. First we'll do
        # all of the batches of size `batch_size`, then we'll do the last batch
        # (if it exists) which may be smaller than `batch_size` if the total
        # number of z-slices is not divisible by `batch_size`.
        for batch in range(batch_count):
            # Get the start and end indices for the batch
            start = batch * batch_size
            end = min((batch + 1) * batch_size, zslice_count)

            batch_array = np.zeros(
                (end - start, shape[1], shape[0]), dtype=self.image["dtype"]
            )
            for i, path in enumerate(zslice_paths[start:end]):
                batch_array[i] = np.array(Image.open(path)).T

            # Upload the batch
            dataset[start:end, 0 : shape[1], 0 : shape[0]] = batch_array

            # Update the progress bar
            if progress:
                progress_bar.update(end - start)  # type: ignore

        # Close the progress bar
        if progress:
            progress_bar.close()  # type: ignore

        return True

    def upload_annotations(self, progress: bool = True) -> bool:
        """
        Upload the annotations to the channel.

        Arguments:
            progress (bool): Whether to show a progress bar.

        Returns:
            bool: Whether the upload was successful.

        """
        # Get the z-slice paths
        zslice_paths = self._get_zslice_annotation_paths()

        for anno_dict, paths in zip(self.annotations, zslice_paths):

            # Get the number of z-slices
            zslice_count = len(paths)

            # Get the shape of the images
            shape = Image.open(paths[0]).size

            # Get the number of images to upload per batch
            batch_size = self._get_permitted_zcount(anno_dict["dtype"])
            # Get the number of batches
            batch_count = math.ceil(zslice_count / batch_size)

            # Set the progress bar lambda
            if progress:
                progress_bar = tqdm(
                    total=zslice_count, desc=f"Uploading channel [{anno_dict['name']}]"
                )

            # Try making the array pointer. If it already exists, then make sure
            # that the shape is the same.
            try:
                # Does it already exist?
                dataset = array(anno_dict["name"])
            except:
                # Create the array
                dataset = array(
                    anno_dict["name"],
                    create_new=True,
                    dtype=anno_dict["dtype"],
                    extents=(zslice_count, shape[1], shape[0]),
                    voxel_size=self.voxel_size,  # type: ignore
                    voxel_unit=self.voxel_unit,
                    source_channel=self.image["name"],
                )

            if dataset.dtype != anno_dict["dtype"]:
                raise ValueError(
                    f"Array [{anno_dict['name']}] already exists, but has a different dtype."
                )
            if dataset.shape != (zslice_count, shape[1], shape[0]):
                raise ValueError(
                    f"Array [{anno_dict['name']}] already exists, but has a different shape."
                )

            # Now break up the images into batches and upload them. First we'll do
            # all of the batches of size `batch_size`, then we'll do the last batch
            # (if it exists) which may be smaller than `batch_size` if the total
            # number of z-slices is not divisible by `batch_size`.
            for batch in range(batch_count):
                # Get the start and end indices for the batch
                start = batch * batch_size
                end = min((batch + 1) * batch_size, zslice_count)

                batch_array = np.zeros(
                    (end - start, shape[1], shape[0]), dtype=anno_dict["dtype"]
                )
                for i, paths in enumerate(zslice_paths[start:end]):
                    batch_array[i] = np.array(Image.open(paths[0])).T

                # Upload the batch
                dataset[start:end, 0 : shape[1], 0 : shape[0]] = batch_array

                # Update the progress bar
                if progress:
                    progress_bar.update(end - start)  # type: ignore

            # Close the progress bar
            if progress:
                progress_bar.close()  # type: ignore

        return True

    def upload(self, progress: bool = True) -> bool:
        """
        Upload the image and annotations to the channel.

        Arguments:
            progress (bool): Whether to show a progress bar.

        Returns:
            bool: Whether the upload was successful.

        """
        # Upload the image
        self.upload_images(progress=progress)

        if len(self.annotations) > 0:
            # Upload the annotations
            self.upload_annotations(progress=progress)

        return True
