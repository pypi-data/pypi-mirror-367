"""The OpenFlexure metadata has changed over development and
was poorly defined. As such we need to test in a somewhat
ad hoc fashion
"""

import os
import tempfile
import shutil

import numpy as np
import pytest

from openflexure_stitching.settings import LoadingSettings, CorrelationSettings
from openflexure_stitching.loading import (
    OFSImage,
    CachedOFSImage,
    OFSImageSet,
    CachedOFSImageSet,
    CorrelatedImageSet,
    CachedCorrelatedImageSet,
)
from openflexure_stitching.loading.image_sets import find_images

THIS_DIR = os.path.dirname(os.path.realpath(__file__))


@pytest.fixture
def mock_correlation(mocker):
    """A fixture to patch displacement_from_crosscorrelation

    In these tests, we are testing the loading functionality, not how
    cross-correlation performs. As such, we do not want the
    cross-correlation function to run, as it is both slow, and because
    it will report as covered even though no checking specific to
    cross-correlation has been performed.

    Any test with this `mock_correlation` fixture as an argument
    will be "patched" so that a random number is returned for the
    cross-correlation positions and peak quality, rather than actually
    running the `displacement_from_crosscorrelation` function
    """
    mock = mocker.patch(
        "openflexure_stitching.loading.image_sets.displacement_from_crosscorrelation"
    )
    mock.side_effect = lambda *args, **kwargs: (np.random.randn(2), {0.9: np.random.randn()})
    return mock


def test_load_set():
    """
    Test that the program loads the 4 images from a specified test folder,
    caches them and that image data between cache and image is consistent
    """
    test_fpath = os.path.join(THIS_DIR, "images", "cropped")
    image_set = OFSImageSet(test_fpath, loading_settings=LoadingSettings())

    assert image_set.folder == test_fpath
    assert len(image_set) == 4

    for image in image_set:
        assert isinstance(image, OFSImage)

    # dump to json string and reload
    json_str = image_set.data_for_caching().model_dump_json()
    cached_image_set = CachedOFSImageSet.model_validate_json(json_str)
    assert isinstance(cached_image_set.images, dict)
    assert len(cached_image_set.images) == 4
    for key, value in cached_image_set.images.items():
        assert isinstance(value, CachedOFSImage)
        # Check the keys are correct and that the image set is indexable by key
        assert key in image_set.keys()
        assert isinstance(image_set[key], OFSImage)


def test_load_set_cache():
    """
    Tests that with no cache, all four images are loaded from disk.
    Once cache is used, all four images are from cache, and none from disk
    """
    test_fpath = os.path.join(THIS_DIR, "images", "cropped")
    # Load an image set with no cache
    image_set = OFSImageSet(test_fpath, loading_settings=LoadingSettings())

    # Cache the results, and reload the images from the cache
    json_str = image_set.data_for_caching().model_dump_json()
    image_set_from_cache = OFSImageSet(
        test_fpath, cached=CachedOFSImageSet.model_validate_json(json_str)
    )

    # The first image set should have loaded everything from disk, as there was no cache
    assert image_set.cache_stats["images_loaded_from_cache"] == 0
    assert image_set.cache_stats["images_loaded_from_disk"] == 4

    # The second image set should have everything in cache, as nothing changed between runs
    assert image_set_from_cache.cache_stats["images_loaded_from_cache"] == 4
    assert image_set_from_cache.cache_stats["images_loaded_from_disk"] == 0


def test_load_correlated_set_cache(mock_correlation):
    """
    Tests that cached images and correlations are used when made available
    """

    test_fpath = os.path.join(THIS_DIR, "images", "cropped")
    # Load an image set with no cache
    image_set = CorrelatedImageSet(test_fpath, loading_settings=LoadingSettings())

    # Cache the results to a string, and reload the images from the cached string
    json_str = image_set.data_for_caching().model_dump_json()
    image_set_from_cache = CorrelatedImageSet(
        test_fpath, cached=CachedCorrelatedImageSet.model_validate_json(json_str)
    )

    # The first image set should have loaded everything from disk, as there was no cache
    assert image_set.cache_stats["images_loaded_from_cache"] == 0
    assert image_set.cache_stats["images_loaded_from_disk"] == 4
    assert image_set.cache_stats["correlations_loaded_from_cache"] == 0
    assert image_set.cache_stats["correlations_loaded_from_disk"] == 6

    # The second image set should have everything in cache, as nothing changed between runs
    assert image_set_from_cache.cache_stats["images_loaded_from_cache"] == 4
    assert image_set_from_cache.cache_stats["images_loaded_from_disk"] == 0
    assert image_set_from_cache.cache_stats["correlations_loaded_from_cache"] == 6
    assert image_set_from_cache.cache_stats["correlations_loaded_from_disk"] == 0
    mock_correlation.assert_called()


