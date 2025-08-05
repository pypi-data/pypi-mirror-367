# SPDX-FileCopyrightText: Copyright © 2023 Idiap Research Institute <contact@idiap.ch>
#
# SPDX-License-Identifier: GPL-3.0-or-later
"""3rd Aptos Competition dataset for automatic report generation on angiography images.

The 3rd Aptos Competition Dataset is the first publicly available angiographic dataset,
comprising images of both fluorescein angiography and indocyanine green angiography (ICGA),
all labeled by retinal specialists.  Collected at the Department of
Ophthalmology, Rajavithi Hospital, Bangkok, Thailand, the final dataset consists of  55,361
images from 1,691 patients (3,179 eyes). Among the 3,179 eyes, 81.8% were examined in both
FA and ICGA modes, 10.3% underwent FA only, and the remaining 7.9% had ICGA only. Since
angiographic imaging methods are non-standardized and vary based on the specialist and patient,
the number of images per eye in this dataset ranges from a few to several hundred. The only
labeled images are those present in the original training split (33,559 images from 1,921 eyes).

The dataset covers 24 medical conditions and provides detailed descriptions of the type, location,
shape, size, and pattern of abnormal fluorescence. Specifically:
- Impression [multiclass]
- HyperF_Type [multiclass]
- HyperF_Area(DA) [multiclass]
- HyperF_Fovea [binary]
- HyperF_ExtraFovea	[multilabel]
- HyperF_Y [multilabel]
- HypoF_Type [multiclass]
- HypoF_Area(DA) [multiclass]
- HypoF_Fovea [binary]
- HypoF_ExtraFovea [multilabel]
- HypoF_Y [multilabel]
- CNV [binary]
- Vascular abnormality (DR)	[multilabel]
- Pattern [multilabel]

We keep only Fluorescein Angiography images in our setup. This reduces the dataset to 30,768
images from 1,877 eyes.

Data specifications:

* Raw data input (on disk):

  * JPEG grayscale images encoded as 8-bit sRGB, with varying resolution
    (most images being 384 x 364 pixels or 256 x 256 pixels, after being
    cropped to obtain only FA images).
  * Total samples: 30,768 (FA images) (Only last frame 1887)

* Output image:

  * Transforms:

    * Load raw JPEG with :py:mod:`PIL`, with auto-conversion to grayscale
    * Crop images to obtain only FA images
    * Convert to torch tensor

* Final specifications

  * Grayscale, encoded as a single plane tensor, 32-bit floats, with varying
    resolution depending on input.
  * Labels: they depend on the task selected.

This module contains the base declaration of common data modules and raw-data
loaders for this database. All configured splits inherit from this definition.
"""

import importlib.resources.abc
import os
import pathlib
import typing

import PIL.Image
import torch
from torchvision import tv_tensors
from torchvision.transforms.v2.functional import to_dtype, to_image

from ...utils.rc import load_rc
from ..datamodule import CachingDataModule
from ..split import JSONDatabaseSplit
from ..typing import RawDataLoader as BaseDataLoader
from ..typing import Sample

DATABASE_SLUG = __name__.rsplit(".", 1)[-1]
"""Pythonic name of this database."""

CONFIGURATION_KEY_DATADIR = "datadir." + DATABASE_SLUG
"""Key to search for in the configuration file for the root directory of this
database."""


class RawDataLoader(BaseDataLoader):
    """A specialized raw-data-loader for the 3rd Aptos Competition dataset.

    Parameters
    ----------
    problem_type
        Specifies the problem type for the current split. Can be ``binary`` or ``multiclass``.
        This parameter controls how the target labels are processed and retrieved from the
        dataset.
    """

    datadir: pathlib.Path
    """This variable contains the base directory where the database raw data is
    stored."""

    def __init__(self, problem_type: typing.Literal["binary", "multiclass"]):
        # Make sure that your mednet.toml file has an entry in datadir.3rd_aptos with the right path to the dataset
        # problem_type is already set up to add "multilabel". Not supported at the moment
        self.datadir = pathlib.Path(
            load_rc().get(
                CONFIGURATION_KEY_DATADIR,
                os.path.realpath(os.curdir),
            ),
        )
        # This attribute changes the way the target is retrieved
        self.problem_type = problem_type

    def sample(self, sample: typing.Any) -> Sample:
        """Load a single image sample from the disk.

        Parameters
        ----------
        sample
            Expects a tuple containing the path suffix, within the dataset root
            folder, where to find the image to be loaded, and an integer,
            representing the sample target.

        Returns
        -------
            The sample representation.
        """

        image = PIL.Image.open(self.datadir / sample[0]).convert("L")
        # crop the image to get only FA image
        width, height = image.size
        box = (0, 0, width - width / 2, height - 50)
        image = image.crop(box)

        image = to_dtype(to_image(image), torch.float32, scale=True)
        image = tv_tensors.Image(image)

        return dict(image=image, target=self.target(sample), name=sample[0])

    def target(self, sample: typing.Any) -> torch.Tensor:
        """Load only sample target from its raw representation.

        Parameters
        ----------
        sample
            A tuple containing the path suffix, within the dataset root folder,
            where to find the image to be loaded, and an integer, representing
            the sample target.

        Returns
        -------
            The label corresponding to the specified sample, encapsulated as a
            1D torch float or 0D long tensor (depending on the problem_type).
        """
        if self.problem_type == "binary":
            return torch.FloatTensor([sample[1]])
        return torch.LongTensor([sample[1]]).squeeze()


class DataModule(CachingDataModule):
    """3rd Aptos-competiotion dataset.

    Parameters
    ----------
    split_path
        Path or traversable (resource) with the JSON split description to load.
    num_classes
        Number of output classes for the task at hand.
    problem_type
        Specifies the problem type for the current split. Can be ``binary`` or ``multiclass``.
        This parameter controls how the target labels are processed and retrieved from the
        dataset.
    """

    def __init__(
        self,
        split_path: pathlib.Path | importlib.resources.abc.Traversable,
        num_classes: int,
        problem_type: typing.Literal["binary", "multiclass"],
    ):
        super().__init__(
            database_split=JSONDatabaseSplit(split_path),
            raw_data_loader=RawDataLoader(problem_type),
            database_name=DATABASE_SLUG,
            split_name=split_path.name.rsplit(".", 2)[0],
            task="classification",
            num_classes=num_classes,
        )
