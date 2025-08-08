"""
This submodule contains custom data types.

Some datatypes are Annotated for more clear typing within the codebase
others use Pydantic to ease serialising for caching to disk.
"""

from typing import Annotated, Union, Literal

import numpy as np
from pydantic import (
    BeforeValidator,
    BaseModel,
    PlainSerializer,
    RootModel,
    WithJsonSchema,
)

JPG_IMAGE = 0
"""Constant representing a JPEG image, for matching to OFSImage.filetype"""
TIFF_IMAGE = 1
"""Constant representing a TIFF image, for matching to OFSImage.filetype"""
PNG_IMAGE = 2
"""Constant representing a PNG image, for matching to OFSImage.filetype"""
GIF_IMAGE = 3
"""Constant representing a GIF image, for matching to OFSImage.filetype"""
BMP_IMAGE = 4
"""Constant representing a Bitmap image, for matching to OFSImage.filetype"""


ImageType = Literal[JPG_IMAGE, TIFF_IMAGE, PNG_IMAGE, GIF_IMAGE, BMP_IMAGE]
"""A type hint for any of the above image types."""


# Define a nested list of floats with 0-6 dimensions
# This would be most elegantly defined as a recursive type
# but the below gets the job done for now.
_Number = Union[int, float]
_NestedListOfNumbers = Union[
    _Number,
    list[_Number],
    list[list[_Number]],
    list[list[list[_Number]]],
    list[list[list[list[_Number]]]],
    list[list[list[list[list[_Number]]]]],
    list[list[list[list[list[list[_Number]]]]]],
    list[list[list[list[list[list[list]]]]]],
]


class _NestedListOfNumbersModel(RootModel):
    root: _NestedListOfNumbers


def _np_to_listoflists(arr: np.ndarray) -> _NestedListOfNumbers:
    """Convert a numpy array to a list of lists

    Note: this will not be quick! Large arrays will be much better
    serialised by dumping to base64 encoding or similar.
    """
    return arr.tolist()


def _listoflists_to_np(lol: _NestedListOfNumbers) -> np.ndarray:
    """Convert a list of lists to a numpy array"""
    return np.asarray(lol)


NDArray = Annotated[
    np.ndarray,
    BeforeValidator(_listoflists_to_np),
    PlainSerializer(_np_to_listoflists, when_used="json-unless-none"),
    WithJsonSchema(_NestedListOfNumbersModel.model_json_schema(), mode="validation"),
]
"""Define an annotated type so Pydantic can serialise and validate with numpy arrays"""


PairKeys = tuple[str, str]
"""A tuple of two image keys a pair of images"""


XYDisplacementInPixels = tuple[float, float]
"""A tuple of the xy displacement between two image in pixels"""


class PairData(BaseModel):
    """The results of correlating images together

    For convenience this also includes an estimate of the displacement between
    images as estimated from the stage coordinates and the transform matrix.
    """

    keys: PairKeys
    image_displacement: XYDisplacementInPixels
    stage_displacement: XYDisplacementInPixels
    # The proportion of pixels in the correlation image beneath a threshold
    fraction_under_threshold: dict[float, float]
