# A program for automatically tiling microscope images

OpenFlexure Stitching is a Python package for tiling and stitching 2D microscope scans into panoramic images. This program has relatively few dependencies and runs quickly with low memory requirements.

The primary target for OpenFlexure Stitching is images collected on the OpenFlexure Microscope. It automatically reads OpenFlexure metadata from the image's ```exif``` data. If this ```exif``` data is not available it will try to infer the stage positions from the file name.

An example dataset can be downloaded from:  
[https://doi.org/10.5281/zenodo.13768403](https://doi.org/10.5281/zenodo.13768403)
[[_TOC_]]
## Installation

You can install OpenFlexure Stitching with

```
pip install openflexure-stitching[libvips]
```

This package requires Python 3.9 or later. Other dependencies should be declared in `pyproject.toml` (and automatically installed by pip).

**Note:** If you get an error that `pyvips-binary` could not be installed this means it is not packaged for your system. Instead you can run `pip install openflexure-stitching` to install OpenFlexure Stitching. But you will then need to [manually install libvips](https://www.libvips.org/install.html) onto your system and add it to the `PATH`.

## Running the program

This program is designed to work without user input. If you have a collection of images from an OpenFlexure Microscope scan, then from the terminal, running

    openflexure-stitch <path to folder of images>

will tile the images together.

Consulting `openflexure-stitch --help` will list available settings and options.

If the images are poorly stitched the first setting to try adjusting is `--high_pass_sigma`. If that doesn't help you can try setting thresholding to manual.

### Running on an OpenFlexure Microscope

OpenFlexure Stitching has been written to allow live stitching of microscope images in the upcoming `v3` release of the OpenFlexure Microscope Server. For the current `v2` OpenFlexure Microscope Server, the operating system is too old to support the correct version of Python. Until `v3` is stable and released (expected in late 2025), you will need to run OpenFlexure Stitching on a different computer.

## Use as a library

To use `openflexure-stitching` as a python-library rather than a command line program [see our API documentation](https://openflexure.gitlab.io/openflexure-stitching/).

## How it works

Given a folder path, OpenFlexure Stitching will use all images in the folder, ignoring any phrases contained in stitching outputs: 

`['stitched', 'comparison', 'Fused', 'stage', 'stitching', 'preview']` are all ignored.

After this the the program performs:

* Offset estimation
* Thresholding and placement optimisation
* Stitching images

as explained below.

### Offset estimation

For each image the stage position will be loaded and converted to image coordinates. Overlapping images are identified as images where the overlap is above the  `--minimum_overlap` parameter. Overlapping images are then compared by cross-correlation to calculate an improved estimate of displacement.

![](README_images/2d.png){width=50%}  
*A correlation map with a single, narrow peak. Useful for tiling.*

![](README_images/2d_fail.png){width=50%}  
*A correlation map with no clear peak or preference for offset. This cross-correlation should  removed by thresholding (see below).*

Cross-correlations are calculated from Fourier Transforms, this technically returns a circular cross-correlation.The circular cross-correlation introduces an ambiguity, this can be fixed by padding the images (default behaviour). Use `--no-pad` to stop the padding, this will reduce the memory requirements of this stage by a factor of 4, but introduces ambiguity. OpenFlexure Stitching will attempt to break this ambiguity, but this isn't 100% reliable.

One of the key advantages of OpenFlexure Stitching is that the correlation values are cached to disk after each run. If the settings are unchanged, the time consuming cross-correlations do not need to be repeated. As new images are added to the folder, only new offsets are calculated. This means live-updating scans can be tiled in near real-time.


### Thresholding and placement optimisation

From the image offsets calculated from cross-correlation, a least squares optimisation of absolute positions is performed. The correlation peaks between some pairs of images may be incorrect, and need to be ignored. For this reason, the fit can be performed with thresholds that ignore offsets which differ too much from the stage-estimated position or where the peak quality in the cross-correlation is too low.



As standard thresholding is automatic, it is adjusted to optimise the image positions. The RMS error of the least squares optimisation is used as a quality metric for thresholding. Multiple thresholds for both position discrepancy and peak quality are tested to create the best estimate of image position.

If manual thresholding is used the program will pause once all offsets have been estimated. Then, a graph will be saved to the file `stitching_correlations.png` showing the discrepancy between the stage-estimated offset and the correlation-estimated offset plotted against the quality of the correlation peak. By reading this graph the user can manually set thresholds.

![](README_images/scatter.png){width=75%}  
*A scatter plot of the quality of each cross-correlation between two images. In manual mode the discrepancy and peak quality can be set thresholds to exclude poorly cross-correlated image pairs from the final optimisation calculation. Colours are for clarity and have no data significance.*

### Stitching images

Finally the image is stitched together. By default a `jpeg` image is produced. For large scans the resulting images can be multiple giga-pixel, and very hard to open. Options also exist to create `dzi` (deep zoom images) and Pyramidal TIFFs. These both reduce the memory needed to open the image, but they require special software for viewing. When opened in microscopy programs such as Qupath, important metadata such as the physical pixel size will be used for labelling the image.

OpenFlexure Stitching also produces a ```OFMTileConfig.txt``` file, which can be read by Fiji Stitching, taking advantage of their range of blending and averaging. To avoid producing artefacts in scans, the stitching in OpenFlexure Stitching does no averaging between images.


## Development

Clone this repository by navigating in your terminal to your required containing folder. Run 
```
git clone https://gitlab.com/openflexure/openflexure-stitching
```
to download the files locally. 

Create and activate a virtual environment:

```
cd openflexure-stitching
python -m venv .venv
.\.venv\Scripts\activate
```

Upgrade `pip` if needed, so you can use the `pyproject.toml` based setup for an editable install

```
python -m pip install --upgrade pip
```

Install the necessary libraries using 
```
pip install -e .[libvips]
```