def test_update_correlated_set_cache(mock_correlation):
    """
    Loads all three images from the folder, creates a cache.
    Then adds another image to the folder, and tests that cached images and
    correlations are loaded from the cache, and the new image and new correlations
    are loaded from disk.

    Note: we don't use the last image in the folder, showing that the cache can add and
    recognise images in any order
    """
    with tempfile.TemporaryDirectory() as test_fpath:
        image_path = os.path.join(THIS_DIR, "images", "cropped")

        # Get a list of the images currently in the folder
        image_list = find_images(image_path)

        image_to_delay = image_list[-2]
        for image in image_list:
            if image != image_to_delay:
                shutil.copy(os.path.join(image_path, image), test_fpath)

        # Build a set of images from the folder
        image_set = CorrelatedImageSet(test_fpath, loading_settings=LoadingSettings())

        shutil.copy(os.path.join(image_path, image_to_delay), test_fpath)

        # Load all four images from the folder, telling it to use the previous cache where possible
        image_set = CorrelatedImageSet(
            test_fpath, loading_settings=LoadingSettings(), cached=image_set.data_for_caching()
        )

        # image_set should have 3 cached images, one new image, and 3 new correlations
        # for the new overlaps
        assert image_set.cache_stats["images_loaded_from_cache"] == 3
        assert image_set.cache_stats["images_loaded_from_disk"] == 1
        assert image_set.cache_stats["correlations_loaded_from_cache"] == 3
        assert image_set.cache_stats["correlations_loaded_from_disk"] == 3
    mock_correlation.assert_called()


def test_cache_changing_loading(mock_correlation):
    """
    Tests that if the loading seetings are changed but the cache is used
    then the values are updated appropriately
    """
    test_fpath = os.path.join(THIS_DIR, "images", "cropped")

    image_set = CorrelatedImageSet(
        test_fpath,
        loading_settings=LoadingSettings(),
        correlation_settings=CorrelationSettings(high_pass_sigma=10),
    )

    # Load an image set from the cached file, but with a different CSM matrix
    # This should refuse to use the cache, as the image locations will change
    # with the CSM
    mod_image_set = CorrelatedImageSet(
        folder=test_fpath,
        loading_settings=LoadingSettings(csm_matrix=[[0, 1.1], [1.1, 0]]),
        correlation_settings=CorrelationSettings(high_pass_sigma=10),
        cached=image_set.data_for_caching(),
    )
    # The image set should have loaded everything from disk, as there was no cache
    assert mod_image_set.cache_stats["images_loaded_from_cache"] == 4
    assert mod_image_set.cache_stats["images_loaded_from_disk"] == 0
    assert mod_image_set.cache_stats["correlations_loaded_from_cache"] == 6
    assert mod_image_set.cache_stats["correlations_loaded_from_disk"] == 0

    # pylint is confused: it thinks image_set is a dict.
    # pylint: disable=consider-using-dict-items
    for key in image_set.keys():
        # Check the CSMs are different
        assert np.array_equal(image_set[key].camera_to_sample_matrix, [[0, 1], [1, 0]])
        assert np.array_equal(mod_image_set[key].camera_to_sample_matrix, [[0, 1.1], [1.1, 0]])
        # the stage positions are unchanged in stage coordinates
        assert image_set[key].stage_position == mod_image_set[key].stage_position

        # But are changed in image coordinates

        assert image_set[key].stage_position_px[0] == mod_image_set[key].stage_position_px[0] * 1.1
        assert image_set[key].stage_position_px[1] == mod_image_set[key].stage_position_px[1] * 1.1

    for orig_pair, mod_pair in zip(image_set.pairs, mod_image_set.pairs):
        # check the pairs are in same order
        assert orig_pair.keys == mod_pair.keys
        # That the correlated positions match
        assert orig_pair.image_displacement == mod_pair.image_displacement
        # But the stage ones don't
        assert orig_pair.image_displacement != mod_pair.stage_displacement
    mock_correlation.assert_called()


def test_cache_changing_correlations(mock_correlation):
    """
    Tests that a cache isn't used if correlation settings are altered.
    """
    test_fpath = os.path.join(THIS_DIR, "images", "cropped")

    default_cache = CorrelatedImageSet(
        test_fpath,
        loading_settings=LoadingSettings(),
        correlation_settings=CorrelationSettings(high_pass_sigma=10),
    ).data_for_caching()

    # An image set, with a different correlation setting
    with pytest.raises(ValueError):
        CorrelatedImageSet(
            folder=test_fpath,
            loading_settings=None,
            correlation_settings=CorrelationSettings(high_pass_sigma=50),
            cached=default_cache,
        )
    mock_correlation.assert_called()


def test_reduce_correlated_set_cache(mock_correlation):
    """
    Loads all four images from the folder, and tests they're cached appropriately.
    Then removes an image to the folder, and tests that cached images and
    correlations are loaded from the cache.
    """
    with tempfile.TemporaryDirectory() as test_fpath:
        image_path = os.path.join(THIS_DIR, "images", "cropped")

        # Get a list of the images currently in the folder
        image_list = find_images(image_path)

        for image in image_list:
            shutil.copy(os.path.join(image_path, image), test_fpath)

        # Build a set of images from the folder
        image_set = CorrelatedImageSet(test_fpath, loading_settings=LoadingSettings())

        # Delete a file
        os.remove(os.path.join(test_fpath, image_list[-2]))

        # Load directory again using cache
        image_set = CorrelatedImageSet(
            test_fpath, loading_settings=LoadingSettings(), cached=image_set.data_for_caching()
        )

        # The cached image set should contain all images, all correlations
        assert image_set.cache_stats["images_loaded_from_cache"] == 3
        assert image_set.cache_stats["images_loaded_from_disk"] == 0
        assert image_set.cache_stats["correlations_loaded_from_cache"] == 3
        assert image_set.cache_stats["correlations_loaded_from_disk"] == 0
    # Finally check the mocker was called
    mock_correlation.assert_called()
